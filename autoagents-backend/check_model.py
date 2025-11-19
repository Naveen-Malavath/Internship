#!/usr/bin/env python3
"""Simple script to check Claude model availability - uses same approach as server code."""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

from anthropic import AsyncAnthropic
from anthropic import APIError

async def check_model(model_name: str, api_key: str):
    """Check if a model is available."""
    try:
        client = AsyncAnthropic(api_key=api_key)
        response = await client.messages.create(
            model=model_name,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        await client.close()
        return {"available": True, "response": response.content[0].text if response.content else "OK"}
    except APIError as e:
        await client.close()
        error_type = getattr(e, 'type', 'unknown')
        status_code = getattr(e, 'status_code', None)
        
        if error_type == 'not_found_error' or status_code == 404:
            return {"available": False, "reason": "model_not_found", "error": str(e)}
        elif status_code == 401 or status_code == 403:
            return {"available": False, "reason": "auth_error", "error": str(e)}
        else:
            return {"available": False, "reason": "api_error", "error": str(e), "type": error_type, "status": status_code}
    except Exception as e:
        return {"available": False, "reason": "unknown_error", "error": str(e), "error_type": type(e).__name__}

async def main():
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("ERROR: API key not found")
        return
    
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}\n")
    
    models = [
        "claude-sonnet-4-5-20250929",
        "claude-3-5-sonnet-latest",
        "claude-3-5-haiku-latest",
    ]
    
    results = {}
    for model in models:
        print(f"Checking {model}...")
        result = await check_model(model, api_key)
        results[model] = result
        
        if result["available"]:
            print(f"  [OK] Available")
        else:
            print(f"  [FAIL] Not available - {result.get('reason', 'unknown')}")
            if result.get('error'):
                error_msg = result['error'][:150]
                print(f"    Error: {error_msg}")
            if result.get('type'):
                print(f"    Error Type: {result['type']}")
            if result.get('status'):
                print(f"    Status Code: {result['status']}")
            if result.get('error_type'):
                print(f"    Exception Type: {result['error_type']}")
        print()
    
    print("=" * 60)
    if results["claude-sonnet-4-5-20250929"]["available"]:
        print("[OK] Your API key HAS ACCESS to Claude Sonnet 4.5!")
    else:
        print("[FAIL] Your API key does NOT have access to Claude Sonnet 4.5")
        if results["claude-3-5-sonnet-latest"]["available"]:
            print("[OK] But claude-3-5-sonnet-latest is available as fallback")

if __name__ == "__main__":
    asyncio.run(main())

