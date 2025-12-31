"""
UIGS Graph Engine - RabbitMQ Consumer

Consumes ingestion events from RabbitMQ and processes them into the graph.
"""
import asyncio
import json
import logging
from typing import Callable, Any

import aio_pika
from aio_pika import IncomingMessage
from aio_pika.abc import AbstractRobustConnection, AbstractChannel

from app.config import Settings
from app.models import IngestionEvent, VerifiableCredential
from app.graph import Neo4jClient, CredentialDecomposer, ConflictDetector

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """
    Consumes messages from RabbitMQ and processes them.
    
    Message flow:
    1. Receive message from graph.engine.queue
    2. Parse as IngestionEvent
    3. Based on source_type, process accordingly
    4. For VC: decompose into graph nodes
    5. Detect conflicts
    6. Acknowledge message
    """
    
    def __init__(
        self,
        settings: Settings,
        neo4j_client: Neo4jClient,
    ):
        self.settings = settings
        self.neo4j_client = neo4j_client
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None
        self._running = False
        
        # Initialize processors
        self.decomposer = CredentialDecomposer(neo4j_client)
        self.conflict_detector = ConflictDetector(neo4j_client)
    
    async def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        self.connection = await aio_pika.connect_robust(self.settings.rabbitmq_url)
        self.channel = await self.connection.channel()
        
        # Set QoS for fair dispatch
        await self.channel.set_qos(prefetch_count=10)
        
        logger.info(f"Connected to RabbitMQ, queue: {self.settings.rabbitmq_queue}")
    
    async def close(self) -> None:
        """Close the RabbitMQ connection."""
        self._running = False
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        logger.info("RabbitMQ connection closed")
    
    async def start_consuming(self) -> None:
        """Start consuming messages from the queue."""
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")
        
        # Declare queue (idempotent)
        queue = await self.channel.declare_queue(
            self.settings.rabbitmq_queue,
            durable=True,
        )
        
        self._running = True
        logger.info(f"Started consuming from {self.settings.rabbitmq_queue}")
        
        # Start consuming
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                if not self._running:
                    break
                await self._process_message(message)
    
    async def process_pending(self, max_messages: int = 100) -> int:
        """Process pending messages without blocking."""
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")
        
        queue = await self.channel.declare_queue(
            self.settings.rabbitmq_queue,
            durable=True,
        )
        
        processed = 0
        
        for _ in range(max_messages):
            try:
                message = await asyncio.wait_for(
                    queue.get(no_ack=False),
                    timeout=1.0,
                )
                await self._process_message(message)
                processed += 1
            except asyncio.TimeoutError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                break
        
        return processed
    
    async def _process_message(self, message: IncomingMessage) -> None:
        """Process a single message from the queue."""
        try:
            # Parse message body
            body = json.loads(message.body.decode())
            event = IngestionEvent.from_dict(body)
            
            logger.info(
                f"Processing event {event.event_id} "
                f"(type: {event.source_type}, user: {event.user_id})"
            )
            
            # Process based on source type
            if event.source_type == "VC":
                await self._process_vc(event)
            elif event.source_type == "OIDC":
                await self._process_oidc(event)
            else:
                logger.warning(f"Unknown source type: {event.source_type}")
            
            # Acknowledge message
            await message.ack()
            logger.debug(f"Message acknowledged: {event.event_id}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {e}")
            await message.reject(requeue=False)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await message.reject(requeue=True)  # Retry later
    
    async def _process_vc(self, event: IngestionEvent) -> None:
        """Process a Verifiable Credential event."""
        # Parse VC from payload
        vc = VerifiableCredential.from_dict(event.payload)
        
        logger.info(
            f"Processing VC: type={vc.get_credential_type()}, "
            f"issuer={vc.get_issuer_id()}"
        )
        
        # Decompose into graph nodes
        result = await self.decomposer.decompose(
            vc=vc,
            user_id=event.user_id,
            event_id=event.event_id,
        )
        
        # Detect conflicts with existing claims
        conflicts = await self.conflict_detector.detect_conflicts(
            user_id=event.user_id,
            new_claims=result.claim_nodes,
        )
        
        result.conflicts_detected = len(conflicts)
        
        logger.info(
            f"VC processed: {len(result.claim_nodes)} claims, "
            f"{result.edges_created} edges, {len(conflicts)} conflicts"
        )
    
    async def _process_oidc(self, event: IngestionEvent) -> None:
        """Process an OIDC token event."""
        # Extract standard OIDC claims
        payload = event.payload
        
        # Map OIDC claims to VC-like structure
        vc_payload = {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "type": ["VerifiableCredential", "OIDCCredential"],
            "issuer": payload.get("iss", "unknown"),
            "issuanceDate": payload.get("timestamp", ""),
            "credentialSubject": {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "name": payload.get("name"),
                "given_name": payload.get("given_name"),
                "family_name": payload.get("family_name"),
                "picture": payload.get("picture"),
            },
        }
        
        # Remove None values
        vc_payload["credentialSubject"] = {
            k: v for k, v in vc_payload["credentialSubject"].items()
            if v is not None
        }
        
        vc = VerifiableCredential.from_dict(vc_payload)
        
        result = await self.decomposer.decompose(
            vc=vc,
            user_id=event.user_id,
            event_id=event.event_id,
        )
        
        logger.info(f"OIDC processed: {len(result.claim_nodes)} claims")
