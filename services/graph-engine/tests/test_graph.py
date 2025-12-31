"""
Unit tests for the Credential Decomposer and Conflict Detector.
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.models import VerifiableCredential, ClaimNode
from app.graph.decomposer import CredentialDecomposer, DecompositionResult
from app.graph.conflict_detector import ConflictDetector, Conflict


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_vc_data():
    """Sample Verifiable Credential data."""
    return {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "type": ["VerifiableCredential", "UniversityDegreeCredential"],
        "issuer": {
            "id": "did:example:university123",
            "name": "Example University"
        },
        "issuanceDate": "2024-01-15T00:00:00Z",
        "credentialSubject": {
            "id": "did:example:student456",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "degree": {
                "type": "BachelorDegree",
                "name": "Computer Science"
            }
        }
    }


@pytest.fixture
def mock_neo4j_client():
    """Mock Neo4j client for testing."""
    client = AsyncMock()
    client.create_user_node = AsyncMock(return_value="user-123")
    client.create_credential_node = AsyncMock(return_value="cred-123")
    client.create_claim_node = AsyncMock(return_value="claim-123")
    client.create_supports_edge = AsyncMock(return_value="edge-123")
    client.create_contradicts_edge = AsyncMock(return_value="conflict-123")
    client.find_existing_claims = AsyncMock(return_value=[])
    return client


# =============================================================================
# VerifiableCredential Model Tests
# =============================================================================

class TestVerifiableCredential:
    """Tests for VerifiableCredential model."""
    
    def test_from_dict_parses_correctly(self, sample_vc_data):
        """Test that VC is parsed correctly from dict."""
        vc = VerifiableCredential.from_dict(sample_vc_data)
        
        assert vc.context == ["https://www.w3.org/2018/credentials/v1"]
        assert "UniversityDegreeCredential" in vc.type
        assert vc.issuance_date == "2024-01-15T00:00:00Z"
        assert vc.credential_subject["name"] == "John Doe"
    
    def test_get_issuer_id_from_object(self, sample_vc_data):
        """Test extracting issuer ID from object format."""
        vc = VerifiableCredential.from_dict(sample_vc_data)
        assert vc.get_issuer_id() == "did:example:university123"
    
    def test_get_issuer_id_from_string(self):
        """Test extracting issuer ID from string format."""
        vc = VerifiableCredential.from_dict({
            "@context": [],
            "type": [],
            "issuer": "did:example:issuer789",
            "credentialSubject": {}
        })
        assert vc.get_issuer_id() == "did:example:issuer789"
    
    def test_get_issuer_name(self, sample_vc_data):
        """Test extracting issuer name."""
        vc = VerifiableCredential.from_dict(sample_vc_data)
        assert vc.get_issuer_name() == "Example University"
    
    def test_get_credential_type(self, sample_vc_data):
        """Test getting specific credential type."""
        vc = VerifiableCredential.from_dict(sample_vc_data)
        assert vc.get_credential_type() == "UniversityDegreeCredential"


# =============================================================================
# CredentialDecomposer Tests
# =============================================================================

class TestCredentialDecomposer:
    """Tests for CredentialDecomposer."""
    
    @pytest.mark.asyncio
    async def test_decompose_creates_credential_node(
        self, sample_vc_data, mock_neo4j_client
    ):
        """Test that decompose creates a credential node."""
        vc = VerifiableCredential.from_dict(sample_vc_data)
        decomposer = CredentialDecomposer(mock_neo4j_client)
        
        result = await decomposer.decompose(vc, "user-123", "event-123")
        
        mock_neo4j_client.create_credential_node.assert_called_once()
        assert result.credential_node is not None
        assert result.credential_node.issuer == "did:example:university123"
    
    @pytest.mark.asyncio
    async def test_decompose_extracts_claims(
        self, sample_vc_data, mock_neo4j_client
    ):
        """Test that decompose extracts all claims."""
        vc = VerifiableCredential.from_dict(sample_vc_data)
        decomposer = CredentialDecomposer(mock_neo4j_client)
        
        result = await decomposer.decompose(vc, "user-123", "event-123")
        
        # Should extract: name, email, degree.type, degree.name (skips id)
        assert len(result.claim_nodes) == 4
        
        attributes = [c.attribute for c in result.claim_nodes]
        assert "name" in attributes
        assert "email" in attributes
        assert "degree.type" in attributes
        assert "degree.name" in attributes
    
    @pytest.mark.asyncio
    async def test_decompose_creates_supports_edges(
        self, sample_vc_data, mock_neo4j_client
    ):
        """Test that decompose creates SUPPORTS edges."""
        vc = VerifiableCredential.from_dict(sample_vc_data)
        decomposer = CredentialDecomposer(mock_neo4j_client)
        
        result = await decomposer.decompose(vc, "user-123", "event-123")
        
        # One SUPPORTS edge per claim
        assert mock_neo4j_client.create_supports_edge.call_count == 4
        assert result.edges_created == 4
    
    def test_extract_claims_flattens_nested(self):
        """Test that nested objects are flattened to dot notation."""
        decomposer = CredentialDecomposer(MagicMock())
        
        credential_subject = {
            "name": "Alice",
            "address": {
                "city": "New York",
                "country": "USA"
            }
        }
        
        claims = decomposer._extract_claims(credential_subject)
        
        assert ("name", "Alice") in claims
        assert ("address.city", "New York") in claims
        assert ("address.country", "USA") in claims


# =============================================================================
# ConflictDetector Tests
# =============================================================================

class TestConflictDetector:
    """Tests for ConflictDetector."""
    
    @pytest.mark.asyncio
    async def test_no_conflicts_when_no_existing_claims(self, mock_neo4j_client):
        """Test that no conflicts are detected when there are no existing claims."""
        mock_neo4j_client.find_existing_claims.return_value = []
        detector = ConflictDetector(mock_neo4j_client)
        
        new_claims = [
            ClaimNode(node_id="new-1", attribute="name", value="John")
        ]
        
        conflicts = await detector.detect_conflicts("user-123", new_claims)
        
        assert len(conflicts) == 0
    
    @pytest.mark.asyncio
    async def test_conflict_detected_when_values_differ(self, mock_neo4j_client):
        """Test that conflict is detected when values differ."""
        mock_neo4j_client.find_existing_claims.return_value = [
            {"node_id": "existing-1", "attribute": "name", "value": "Jane"}
        ]
        detector = ConflictDetector(mock_neo4j_client)
        
        new_claims = [
            ClaimNode(node_id="new-1", attribute="name", value="John")
        ]
        
        conflicts = await detector.detect_conflicts("user-123", new_claims)
        
        assert len(conflicts) == 1
        assert conflicts[0].attribute == "name"
        mock_neo4j_client.create_contradicts_edge.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_no_conflict_when_values_same(self, mock_neo4j_client):
        """Test that no conflict when values are the same."""
        mock_neo4j_client.find_existing_claims.return_value = [
            {"node_id": "existing-1", "attribute": "name", "value": "John"}
        ]
        detector = ConflictDetector(mock_neo4j_client)
        
        new_claims = [
            ClaimNode(node_id="new-1", attribute="name", value="John")
        ]
        
        conflicts = await detector.detect_conflicts("user-123", new_claims)
        
        assert len(conflicts) == 0
    
    @pytest.mark.asyncio
    async def test_skips_self_comparison(self, mock_neo4j_client):
        """Test that detector skips comparing claim to itself."""
        mock_neo4j_client.find_existing_claims.return_value = [
            {"node_id": "same-id", "attribute": "name", "value": "Different"}
        ]
        detector = ConflictDetector(mock_neo4j_client)
        
        new_claims = [
            ClaimNode(node_id="same-id", attribute="name", value="John")
        ]
        
        conflicts = await detector.detect_conflicts("user-123", new_claims)
        
        # Should skip because node_id matches
        assert len(conflicts) == 0
