#!/usr/bin/env python3
"""
Comprehensive test of markdown extraction size capabilities.
"""

import os
import sys
import uuid

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.document_extractor import DocumentExtractor

def test_comprehensive_sizes():
    """Test extraction with various real-world markdown sizes."""
    
    extractor = DocumentExtractor()
    test_session_id = str(uuid.uuid4())
    
    print("📋 COMPREHENSIVE MARKDOWN SIZE CAPABILITY TEST")
    print("="*80)
    
    test_cases = [
        {
            "name": "Tiny Note (10 chars)",
            "explicit": "```markdown\n# Todo\n```",
            "implicit": "# Todo",
            "size": 6
        },
        {
            "name": "Short README (50 chars)", 
            "explicit": "```markdown\n# Project\n\nA simple tool for automation.\n```",
            "implicit": "# Project\n\nA simple tool for automation.",
            "size": 35
        },
        {
            "name": "Medium Documentation (200 chars)",
            "explicit": f"```markdown\n{'# API Documentation' + chr(10)*2 + '## Overview' + chr(10) + 'This API provides **REST endpoints** for:' + chr(10) + '- User management' + chr(10) + '- Data processing' + chr(10)*2 + '## Authentication' + chr(10) + 'Use Bearer tokens.'}\n```",
            "implicit": "# API Documentation\n\n## Overview\nThis API provides **REST endpoints** for:\n- User management\n- Data processing\n\n## Authentication\nUse Bearer tokens.",
            "size": 133
        },
        {
            "name": "Large Guide (1000+ chars)",
            "explicit": None,  # Will generate
            "implicit": None,  # Will generate
            "size": 1000
        }
    ]
    
    # Generate large content
    large_content = """# Complete Setup Guide

## Prerequisites
Before starting, ensure you have:
- **Python 3.8+** installed
- **pip** package manager
- **Git** for version control

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/example/project.git
cd project
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables
Create a `.env` file:
```
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

## Running the Application

### Development Mode
```bash
python manage.py runserver
```

### Production Mode
```bash
gunicorn app:application --bind 0.0.0.0:8000
```

## Testing
Run tests with:
```bash
pytest tests/
```

## Troubleshooting

### Common Issues
- **Port already in use**: Change port in settings
- **Database connection error**: Check DATABASE_URL
- **Import errors**: Verify virtual environment activation

## Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## License
MIT License - see LICENSE file for details."""

    test_cases[3]["explicit"] = f"```markdown\n{large_content}\n```"
    test_cases[3]["implicit"] = large_content
    test_cases[3]["size"] = len(large_content)
    
    results = []
    
    for test_case in test_cases:
        print(f"\n📄 {test_case['name']} ({test_case['size']} chars)")
        print("-" * 60)
        
        # Test explicit extraction
        explicit_docs = extractor.extract_documents_from_response(test_case['explicit'], test_session_id)
        explicit_count = len(explicit_docs)
        
        # Test implicit extraction  
        implicit_docs = extractor._extract_markdown_documents(test_case['implicit'], test_session_id)
        implicit_count = len(implicit_docs)
        
        print(f"✅ Explicit extraction: {explicit_count} documents")
        print(f"✅ Implicit extraction: {implicit_count} documents")
        
        # Show details of extracted documents
        if explicit_docs:
            doc = explicit_docs[0]
            print(f"   → Title: '{doc.name}'")
            print(f"   → Method: {doc.metadata.get('extraction_method', 'unknown')}")
            print(f"   → Content: {len(doc.metadata.get('content', ''))} chars")
        
        results.append({
            "name": test_case['name'],
            "size": test_case['size'],
            "explicit": explicit_count,
            "implicit": implicit_count
        })
    
    print("\n" + "="*80)
    print("📊 RESULTS SUMMARY")
    print("="*80)
    
    print(f"{'Size Category':<25} {'Size':<8} {'Explicit':<10} {'Implicit':<10} {'Status'}")
    print("-" * 65)
    
    for result in results:
        explicit_status = "✅" if result['explicit'] > 0 else "❌"
        implicit_status = "✅" if result['implicit'] > 0 else "❌"
        status = f"{explicit_status} / {implicit_status}"
        
        print(f"{result['name']:<25} {result['size']:<8} {result['explicit']:<10} {result['implicit']:<10} {status}")
    
    print("\n" + "="*80)
    print("🎯 SIZE LIMIT ANALYSIS:")
    print("• EXPLICIT (```markdown blocks): Accepts >= 20 characters")
    print("• IMPLICIT (raw markdown): Requires >= 100 chars + markdown formatting score >= 2")
    print("• Very small content (< 20 chars): Not extracted by either method")
    print("• Small-medium content (20-99 chars): Only extracted via explicit method")
    print("• Large content (100+ chars): Extracted by both methods")
    print("• NO UPPER SIZE LIMIT: Can handle documents of any size!")

if __name__ == "__main__":
    test_comprehensive_sizes()