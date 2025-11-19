#!/usr/bin/env python3
"""Test script to check if Claude Sonnet 4.5 model is available with your API key."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

try:
    from anthropic import AsyncAnthropic
    import asyncio
except ImportError:
    print("ERROR: anthropic package not installed. Install it with: pip install anthropic")
    sys.exit(1)

async def test_model_async(model_name: str, api_key: str) -> dict:
    """Test if a specific model is available (async version)."""
    try:
        # Initialize async client (same as used in the actual code)
        client = AsyncAnthropic(api_key=api_key)
        
        # Try a simple API call with the model
        response = await client.messages.create(
            model=model_name,
            max_tokens=10,
            messages=[{
                "role": "user",
                "content": "Say 'test'"
            }]
        )
        
        return {
            "available": True,
            "message": "Model is available and working!",
            "response": response.content[0].text if response.content else None
        }
    except Exception as e:
        error_type = getattr(e, 'type', 'unknown')
        status_code = getattr(e, 'status_code', None)
        
        # Check for specific error types
        error_str = str(e).lower()
        if 'not_found' in error_str or '404' in error_str or 'model not found' in error_str:
            error_type = 'model_not_found'
        elif 'authentication' in error_str or '401' in error_str or '403' in error_str:
            error_type = 'authentication_error'
        elif 'rate_limit' in error_str or '429' in error_str:
            error_type = 'rate_limit'
        
        return {
            "available": False,
            "error_type": error_type,
            "status_code": status_code,
            "error_message": str(e)
        }

def test_model(model_name: str, api_key: str) -> dict:
    """Test if a specific model is available (sync wrapper for async)."""
    return asyncio.run(test_model_async(model_name, api_key))

def main():
    print("=" * 70)
    print("Claude Model Availability Checker")
    print("=" * 70)
    print()
    
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY or CLAUDE_API_KEY not found in environment variables")
        print("Make sure your .env file is in the autoagents-backend directory")
        sys.exit(1)
    
    print(f"API Key found: {api_key[:20]}...{api_key[-10:]}")
    print()
    
    # Models to test
    models_to_test = [
        "claude-sonnet-4-5-20250929",  # Sonnet 4.5
        "claude-3-5-sonnet-latest",    # Sonnet 3.5 (fallback)
        "claude-3-5-haiku-latest",     # Haiku 3.5 (for comparison)
        "claude-3-5-opus-latest",      # Opus 3.5 (for comparison)
    ]
    
    results = {}
    
    for model_name in models_to_test:
        print(f"Testing model: {model_name}")
        print("-" * 70)
        result = test_model(model_name, api_key)
        results[model_name] = result
        
        if result["available"]:
            print(f"[OK] {model_name} - AVAILABLE")
            if result.get("response"):
                print(f"   Response: {result['response']}")
        else:
            print(f"[FAIL] {model_name} - NOT AVAILABLE")
            print(f"   Error Type: {result.get('error_type', 'N/A')}")
            print(f"   Status Code: {result.get('status_code', 'N/A')}")
            if result.get('error_message'):
                error_msg = result['error_message'][:200]  # Limit length
                print(f"   Error: {error_msg}")
        print()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if results.get("claude-sonnet-4-5-20250929", {}).get("available"):
        print("[OK] Your API key HAS ACCESS to Claude Sonnet 4.5!")
        print("   Model: claude-sonnet-4-5-20250929")
    else:
        print("[FAIL] Your API key DOES NOT have access to Claude Sonnet 4.5")
        print("   Using fallback model: claude-3-5-sonnet-latest")
        
        if results.get("claude-3-5-sonnet-latest", {}).get("available"):
            print("   [OK] Fallback model is available and will be used")
        else:
            print("   [WARNING] Fallback model is also not available!")
    
    print()
    
    # Show which models are available
    available_models = [name for name, result in results.items() if result.get("available")]
    if available_models:
        print("Available models:")
        for model in available_models:
            print(f"  [OK] {model}")
    else:
        print("[WARNING] No models are available. Check your API key and network connection.")

if __name__ == "__main__":
    main()
