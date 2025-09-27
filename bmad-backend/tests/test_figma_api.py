import pytest
import os
import sys
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.models import ManagedDocument
from app.security import get_current_user
from app.services.token_service import TokenService

# Test credentials from environment
FIGMA_TEST_TOKEN = os.getenv("FIGMA_TEST_TOKEN")
FIGMA_TEST_URL = os.getenv("FIGMA_TEST_URL")

def extract_file_id_from_url(url: str) -> str:
    """Extract Figma file ID from URL."""
    if "/design/" in url:
        return url.split("/design/")[1].split("/")[0]
    elif "/file/" in url:
        return url.split("/file/")[1].split("/")[0]
    else:
        raise ValueError("Invalid Figma URL format")

FIGMA_TEST_FILE_ID = extract_file_id_from_url(FIGMA_TEST_URL) if FIGMA_TEST_URL else None

class TestFigmaAPI:
    """Test suite for credentials-related endpoints (Figma specific API endpoints are not implemented)."""

    @pytest.fixture
    def client(self):
        # Provide dependency override to bypass real auth
        async def mock_user():
            return {"id": "test-user-id", "username": "tester", "name": "Tester", "email": "t@example.com"}
        app.dependency_overrides[get_current_user] = mock_user
        return TestClient(app)
    
    @pytest.fixture
    def test_session_id(self):
        """Generate a test session ID."""
        return "test_session_api"
    
    def test_store_figma_credentials(self, client, test_session_id):
        """Test storing Figma credentials."""
        if not FIGMA_TEST_TOKEN:
            pytest.skip("FIGMA_TEST_TOKEN not available")
        
        credentials_data = {
            "session_id": test_session_id,
            "service": "figma",
            "credentials": {
                "token": FIGMA_TEST_TOKEN,
                "email": ""
            }
        }
        
        response = client.post("/api/credentials", json=credentials_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["message"] == "Credentials stored for figma"
        assert result["session_id"] == test_session_id
        
        print(f"\n=== Store Credentials Test ===")
        print(f"Response: {result}")
    
    def test_get_figma_credentials(self, client, test_session_id):
        """Test retrieving Figma credentials."""
        if not FIGMA_TEST_TOKEN:
            pytest.skip("FIGMA_TEST_TOKEN not available")
        
        # First store credentials
        credentials_data = {
            "session_id": test_session_id,
            "service": "figma",
            "credentials": {
                "token": FIGMA_TEST_TOKEN,
                "email": ""
            }
        }
        client.post("/api/credentials", json=credentials_data)
        
        # Then retrieve them
        response = client.get(f"/api/credentials/{test_session_id}/figma")
        
        assert response.status_code == 200
        result = response.json()
        assert result["token"] == FIGMA_TEST_TOKEN
        assert "email" in result
        
        print(f"\n=== Get Credentials Test ===")
        print(f"Retrieved credentials: {result}")
    
    def test_get_credentials_not_found(self, client):
        """Test getting credentials for non-existent session."""
        response = client.get("/api/credentials/nonexistent_session/figma")
        
        assert response.status_code == 404
        result = response.json()
        assert "Session not found" in result["detail"]
    
    def test_get_service_not_found(self, client, test_session_id):
        """Test getting credentials for non-existent service."""
        # Store credentials for figma
        if FIGMA_TEST_TOKEN:
            credentials_data = {
                "session_id": test_session_id,
                "service": "figma",
                "credentials": {
                    "token": FIGMA_TEST_TOKEN,
                    "email": ""
                }
            }
            client.post("/api/credentials", json=credentials_data)
        
        # Try to get credentials for a different service
        response = client.get(f"/api/credentials/{test_session_id}/jira")
        
        assert response.status_code == 404
        result = response.json()
        assert "Credentials for jira not found" in result["detail"]
    
    def test_get_figma_components_endpoint(self):
        pytest.skip("/api/figma/components endpoint not implemented in current application")
    
    def test_get_figma_user_flows_endpoint(self):
        pytest.skip("/api/figma/user-flows endpoint not implemented in current application")
    
    def test_figma_components_without_credentials(self):
        pytest.skip("/api/figma/components endpoint not implemented in current application")
    
    def test_figma_user_flows_without_credentials(self):
        pytest.skip("/api/figma/user-flows endpoint not implemented in current application")
    
    def test_figma_components_missing_parameters(self):
        pytest.skip("/api/figma/components endpoint not implemented in current application")
    
    def test_figma_user_flows_missing_parameters(self):
        pytest.skip("/api/figma/user-flows endpoint not implemented in current application")
    
    def test_get_documents_after_figma_operations(self, client, test_session_id):
        """Test that documents are created and retrievable."""
        if not FIGMA_TEST_TOKEN or not FIGMA_TEST_FILE_ID:
            pytest.skip("FIGMA_TEST_TOKEN or FIGMA_TEST_FILE_ID not available")
        pytest.skip("/api/figma/components endpoint not implemented in current application")

if __name__ == "__main__":
    # Print test configuration
    print("=== Figma API Test Configuration ===")
    print(f"FIGMA_TEST_TOKEN: {'Set' if FIGMA_TEST_TOKEN else 'Not Set'}")
    print(f"FIGMA_TEST_URL: {FIGMA_TEST_URL if FIGMA_TEST_URL else 'Not Set'}")
    print(f"FIGMA_TEST_FILE_ID: {FIGMA_TEST_FILE_ID if FIGMA_TEST_FILE_ID else 'Not Set'}")
    print("=" * 40)
    
    # Run the tests
    pytest.main([__file__, "-v", "-s"])