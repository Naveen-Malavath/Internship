#!/usr/bin/env python3
"""
Quick test script to verify LLD diagram generation with proper styling.
This simulates the diagram generation process without requiring a full project setup.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent / "autoagents-backend"))

from app.services.agent3 import Agent3Service


async def test_lld_generation():
    """Test LLD diagram generation with sample features and stories."""
    
    print("=" * 80)
    print("LLD DIAGRAM GENERATION TEST")
    print("=" * 80)
    
    # Check if API key is configured
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY or CLAUDE_API_KEY not found in environment")
        print("Please set your API key in .env file:")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    # Sample features and stories
    sample_features = [
        {
            "id": "feat1",
            "title": "User Authentication",
            "feature_text": "User Authentication",
            "description": "Allow users to register, login, and manage their accounts"
        },
        {
            "id": "feat2",
            "title": "Task Management",
            "feature_text": "Task Management",
            "description": "Create, update, delete, and organize tasks"
        },
        {
            "id": "feat3",
            "title": "Team Collaboration",
            "feature_text": "Team Collaboration",
            "description": "Share tasks and collaborate with team members"
        }
    ]
    
    sample_stories = [
        {
            "feature_id": "feat1",
            "story_text": "As a user, I want to register with email and password",
            "user_story": "As a user, I want to register with email and password",
            "acceptance_criteria": ["Email validation", "Password strength check", "Confirmation email sent"]
        },
        {
            "feature_id": "feat1",
            "story_text": "As a user, I want to login securely",
            "user_story": "As a user, I want to login securely",
            "acceptance_criteria": ["JWT token generation", "Session management", "Password encryption"]
        },
        {
            "feature_id": "feat2",
            "story_text": "As a user, I want to create tasks with title and description",
            "user_story": "As a user, I want to create tasks with title and description",
            "acceptance_criteria": ["Form validation", "Save to database", "Real-time UI update"]
        },
        {
            "feature_id": "feat2",
            "story_text": "As a user, I want to mark tasks as complete",
            "user_story": "As a user, I want to mark tasks as complete",
            "acceptance_criteria": ["Toggle completion status", "Update database", "Visual indication"]
        },
        {
            "feature_id": "feat3",
            "story_text": "As a user, I want to invite team members",
            "user_story": "As a user, I want to invite team members",
            "acceptance_criteria": ["Email invitation", "Permission levels", "Notification system"]
        }
    ]
    
    # Initialize Agent3 service
    print("\n" + "-" * 80)
    print("Initializing Agent3 Service...")
    print("-" * 80)
    agent3 = Agent3Service()
    
    # Test LLD generation
    print("\n" + "-" * 80)
    print("Generating LLD Diagram...")
    print("-" * 80)
    print(f"Features: {len(sample_features)}")
    print(f"Stories: {len(sample_stories)}")
    
    try:
        lld_diagram = await agent3.generate_mermaid(
            project_title="Task Management App",
            features=sample_features,
            stories=sample_stories,
            diagram_type="lld",
            original_prompt="Build a collaborative task management application with user authentication and team features"
        )
        
        print("\n" + "=" * 80)
        print("✅ LLD DIAGRAM GENERATED SUCCESSFULLY")
        print("=" * 80)
        
        # Check for styling
        has_classdef = "classDef" in lld_diagram
        has_class_statements = "\nclass " in lld_diagram or "\n    class " in lld_diagram
        has_colors = "#" in lld_diagram and any(color in lld_diagram for color in ["#3b82f6", "#10b981", "#ef4444", "#f59e0b", "#8b5cf6"])
        
        print(f"\n📊 Diagram Statistics:")
        print(f"  Length: {len(lld_diagram)} characters")
        print(f"  Lines: {len(lld_diagram.split(chr(10)))} lines")
        print(f"  Has classDef: {'✅ Yes' if has_classdef else '❌ No'}")
        print(f"  Has class statements: {'✅ Yes' if has_class_statements else '❌ No'}")
        print(f"  Has colors: {'✅ Yes' if has_colors else '❌ No'}")
        
        # Display first 1000 characters
        print(f"\n📝 Diagram Preview (first 1000 chars):")
        print("-" * 80)
        print(lld_diagram[:1000])
        if len(lld_diagram) > 1000:
            print(f"... ({len(lld_diagram) - 1000} more characters)")
        print("-" * 80)
        
        # Save to file
        output_file = "test_lld_output.mmd"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(lld_diagram)
        print(f"\n💾 Full diagram saved to: {output_file}")
        
        # Verify styling
        print(f"\n🎨 Styling Verification:")
        if has_colors and has_classdef and has_class_statements:
            print("  ✅ LLD diagram has FULL COLOR STYLING!")
            print("  ✅ No styling was stripped")
            print("  ✅ TEST PASSED")
            return True
        else:
            print("  ⚠️ WARNING: Styling may be incomplete")
            if not has_colors:
                print("    - No color codes found")
            if not has_classdef:
                print("    - No classDef statements found")
            if not has_class_statements:
                print("    - No class assignments found")
            print("  ❌ TEST FAILED")
            return False
            
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR DURING LLD GENERATION")
        print("=" * 80)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        return False


async def test_all_diagram_types():
    """Test all three diagram types: HLD, LLD, DBD."""
    
    print("\n" + "=" * 80)
    print("TESTING ALL DIAGRAM TYPES")
    print("=" * 80)
    
    # Sample data
    sample_features = [
        {
            "id": "feat1",
            "title": "User Management",
            "feature_text": "User Management",
            "description": "User registration and authentication"
        }
    ]
    
    sample_stories = [
        {
            "feature_id": "feat1",
            "story_text": "As a user, I want to register",
            "user_story": "As a user, I want to register",
            "acceptance_criteria": ["Email validation", "Password encryption"]
        }
    ]
    
    agent3 = Agent3Service()
    results = {}
    
    for diagram_type in ["hld", "lld", "database"]:
        print(f"\n{'-' * 80}")
        print(f"Testing {diagram_type.upper()} diagram...")
        print(f"{'-' * 80}")
        
        try:
            diagram = await agent3.generate_mermaid(
                project_title="Test App",
                features=sample_features,
                stories=sample_stories,
                diagram_type=diagram_type,
                original_prompt="Test application"
            )
            
            has_styling = "classDef" in diagram or "class " in diagram
            has_colors = "#" in diagram
            
            print(f"✅ {diagram_type.upper()} generated: {len(diagram)} chars")
            print(f"   Styling: {'Yes' if has_styling else 'No'}")
            print(f"   Colors: {'Yes' if has_colors else 'No'}")
            
            results[diagram_type] = True
            
        except Exception as e:
            print(f"❌ {diagram_type.upper()} failed: {str(e)}")
            results[diagram_type] = False
    
    print(f"\n{'=' * 80}")
    print("RESULTS SUMMARY")
    print(f"{'=' * 80}")
    for dtype, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {dtype.upper()}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    return all_passed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test LLD diagram generation")
    parser.add_argument("--all", action="store_true", help="Test all diagram types (HLD, LLD, DBD)")
    parser.add_argument("--lld-only", action="store_true", help="Test only LLD diagram (default)")
    args = parser.parse_args()
    
    # Load .env file if it exists
    env_file = Path(__file__).parent / "autoagents-backend" / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    
    if args.all:
        success = asyncio.run(test_all_diagram_types())
    else:
        success = asyncio.run(test_lld_generation())
    
    sys.exit(0 if success else 1)

