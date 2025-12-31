"""
UIGS Graph Engine - GraphQL Resolvers

Implements the query and mutation resolvers.
"""
import strawberry
from datetime import datetime
from typing import Optional

from app.api.schema import (
    IdentityGraphType,
    GraphNodeType,
    GraphEdgeType,
    ConflictType,
    ProcessingResultType,
    HealthType,
)


def create_schema(neo4j_client, consumer) -> strawberry.Schema:
    """Create the GraphQL schema with resolvers."""
    
    @strawberry.type
    class Query:
        @strawberry.field
        async def health(self) -> HealthType:
            """Check the health of the service."""
            neo4j_status = "healthy"
            rabbitmq_status = "healthy"
            
            try:
                if neo4j_client._driver:
                    await neo4j_client._driver.verify_connectivity()
            except Exception:
                neo4j_status = "unhealthy"
            
            try:
                if consumer.connection and not consumer.connection.is_closed:
                    rabbitmq_status = "healthy"
                else:
                    rabbitmq_status = "disconnected"
            except Exception:
                rabbitmq_status = "unhealthy"
            
            overall = "healthy" if neo4j_status == "healthy" and rabbitmq_status == "healthy" else "degraded"
            
            return HealthType(
                status=overall,
                neo4j=neo4j_status,
                rabbitmq=rabbitmq_status,
                timestamp=datetime.utcnow().isoformat(),
            )
        
        @strawberry.field
        async def identity_graph(self, user_id: Optional[str] = None) -> IdentityGraphType:
            """Get the identity graph for a user."""
            from app.config import get_settings
            
            if not user_id:
                user_id = get_settings().default_user_id
            
            graph_data = await neo4j_client.get_user_graph(user_id)
            
            nodes = [
                GraphNodeType(
                    node_id=n["node_id"],
                    node_type=n["node_type"],
                    properties=n["properties"],
                )
                for n in graph_data.get("nodes", [])
                if n.get("node_id")
            ]
            
            edges = [
                GraphEdgeType(
                    edge_id=e.get("edge_id", ""),
                    edge_type=e.get("edge_type", ""),
                    source_id=e.get("source_id", ""),
                    target_id=e.get("target_id", ""),
                    confidence=e.get("confidence", 1.0),
                )
                for e in graph_data.get("edges", [])
                if e.get("edge_type")
            ]
            
            return IdentityGraphType(
                nodes=nodes,
                edges=edges,
                node_count=len(nodes),
                edge_count=len(edges),
            )
        
        @strawberry.field
        async def node(self, node_id: str) -> Optional[GraphNodeType]:
            """Get a specific node by ID."""
            node_data = await neo4j_client.get_node_by_id(node_id)
            
            if not node_data:
                return None
            
            return GraphNodeType(
                node_id=node_data["node_id"],
                node_type=node_data["node_type"],
                properties=node_data["properties"],
            )
        
        @strawberry.field
        async def conflicts(self, user_id: Optional[str] = None) -> list[ConflictType]:
            """Get all conflicts for a user."""
            from app.config import get_settings
            
            if not user_id:
                user_id = get_settings().default_user_id
            
            conflicts_data = await neo4j_client.get_conflicts(user_id)
            
            return [
                ConflictType(
                    conflict_id=c.get("conflict_id", ""),
                    attribute=c.get("attribute", ""),
                    claim_a_id=c.get("claim_a_id", ""),
                    claim_a_value=str(c.get("claim_a_value", "")),
                    claim_b_id=c.get("claim_b_id", ""),
                    claim_b_value=str(c.get("claim_b_value", "")),
                )
                for c in conflicts_data
            ]
    
    @strawberry.type
    class Mutation:
        @strawberry.mutation
        async def process_pending_events(
            self, max_messages: int = 100
        ) -> ProcessingResultType:
            """Process pending messages from the queue."""
            try:
                processed = await consumer.process_pending(max_messages)
                return ProcessingResultType(
                    success=True,
                    messages_processed=processed,
                    errors=[],
                )
            except Exception as e:
                return ProcessingResultType(
                    success=False,
                    messages_processed=0,
                    errors=[str(e)],
                )
        
        @strawberry.mutation
        async def confirm_link(
            self, fragment_a_id: str, fragment_b_id: str
        ) -> bool:
            """Confirm that two fragments belong to the same identity."""
            # TODO: Implement in Phase 4
            return True
        
        @strawberry.mutation
        async def reject_link(
            self, fragment_a_id: str, fragment_b_id: str
        ) -> bool:
            """Reject a suggested link between fragments."""
            # TODO: Implement in Phase 4
            return True
        
        @strawberry.mutation
        async def resolve_conflict(
            self, conflict_id: str, preferred_claim_id: str
        ) -> bool:
            """Resolve a conflict by marking a claim as preferred."""
            from app.graph import ConflictDetector
            detector = ConflictDetector(neo4j_client)
            return await detector.resolve_conflict(conflict_id, preferred_claim_id)
    
    return strawberry.Schema(query=Query, mutation=Mutation)
