from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import List, Optional
import uuid
import logging

from app.models import ManagedDocument, ManagedDocumentsResponse
from app.services.document_storage import DocumentStorage
from app.services.document_extractor import DocumentExtractor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("document_routes")

# Initialize services
document_storage = DocumentStorage()
document_extractor = DocumentExtractor()

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/", response_model=ManagedDocumentsResponse)
async def get_all_documents(session_id: Optional[str] = Query(None)):
    """
    Get all documents, optionally filtered by session_id.
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
    session_id: str = Query(..., description="Session ID to associate extracted documents with")
):
    """
    Extract documents from provided text (typically an LLM response)
    and store them associated with the given session ID.
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