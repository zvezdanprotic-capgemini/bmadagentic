import os
import shutil
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
import threading
import logging
import uuid

from app.models import ManagedDocument

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("document_storage")

class DocumentStorage:
    """
    Service to manage persistent storage of documents organized by session ID,
    with automatic timeout-based cleanup.
    """
    
    def __init__(self, base_path: str = None, session_timeout_hours: int = 24):
        """
        Initialize the document storage service.
        
        Args:
            base_path: Base directory for document storage. Defaults to 'document_storage' in project root.
            session_timeout_hours: Hours after which inactive sessions are cleaned up. Default is 24 hours.
        """
        # Set up storage path
        if base_path is None:
            # Default to a 'document_storage' directory in the parent directory of this file
            self.base_path = Path(__file__).parent.parent.parent / "document_storage"
        else:
            self.base_path = Path(base_path)
        
        # Create base directory if it doesn't exist
        self.base_path.mkdir(exist_ok=True, parents=True)
        
        # Set timeout duration
        self.session_timeout = timedelta(hours=session_timeout_hours)
        
        # Dictionary to track last access time for each session
        self.session_last_access = {}
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_thread, daemon=True)
        self.cleanup_thread.start()
        
        logger.info(f"Document storage initialized at: {self.base_path}")
    
    def _get_session_path(self, session_id: str) -> Path:
        """Get the path to a session's document directory."""
        session_path = self.base_path / session_id
        session_path.mkdir(exist_ok=True, parents=True)
        return session_path
    
    def _update_session_access_time(self, session_id: str):
        """Update the last access time for a session."""
        self.session_last_access[session_id] = datetime.now()
    
    def save_document(self, document: ManagedDocument, session_id: str) -> ManagedDocument:
        """
        Save a document to persistent storage and update its local_path.
        
        Args:
            document: ManagedDocument object to save
            session_id: Session ID to associate with the document
            
        Returns:
            Updated ManagedDocument with local_path set
        """
        session_path = self._get_session_path(session_id)
        self._update_session_access_time(session_id)
        
        # Create a unique filename if none exists
        if not document.local_path:
            # Use document ID as filename, sanitize the name, and add appropriate extension based on type
            filename = f"{document.id}"
            extension = self._get_extension_for_document_type(document.type)
            filepath = session_path / f"{filename}{extension}"
            
            # Set the local path in the document
            document.local_path = str(filepath)
        else:
            # If document has a path already, make sure it's in the session directory
            filepath = Path(document.local_path)
            
        # Save document content to file
        try:
            # Create document metadata to help with reconstruction
            metadata = {
                "id": str(document.id),
                "name": document.name,
                "type": document.type,
                "source": document.source,
                "external_url": document.external_url,
                "created_at": document.created_at.isoformat() if document.created_at else datetime.now().isoformat(),
                "metadata": document.metadata,
            }
            
            # Write metadata file
            metadata_path = session_path / f"{document.id}.meta.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            # Write content file (if content exists in metadata)
            if "content" in document.metadata:
                content = document.metadata["content"]
                
                # Handle different types of content
                if isinstance(content, dict) or isinstance(content, list):
                    # JSON content
                    with open(filepath, "w") as f:
                        json.dump(content, f, indent=2)
                else:
                    # Text content
                    with open(filepath, "w") as f:
                        f.write(str(content))
            
            logger.info(f"Document saved: {filepath}")
            return document
            
        except Exception as e:
            logger.error(f"Error saving document {document.id}: {e}")
            raise
    
    def get_documents_for_session(self, session_id: str) -> List[ManagedDocument]:
        """
        Get all documents for a specific session ID.
        
        Args:
            session_id: Session ID to retrieve documents for
            
        Returns:
            List of ManagedDocument objects
        """
        session_path = self._get_session_path(session_id)
        self._update_session_access_time(session_id)
        
        documents = []
        
        # Check if the session directory exists
        if not session_path.exists():
            return []
        
        # Find all metadata files
        for meta_file in session_path.glob("*.meta.json"):
            try:
                with open(meta_file, "r") as f:
                    metadata = json.load(f)
                
                # Reconstruct the document from metadata
                doc = ManagedDocument(
                    id=uuid.UUID(metadata["id"]),
                    name=metadata["name"],
                    type=metadata["type"],
                    source=metadata["source"],
                    external_url=metadata.get("external_url"),
                    local_path=str(session_path / f"{metadata['id']}{self._get_extension_for_document_type(metadata['type'])}"),
                    created_at=datetime.fromisoformat(metadata["created_at"]),
                    metadata=metadata.get("metadata", {})
                )
                
                documents.append(doc)
                
            except Exception as e:
                logger.error(f"Error loading document metadata {meta_file}: {e}")
        
        return documents
    
    def get_all_documents(self) -> List[ManagedDocument]:
        """
        Get all documents across all sessions.
        
        Returns:
            List of ManagedDocument objects
        """
        all_documents = []
        
        # Iterate through all session directories
        for session_path in self.base_path.iterdir():
            if session_path.is_dir():
                session_id = session_path.name
                try:
                    documents = self.get_documents_for_session(session_id)
                    all_documents.extend(documents)
                except Exception as e:
                    logger.error(f"Error getting documents for session {session_id}: {e}")
        
        return all_documents
    
    def _get_extension_for_document_type(self, document_type: str) -> str:
        """Get the appropriate file extension based on document type."""
        extension_map = {
            "markdown": ".md",
            "json": ".json",
            "text": ".txt",
            "code": ".py",
            "diagram": ".svg",
            "figma_components": ".json",
            "image": ".png",
            "html": ".html",
        }
        
        return extension_map.get(document_type, ".txt")
    
    def _cleanup_thread(self):
        """Thread to periodically clean up old sessions."""
        while True:
            try:
                self._cleanup_old_sessions()
            except Exception as e:
                logger.error(f"Error in cleanup thread: {e}")
            
            # Sleep for 1 hour between cleanup runs
            time.sleep(3600)
    
    def _cleanup_old_sessions(self):
        """Remove session directories that have been inactive for longer than the timeout period."""
        now = datetime.now()
        sessions_to_remove = []
        
        # Find sessions that have timed out
        for session_id, last_access in self.session_last_access.items():
            if now - last_access > self.session_timeout:
                sessions_to_remove.append(session_id)
        
        # Remove session directories and update tracking dict
        for session_id in sessions_to_remove:
            session_path = self._get_session_path(session_id)
            try:
                if session_path.exists():
                    shutil.rmtree(session_path)
                    logger.info(f"Removed inactive session directory: {session_id}")
                
                del self.session_last_access[session_id]
            except Exception as e:
                logger.error(f"Error removing session directory {session_id}: {e}")