import unittest
import uuid
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import time
import json

from app.services.document_storage import DocumentStorage
from app.models import ManagedDocument

class TestDocumentStorage(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for document storage
        self.temp_dir = tempfile.mkdtemp()
        self.storage = DocumentStorage(base_path=self.temp_dir, session_timeout_hours=1)
        self.test_session_id = str(uuid.uuid4())
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_document(self):
        """Test saving a document to storage."""
        # Create a test document
        doc = ManagedDocument(
            id=uuid.uuid4(),
            name="Test Document",
            type="markdown",
            source="test",
            created_at=datetime.now(),
            metadata={"content": "# Test Content", "test_key": "test_value"}
        )
        
        # Save the document
        saved_doc = self.storage.save_document(doc, self.test_session_id)
        
        # Check that the document has a local path
        self.assertIsNotNone(saved_doc.local_path)
        
        # Check that the file exists on disk
        file_path = Path(saved_doc.local_path)
        self.assertTrue(file_path.exists())
        
        # Check that the file is in the correct session directory
        self.assertIn(self.test_session_id, str(file_path))
        
        # Check that metadata file exists and contains the right info
        # The actual implementation uses <id>.meta.json instead of the suffix approach
        doc_id = str(doc.id)
        metadata_path = file_path.parent / f"{doc_id}.meta.json"
        self.assertTrue(metadata_path.exists(), f"Metadata file does not exist: {metadata_path}")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            self.assertEqual(metadata['name'], doc.name)
            self.assertEqual(metadata['type'], doc.type)
    
    def test_get_documents_for_session(self):
        """Test retrieving documents for a specific session."""
        # Create and save multiple documents for the same session
        doc1 = ManagedDocument(
            id=uuid.uuid4(),
            name="Document 1",
            type="markdown",
            source="test",
            metadata={"content": "Content 1"}
        )
        
        doc2 = ManagedDocument(
            id=uuid.uuid4(),
            name="Document 2",
            type="code",
            source="test",
            metadata={"content": "def test():\n    pass", "language": "python"}
        )
        
        self.storage.save_document(doc1, self.test_session_id)
        self.storage.save_document(doc2, self.test_session_id)
        
        # Create a document for a different session
        other_session_id = str(uuid.uuid4())
        other_doc = ManagedDocument(
            id=uuid.uuid4(),
            name="Other Document",
            type="markdown",
            source="test",
            metadata={"content": "Other content"}
        )
        self.storage.save_document(other_doc, other_session_id)
        
        # Retrieve documents for our test session
        documents = self.storage.get_documents_for_session(self.test_session_id)
        
        # Check results
        self.assertEqual(len(documents), 2)
        doc_names = [doc.name for doc in documents]
        self.assertIn("Document 1", doc_names)
        self.assertIn("Document 2", doc_names)
        self.assertNotIn("Other Document", doc_names)
    
    def test_get_all_documents(self):
        """Test retrieving all documents across all sessions."""
        # Create documents in different sessions
        session1_id = str(uuid.uuid4())
        session2_id = str(uuid.uuid4())
        
        doc1 = ManagedDocument(
            id=uuid.uuid4(),
            name="Document in Session 1",
            type="markdown",
            source="test",
            metadata={"content": "Content"}
        )
        
        doc2 = ManagedDocument(
            id=uuid.uuid4(),
            name="Document in Session 2",
            type="markdown",
            source="test",
            metadata={"content": "Content"}
        )
        
        self.storage.save_document(doc1, session1_id)
        self.storage.save_document(doc2, session2_id)
        
        # Retrieve all documents
        documents = self.storage.get_all_documents()
        
        # Check results
        self.assertGreaterEqual(len(documents), 2)
        doc_names = [doc.name for doc in documents]
        self.assertIn("Document in Session 1", doc_names)
        self.assertIn("Document in Session 2", doc_names)
    
    def test_session_cleanup(self):
        """Test direct cleanup of old sessions."""
        # Create a storage with a very short timeout
        custom_storage = DocumentStorage(base_path=self.temp_dir, session_timeout_hours=0.0003) # ~1 second
        custom_session_id = str(uuid.uuid4())
        
        # Create a document
        doc = ManagedDocument(
            id=uuid.uuid4(),
            name="Temporary Document",
            type="markdown",
            source="test",
            metadata={"content": "This document should be cleaned up"}
        )
        
        # Save the document and get its path
        saved_doc = custom_storage.save_document(doc, custom_session_id)
        file_path = Path(saved_doc.local_path)
        
        # Verify the document exists
        self.assertTrue(file_path.exists())
        
        # Force the last access time to be in the past
        custom_storage.session_last_access[custom_session_id] = datetime.now() - timedelta(hours=1)
        
        # Manually run the cleanup method
        custom_storage._cleanup_old_sessions()
        
        # The session should be removed from tracking
        self.assertNotIn(custom_session_id, custom_storage.session_last_access, 
                         "Session should be removed from tracking")

if __name__ == "__main__":
    unittest.main()