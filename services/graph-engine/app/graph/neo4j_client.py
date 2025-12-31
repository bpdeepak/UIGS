"""
UIGS Graph Engine - Neo4j Client
"""
import logging
from contextlib import asynccontextmanager
from typing import Any, Optional

from neo4j import AsyncGraphDatabase, AsyncDriver
from neo4j.exceptions import Neo4jError
from neo4j.time import DateTime as Neo4jDateTime

from app.models import GraphNode, GraphEdge, ClaimNode, CredentialNode, FragmentNode, EdgeType

logger = logging.getLogger(__name__)


def _serialize_properties(props: dict[str, Any]) -> dict[str, Any]:
    """Convert Neo4j types to JSON-serializable Python types."""
    result = {}
    for key, value in props.items():
        if isinstance(value, Neo4jDateTime):
            result[key] = value.isoformat()
        elif hasattr(value, 'isoformat'):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


class Neo4jClient:
    """Client for interacting with Neo4j graph database."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver: Optional[AsyncDriver] = None
    
    async def connect(self) -> None:
        """Establish connection to Neo4j."""
        self._driver = AsyncGraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password),
        )
        # Verify connectivity
        await self._driver.verify_connectivity()
        logger.info(f"Connected to Neo4j at {self.uri}")
        
        # Create indexes
        await self._create_indexes()
    
    async def close(self) -> None:
        """Close the Neo4j connection."""
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j connection closed")
    
    async def _create_indexes(self) -> None:
        """Create indexes for efficient querying."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (n:Claim) ON (n.attribute)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Claim) ON (n.node_id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Credential) ON (n.node_id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Fragment) ON (n.node_id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:User) ON (n.node_id)",
        ]
        async with self._driver.session() as session:
            for index_query in indexes:
                try:
                    await session.run(index_query)
                except Neo4jError as e:
                    logger.warning(f"Index creation warning: {e}")
    
    # =========================================================================
    # Node Operations
    # =========================================================================
    
    async def create_user_node(self, user_id: str) -> str:
        """Create or get a User node."""
        query = """
        MERGE (u:User {node_id: $user_id})
        ON CREATE SET u.created_at = datetime()
        RETURN u.node_id AS node_id
        """
        async with self._driver.session() as session:
            result = await session.run(query, user_id=user_id)
            record = await result.single()
            return record["node_id"]
    
    async def create_fragment_node(self, fragment: FragmentNode, user_id: str) -> str:
        """Create a Fragment node linked to a User."""
        query = """
        MATCH (u:User {node_id: $user_id})
        CREATE (f:Fragment {
            node_id: $node_id,
            source: $source,
            source_id: $source_id,
            created_at: datetime($created_at)
        })
        CREATE (f)-[:BELONGS_TO]->(u)
        RETURN f.node_id AS node_id
        """
        async with self._driver.session() as session:
            result = await session.run(
                query,
                user_id=user_id,
                node_id=fragment.node_id,
                source=fragment.source,
                source_id=fragment.source_id,
                created_at=fragment.created_at.isoformat(),
            )
            record = await result.single()
            return record["node_id"]
    
    async def create_credential_node(self, credential: CredentialNode, user_id: str) -> str:
        """Create a Credential node linked to a User."""
        query = """
        MATCH (u:User {node_id: $user_id})
        CREATE (c:Credential {
            node_id: $node_id,
            issuer: $issuer,
            credential_type: $credential_type,
            issuance_date: $issuance_date,
            created_at: datetime($created_at)
        })
        CREATE (c)-[:BELONGS_TO]->(u)
        RETURN c.node_id AS node_id
        """
        async with self._driver.session() as session:
            result = await session.run(
                query,
                user_id=user_id,
                node_id=credential.node_id,
                issuer=credential.issuer,
                credential_type=credential.credential_type,
                issuance_date=credential.issuance_date.isoformat() if credential.issuance_date else None,
                created_at=credential.created_at.isoformat(),
            )
            record = await result.single()
            return record["node_id"]
    
    async def create_claim_node(self, claim: ClaimNode) -> str:
        """Create a Claim node."""
        query = """
        CREATE (c:Claim {
            node_id: $node_id,
            attribute: $attribute,
            value: $value,
            confidence: $confidence,
            created_at: datetime($created_at)
        })
        RETURN c.node_id AS node_id
        """
        async with self._driver.session() as session:
            result = await session.run(
                query,
                node_id=claim.node_id,
                attribute=claim.attribute,
                value=str(claim.value) if claim.value is not None else None,
                confidence=claim.confidence,
                created_at=claim.created_at.isoformat(),
            )
            record = await result.single()
            return record["node_id"]
    
    # =========================================================================
    # Edge Operations
    # =========================================================================
    
    async def create_supports_edge(self, credential_id: str, claim_id: str) -> str:
        """Create a SUPPORTS edge from Credential to Claim."""
        query = """
        MATCH (cr:Credential {node_id: $credential_id})
        MATCH (cl:Claim {node_id: $claim_id})
        CREATE (cr)-[r:SUPPORTS {
            edge_id: randomUUID(),
            created_at: datetime()
        }]->(cl)
        RETURN r.edge_id AS edge_id
        """
        async with self._driver.session() as session:
            result = await session.run(
                query, credential_id=credential_id, claim_id=claim_id
            )
            record = await result.single()
            return record["edge_id"]
    
    async def create_contradicts_edge(
        self, claim_a_id: str, claim_b_id: str, confidence: float = 1.0
    ) -> str:
        """Create a CONTRADICTS edge between two Claims."""
        query = """
        MATCH (a:Claim {node_id: $claim_a_id})
        MATCH (b:Claim {node_id: $claim_b_id})
        CREATE (a)-[r:CONTRADICTS {
            edge_id: randomUUID(),
            confidence: $confidence,
            created_at: datetime()
        }]->(b)
        RETURN r.edge_id AS edge_id
        """
        async with self._driver.session() as session:
            result = await session.run(
                query,
                claim_a_id=claim_a_id,
                claim_b_id=claim_b_id,
                confidence=confidence,
            )
            record = await result.single()
            return record["edge_id"]
    
    # =========================================================================
    # Query Operations
    # =========================================================================
    
    async def get_user_graph(self, user_id: str) -> dict[str, Any]:
        """Get the complete identity graph for a user."""
        query = """
        MATCH (u:User {node_id: $user_id})
        OPTIONAL MATCH (n)-[:BELONGS_TO]->(u)
        OPTIONAL MATCH (n)-[r]-(m)
        WITH collect(DISTINCT n) + collect(DISTINCT m) AS all_nodes,
             collect(DISTINCT r) AS all_edges
        UNWIND all_nodes AS node
        WITH collect(DISTINCT node) AS nodes, all_edges
        RETURN nodes, all_edges AS edges
        """
        async with self._driver.session() as session:
            result = await session.run(query, user_id=user_id)
            record = await result.single()
            
            if not record:
                return {"nodes": [], "edges": []}
            
            nodes = []
            for node in record["nodes"]:
                if node:
                    nodes.append({
                        "node_id": node.get("node_id"),
                        "node_type": list(node.labels)[0] if node.labels else "Unknown",
                        "properties": _serialize_properties(dict(node)),
                    })
            
            edges = []
            for edge in record["edges"]:
                if edge:
                    edges.append({
                        "edge_id": edge.get("edge_id", str(edge.id)),
                        "edge_type": edge.type,
                        "source_id": edge.start_node.get("node_id"),
                        "target_id": edge.end_node.get("node_id"),
                        "confidence": edge.get("confidence", 1.0),
                    })
            
            return {"nodes": nodes, "edges": edges}
    
    async def find_existing_claims(
        self, user_id: str, attribute: str
    ) -> list[dict[str, Any]]:
        """Find existing claims with the same attribute for a user."""
        query = """
        MATCH (u:User {node_id: $user_id})
        MATCH (c:Claim {attribute: $attribute})<-[:SUPPORTS]-(cr:Credential)-[:BELONGS_TO]->(u)
        RETURN c.node_id AS node_id, c.attribute AS attribute, c.value AS value
        """
        async with self._driver.session() as session:
            result = await session.run(query, user_id=user_id, attribute=attribute)
            records = await result.data()
            return records
    
    async def get_node_by_id(self, node_id: str) -> Optional[dict[str, Any]]:
        """Get a node by its ID."""
        query = """
        MATCH (n {node_id: $node_id})
        RETURN n, labels(n) AS labels
        """
        async with self._driver.session() as session:
            result = await session.run(query, node_id=node_id)
            record = await result.single()
            
            if not record:
                return None
            
            node = record["n"]
            return {
                "node_id": node.get("node_id"),
                "node_type": record["labels"][0] if record["labels"] else "Unknown",
                "properties": _serialize_properties(dict(node)),
            }
    
    async def get_conflicts(self, user_id: str) -> list[dict[str, Any]]:
        """Get all conflicts for a user."""
        query = """
        MATCH (u:User {node_id: $user_id})
        MATCH (c1:Claim)-[r:CONTRADICTS]-(c2:Claim)
        WHERE (c1)<-[:SUPPORTS]-(:Credential)-[:BELONGS_TO]->(u)
        RETURN DISTINCT
            r.edge_id AS conflict_id,
            c1.attribute AS attribute,
            c1.node_id AS claim_a_id,
            c1.value AS claim_a_value,
            c2.node_id AS claim_b_id,
            c2.value AS claim_b_value
        """
        async with self._driver.session() as session:
            result = await session.run(query, user_id=user_id)
            return await result.data()
