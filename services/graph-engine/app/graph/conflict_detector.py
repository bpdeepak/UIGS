"""
UIGS Graph Engine - Conflict Detector

Detects conflicting claims in the identity graph.
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.models import ClaimNode
from app.graph.neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)


@dataclass
class Conflict:
    """Represents a conflict between two claims."""
    conflict_id: str
    attribute: str
    claim_a: ClaimNode
    claim_b: ClaimNode
    detected_at: datetime


class ConflictDetector:
    """
    Detects conflicting claims in the identity graph.
    
    A conflict occurs when:
    - Two claims have the same attribute (e.g., "dateOfBirth")
    - But different values (e.g., "1990-01-01" vs "1991-02-02")
    - Both belong to the same user
    
    When a conflict is detected, a CONTRADICTS edge is created.
    """
    
    def __init__(self, neo4j_client: Neo4jClient):
        self.client = neo4j_client
    
    async def detect_conflicts(
        self, user_id: str, new_claims: list[ClaimNode]
    ) -> list[Conflict]:
        """
        Detect conflicts between new claims and existing claims.
        
        Args:
            user_id: The user whose claims to check
            new_claims: List of newly created claim nodes
        
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        for new_claim in new_claims:
            # Find existing claims with the same attribute
            existing = await self.client.find_existing_claims(
                user_id, new_claim.attribute
            )
            
            for existing_claim in existing:
                # Skip if it's the same claim
                if existing_claim["node_id"] == new_claim.node_id:
                    continue
                
                # Check if values differ
                existing_value = str(existing_claim.get("value", ""))
                new_value = str(new_claim.value) if new_claim.value else ""
                
                if existing_value != new_value:
                    # Create CONTRADICTS edge
                    edge_id = await self.client.create_contradicts_edge(
                        new_claim.node_id,
                        existing_claim["node_id"],
                        confidence=1.0,
                    )
                    
                    # Create conflict object
                    conflict = Conflict(
                        conflict_id=edge_id,
                        attribute=new_claim.attribute,
                        claim_a=new_claim,
                        claim_b=ClaimNode(
                            node_id=existing_claim["node_id"],
                            attribute=existing_claim["attribute"],
                            value=existing_claim["value"],
                        ),
                        detected_at=datetime.utcnow(),
                    )
                    conflicts.append(conflict)
                    
                    logger.warning(
                        f"Conflict detected: {new_claim.attribute} = "
                        f"'{new_value}' vs '{existing_value}'"
                    )
        
        if conflicts:
            logger.info(f"Detected {len(conflicts)} conflicts for user {user_id}")
        
        return conflicts
    
    async def get_user_conflicts(self, user_id: str) -> list[dict[str, Any]]:
        """Get all conflicts for a user from the graph."""
        return await self.client.get_conflicts(user_id)
    
    async def resolve_conflict(
        self, conflict_id: str, preferred_claim_id: str
    ) -> bool:
        """
        Resolve a conflict by marking one claim as preferred.
        
        Future implementation: Add a PREFERRED edge or property.
        """
        # TODO: Implement conflict resolution
        logger.info(f"Resolving conflict {conflict_id}, preferred: {preferred_claim_id}")
        return True
