#!/usr/bin/env python3
"""
Debug implicit markdown detection.
"""

import os
import sys
import uuid

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.document_extractor import DocumentExtractor

def debug_implicit_detection():
    """Debug why implicit detection isn't working."""
    
    extractor = DocumentExtractor()
    test_session_id = str(uuid.uuid4())
    
    test_content = """# Good Document
            
## Section 1
This is a **good document** with:
- Multiple items
- Bold text
- Good structure

## Section 2  
More content here."""
    
    print(f"Testing content ({len(test_content)} chars):")
    print(repr(test_content))
    print("\n" + "="*60)
    
    # Test the _is_likely_markdown_document method
    is_markdown = extractor._is_likely_markdown_document(test_content)
    print(f"_is_likely_markdown_document result: {is_markdown}")
    
    # Test section splitting
    sections = extractor._split_text_by_headers(test_content)
    print(f"Number of sections: {len(sections)}")
    
    for i, section in enumerate(sections):
        print(f"Section {i+1} ({len(section)} chars): {repr(section[:100])}...")
        is_section_markdown = extractor._is_likely_markdown_document(section)
        print(f"  → Is markdown: {is_section_markdown}")
    
    print("\n" + "="*60)
    
    # Test direct implicit extraction
    implicit_docs = extractor._extract_implicit_markdown_sections(test_content, test_session_id)
    print(f"Implicit extraction result: {len(implicit_docs)} documents")
    
    # Now test without explicit extraction (force implicit)
    print("\n" + "="*60)
    print("Testing direct _extract_markdown_documents (should use implicit):")
    
    # Temporarily disable explicit extraction by testing content without ```markdown blocks
    direct_docs = extractor._extract_markdown_documents(test_content, test_session_id)
    print(f"Direct markdown extraction: {len(direct_docs)} documents")
    
    for doc in direct_docs:
        print(f"  → Document: {doc.name} ({len(doc.metadata.get('content', ''))} chars)")

if __name__ == "__main__":
    debug_implicit_detection()