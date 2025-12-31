"""
UIGS Graph Engine - GraphQL Schema

Defines the GraphQL schema using Strawberry.
"""
import strawberry
from typing import Optional
from datetime import datetime


@strawberry.type
class ClaimType:
    """GraphQL type for a Claim node."""
    node_id: str
    attribute: str
    value: Optional[str]
    confidence: float
    created_at: Optional[str] = None


@strawberry.type
class CredentialType:
    """GraphQL type for a Credential node."""
    node_id: str
    issuer: str
    issuer_name: Optional[str]
    credential_type: str
    issuance_date: Optional[str]
    created_at: Optional[str] = None


@strawberry.type
class FragmentType:
    """GraphQL type for a Fragment node."""
    node_id: str
    source: str
    source_id: str
    created_at: Optional[str] = None


@strawberry.type
class GraphNodeType:
    """GraphQL type for a generic graph node."""
    node_id: str
    node_type: str
    properties: strawberry.scalars.JSON


@strawberry.type
class GraphEdgeType:
    """GraphQL type for a graph edge."""
    edge_id: str
    edge_type: str
    source_id: str
    target_id: str
    confidence: float


@strawberry.type
class IdentityGraphType:
    """GraphQL type for the complete identity graph."""
    nodes: list[GraphNodeType]
    edges: list[GraphEdgeType]
    node_count: int
    edge_count: int


@strawberry.type
class ConflictType:
    """GraphQL type for a detected conflict."""
    conflict_id: str
    attribute: str
    claim_a_id: str
    claim_a_value: str
    claim_b_id: str
    claim_b_value: str


@strawberry.type
class ProcessingResultType:
    """GraphQL type for processing result."""
    success: bool
    messages_processed: int
    errors: list[str]


@strawberry.type
class HealthType:
    """GraphQL type for health check."""
    status: str
    neo4j: str
    rabbitmq: str
    timestamp: str
