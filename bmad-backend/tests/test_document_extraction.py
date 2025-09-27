import unittest
import uuid
from datetime import datetime
from app.services.document_extractor import DocumentExtractor
from app.models import ManagedDocument

class TestDocumentExtractor(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.extractor = DocumentExtractor()
        self.test_session_id = str(uuid.uuid4())
    
    def test_extract_markdown_documents(self):
        """Test extraction of markdown documents from text."""
        # Test input with markdown in code blocks (explicit extraction)
        markdown_text_with_blocks = """
Here's a markdown document:

```markdown
# Document Title
This is a comprehensive document with substantial content that includes multiple paragraphs,
lists, and various markdown formatting elements to ensure it meets the extraction criteria.

## Features
- Feature 1: This is a detailed description of the first feature
- Feature 2: This is a detailed description of the second feature  
- Feature 3: This is a detailed description of the third feature

## Additional Content
More detailed content here with **bold text** and *italic text* to demonstrate
various markdown formatting options. This ensures the document has enough content
and formatting to be recognized as a valid markdown document.

### Subsection
Even more content to make this a substantial document that will definitely
meet all the extraction criteria for our improved parser.
```
        """
        
        # Test the private method directly
        documents = self.extractor._extract_markdown_documents(markdown_text_with_blocks, self.test_session_id)
        
        # Check results  
        self.assertTrue(len(documents) > 0, "Should extract at least one markdown document")
        doc = documents[0]
        self.assertEqual(doc.name, "Document Title")
        self.assertEqual(doc.type, "markdown")
        self.assertEqual(doc.source, "llm_response")
        self.assertIn("content", doc.metadata)
        self.assertIn("# Document Title", doc.metadata["content"])
    
    def test_extract_code_blocks(self):
        """Test extraction of code blocks from text."""
        # Test input with code blocks
        code_text = """
Here's a Python function:

```python
def hello_world():
    # filename: hello.py
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
```

And here's some JavaScript:

```javascript
function calculateSum(a, b) {
    return a + b;
}

console.log(calculateSum(5, 10));
```
        """
        
        documents = self.extractor._extract_code_blocks(code_text, self.test_session_id)
        
        # Check results
        self.assertEqual(len(documents), 2, "Should extract two code blocks")
        
        # Check Python code block
        python_doc = next((doc for doc in documents if doc.metadata["language"] == "python"), None)
        self.assertIsNotNone(python_doc)
        self.assertEqual(python_doc.name, "hello.py")
        self.assertIn("def hello_world", python_doc.metadata["content"])
        
        # Check JavaScript code block
        js_doc = next((doc for doc in documents if doc.metadata["language"] == "javascript"), None)
        self.assertIsNotNone(js_doc)
        self.assertIn("function calculateSum", js_doc.metadata["content"])
    
    def test_extract_diagrams(self):
        """Test extraction of diagram specifications from text."""
        # Test input with a mermaid diagram
        diagram_text = """
Here's a sequence diagram:

```mermaid
sequenceDiagram
    participant User
    participant System
    User->>System: Request data
    System-->>User: Return data
```
        """
        
        documents = self.extractor._extract_diagrams(diagram_text, self.test_session_id)
        
        # Check results
        self.assertEqual(len(documents), 1, "Should extract one diagram")
        doc = documents[0]
        self.assertEqual(doc.type, "diagram")
        self.assertEqual(doc.metadata["format"], "mermaid")
        self.assertIn("sequenceDiagram", doc.metadata["content"])
    
    def test_extract_json_documents(self):
        """Test extraction of JSON documents from text."""
        # Test input with JSON blocks
        json_text = """
Here's a JSON configuration:

```json
{
    "name": "Configuration File",
    "version": "1.0",
    "settings": {
        "enabled": true,
        "timeout": 30
    }
}
```
        """
        
        documents = self.extractor._extract_json_documents(json_text, self.test_session_id)
        
        # Check results
        self.assertEqual(len(documents), 1, "Should extract one JSON document")
        doc = documents[0]
        self.assertEqual(doc.type, "json")
        self.assertEqual(doc.name, "Configuration File")
        self.assertEqual(doc.metadata["content"]["version"], "1.0")
    
    def test_extract_documents_from_response(self):
        """Test the main extraction method with a combined response."""
        # Combined text with different document types
        combined_text = """
# Analysis Report

This document provides an analysis of the project requirements.

## Findings

Here are the key findings:

```json
{
    "name": "Project Requirements",
    "priority": "high",
    "components": ["frontend", "backend", "database"]
}
```

## Implementation Plan

Here's a sample implementation:

```python
def implement_feature():
    # filename: feature_implementation.py
    print("Implementing feature...")
    return {"status": "complete"}
```

## Architecture Diagram

```mermaid
flowchart TD
    A[Client] --> B[API]
    B --> C[Database]
    B --> D[External Service]
```
        """
        
        documents = self.extractor.extract_documents_from_response(combined_text, self.test_session_id)
        
        # Check that all document types were extracted
        self.assertGreaterEqual(len(documents), 3, "Should extract multiple documents")
        
        # Check document types
        doc_types = {doc.type for doc in documents}
        self.assertIn("markdown", doc_types)
        self.assertIn("code", doc_types)
        self.assertIn("diagram", doc_types)
        self.assertIn("json", doc_types)
        
        # Debug output to understand what's in the documents
        for i, doc in enumerate(documents):
            print(f"Document {i}: {doc.type} - {doc.name}")
            if doc.type == "code":
                print(f"  Content: {doc.metadata['content'][:30]}...")
                print(f"  Language: {doc.metadata.get('language', 'unknown')}")
        
        # Verify code document
        python_code_doc = next((doc for doc in documents if doc.type == "code" and doc.metadata.get("language") == "python"), None)
        self.assertIsNotNone(python_code_doc, "Should have found a Python code document")
        self.assertIn("implement_feature", python_code_doc.metadata["content"])
        
        # Verify json document
        json_doc = next((doc for doc in documents if doc.type == "json"), None)
        self.assertIsNotNone(json_doc)
        self.assertEqual(json_doc.name, "Project Requirements")

if __name__ == "__main__":
    unittest.main()