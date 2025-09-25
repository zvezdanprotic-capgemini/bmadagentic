#!/usr/bin/env python3
"""
Diagnostic script to test Azure OpenAI connectivity with detailed logging.
This script helps diagnose connection issues when the main application 
encounters APIConnectionError but AzureTest.py works.
"""

import os
import sys
import logging
import traceback
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

def test_with_direct_openai():
    """Test with direct OpenAI library."""
    try:
        from openai import AzureOpenAI
        
        # Get config from environment variables
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        logging.info("Testing direct Azure OpenAI connection...")
        logging.debug(f"Endpoint: {endpoint}")
        logging.debug(f"API version: {api_version}")
        logging.debug(f"Deployment: {deployment}")
        logging.debug(f"API key: {'*' * 10 + api_key[-5:] if api_key else 'Not set'}")
        
        client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=api_key,
        )
        
        logging.info("Client created, attempting completion...")
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Test connection"}
            ],
            max_completion_tokens=50,  # Use max_completion_tokens for newer API versions
            model=deployment
        )
        
        logging.info("Direct OpenAI test successful!")
        logging.info(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        logging.error(f"Direct OpenAI test failed: {e}")
        logging.error(f"Error details: {traceback.format_exc()}")
        return False

def test_with_langchain():
    """Test with LangChain library."""
    try:
        from langchain_openai import AzureChatOpenAI
        
        # Get config from environment variables
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        logging.info("Testing LangChain Azure OpenAI connection...")
        logging.debug(f"Endpoint: {endpoint}")
        logging.debug(f"API version: {api_version}")
        logging.debug(f"Deployment: {deployment}")
        logging.debug(f"API key: {'*' * 10 + api_key[-5:] if api_key else 'Not set'}")
        
        llm = AzureChatOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
            azure_deployment=deployment
        )
        
        logging.info("LangChain client created, attempting invocation...")
        
        response = llm.invoke("Test connection with LangChain")
        
        logging.info("LangChain test successful!")
        logging.info(f"Response: {response.content}")
        return True
    except Exception as e:
        logging.error(f"LangChain test failed: {e}")
        logging.error(f"Error details: {traceback.format_exc()}")
        return False

def check_network():
    """Perform basic network connectivity checks."""
    try:
        import socket
        import requests
        
        logging.info("Testing network connectivity...")
        
        # Get endpoint from environment
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        if not endpoint:
            logging.error("AZURE_OPENAI_ENDPOINT not set, skipping network check")
            return
            
        # Extract hostname from endpoint
        import re
        hostname_match = re.match(r'https?://([^:/]+)', endpoint)
        if not hostname_match:
            logging.error(f"Could not extract hostname from endpoint: {endpoint}")
            return
            
        hostname = hostname_match.group(1)
        logging.info(f"Testing connectivity to {hostname}")
        
        # Test basic socket connection
        try:
            socket.create_connection((hostname, 443), timeout=5)
            logging.info(f"Socket connection to {hostname}:443 successful")
        except Exception as e:
            logging.error(f"Socket connection failed: {e}")
            
        # Test HTTPS request
        try:
            response = requests.get(endpoint, timeout=5)
            logging.info(f"HTTPS request to {endpoint} status code: {response.status_code}")
        except Exception as e:
            logging.error(f"HTTPS request failed: {e}")
    
    except Exception as e:
        logging.error(f"Network check failed: {e}")
        logging.error(f"Error details: {traceback.format_exc()}")

def main():
    """Run all tests."""
    logging.info("Starting Azure OpenAI diagnostic tests")
    logging.info(f"Python version: {sys.version}")
    
    # Check network connectivity
    check_network()
    
    # Run direct OpenAI test
    direct_test = test_with_direct_openai()
    
    # Run LangChain test
    langchain_test = test_with_langchain()
    
    # Summary
    logging.info("\n=== Test Summary ===")
    logging.info(f"Direct OpenAI test: {'PASSED' if direct_test else 'FAILED'}")
    logging.info(f"LangChain test: {'PASSED' if langchain_test else 'FAILED'}")
    
    # Provide diagnostic information if tests have different results
    if direct_test and not langchain_test:
        logging.warning("The direct OpenAI test passed but the LangChain test failed. "
                       "This suggests an issue with the LangChain integration rather "
                       "than with the Azure OpenAI credentials or network connectivity.")
    elif not direct_test and langchain_test:
        logging.warning("Unusual result: LangChain test passed but direct test failed.")
        
    if not direct_test and not langchain_test:
        logging.error("All tests failed. Check your Azure OpenAI credentials, "
                     "network connectivity, and whether your IP is allowed to "
                     "access the Azure OpenAI resource.")

if __name__ == "__main__":
    main()