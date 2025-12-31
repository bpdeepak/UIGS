"""
UIGS Graph Engine - Credential Decomposer

Decomposes Verifiable Credentials into atomic graph nodes and edges.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.models import (
    VerifiableCredential,
    ClaimNode,
    CredentialNode,
    FragmentNode,
    GraphEdge,
    EdgeType,
)
from app.graph.neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)


@dataclass
class DecompositionResult:
    """Result of decomposing a credential into graph elements."""
    credential_node: CredentialNode
    claim_nodes: list[ClaimNode] = field(default_factory=list)
    fragment_node: FragmentNode | None = None
    edges_created: int = 0
    conflicts_detected: int = 0


class CredentialDecomposer:
    """
    Decomposes a Verifiable Credential into atomic graph nodes.
    
    Process:
    1. Parse VC and extract metadata
    2. Create CredentialNode for the VC
    3. Extract claims from credentialSubject
    4. For each claim, create ClaimNode
    5. Create SUPPORTS edges (Credential -> Claim)
    """
    
    def __init__(self, neo4j_client: Neo4jClient):
        self.client = neo4j_client
    
    async def decompose(
        self, vc: VerifiableCredential, user_id: str, event_id: str
    ) -> DecompositionResult:
        """
        Decompose a Verifiable Credential into graph nodes and edges.
        
        Args:
            vc: The Verifiable Credential to decompose
            user_id: The user who owns this credential
            event_id: The ingestion event ID for traceability
        
        Returns:
            DecompositionResult with created nodes and statistics
        """
        logger.info(f"Decomposing credential for user {user_id}, event {event_id}")
        
        # Ensure user node exists
        await self.client.create_user_node(user_id)
        
        # Parse issuance date
        issuance_date = None
        if vc.issuance_date:
            try:
                issuance_date = datetime.fromisoformat(
                    vc.issuance_date.replace("Z", "+00:00")
                )
            except ValueError:
                logger.warning(f"Could not parse issuance date: {vc.issuance_date}")
        
        # Create Credential node
        credential_node = CredentialNode(
            issuer=vc.get_issuer_id(),
            credential_type=vc.get_credential_type(),
            issuance_date=issuance_date,
        )
        credential_node.properties["event_id"] = event_id
        credential_node.properties["issuer_name"] = vc.get_issuer_name()
        
        await self.client.create_credential_node(credential_node, user_id)
        logger.debug(f"Created credential node: {credential_node.node_id}")
        
        # Extract and create claim nodes
        claims = self._extract_claims(vc.credential_subject)
        claim_nodes = []
        edges_created = 0
        
        for attribute, value in claims:
            # Skip the 'id' field (subject identifier)
            if attribute == "id":
                continue
            
            claim_node = ClaimNode(
                attribute=attribute,
                value=value,
                confidence=1.0,
            )
            
            await self.client.create_claim_node(claim_node)
            await self.client.create_supports_edge(
                credential_node.node_id, claim_node.node_id
            )
            
            claim_nodes.append(claim_node)
            edges_created += 1
            
            logger.debug(f"Created claim: {attribute} = {value}")
        
        result = DecompositionResult(
            credential_node=credential_node,
            claim_nodes=claim_nodes,
            edges_created=edges_created,
        )
        
        logger.info(
            f"Decomposition complete: {len(claim_nodes)} claims, "
            f"{edges_created} edges created"
        )
        
        return result
    
    def _extract_claims(
        self, credential_subject: dict[str, Any], prefix: str = ""
    ) -> list[tuple[str, Any]]:
        """
        Recursively extract claims from the credential subject.
        
        Flattens nested objects into dot-notation keys.
        e.g., {"degree": {"type": "BS"}} -> [("degree.type", "BS")]
        """
        claims = []
        
        for key, value in credential_subject.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # Recurse into nested objects
                claims.extend(self._extract_claims(value, full_key))
            elif isinstance(value, list):
                # Handle arrays - store as JSON string for now
                claims.append((full_key, str(value)))
            else:
                # Atomic value
                claims.append((full_key, value))
        
        return claims
