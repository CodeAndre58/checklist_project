#!/usr/bin/env python3
"""
Test script for remote Ollama connectivity and authentication.
Verifies configuration before running full analysis.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.llm_engine.ollama_client import OllamaClient


def test_remote_ollama():
    """Test remote Ollama connection and authentication."""
    
    print("=" * 60)
    print("🔍 Remote Ollama Connection Test")
    print("=" * 60)
    
    # Load environment
    load_dotenv()
    
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    model = os.getenv('OLLAMA_MODEL', 'gemma4:31b-cloud')
    api_key = os.getenv('OLLAMA_API_KEY', '')
    
    print(f"\n📋 Configuration:")
    print(f"  Base URL:  {base_url}")
    print(f"  Model:     {model}")
    print(f"  API Key:   {'*****' if api_key else '(none - local setup)'}")
    
    # Create client
    try:
        client = OllamaClient(
            model_name=model,
            base_url=base_url,
            api_key=api_key if api_key else None
        )
        print(f"\n✓ OllamaClient created successfully")
    except Exception as e:
        print(f"\n✗ Failed to create OllamaClient: {e}")
        return False
    
    # Check if remote
    print(f"\n🌐 Connection Type:")
    if client.is_remote:
        print(f"  Type: REMOTE (cloud)")
        if client.api_key:
            print(f"  Auth: Yes (Bearer token)")
        else:
            print(f"  Auth: No (using base_url only)")
    else:
        print(f"  Type: LOCAL (localhost)")
    
    # Test availability
    print(f"\n⏳ Testing connectivity...")
    try:
        available = client.is_available()
        if available:
            print(f"  ✓ Server is reachable")
        else:
            print(f"  ✗ Server not reachable")
            return False
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return False
    
    # Test simple query
    print(f"\n📝 Testing model query...")
    try:
        test_prompt = "Say 'Hello from PRISMA Analyzer' in one sentence only."
        response = client.query(test_prompt)
        
        if response:
            print(f"  ✓ Model responded successfully")
            response_str = str(response)
            print(f"  Response preview: {response_str[:100]}...")
            return True
        else:
            print(f"  ✗ No response from model")
            return False
            
    except Exception as e:
        print(f"  ✗ Query failed: {e}")
        return False


def test_with_args():
    """Test with command-line arguments."""
    
    print("\n" + "=" * 60)
    print("🔧 Testing with CLI Arguments")
    print("=" * 60)
    
    # Example: python3 test_remote.py --url https://api.xxx.com --api-key sk_xxx
    import argparse
    
    parser = argparse.ArgumentParser(description='Test remote Ollama')
    parser.add_argument('--url', default=None, help='Ollama server URL')
    parser.add_argument('--api-key', default=None, help='API key for remote')
    parser.add_argument('--model', default=None, help='Model name')
    
    args = parser.parse_args()
    
    base_url = args.url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    model = args.model or os.getenv('OLLAMA_MODEL', 'gemma4:31b-cloud')
    api_key = args.api_key or os.getenv('OLLAMA_API_KEY', '')
    
    print(f"\n📋 CLI Configuration:")
    print(f"  URL:       {base_url}")
    print(f"  Model:     {model}")
    print(f"  API Key:   {'*' * 8 if api_key else '(none)'}")
    
    try:
        client = OllamaClient(
            model_name=model,
            base_url=base_url,
            api_key=api_key if api_key else None
        )
        
        available = client.is_available()
        if available:
            print(f"\n  ✓ Connection successful!")
            return True
        else:
            print(f"\n  ✗ Server unreachable")
            return False
            
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        return False


if __name__ == '__main__':
    # Test main configuration from .env
    success = test_remote_ollama()
    
    # If --url or --api-key provided, test CLI args
    if '--url' in sys.argv or '--api-key' in sys.argv:
        cli_success = test_with_args()
        success = success and cli_success
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Remote Ollama is ready to use.")
        print(f"\n   Run: python3 cli.py your_paper.pdf")
        sys.exit(0)
    else:
        print("❌ Tests failed. Check configuration above.")
        print(f"\n   See REMOTE_OLLAMA.md for troubleshooting.")
        sys.exit(1)
