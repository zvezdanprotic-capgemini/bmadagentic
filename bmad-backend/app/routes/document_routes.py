from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from typing import List, Optional, Dict, Any
import uuid
import logging

from app.models import ManagedDocument, ManagedDocumentsResponse
import re
from urllib.parse import quote
from app.services.document_storage import DocumentStorage
from app.services.document_extractor import DocumentExtractor
from app.security import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("document_routes")

# Initialize services
document_storage = DocumentStorage()
document_extractor = DocumentExtractor()

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/", response_model=ManagedDocumentsResponse)
async def get_all_documents(
    session_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all documents, optionally filtered by session_id.
    Requires authentication.
    """
    try:
        if session_id:
            documents = document_storage.get_documents_for_session(session_id)
        else:
            documents = document_storage.get_all_documents()
            
        return ManagedDocumentsResponse(documents=documents)
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@router.post("/extract", response_model=ManagedDocumentsResponse)
async def extract_documents_from_text(
    text: str, 
    session_id: str = Query(..., description="Session ID to associate extracted documents with"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Extract documents from provided text (typically an LLM response)
    and store them associated with the given session ID.
    Requires authentication.
    """
    try:
        # Extract documents from the text
        documents = document_extractor.extract_documents_from_response(text, session_id)
        
        # Save the extracted documents
        saved_documents = []
        for doc in documents:
            saved_doc = document_storage.save_document(doc, session_id)
            saved_documents.append(saved_doc)
        
        return ManagedDocumentsResponse(documents=saved_documents)
    except Exception as e:
        logger.error(f"Error extracting documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error extracting documents: {str(e)}")

@router.get("/{document_id}")
async def get_document(
    document_id: str = Path(..., description="ID of the document to download"),
    session_id: str = Query(..., description="Session ID that owns the document"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Download a specific document by ID.
    Requires authentication.
    Handles Unicode characters in filenames by providing both a sanitized ASCII fallback
    and an RFC 5987 encoded filename* parameter to avoid latin-1 encoding errors.
    """
    try:
        document_name, content_type, content = document_storage.read_document_content(document_id, session_id)

        # Build a safe Content-Disposition header preserving original name if possible.
        full_name = document_name  # Do not append extensions to keep original behavior / tests
        ascii_fallback = re.sub(r'[^A-Za-z0-9._-]+', '_', full_name)
        encoded = quote(full_name)

        try:
            # If this succeeds, all chars are latin-1 encodable and safe
            full_name.encode('latin-1')
            content_disposition = f'attachment; filename="{full_name}"'
        except UnicodeEncodeError:
            # Provide RFC 5987 encoded variant plus ASCII fallback
            content_disposition = (
                f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{encoded}"
            )

        from fastapi.responses import Response
        return Response(
            content=content,
            media_type=content_type,
            headers={"Content-Disposition": content_disposition}
        )
    except ValueError as e:
        # Document missing
        logger.error(f"Document not found: {document_id} in session {session_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error downloading document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")