"""
UIGS Graph Engine - Node Models
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid


class NodeType(str, Enum):
    """Types of nodes in the identity graph."""
    USER = "User"
    FRAGMENT = "Fragment"
    CREDENTIAL = "Credential"
    CLAIM = "Claim"
    CONTEXT = "Context"


@dataclass
class GraphNode:
    """Base class for all graph nodes."""
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_type: NodeType = NodeType.FRAGMENT
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary for Neo4j."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


@dataclass
class ClaimNode(GraphNode):
    """Represents an atomic identity claim (e.g., name=John Doe)."""
    attribute: str = ""
    value: Any = None
    confidence: float = 1.0
    
    def __post_init__(self):
        self.node_type = NodeType.CLAIM
        self.properties.update({
            "attribute": self.attribute,
            "value": str(self.value) if self.value is not None else None,
            "confidence": self.confidence,
        })


@dataclass
class CredentialNode(GraphNode):
    """Represents a Verifiable Credential."""
    issuer: str = ""
    credential_type: str = ""
    issuance_date: Optional[datetime] = None
    
    def __post_init__(self):
        self.node_type = NodeType.CREDENTIAL
        self.properties.update({
            "issuer": self.issuer,
            "credential_type": self.credential_type,
            "issuance_date": self.issuance_date.isoformat() if self.issuance_date else None,
        })


@dataclass
class FragmentNode(GraphNode):
    """Represents an identity fragment (e.g., a user account from a specific source)."""
    source: str = ""
    source_id: str = ""
    
    def __post_init__(self):
        self.node_type = NodeType.FRAGMENT
        self.properties.update({
            "source": self.source,
            "source_id": self.source_id,
        })
