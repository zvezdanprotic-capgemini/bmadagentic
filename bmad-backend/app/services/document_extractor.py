import json
import re
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import markdown
from bs4 import BeautifulSoup, NavigableString

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
        """Extract markdown-formatted sections from text using advanced parsing."""
        documents = []
        
        # First, try to extract explicit markdown blocks (```markdown ... ```)
        explicit_docs = self._extract_explicit_markdown_blocks(text, session_id)
        documents.extend(explicit_docs)
        
        # Only try implicit extraction if no explicit blocks were found
        # This prevents over-fragmentation when we have complete documents
        if not explicit_docs:
            documents.extend(self._extract_implicit_markdown_sections(text, session_id))
        
        return documents
    
    def _extract_explicit_markdown_blocks(self, text: str, session_id: str) -> List[ManagedDocument]:
        """Extract explicitly marked markdown blocks."""
        documents = []
        
        # Pattern for markdown code blocks
        markdown_pattern = r'```(?:markdown|md)\n([\s\S]*?)\n```'
        matches = re.finditer(markdown_pattern, text, re.IGNORECASE)
        
        for i, match in enumerate(matches):
            markdown_content = match.group(1).strip()
            
            if len(markdown_content) < 20:  # Skip very short content
                continue
                
            # Parse the markdown to extract title
            title = self._extract_title_from_markdown(markdown_content)
            if not title:
                title = f"Markdown Document {i+1}"
            
            doc = ManagedDocument(
                id=uuid.uuid4(),
                name=title,
                type="markdown",
                source="llm_response",
                created_at=datetime.now(),
                metadata={
                    "content": markdown_content,
                    "session_id": session_id,
                    "extraction_method": "explicit_markdown_block"
                }
            )
            documents.append(doc)
        
        return documents
    
    def _extract_implicit_markdown_sections(self, text: str, session_id: str) -> List[ManagedDocument]:
        """Extract sections that appear to be markdown documents based on structure."""
        documents = []
        
        # First, check if the entire text is a valid markdown document
        if self._is_likely_markdown_document(text):
            title = self._extract_title_from_markdown(text)
            if not title:
                title = "Markdown Document"
                
            doc = ManagedDocument(
                id=uuid.uuid4(),
                name=title,
                type="markdown",
                source="llm_response",
                created_at=datetime.now(),
                metadata={
                    "content": text.strip(),
                    "session_id": session_id,
                    "extraction_method": "implicit_markdown_document"
                }
            )
            documents.append(doc)
            return documents  # Return the whole document, don't fragment it
        
        # Only if the whole text isn't a good markdown document, try splitting
        sections = self._split_text_by_headers(text)
        
        for section in sections:
            if self._is_likely_markdown_document(section):
                title = self._extract_title_from_markdown(section)
                if not title:
                    title = f"Document Section {len(documents)+1}"
                
                doc = ManagedDocument(
                    id=uuid.uuid4(),
                    name=title,
                    type="markdown",
                    source="llm_response",
                    created_at=datetime.now(),
                    metadata={
                        "content": section.strip(),
                        "session_id": session_id,
                        "extraction_method": "implicit_markdown_section"
                    }
                )
                documents.append(doc)
        
        return documents
    
    def _extract_title_from_markdown(self, markdown_text: str) -> Optional[str]:
        """Extract title from markdown content using the markdown library."""
        try:
            # Convert markdown to HTML
            html = markdown.markdown(markdown_text)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for the first heading
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                heading = soup.find(tag)
                if heading and heading.get_text().strip():
                    return heading.get_text().strip()
            
            # Fallback: look for first line that starts with #
            lines = markdown_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    # Remove markdown header syntax
                    title = re.sub(r'^#+\s*', '', line).strip()
                    if title:
                        return title
                        
        except Exception as e:
            logger.warning(f"Failed to extract title from markdown: {e}")
            
        return None
    
    def _split_text_by_headers(self, text: str) -> List[str]:
        """Split text into sections based on markdown headers."""
        sections = []
        current_section = []
        
        lines = text.split('\n')
        for line in lines:
            # Check if this line is a header (starts with #)
            if re.match(r'^#+\s+', line.strip()):
                # If we have accumulated content, save it as a section
                if current_section and len('\n'.join(current_section).strip()) > 50:
                    sections.append('\n'.join(current_section))
                # Start new section
                current_section = [line]
            else:
                current_section.append(line)
        
        # Don't forget the last section
        if current_section and len('\n'.join(current_section).strip()) > 50:
            sections.append('\n'.join(current_section))
        
        return sections
    
    def _is_likely_markdown_document(self, text: str) -> bool:
        """Determine if a text section is likely a standalone markdown document."""
        # Check for markdown indicators
        markdown_indicators = [
            r'^#+\s+',  # Headers
            r'^\*\s+',  # Bullet lists
            r'^\d+\.\s+',  # Numbered lists
            r'^>\s+',  # Blockquotes
            r'\*\*.*?\*\*',  # Bold text
            r'\*.*?\*',  # Italic text
            r'`.*?`',  # Inline code
            r'^\|.*\|',  # Tables
            r'^---+$',  # Horizontal rules
        ]
        
        score = 0
        lines = text.split('\n')
        
        for pattern in markdown_indicators:
            matches = re.findall(pattern, text, re.MULTILINE)
            score += len(matches)
        
        # Must have at least some markdown formatting and be substantial
        return score >= 2 and len(text.strip()) > 100 and len(lines) > 3
    
    def _extract_code_blocks(self, text: str, session_id: str) -> List[ManagedDocument]:
        """Extract code blocks from text."""
        documents = []
        
        # Pattern for code blocks with language specification
        code_pattern = r'```(?P<language>\w+)?\n(?P<code>[\s\S]*?)\n```'
        matches = re.finditer(code_pattern, text)
        
        for i, match in enumerate(matches):
            language = match.group('language') or "text"
            code = match.group('code')
            
            # Skip markdown blocks (they're handled by markdown extractor)
            if language and language.lower() in ['markdown', 'md']:
                continue
                
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