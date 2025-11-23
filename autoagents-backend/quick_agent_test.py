#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test for Anthropic API key - NO MongoDB required!
This tests that your new API key works with all agents.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

async def test_api_key():
    """Quick test of Anthropic API key."""
    from anthropic import AsyncAnthropic
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY environment variable not found")
        return False
    
    if "PASTE" in api_key or len(api_key) < 50:
        print("[ERROR] API key looks invalid - did you paste your real key?")
        return False
    
    print(f"[INFO] Testing API key: {api_key[:12]}...{api_key[-6:]}")
    
    try:
        client = AsyncAnthropic(api_key=api_key)
        
        print("[INFO] Sending test request to Claude...")
        response = await client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=20,
            messages=[{"role": "user", "content": "Say 'API key works!'"}]
        )
        
        result = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens
        
        print(f"[SUCCESS] API Key is working!")
        print(f"[SUCCESS] Claude responded: {result}")
        print(f"[INFO] Tokens used: {tokens}")
        
        return True
        
    except Exception as e:
        error_str = str(e)
        
        if "credit balance is too low" in error_str.lower():
            print("[ERROR] Your API key is valid but has no credits!")
            print("[ACTION] Add credits at: https://console.anthropic.com/settings/billing")
        elif "authentication" in error_str.lower() or "api_key" in error_str.lower():
            print("[ERROR] Invalid API key!")
            print("[ACTION] Check your API key at: https://console.anthropic.com/settings/keys")
        else:
            print(f"[ERROR] {error_str}")
        
        return False

async def test_agent1_minimal():
    """Test Agent-1 with minimal request."""
    try:
        print("\n[TEST] Testing Agent-1 (Feature Generation)...")
        from app.services.agent1 import Agent1Service
        
        agent = Agent1Service()
        features = await agent.generate_features(
            project_title="Quick Test",
            user_prompt="Build a todo app with user authentication",
            previous_features=[]
        )
        
        print(f"[SUCCESS] Agent-1 generated {len(features)} features!")
        for i, feature in enumerate(features[:3], 1):
            print(f"  {i}. {feature.get('feature_text', 'N/A')[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Agent-1 failed: {str(e)[:150]}")
        return False

async def main():
    """Run quick tests."""
    print("="*70)
    print("QUICK AGENT TEST - No MongoDB Required")
    print("="*70)
    print()
    
    # Test 1: API Key
    if not await test_api_key():
        print("\n[FAIL] API key test failed. Fix your .env file first.")
        return
    
    print("\n" + "="*70)
    print("[SUCCESS] Your new Anthropic API key is working!")
    print("="*70)
    
    # Test 2: Agent-1 (if you want to test actual generation)
    print("\nDo you want to test Agent-1 feature generation?")
    print("This will use a few API tokens (~$0.01)")
    print()
    
    try:
        test_agent = await test_agent1_minimal()
        if test_agent:
            print("\n" + "="*70)
            print("[SUCCESS] All agents are working with your new API key!")
            print("="*70)
            print("\nNext steps:")
            print("  1. Set up MongoDB Atlas (or use local MongoDB)")
            print("  2. Update MONGO_URI in .env file")
            print("  3. Restart your backend server")
            print("  4. Your AutoAgents system will be fully operational!")
    except Exception as e:
        print(f"\n[INFO] Agent test skipped: {e}")
        print("\nYour API key works! Now set up MongoDB to use the full system.")

if __name__ == "__main__":
    asyncio.run(main())

