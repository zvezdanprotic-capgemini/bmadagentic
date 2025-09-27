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
    
    def test_get_file_components_without_token(self):
        """Test getting components without token returns empty list (no token => no figma_py)."""
        service = FigmaService()
        result = service.get_file_components("test_file_id", "test_session")
        assert result == []
    
    def test_get_user_flow_diagram_without_token(self):
        """Test getting user flows without token returns empty list."""
        service = FigmaService()
        result = service.get_user_flow_diagram("test_file_id", "test_session")
        assert result == []
    
    @pytest.mark.skipif(not FIGMA_TEST_TOKEN or not FIGMA_TEST_FILE_ID, 
                       reason="FIGMA_TEST_TOKEN or FIGMA_TEST_FILE_ID not available")
    def test_get_file_components_real_api(self, figma_service):
        """Test getting components from real Figma API."""
        session_id = "test_session_components"
        
        result = figma_service.get_file_components(FIGMA_TEST_FILE_ID, session_id)
        
        if isinstance(result, dict) and "error" in result:
            pytest.skip(f"Figma API access error: {result['error']}")
        assert isinstance(result, list)
        assert len(result) == 1
        doc = result[0]
        assert isinstance(doc, ManagedDocument)
        assert doc.type == "figma_components"
        assert FIGMA_TEST_FILE_ID in doc.source
    
    @pytest.mark.skipif(not FIGMA_TEST_TOKEN or not FIGMA_TEST_FILE_ID, 
                       reason="FIGMA_TEST_TOKEN or FIGMA_TEST_FILE_ID not available")
    def test_get_user_flow_diagram_real_api(self, figma_service):
        """Test getting user flows from real Figma API."""
        session_id = "test_session_flows"
        
        result = figma_service.get_user_flow_diagram(FIGMA_TEST_FILE_ID, session_id)
        if isinstance(result, dict) and "error" in result:
            pytest.skip(f"Figma API access error: {result['error']}")
        assert isinstance(result, list)
        assert len(result) == 1
        doc = result[0]
        assert isinstance(doc, ManagedDocument)
        assert doc.type == "figma_user_flows"
        assert FIGMA_TEST_FILE_ID in doc.source
    
    def test_invalid_file_id(self, figma_service):
        """Test handling of invalid file ID."""
        if not FIGMA_TEST_TOKEN:
            pytest.skip("FIGMA_TEST_TOKEN not available")
            
        invalid_file_id = "invalid_file_id_12345"
        session_id = "test_session_invalid"
        
        result = figma_service.get_file_components(invalid_file_id, session_id)
        # Acceptable outcomes: empty list (no data) or error dict
        assert (isinstance(result, list) and result == []) or (isinstance(result, dict) and "error" in result)

    def test_document_management_integration(self, figma_service):
        """Test that documents are properly managed."""
        if not FIGMA_TEST_TOKEN or not FIGMA_TEST_FILE_ID:
            pytest.skip("FIGMA_TEST_TOKEN or FIGMA_TEST_FILE_ID not available")
        
        session_id = "test_session_docs"
        
        # Get components - should add one document
        result1 = figma_service.get_file_components(FIGMA_TEST_FILE_ID, session_id)
        if isinstance(result1, dict) and "error" in result1:
            pytest.skip(f"Components API error: {result1['error']}")
        assert isinstance(result1, list) and len(result1) == 1
        result2 = figma_service.get_user_flow_diagram(FIGMA_TEST_FILE_ID, session_id)
        if isinstance(result2, dict) and "error" in result2:
            pytest.skip(f"User flows API error: {result2['error']}")
        assert isinstance(result2, list) and len(result2) == 1
        types = {result1[0].type, result2[0].type}
        assert "figma_components" in types and "figma_user_flows" in types

if __name__ == "__main__":
    # Print test configuration
    print("=== Figma Test Configuration ===")
    print(f"FIGMA_TEST_TOKEN: {'Set' if FIGMA_TEST_TOKEN else 'Not Set'}")
    print(f"FIGMA_TEST_URL: {FIGMA_TEST_URL if FIGMA_TEST_URL else 'Not Set'}")
    print(f"FIGMA_TEST_FILE_ID: {FIGMA_TEST_FILE_ID if FIGMA_TEST_FILE_ID else 'Not Set'}")
    print("=" * 40)
    
    # Run the tests
    pytest.main([__file__, "-v", "-s"])