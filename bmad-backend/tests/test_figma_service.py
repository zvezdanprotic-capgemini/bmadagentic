import pytest
import os
import sys
from unittest.mock import MagicMock
from typing import List

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.figma_service import FigmaService
from app.models import ManagedDocument

# Test credentials from environment
FIGMA_TEST_TOKEN = os.getenv("FIGMA_TEST_TOKEN")
FIGMA_TEST_URL = os.getenv("FIGMA_TEST_URL")

# Extract file ID from the test URL
# Example URL: https://www.figma.com/design/Rassb1QLx2nZ6bmRe3Eeo7/TestFile?node-id=0-1&p=f&t=fb9p1qnMTmZgb9eX-0
# File ID is: Rassb1QLx2nZ6bmRe3Eeo7
def extract_file_id_from_url(url: str) -> str:
    """Extract Figma file ID from URL."""
    if "/design/" in url:
        return url.split("/design/")[1].split("/")[0]
    elif "/file/" in url:
        return url.split("/file/")[1].split("/")[0]
    else:
        raise ValueError("Invalid Figma URL format")

FIGMA_TEST_FILE_ID = extract_file_id_from_url(FIGMA_TEST_URL) if FIGMA_TEST_URL else None

class TestFigmaService:
    """Test suite for Figma service integration."""
    
    @pytest.fixture
    def figma_service(self):
        """Create a FigmaService instance with test credentials."""
        if not FIGMA_TEST_TOKEN:
            pytest.skip("FIGMA_TEST_TOKEN not found in environment variables")
        return FigmaService(token=FIGMA_TEST_TOKEN)
    
    @pytest.fixture
    def managed_documents(self):
        """Create an empty list for managed documents."""
        return []
    
    def test_figma_service_initialization(self):
        """Test FigmaService initialization."""
        # Test initialization without token
        service = FigmaService()
        assert service.token is None
        assert service.figma_py is None
        
        # Test initialization with token
        if FIGMA_TEST_TOKEN:
            service = FigmaService(token=FIGMA_TEST_TOKEN)
            assert service.token == FIGMA_TEST_TOKEN
            assert service.figma_py is not None
    
    def test_set_token(self, figma_service):
        """Test setting token after initialization."""
        new_token = "test_token_123"
        figma_service.set_token(new_token)
        assert figma_service.token == new_token
        assert figma_service.figma_py is not None
    
    def test_get_file_components_without_token(self, managed_documents):
        """Test getting components without token."""
        service = FigmaService()
        result = service.get_file_components("test_file_id", "test_session", managed_documents)
        
        assert "error" in result
        assert result["error"] == "Figma token not configured"
        assert result["components"] == []
    
    def test_get_user_flow_diagram_without_token(self, managed_documents):
        """Test getting user flows without token."""
        service = FigmaService()
        result = service.get_user_flow_diagram("test_file_id", "test_session", managed_documents)
        
        assert "error" in result
        assert result["error"] == "Figma token not configured"
        assert result["user_flows"] == []
    
    @pytest.mark.skipif(not FIGMA_TEST_TOKEN or not FIGMA_TEST_FILE_ID, 
                       reason="FIGMA_TEST_TOKEN or FIGMA_TEST_FILE_ID not available")
    def test_get_file_components_real_api(self, figma_service, managed_documents):
        """Test getting components from real Figma API."""
        session_id = "test_session_components"
        
        result = figma_service.get_file_components(FIGMA_TEST_FILE_ID, session_id, managed_documents)
        
        # Check that we got a successful response
        if "error" not in result:
            assert "components" in result
            assert "file_name" in result
            assert "total_components" in result
            assert "document_id" in result
            assert isinstance(result["components"], list)
            assert isinstance(result["total_components"], int)
            
            # Check that a document was added to managed_documents
            assert len(managed_documents) == 1
            doc = managed_documents[0]
            assert isinstance(doc, ManagedDocument)
            assert doc.type == "figma_components"
            assert FIGMA_TEST_FILE_ID in doc.source
            
            # Print results for manual verification
            print(f"\n=== Figma Components Test Results ===")
            print(f"File Name: {result['file_name']}")
            print(f"Total Components: {result['total_components']}")
            print(f"Document ID: {result['document_id']}")
            if result["components"]:
                print("Sample Components:")
                for i, component in enumerate(result["components"][:3]):  # Show first 3
                    print(f"  {i+1}. {component.get('name', 'Unnamed')} ({component.get('type', 'Unknown')})")
        else:
            print(f"\n=== Figma Components Test Error ===")
            print(f"Error: {result['error']}")
            # Don't fail the test if it's an API access issue
            pytest.skip(f"Figma API access error: {result['error']}")
    
    @pytest.mark.skipif(not FIGMA_TEST_TOKEN or not FIGMA_TEST_FILE_ID, 
                       reason="FIGMA_TEST_TOKEN or FIGMA_TEST_FILE_ID not available")
    def test_get_user_flow_diagram_real_api(self, figma_service, managed_documents):
        """Test getting user flows from real Figma API."""
        session_id = "test_session_flows"
        
        result = figma_service.get_user_flow_diagram(FIGMA_TEST_FILE_ID, session_id, managed_documents)
        
        # Check that we got a successful response
        if "error" not in result:
            assert "user_flows" in result
            assert "screens" in result
            assert "file_name" in result
            assert "total_screens" in result
            assert "total_flows" in result
            assert "document_id" in result
            assert isinstance(result["user_flows"], list)
            assert isinstance(result["screens"], list)
            assert isinstance(result["total_screens"], int)
            assert isinstance(result["total_flows"], int)
            
            # Check that a document was added to managed_documents
            assert len(managed_documents) == 1
            doc = managed_documents[0]
            assert isinstance(doc, ManagedDocument)
            assert doc.type == "figma_user_flows"
            assert FIGMA_TEST_FILE_ID in doc.source
            
            # Print results for manual verification
            print(f"\n=== Figma User Flows Test Results ===")
            print(f"File Name: {result['file_name']}")
            print(f"Total Screens: {result['total_screens']}")
            print(f"Total Flows: {result['total_flows']}")
            print(f"Document ID: {result['document_id']}")
            if result["screens"]:
                print("Sample Screens:")
                for i, screen in enumerate(result["screens"][:3]):  # Show first 3
                    print(f"  {i+1}. {screen.get('name', 'Unnamed')} ({screen.get('type', 'Unknown')})")
            if result["user_flows"]:
                print("Sample Flow Connectors:")
                for i, flow in enumerate(result["user_flows"][:3]):  # Show first 3
                    print(f"  {i+1}. {flow.get('name', 'Unnamed')} ({flow.get('type', 'Unknown')})")
        else:
            print(f"\n=== Figma User Flows Test Error ===")
            print(f"Error: {result['error']}")
            # Don't fail the test if it's an API access issue
            pytest.skip(f"Figma API access error: {result['error']}")
    
    def test_invalid_file_id(self, figma_service, managed_documents):
        """Test handling of invalid file ID."""
        if not FIGMA_TEST_TOKEN:
            pytest.skip("FIGMA_TEST_TOKEN not available")
            
        invalid_file_id = "invalid_file_id_12345"
        session_id = "test_session_invalid"
        
        result = figma_service.get_file_components(invalid_file_id, session_id, managed_documents)
        
        # Should get an error for invalid file ID
        if "error" in result:
            print(f"\n=== Invalid File ID Test ===")
            print(f"Expected error for invalid file ID: {result['error']}")
            assert "error" in result
        else:
            # If no error, something unexpected happened
            pytest.fail("Expected error for invalid file ID, but got success response")

    def test_document_management_integration(self, figma_service, managed_documents):
        """Test that documents are properly managed."""
        if not FIGMA_TEST_TOKEN or not FIGMA_TEST_FILE_ID:
            pytest.skip("FIGMA_TEST_TOKEN or FIGMA_TEST_FILE_ID not available")
        
        session_id = "test_session_docs"
        
        # Get components - should add one document
        result1 = figma_service.get_file_components(FIGMA_TEST_FILE_ID, session_id, managed_documents)
        
        if "error" not in result1:
            initial_count = len(managed_documents)
            assert initial_count >= 1
            
            # Get user flows - should add another document
            result2 = figma_service.get_user_flow_diagram(FIGMA_TEST_FILE_ID, session_id, managed_documents)
            
            if "error" not in result2:
                final_count = len(managed_documents)
                assert final_count == initial_count + 1
                
                # Check that documents have different types
                doc_types = [doc.type for doc in managed_documents]
                assert "figma_components" in doc_types
                assert "figma_user_flows" in doc_types
                
                print(f"\n=== Document Management Test ===")
                print(f"Total documents created: {len(managed_documents)}")
                for i, doc in enumerate(managed_documents):
                    print(f"  {i+1}. {doc.name} ({doc.type}) - {doc.id}")
            else:
                pytest.skip(f"User flows API error: {result2['error']}")
        else:
            pytest.skip(f"Components API error: {result1['error']}")

if __name__ == "__main__":
    # Print test configuration
    print("=== Figma Test Configuration ===")
    print(f"FIGMA_TEST_TOKEN: {'Set' if FIGMA_TEST_TOKEN else 'Not Set'}")
    print(f"FIGMA_TEST_URL: {FIGMA_TEST_URL if FIGMA_TEST_URL else 'Not Set'}")
    print(f"FIGMA_TEST_FILE_ID: {FIGMA_TEST_FILE_ID if FIGMA_TEST_FILE_ID else 'Not Set'}")
    print("=" * 40)
    
    # Run the tests
    pytest.main([__file__, "-v", "-s"])