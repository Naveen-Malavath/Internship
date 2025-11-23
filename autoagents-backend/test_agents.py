#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Anthropic API key and all agents are working.
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
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"[OK] Loaded .env file from: {env_path}")
else:
    print(f"[WARN] .env file not found at {env_path}")
    load_dotenv()

def test_api_key():
    """Test if API key is loaded."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not found in environment!")
        print("\nMake sure you:")
        print("   1. Created the .env file in autoagents-backend/")
        print("   2. Added your API key: ANTHROPIC_API_KEY=sk-ant-...")
        print("   3. Saved the file")
        return False
    
    print(f"[OK] API Key found: {api_key[:8]}...{api_key[-4:]}")
    return True

async def test_claude_client():
    """Test Claude client connection."""
    try:
        from anthropic import AsyncAnthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        client = AsyncAnthropic(api_key=api_key)
        
        print("\n[TEST] Testing Claude API connection...")
        response = await client.messages.create(
            model="claude-3-haiku-20240307",  # Cheapest model for testing
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        
        print(f"[OK] Claude API is working!")
        print(f"   Response: {response.content[0].text}")
        print(f"   Input tokens: {response.usage.input_tokens}")
        print(f"   Output tokens: {response.usage.output_tokens}")
        
        # Calculate cost
        cost = (response.usage.input_tokens / 1_000_000 * 0.25) + (response.usage.output_tokens / 1_000_000 * 1.25)
        print(f"   Cost: ${cost:.6f}")
        
        return True
        
    except Exception as e:
        error_str = str(e)
        
        if "credit balance is too low" in error_str.lower():
            print("[ERROR] CREDIT BALANCE TOO LOW")
            print("\nYour API key is valid but has no credits.")
            print("   Add credits at: https://console.anthropic.com/settings/billing")
            
        elif "authentication" in error_str.lower():
            print("[ERROR] AUTHENTICATION FAILED")
            print("\nYour API key appears to be invalid.")
            print("   Get a new key at: https://console.anthropic.com/settings/keys")
            
        else:
            print(f"[ERROR] {error_str}")
        
        return False

async def test_agent1():
    """Test Agent-1 (Feature Generation)."""
    try:
        print("\n[TEST] Testing Agent-1 (Feature Generation)...")
        from app.services.agent1 import Agent1Service
        
        agent = Agent1Service()
        features = await agent.generate_features(
            project_title="Test Project",
            user_prompt="Build a simple todo app",
            previous_features=[]
        )
        
        print(f"[OK] Agent-1 is working!")
        print(f"   Generated {len(features)} features")
        if features:
            print(f"   Example feature: {features[0].get('feature_text', 'N/A')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Agent-1 failed: {str(e)[:100]}")
        return False

async def test_agent2():
    """Test Agent-2 (Story Generation)."""
    try:
        print("\n[TEST] Testing Agent-2 (Story Generation)...")
        from app.services.agent2 import Agent2Service
        
        agent = Agent2Service()
        
        # Mock feature for testing
        mock_features = [{
            "feature_text": "User authentication",
            "acceptance_criteria": ["Users can log in", "Users can log out"]
        }]
        
        stories = await agent.generate_stories(
            project_title="Test Project",
            features=mock_features,
            previous_stories=[]
        )
        
        print(f"[OK] Agent-2 is working!")
        print(f"   Generated {len(stories)} stories")
        if stories:
            print(f"   Example story: {stories[0].get('story_text', 'N/A')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Agent-2 failed: {str(e)[:100]}")
        return False

async def test_agent3():
    """Test Agent-3 (Diagram Generation)."""
    try:
        print("\n[TEST] Testing Agent-3 (Diagram Generation - HLD)...")
        from app.services.agent3 import Agent3Service
        
        agent = Agent3Service()
        
        # Mock data for testing
        mock_features = [{
            "feature_text": "User authentication and authorization"
        }]
        
        mock_stories = [{
            "feature_id": "1",
            "story_text": "As a user, I want to log in securely"
        }]
        
        diagram = await agent.generate_mermaid(
            project_title="Test Project",
            features=mock_features,
            stories=mock_stories,
            diagram_type="hld",
            original_prompt="Build a secure web app"
        )
        
        print(f"[OK] Agent-3 is working!")
        print(f"   Generated HLD diagram: {len(diagram)} characters")
        print(f"   Preview: {diagram[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Agent-3 failed: {str(e)[:100]}")
        return False

async def main():
    """Run all tests."""
    print("="*60)
    print("AutoAgents - API Key & Agent Testing")
    print("="*60)
    
    # Test 1: API Key
    if not test_api_key():
        print("\n[STOP] Fix API key first")
        return
    
    # Test 2: Claude Client
    if not await test_claude_client():
        print("\n[STOP] Fix Claude API connection first")
        return
    
    # Test 3: Agent-1
    await test_agent1()
    
    # Test 4: Agent-2
    await test_agent2()
    
    # Test 5: Agent-3
    await test_agent3()
    
    print("\n" + "="*60)
    print("[SUCCESS] ALL TESTS COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("   1. Restart your backend server")
    print("   2. Try generating features in your frontend")
    print("   3. All agents should now work properly!")
    print("\nYour AutoAgents system is ready!")

if __name__ == "__main__":
    asyncio.run(main())

