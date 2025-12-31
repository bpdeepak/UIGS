"""
UIGS Graph Engine - Edge Models
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid


class EdgeType(str, Enum):
    """Types of edges in the identity graph."""
    SUPPORTS = "SUPPORTS"           # Credential -> Claim
    CONTRADICTS = "CONTRADICTS"     # Claim <-> Claim (conflicting values)
    DERIVED_FROM = "DERIVED_FROM"   # Claim -> Credential
    LIKELY_SAME = "LIKELY_SAME"     # Fragment ~ Fragment (probabilistic)
    CONFIRMED_SAME = "CONFIRMED_SAME"  # Fragment = Fragment (user confirmed)
    BELONGS_TO = "BELONGS_TO"       # Fragment/Credential -> User
    TEMPORAL_SUCCESSOR = "TEMPORAL_SUCCESSOR"  # Claim -> Claim (updated value)


@dataclass
class GraphEdge:
    """Represents an edge (relationship) in the identity graph."""
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    edge_type: EdgeType = EdgeType.SUPPORTS
    source_id: str = ""
    target_id: str = ""
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    properties: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert edge to dictionary for storage."""
        return {
            "edge_id": self.edge_id,
            "edge_type": self.edge_type.value,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "properties": self.properties,
        }
