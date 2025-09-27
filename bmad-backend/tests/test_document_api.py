import unittest
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models import ManagedDocument
from app.routes.document_routes import router as document_router
from app.security import get_current_user

# Create a test app with just the document routes
test_app = FastAPI()
test_app.include_router(document_router)

# Mock the authentication dependency (always returns a test user)
async def mock_current_user():
    return {
        "id": "test-user-id",
        "username": "testuser",
        "name": "Test User",
        "email": "test@example.com"
    }

test_app.dependency_overrides[get_current_user] = mock_current_user

client = TestClient(test_app)

class TestDocumentRoutes(unittest.TestCase):
    def setUp(self):
        self.test_session_id = str(uuid.uuid4())
    
    @patch("app.routes.document_routes.document_storage")
    def test_get_all_documents_endpoint(self, mock_storage):
        """Test the GET /documents endpoint."""
        # Create mock documents
        mock_documents = [
            ManagedDocument(
                id=uuid.uuid4(),
                name="Test Document 1",
                type="markdown",
                source="test",
                created_at=datetime.now(),
                metadata={"content": "Content 1"}
            ),
            ManagedDocument(
                id=uuid.uuid4(),
                name="Test Document 2",
                type="code",
                source="test",
                created_at=datetime.now(),
                metadata={"content": "Content 2", "language": "python"}
            )
        ]
        
        # Configure mock to return documents
        mock_storage.get_all_documents.return_value = mock_documents
        mock_storage.get_documents_for_session.return_value = [mock_documents[0]]
        
        # Test getting all documents
        response = client.get("/documents/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["documents"]), 2)
        
        # Test getting documents by session
        response = client.get(f"/documents/?session_id={self.test_session_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["documents"]), 1)
    
    @patch("app.routes.document_routes.document_extractor")
    @patch("app.routes.document_routes.document_storage")
    def test_extract_documents_endpoint(self, mock_storage, mock_extractor):
        """Test the POST /documents/extract endpoint."""
        # Create mock documents that would be extracted
        mock_extracted_docs = [
            ManagedDocument(
                id=uuid.uuid4(),
                name="Extracted Markdown",
                type="markdown",
                source="llm_response",
                created_at=datetime.now(),
                metadata={"content": "# Heading\nContent", "session_id": self.test_session_id}
            ),
            ManagedDocument(
                id=uuid.uuid4(),
                name="Extracted Code",
                type="code",
                source="llm_response",
                created_at=datetime.now(),
                metadata={"content": "def test():\n    pass", "language": "python", "session_id": self.test_session_id}
            )
        ]
        
        # Configure mocks
        mock_extractor.extract_documents_from_response.return_value = mock_extracted_docs
        # Mock storage to return the documents that were passed to save_document
        mock_storage.save_document.side_effect = lambda doc, session_id: doc
        
        # Test data
        test_text = """
        # Sample Heading
        
        Here's some sample text with a code block:
        
        ```python
        def sample_function():
            return "Hello World"
        ```
        """
        
        # Make request to extract documents
        response = client.post(
            "/documents/extract",
            params={"text": test_text, "session_id": self.test_session_id}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["documents"]), 2)
        
        # Verify that the extractor was called with the right parameters
        mock_extractor.extract_documents_from_response.assert_called_once_with(test_text, self.test_session_id)
        
        # Verify that storage.save_document was called for each extracted document
        self.assertEqual(mock_storage.save_document.call_count, 2)

if __name__ == "__main__":
    unittest.main()