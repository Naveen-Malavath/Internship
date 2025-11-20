#!/usr/bin/env python3
"""
Script to list available Claude/Anthropic models for the configured API key.

This script:
1. Reads the API key from environment variables (ANTHROPIC_API_KEY or CLAUDE_API_KEY)
2. Validates the API key by making a test call
3. Lists known Claude models and optionally tests which ones are accessible
"""

import asyncio
import os
import sys
from typing import List, Optional

from anthropic import Anthropic, AsyncAnthropic
from anthropic import APIError

# Try to load from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not available, skip


# Known Claude models (as of 2024)
KNOWN_MODELS = [
    # Claude 3.5 Sonnet
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-5-sonnet-latest",
    "claude-sonnet-4-5-20250929",
    
    # Claude 3 Opus
    "claude-3-opus-20240229",
    "claude-3-opus-latest",
    
    # Claude 3 Sonnet
    "claude-3-sonnet-20240229",
    "claude-3-sonnet-latest",
    
    # Claude 3 Haiku
    "claude-3-haiku-20240307",
    "claude-3-5-haiku-20241022",
    "claude-3-5-haiku-latest",
    "claude-3-haiku-latest",
    
    # Claude 2
    "claude-2.1",
    "claude-2.0",
    
    # Claude Instant
    "claude-instant-1.2",
]


def get_api_key() -> Optional[str]:
    """Get API key from environment variables."""
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    return api_key


def validate_api_key(api_key: str) -> bool:
    """Validate the API key by making a simple test call."""
    try:
        client = Anthropic(api_key=api_key)
        # Make a minimal test call
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Use a lightweight model for testing
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}],
        )
        return True
    except APIError as e:
        print(f"❌ API Key validation failed: {e.message}", file=sys.stderr)
        if hasattr(e, 'status_code'):
            print(f"   Status code: {e.status_code}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error during API key validation: {e}", file=sys.stderr)
        return False


async def test_model_async(client: AsyncAnthropic, model: str) -> tuple[str, bool, Optional[str]]:
    """Test if a model is accessible with the given API key."""
    try:
        response = await client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}],
        )
        return (model, True, None)
    except APIError as e:
        error_msg = e.message or str(e)
        if hasattr(e, 'status_code') and e.status_code == 404:
            return (model, False, "Model not found")
        elif hasattr(e, 'status_code') and e.status_code == 401:
            return (model, False, "Unauthorized")
        else:
            return (model, False, error_msg)
    except Exception as e:
        return (model, False, str(e))


async def test_all_models(api_key: Optional[str] = None, test_models: bool = False) -> None:
    """List and optionally test all known models."""
    if test_models and not api_key:
        raise ValueError("API key is required when testing models")
    
    if api_key:
        client = AsyncAnthropic(api_key=api_key)
    
    print("\n" + "=" * 70)
    print("Claude/Anthropic Models")
    print("=" * 70)
    if api_key:
        print(f"\nAPI Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
    else:
        print("\n⚠️  No API key provided - showing known models only")
    print(f"\nTotal known models: {len(KNOWN_MODELS)}")
    
    if not test_models:
        print("\n📋 Known Claude Models:")
        print("-" * 70)
        for i, model in enumerate(KNOWN_MODELS, 1):
            print(f"{i:2d}. {model}")
        print("\n💡 Tip: Use --test flag to test which models are accessible with your API key")
    else:
        print("\n🧪 Testing models (this may take a moment)...")
        print("-" * 70)
        
        # Test models concurrently (but limit concurrency to avoid rate limits)
        semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests
        
        async def test_with_semaphore(model: str):
            async with semaphore:
                return await test_model_async(client, model)
        
        tasks = [test_with_semaphore(model) for model in KNOWN_MODELS]
        results = await asyncio.gather(*tasks)
        
        accessible = []
        inaccessible = []
        
        for model, accessible_flag, error in results:
            if accessible_flag:
                accessible.append(model)
            else:
                inaccessible.append((model, error))
        
        print(f"\n✅ Accessible Models ({len(accessible)}):")
        for model in accessible:
            print(f"   • {model}")
        
        if inaccessible:
            print(f"\n❌ Inaccessible Models ({len(inaccessible)}):")
            for model, error in inaccessible:
                print(f"   • {model}")
                if error:
                    print(f"     └─ {error}")
    
    print("\n" + "=" * 70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="List available Claude/Anthropic models for the configured API key"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test which models are accessible with the API key (slower but more accurate)"
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip API key validation (faster but may show incorrect results)"
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = get_api_key()
    
    # If testing models, API key is required
    if args.test and not api_key:
        print("❌ Error: API key is required when using --test flag.", file=sys.stderr)
        print("   Please set ANTHROPIC_API_KEY or CLAUDE_API_KEY", file=sys.stderr)
        sys.exit(1)
    
    # Validate API key unless --no-validate is used or no API key provided
    if api_key and not args.no_validate:
        print("🔑 Validating API key...")
        if not validate_api_key(api_key):
            print("\n❌ API key validation failed. Please check your API key.", file=sys.stderr)
            sys.exit(1)
        print("✅ API key is valid!\n")
    elif not api_key:
        print("⚠️  No API key found. Listing known models only.", file=sys.stderr)
        print("   Set ANTHROPIC_API_KEY or CLAUDE_API_KEY to test models.\n", file=sys.stderr)
    
    # List and optionally test models
    try:
        asyncio.run(test_all_models(api_key, test_models=args.test))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

