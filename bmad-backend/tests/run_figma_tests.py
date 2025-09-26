#!/usr/bin/env python3
"""
Simple test runner for Figma integration tests.
This script can be run without pytest if needed.
"""

import os
import sys
from typing import List
import traceback

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_figma_credentials():
    """Test that Figma credentials are properly configured."""
    print("=== Testing Figma Credentials Configuration ===")
    
    figma_token = os.getenv("FIGMA_TEST_TOKEN")
    figma_url = os.getenv("FIGMA_TEST_URL")
    
    print(f"FIGMA_TEST_TOKEN: {'✓ Set' if figma_token else '✗ Not Set'}")
    print(f"FIGMA_TEST_URL: {'✓ Set' if figma_url else '✗ Not Set'}")
    
    if figma_token and figma_url:
        # Extract file ID
        try:
            if "/design/" in figma_url:
                file_id = figma_url.split("/design/")[1].split("/")[0]
            elif "/file/" in figma_url:
                file_id = figma_url.split("/file/")[1].split("/")[0]
            else:
                raise ValueError("Invalid Figma URL format")
            
            print(f"Extracted File ID: {file_id}")
            print("✓ Credentials configuration looks good!")
            return True, file_id
        except Exception as e:
            print(f"✗ Error extracting file ID: {e}")
            return False, None
    else:
        print("✗ Missing required credentials")
        return False, None

def test_figma_service_basic():
    """Test basic FigmaService functionality."""
    print("\n=== Testing FigmaService Basic Functionality ===")
    
    try:
        from app.services.figma_service import FigmaService
        from app.models import ManagedDocument
        
        # Test initialization
        service = FigmaService()
        print("✓ FigmaService initialized without token")
        
        # Test token setting
        service.set_token("test_token")
        print("✓ Token setting works")
        
        # Test error handling
        managed_docs = []
        result = service.get_file_components("invalid_id", "test_session", managed_docs)
        
        if "error" in result and "not configured" in result["error"]:
            print("✗ Expected 'not configured' error but got different error")
            return False
        
        print("✓ Basic service functionality works")
        return True
        
    except Exception as e:
        print(f"✗ Error testing basic functionality: {e}")
        traceback.print_exc()
        return False

def test_figma_api_real():
    """Test real Figma API calls."""
    print("\n=== Testing Real Figma API Calls ===")
    
    figma_token = os.getenv("FIGMA_TEST_TOKEN")
    figma_url = os.getenv("FIGMA_TEST_URL")
    
    if not figma_token or not figma_url:
        print("✗ Skipping real API test - credentials not available")
        return True  # Not a failure, just skipped
    
    try:
        from app.services.figma_service import FigmaService
        from app.models import ManagedDocument
        
        # Extract file ID
        if "/design/" in figma_url:
            file_id = figma_url.split("/design/")[1].split("/")[0]
        elif "/file/" in figma_url:
            file_id = figma_url.split("/file/")[1].split("/")[0]
        else:
            raise ValueError("Invalid Figma URL format")
        
        service = FigmaService(token=figma_token)
        managed_docs = []
        
        print(f"Testing with File ID: {file_id}")
        
        # Test components
        print("Testing get_file_components...")
        result = service.get_file_components(file_id, "test_session", managed_docs)
        
        if "error" in result:
            print(f"✗ Components API error: {result['error']}")
            return False
        else:
            print(f"✓ Components fetched successfully!")
            print(f"  - File: {result.get('file_name', 'Unknown')}")
            print(f"  - Components found: {result.get('total_components', 0)}")
            print(f"  - Document created: {result.get('document_id', 'None')}")
        
        # Test user flows
        print("Testing get_user_flow_diagram...")
        result = service.get_user_flow_diagram(file_id, "test_session_2", managed_docs)
        
        if "error" in result:
            print(f"✗ User flows API error: {result['error']}")
            return False
        else:
            print(f"✓ User flows fetched successfully!")
            print(f"  - File: {result.get('file_name', 'Unknown')}")
            print(f"  - Screens found: {result.get('total_screens', 0)}")
            print(f"  - Flows found: {result.get('total_flows', 0)}")
            print(f"  - Document created: {result.get('document_id', 'None')}")
        
        print(f"✓ Total managed documents created: {len(managed_docs)}")
        return True
        
    except Exception as e:
        print(f"✗ Error in real API test: {e}")
        traceback.print_exc()
        return False

def test_figma_api_endpoints():
    """Test Figma API endpoints."""
    print("\n=== Testing Figma API Endpoints ===")
    
    figma_token = os.getenv("FIGMA_TEST_TOKEN")
    figma_url = os.getenv("FIGMA_TEST_URL")
    
    if not figma_token or not figma_url:
        print("✗ Skipping API endpoint test - credentials not available")
        return True  # Not a failure, just skipped
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Extract file ID
        if "/design/" in figma_url:
            file_id = figma_url.split("/design/")[1].split("/")[0]
        elif "/file/" in figma_url:
            file_id = figma_url.split("/file/")[1].split("/")[0]
        else:
            raise ValueError("Invalid Figma URL format")
        
        session_id = "test_session_endpoints"
        
        # Store credentials
        print("Testing credential storage...")
        credentials_data = {
            "session_id": session_id,
            "service": "figma",
            "credentials": {
                "token": figma_token,
                "email": ""
            }
        }
        
        response = client.post("/api/credentials", json=credentials_data)
        if response.status_code != 200:
            print(f"✗ Credential storage failed: {response.status_code} - {response.text}")
            return False
        
        print("✓ Credentials stored successfully")
        
        # Test components endpoint
        print("Testing components endpoint...")
        components_request = {
            "session_id": session_id,
            "file_id": file_id
        }
        
        response = client.post("/api/figma/components", json=components_request)
        if response.status_code != 200:
            print(f"✗ Components endpoint failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if "error" in result:
            print(f"✗ Components API returned error: {result['error']}")
            return False
        
        print("✓ Components endpoint works!")
        print(f"  - File: {result.get('file_name', 'Unknown')}")
        print(f"  - Components: {result.get('total_components', 0)}")
        
        # Test user flows endpoint
        print("Testing user flows endpoint...")
        flows_request = {
            "session_id": session_id,
            "file_id": file_id
        }
        
        response = client.post("/api/figma/user-flows", json=flows_request)
        if response.status_code != 200:
            print(f"✗ User flows endpoint failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if "error" in result:
            print(f"✗ User flows API returned error: {result['error']}")
            return False
        
        print("✓ User flows endpoint works!")
        print(f"  - File: {result.get('file_name', 'Unknown')}")
        print(f"  - Screens: {result.get('total_screens', 0)}")
        print(f"  - Flows: {result.get('total_flows', 0)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in API endpoint test: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Running Figma Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Credentials Configuration", test_figma_credentials),
        ("Service Basic Functionality", test_figma_service_basic),
        ("Real Figma API", test_figma_api_real),
        ("API Endpoints", test_figma_api_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            if test_name == "Credentials Configuration":
                success, file_id = test_func()
            else:
                success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:<8} {test_name}")
        if success:
            passed += 1
    
    print("-" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())