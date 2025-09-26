import json
import re
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.models import ManagedDocument

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("document_extractor")

class DocumentExtractor:
    """
    Service to extract documents from LLM responses.
    This service detects various types of documents embedded in the response text
    and extracts them into structured ManagedDocument objects.
    """
    
    def __init__(self):
        """Initialize the document extractor service."""
        logger.info("Document extractor service initialized")

    def extract_documents_from_response(self, response_text: str, session_id: str) -> List[ManagedDocument]:
        """
        Extract documents from a given LLM response.
        
        Args:
            response_text: Text of the LLM response to analyze
            session_id: Session ID to associate with extracted documents
            
        Returns:
            List of extracted ManagedDocument objects
        """
        documents = []
        
        # Attempt to extract different types of documents
        documents.extend(self._extract_markdown_documents(response_text, session_id))
        documents.extend(self._extract_code_blocks(response_text, session_id))
        documents.extend(self._extract_diagrams(response_text, session_id))
        documents.extend(self._extract_json_documents(response_text, session_id))
        
        return documents
    
    def _extract_markdown_documents(self, text: str, session_id: str) -> List[ManagedDocument]:
        """Extract markdown-formatted sections from text."""
        documents = []
        
        # Look for markdown sections with headers
        markdown_pattern = r'(?:^|\n)(?:#{1,6}\s+)(.+?)(?:\n|$)((?:(?!\n#{1,6}\s+)[^\n]*(?:\n|$))+)'
        matches = re.finditer(markdown_pattern, text, re.MULTILINE)
        
        for match in matches:
            title = match.group(1).strip()
            content = match.group(0).strip()
            
            # Only consider substantial content (more than just a title)
            if len(content.split('\n')) > 1:
                doc = ManagedDocument(
                    id=uuid.uuid4(),
                    name=title,
                    type="markdown",
                    source="llm_response",
                    created_at=datetime.now(),
                    metadata={
                        "content": content,
                        "session_id": session_id,
                        "extraction_method": "markdown_section"
                    }
                )
                documents.append(doc)
        
        return documents
    
    def _extract_code_blocks(self, text: str, session_id: str) -> List[ManagedDocument]:
        """Extract code blocks from text."""
        documents = []
        
        # Pattern for code blocks with language specification
        code_pattern = r'```(?P<language>\w+)?\n(?P<code>[\s\S]*?)\n```'
        matches = re.finditer(code_pattern, text)
        
        for i, match in enumerate(matches):
            language = match.group('language') or "text"
            code = match.group('code')
            
            # Skip very short code snippets
            if len(code.strip().split('\n')) < 3:
                continue
                
            # Try to find a name for the code block
            name = f"Code Snippet {i+1} ({language})"
            
            # Look for filename comments or patterns in the code
            filename_pattern = r'(?:\/\/|#)\s*(?:filename|file):?\s*([^\n]+)'
            filename_match = re.search(filename_pattern, code)
            if filename_match:
                name = filename_match.group(1).strip()
            
            doc = ManagedDocument(
                id=uuid.uuid4(),
                name=name,
                type="code",
                source="llm_response",
                created_at=datetime.now(),
                metadata={
                    "content": code,
                    "language": language,
                    "session_id": session_id,
                    "extraction_method": "code_block"
                }
            )
            documents.append(doc)
        
        return documents
    
    def _extract_diagrams(self, text: str, session_id: str) -> List[ManagedDocument]:
        """Extract diagram specifications from text."""
        documents = []
        
        # Pattern for mermaid diagrams
        mermaid_pattern = r'```mermaid\n([\s\S]*?)\n```'
        matches = re.finditer(mermaid_pattern, text)
        
        for i, match in enumerate(matches):
            diagram_code = match.group(1)
            
            doc = ManagedDocument(
                id=uuid.uuid4(),
                name=f"Diagram {i+1}",
                type="diagram",
                source="llm_response",
                created_at=datetime.now(),
                metadata={
                    "content": diagram_code,
                    "format": "mermaid",
                    "session_id": session_id,
                    "extraction_method": "mermaid_diagram"
                }
            )
            documents.append(doc)
        
        return documents
    
    def _extract_json_documents(self, text: str, session_id: str) -> List[ManagedDocument]:
        """Extract JSON objects from text."""
        documents = []
        
        # Pattern for JSON blocks
        json_pattern = r'```json\n([\s\S]*?)\n```'
        matches = re.finditer(json_pattern, text)
        
        for i, match in enumerate(matches):
            json_text = match.group(1)
            
            try:
                # Try to parse the JSON to validate it
                json_data = json.loads(json_text)
                
                # Try to determine a name for the JSON document
                name = f"JSON Document {i+1}"
                if isinstance(json_data, dict) and "name" in json_data:
                    name = json_data["name"]
                elif isinstance(json_data, dict) and "title" in json_data:
                    name = json_data["title"]
                
                doc = ManagedDocument(
                    id=uuid.uuid4(),
                    name=name,
                    type="json",
                    source="llm_response",
                    created_at=datetime.now(),
                    metadata={
                        "content": json_data,
                        "session_id": session_id,
                        "extraction_method": "json_block"
                    }
                )
                documents.append(doc)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON block: {json_text[:100]}...")
        
        return documents