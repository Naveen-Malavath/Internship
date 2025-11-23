"""Test script to diagnose the visualizer endpoint 500 error."""
import asyncio
import sys
import traceback
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.services.agent3 import Agent3Service
from app.services.claude_client import get_claude_client


async def test_agent3():
    """Test Agent3Service.generate_mermaid method."""
    print("=" * 80)
    print("Testing Agent3Service...")
    print("=" * 80)
    
    # Test data
    features = [
        {
            "title": "User Authentication",
            "feature_text": "User Authentication",
            "description": "Allow users to login and register"
        },
        {
            "title": "Dashboard",
            "feature_text": "Dashboard",
            "description": "Display user's projects and stats"
        }
    ]
    
    stories = [
        {
            "feature_id": "User Authentication",
            "story_text": "As a user, I want to register with email and password",
            "user_story": "As a user, I want to register with email and password",
            "acceptance_criteria": ["Email validation", "Password strength check"],
            "implementation_notes": ["Use bcrypt for password hashing"]
        },
        {
            "feature_id": "Dashboard",
            "story_text": "As a user, I want to see my recent projects",
            "user_story": "As a user, I want to see my recent projects",
            "acceptance_criteria": ["Show last 10 projects", "Sort by date"],
            "implementation_notes": ["Cache results for performance"]
        }
    ]
    
    # Test each diagram type
    diagram_types = ["hld", "lld", "database"]
    
    for diagram_type in diagram_types:
        print(f"\n{'=' * 80}")
        print(f"Testing {diagram_type.upper()} diagram generation...")
        print(f"{'=' * 80}")
        
        try:
            agent3 = Agent3Service()
            print(f"OK Agent3Service created successfully")
            print(f"  Model: {agent3.model}")
            
            mermaid = await agent3.generate_mermaid(
                project_title="Test Project",
                features=features,
                stories=stories,
                diagram_type=diagram_type,
                original_prompt="Test prompt for diagnostic purposes"
            )
            
            print(f"\nOK {diagram_type.upper()} diagram generated successfully!")
            print(f"  Length: {len(mermaid)} chars")
            print(f"  Preview (first 200 chars):\n{mermaid[:200]}")
            print(f"  Has styling: {'Yes' if 'classDef' in mermaid or 'style ' in mermaid else 'No'}")
            
        except Exception as exc:
            print(f"\nX ERROR generating {diagram_type.upper()} diagram:")
            print(f"  Error type: {type(exc).__name__}")
            print(f"  Error message: {exc}")
            print(f"\nFull traceback:")
            traceback.print_exc()
            return False
    
    print(f"\n{'=' * 80}")
    print("OK All diagram types generated successfully!")
    print(f"{'=' * 80}")
    return True


if __name__ == "__main__":
    print("Testing Agent3 Visualization Service")
    print("=" * 80)
    
    # Test Claude client first
    try:
        print("\n1. Testing Claude client...")
        client = get_claude_client()
        print(f"   OK Claude client created successfully")
        print(f"   Type: {type(client)}")
    except Exception as exc:
        print(f"   X ERROR: Failed to create Claude client")
        print(f"   Error: {exc}")
        traceback.print_exc()
        sys.exit(1)
    
    # Test Agent3 service
    print("\n2. Testing Agent3Service...")
    success = asyncio.run(test_agent3())
    
    if success:
        print("\n" + "=" * 80)
        print("OK ALL TESTS PASSED!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("X TESTS FAILED!")
        print("=" * 80)
        sys.exit(1)

