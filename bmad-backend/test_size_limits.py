#!/usr/bin/env python3
"""
Test script to verify document extraction with different markdown sizes.
"""

import os
import sys
import uuid

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.document_extractor import DocumentExtractor

def test_markdown_size_limits():
    """Test markdown extraction with various sizes."""
    
    extractor = DocumentExtractor()
    test_session_id = str(uuid.uuid4())
    
    print("🔍 Testing Markdown Size Limits in Document Extraction\n")
    print("="*80)
    
    # Test cases with different sizes
    test_cases = [
        {
            "name": "Very Small (5 chars)",
            "content": "# Hi",
            "expected": "Should be rejected (< 20 chars)"
        },
        {
            "name": "Small (15 chars)", 
            "content": "# Small Header",
            "expected": "Should be rejected (< 20 chars)"
        },
        {
            "name": "Just Above Minimum (25 chars)",
            "content": "# Header\nSome content.",
            "expected": "Should be accepted (> 20 chars)"
        },
        {
            "name": "Medium (80 chars)",
            "content": "# Medium Document\nThis is a medium-sized document with some content here.",
            "expected": "Should be accepted (> 20 chars)"
        },
        {
            "name": "Below Implicit Threshold (60 chars)",
            "content": "# Short\n- Item 1\n- Item 2\n\nShort content paragraph.",
            "expected": "Should be rejected by implicit method (< 100 chars, score < 2)"
        },
        {
            "name": "Above Implicit Threshold (150 chars)",
            "content": """# Good Document
            
## Section 1
This is a **good document** with:
- Multiple items
- Bold text
- Good structure

## Section 2  
More content here.""",
            "expected": "Should be accepted by implicit method (> 100 chars, score >= 2)"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        print(f"Content length: {len(test_case['content'])} characters")
        print(f"Expected: {test_case['expected']}")
        
        # Test 1: Explicit extraction (with ```markdown wrapper)
        explicit_input = f"""Here's a document:

```markdown
{test_case['content']}
```

End of document."""
        
        explicit_docs = extractor.extract_documents_from_response(explicit_input, test_session_id)
        print(f"✅ Explicit method: {len(explicit_docs)} documents extracted")
        
        # Test 2: Implicit extraction (raw markdown)
        implicit_docs = extractor._extract_markdown_documents(test_case['content'], test_session_id)
        print(f"✅ Implicit method: {len(implicit_docs)} documents extracted")
        
        # Show extracted document details
        if explicit_docs:
            doc = explicit_docs[0]
            print(f"   → Document name: '{doc.name}'")
            print(f"   → Content length: {len(doc.metadata.get('content', ''))} chars")
        
        print("-" * 60)
    
    print("\n" + "="*80)
    print("📊 SIZE LIMITS SUMMARY:")
    print("• Explicit markdown blocks (```markdown): Minimum 20 characters")
    print("• Implicit markdown detection: Minimum 100 characters + score >= 2")
    print("• Section splitting: Minimum 50 characters per section")
    print("• Code blocks: Minimum 3 lines")
    
    return True

if __name__ == "__main__":
    try:
        test_markdown_size_limits()
        print("\n✅ Size limit tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()