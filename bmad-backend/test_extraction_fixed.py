#!/usr/bin/env python3
"""
Test script to verify document extraction functionality using the selected BRD file.
"""

import os
import sys
import uuid
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.document_extractor import DocumentExtractor
from app.services.document_storage import DocumentStorage

def test_document_extraction():
    """Test document extraction with the BRD file."""
    
    # Read the BRD file content
    brd_file_path = "/Users/zvezdanprotic/Downloads/BMAD/bmad-backend/tests/Online_Appointment_Booking_System_BRD.md"
    
    with open(brd_file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    print(f"File content length: {len(file_content)} characters")
    print(f"First 200 characters:\n{file_content[:200]}...")
    print("\n" + "="*80 + "\n")
    
    # Initialize services
    extractor = DocumentExtractor()
    document_storage = DocumentStorage()
    test_session_id = str(uuid.uuid4())
    
    print(f"Test session ID: {test_session_id}")
    
    # Test 1: Direct markdown extraction
    print("TEST 1: Testing direct markdown extraction...")
    documents = extractor._extract_markdown_documents(file_content, test_session_id)
    print(f"Direct extraction found {len(documents)} documents")
    
    for i, doc in enumerate(documents):
        print(f"  Document {i+1}: {doc.name} (type: {doc.type}, method: {doc.metadata.get('extraction_method', 'unknown')})")
    
    print("\n" + "-"*60 + "\n")
    
    # Test 2: Full response extraction (simulate LLM response)
    print("TEST 2: Testing full response extraction...")
    # Wrap the content as if it came from an LLM response
    llm_response = f"""Here's the business requirements document:

```markdown
{file_content}
```

This document contains comprehensive requirements for the appointment booking system."""
    
    documents = extractor.extract_documents_from_response(llm_response, test_session_id)
    print(f"Full extraction found {len(documents)} documents")
    
    for i, doc in enumerate(documents):
        print(f"  Document {i+1}: {doc.name} (type: {doc.type}, method: {doc.metadata.get('extraction_method', 'unknown')})")
        print(f"    Content length: {len(doc.metadata.get('content', ''))} characters")
        
        # Save each document to storage
        try:
            document_storage.save_document(doc, test_session_id)
            print(f"    ✅ Saved to storage successfully")
        except Exception as e:
            print(f"    ❌ Failed to save: {e}")
    
    print("\n" + "-"*60 + "\n")
    
    # Test 3: Verify documents are in storage
    print("TEST 3: Verifying documents in storage...")
    stored_documents = document_storage.get_documents_for_session(test_session_id)
    print(f"Found {len(stored_documents)} documents in storage for session")
    
    for i, doc in enumerate(stored_documents):
        print(f"  Stored Document {i+1}: {doc.name} (ID: {doc.id})")
        
        # Try to retrieve content
        try:
            filename, mime_type, content_bytes = document_storage.read_document_content(str(doc.id), test_session_id)
            content = content_bytes.decode('utf-8')
            print(f"    Content retrieved: {len(content)} characters")
            print(f"    File: {filename}, MIME: {mime_type}")
            print(f"    First 100 chars: {content[:100]}...")
        except Exception as e:
            print(f"    ❌ Failed to retrieve content: {e}")
    
    print("\n" + "="*80 + "\n")
    print("Test Summary:")
    print(f"- Direct extraction: {len(documents)} documents")
    print(f"- Storage verification: {len(stored_documents)} documents saved")
    
    return documents, stored_documents

if __name__ == "__main__":
    try:
        docs, stored = test_document_extraction()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()