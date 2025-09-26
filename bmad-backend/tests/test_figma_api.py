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
    """Test suite for Figma API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
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
    
    @pytest.mark.skipif(not FIGMA_TEST_TOKEN or not FIGMA_TEST_FILE_ID, 
                       reason="FIGMA_TEST_TOKEN or FIGMA_TEST_FILE_ID not available")
    def test_get_figma_components_endpoint(self, client, test_session_id):
        """Test the Figma components API endpoint."""
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
        
        # Then request components
        components_request = {
            "session_id": test_session_id,
            "file_id": FIGMA_TEST_FILE_ID
        }
        
        response = client.post("/api/figma/components", json=components_request)
        
        assert response.status_code == 200
        result = response.json()
        
        if "error" not in result:
            assert "components" in result
            assert "file_name" in result
            assert "total_components" in result
            assert "document_id" in result
            
            print(f"\n=== Figma Components API Test ===")
            print(f"File Name: {result['file_name']}")
            print(f"Total Components: {result['total_components']}")
            print(f"Document ID: {result['document_id']}")
            if result["components"]:
                print("Sample Components:")
                for i, component in enumerate(result["components"][:2]):  # Show first 2
                    print(f"  {i+1}. {component.get('name', 'Unnamed')} ({component.get('type', 'Unknown')})")
        else:
            print(f"\n=== Figma Components API Error ===")
            print(f"Error: {result['error']}")
            pytest.skip(f"Figma API access error: {result['error']}")
    
    @pytest.mark.skipif(not FIGMA_TEST_TOKEN or not FIGMA_TEST_FILE_ID, 
                       reason="FIGMA_TEST_TOKEN or FIGMA_TEST_FILE_ID not available")
    def test_get_figma_user_flows_endpoint(self, client, test_session_id):
        """Test the Figma user flows API endpoint."""
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
        
        # Then request user flows
        flows_request = {
            "session_id": test_session_id,
            "file_id": FIGMA_TEST_FILE_ID
        }
        
        response = client.post("/api/figma/user-flows", json=flows_request)
        
        assert response.status_code == 200
        result = response.json()
        
        if "error" not in result:
            assert "user_flows" in result
            assert "screens" in result
            assert "file_name" in result
            assert "total_screens" in result
            assert "total_flows" in result
            assert "document_id" in result
            
            print(f"\n=== Figma User Flows API Test ===")
            print(f"File Name: {result['file_name']}")
            print(f"Total Screens: {result['total_screens']}")
            print(f"Total Flows: {result['total_flows']}")
            print(f"Document ID: {result['document_id']}")
            if result["screens"]:
                print("Sample Screens:")
                for i, screen in enumerate(result["screens"][:2]):  # Show first 2
                    print(f"  {i+1}. {screen.get('name', 'Unnamed')} ({screen.get('type', 'Unknown')})")
        else:
            print(f"\n=== Figma User Flows API Error ===")
            print(f"Error: {result['error']}")
            pytest.skip(f"Figma API access error: {result['error']}")
    
    def test_figma_components_without_credentials(self, client):
        """Test Figma components endpoint without stored credentials."""
        # Use a session that definitely doesn't exist
        components_request = {
            "session_id": "nonexistent_session_12345",
            "file_id": "test_file_id"
        }
        
        response = client.post("/api/figma/components", json=components_request)
        
        assert response.status_code == 401
        result = response.json()
        assert "Figma credentials not found" in result["detail"]
    
    def test_figma_user_flows_without_credentials(self, client):
        """Test Figma user flows endpoint without stored credentials."""
        # Use a session that definitely doesn't exist
        flows_request = {
            "session_id": "nonexistent_session_12345",
            "file_id": "test_file_id"
        }
        
        response = client.post("/api/figma/user-flows", json=flows_request)
        
        assert response.status_code == 401
        result = response.json()
        assert "Figma credentials not found" in result["detail"]
    
    def test_figma_components_missing_parameters(self, client):
        """Test Figma components endpoint with missing parameters."""
        # Missing file_id
        response = client.post("/api/figma/components", json={"session_id": "test"})
        assert response.status_code == 400
        
        # Missing session_id
        response = client.post("/api/figma/components", json={"file_id": "test"})
        assert response.status_code == 400
        
        # Missing both
        response = client.post("/api/figma/components", json={})
        assert response.status_code == 400
    
    def test_figma_user_flows_missing_parameters(self, client):
        """Test Figma user flows endpoint with missing parameters."""
        # Missing file_id
        response = client.post("/api/figma/user-flows", json={"session_id": "test"})
        assert response.status_code == 400
        
        # Missing session_id
        response = client.post("/api/figma/user-flows", json={"file_id": "test"})
        assert response.status_code == 400
        
        # Missing both
        response = client.post("/api/figma/user-flows", json={})
        assert response.status_code == 400
    
    def test_get_documents_after_figma_operations(self, client, test_session_id):
        """Test that documents are created and retrievable."""
        if not FIGMA_TEST_TOKEN or not FIGMA_TEST_FILE_ID:
            pytest.skip("FIGMA_TEST_TOKEN or FIGMA_TEST_FILE_ID not available")
        
        # Store credentials
        credentials_data = {
            "session_id": test_session_id,
            "service": "figma",
            "credentials": {
                "token": FIGMA_TEST_TOKEN,
                "email": ""
            }
        }
        client.post("/api/credentials", json=credentials_data)
        
        # Get initial document count
        initial_response = client.get("/api/documents")
        initial_count = len(initial_response.json())
        
        # Fetch components
        components_request = {
            "session_id": test_session_id,
            "file_id": FIGMA_TEST_FILE_ID
        }
        components_response = client.post("/api/figma/components", json=components_request)
        
        if components_response.status_code == 200 and "error" not in components_response.json():
            # Check that documents increased
            final_response = client.get("/api/documents")
            final_docs = final_response.json()
            final_count = len(final_docs)
            
            assert final_count > initial_count
            
            # Check that at least one document is a Figma document
            figma_docs = [doc for doc in final_docs if doc.get("type", "").startswith("figma_")]
            assert len(figma_docs) > 0
            
            print(f"\n=== Document Creation Test ===")
            print(f"Initial document count: {initial_count}")
            print(f"Final document count: {final_count}")
            print(f"Figma documents created: {len(figma_docs)}")
            for doc in figma_docs[-2:]:  # Show last 2 Figma docs
                print(f"  - {doc.get('name', 'Unnamed')} ({doc.get('type', 'Unknown')})")
        else:
            pytest.skip("Could not create Figma documents for testing")

if __name__ == "__main__":
    # Print test configuration
    print("=== Figma API Test Configuration ===")
    print(f"FIGMA_TEST_TOKEN: {'Set' if FIGMA_TEST_TOKEN else 'Not Set'}")
    print(f"FIGMA_TEST_URL: {FIGMA_TEST_URL if FIGMA_TEST_URL else 'Not Set'}")
    print(f"FIGMA_TEST_FILE_ID: {FIGMA_TEST_FILE_ID if FIGMA_TEST_FILE_ID else 'Not Set'}")
    print("=" * 40)
    
    # Run the tests
    pytest.main([__file__, "-v", "-s"])