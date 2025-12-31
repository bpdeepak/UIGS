"""
UIGS Graph Engine - Credential Models
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class VerifiableCredential:
    """Represents a W3C Verifiable Credential."""
    context: list[str] = field(default_factory=list)
    type: list[str] = field(default_factory=list)
    id: Optional[str] = None
    issuer: str | dict[str, Any] = ""
    issuance_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_subject: dict[str, Any] = field(default_factory=dict)
    proof: Optional[dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VerifiableCredential":
        """Create VC from dictionary (JSON payload)."""
        return cls(
            context=data.get("@context", []),
            type=data.get("type", []),
            id=data.get("id"),
            issuer=data.get("issuer", ""),
            issuance_date=data.get("issuanceDate"),
            expiration_date=data.get("expirationDate"),
            credential_subject=data.get("credentialSubject", {}),
            proof=data.get("proof"),
        )
    
    def get_issuer_id(self) -> str:
        """Extract issuer ID from issuer field."""
        if isinstance(self.issuer, str):
            return self.issuer
        elif isinstance(self.issuer, dict):
            return self.issuer.get("id", str(self.issuer))
        return str(self.issuer)
    
    def get_issuer_name(self) -> Optional[str]:
        """Extract issuer name if available."""
        if isinstance(self.issuer, dict):
            return self.issuer.get("name")
        return None
    
    def get_credential_type(self) -> str:
        """Get the most specific credential type."""
        # Filter out generic types
        specific_types = [t for t in self.type if t != "VerifiableCredential"]
        return specific_types[0] if specific_types else "VerifiableCredential"


@dataclass
class IngestionEvent:
    """Represents an ingestion event from RabbitMQ."""
    event_id: str = ""
    user_id: str = ""
    source_type: str = ""  # VC, OIDC, MANUAL
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IngestionEvent":
        """Create event from dictionary (queue message)."""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        
        return cls(
            event_id=data.get("event_id", ""),
            user_id=data.get("user_id", ""),
            source_type=data.get("source_type", ""),
            payload=data.get("payload", {}),
            timestamp=timestamp,
        )
