# Add this method to the DocumentStorage class in document_storage.py

def get_document_by_id(self, document_id: str, session_id: str = None) -> Optional[ManagedDocument]:
    """
    Get a specific document by its ID.
    
    Args:
        document_id: ID of the document to retrieve
        session_id: Optional session ID to limit search to a specific session
        
    Returns:
        ManagedDocument if found, None otherwise
    """
    # If session_id is provided, only search in that session
    if session_id:
        documents = self.get_documents_for_session(session_id)
    else:
        documents = self.get_all_documents()
    
    # Find document with matching ID
    for doc in documents:
        if str(doc.id) == document_id:
            return doc
    
    return None

def read_document_content(self, document_id: str, session_id: str) -> tuple[str, str, bytes]:
    """
    Read the content of a document as bytes.
    
    Args:
        document_id: ID of the document to read
        session_id: Session ID to limit search to a specific session
        
    Returns:
        Tuple of (filename, content_type, bytes content) of the document
        
    Raises:
        ValueError: If document not found or cannot be read
    """
    document = self.get_document_by_id(document_id, session_id)
    if not document:
        raise ValueError(f"Document {document_id} not found in session {session_id}")
    
    if not document.local_path:
        raise ValueError(f"Document {document_id} has no local path")
    
    try:
        # Get MIME type based on document type
        content_type = self._get_mime_type_for_document_type(document.type)
        
        # Read file content as bytes
        with open(document.local_path, "rb") as f:
            content = f.read()
        
        return document.name, content_type, content
    except Exception as e:
        logger.error(f"Error reading document {document_id}: {e}")
        raise ValueError(f"Error reading document: {str(e)}")

def _get_mime_type_for_document_type(self, document_type: str) -> str:
    """Get the appropriate MIME type based on document type."""
    mime_type_map = {
        "markdown": "text/markdown",
        "json": "application/json",
        "text": "text/plain",
        "code": "text/plain",
        "diagram": "image/svg+xml",
        "figma_components": "application/json",
        "image": "image/png",
        "html": "text/html",
    }
    
    return mime_type_map.get(document_type, "application/octet-stream")