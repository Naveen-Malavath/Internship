"""Test script for the Feedback Chatbot integration."""

import asyncio
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_chatbot_service():
    """Test the FeedbackChatbotService directly."""
    from app.services.feedback_chatbot_service import FeedbackChatbotService
    
    print("=" * 60)
    print("Testing Feedback Chatbot Service")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\n1. Initializing chatbot service...")
        chatbot = FeedbackChatbotService()
        print("✓ Chatbot service initialized successfully")
        
        # Test 1: Basic message
        print("\n2. Testing basic message...")
        response = await chatbot.generate_response(
            user_message="How can I improve feedback for a login feature?",
            chat_history=None,
            context={"itemType": "feature"}
        )
        print(f"✓ Message ID: {response['message_id']}")
        print(f"✓ Response: {response['response'][:200]}...")
        if response.get('metadata'):
            print(f"✓ Tokens used: input={response['metadata'].get('input_tokens')}, output={response['metadata'].get('output_tokens')}")
        
        # Test 2: Conversation with history
        print("\n3. Testing conversation with history...")
        chat_history = [
            {"role": "user", "content": "I'm working on a login feature"},
            {"role": "assistant", "content": "Great! What aspects of the login feature would you like to improve?"}
        ]
        response2 = await chatbot.generate_response(
            user_message="I want to add OAuth support",
            chat_history=chat_history,
            context={"itemType": "feature", "itemTitle": "User Login"}
        )
        print(f"✓ Follow-up response: {response2['response'][:200]}...")
        
        # Test 3: Feedback improvement suggestions
        print("\n4. Testing feedback improvement suggestions...")
        suggestions = await chatbot.suggest_feedback_improvements(
            original_feedback="This login feature needs to be better",
            item_type="feature",
            item_content={
                "title": "User Login",
                "description": "Basic authentication system"
            }
        )
        print(f"✓ Suggestions: {suggestions['suggestions'][:200]}...")
        
        # Test 4: Regeneration explanation
        print("\n5. Testing regeneration explanation...")
        explanation = await chatbot.explain_regeneration(
            item_type="feature",
            original_content={
                "title": "Basic Login",
                "description": "Simple username/password login"
            },
            regenerated_content={
                "title": "Secure Authentication",
                "description": "Multi-factor authentication with OAuth2 support"
            },
            feedback="Add OAuth support and two-factor authentication"
        )
        print(f"✓ Explanation: {explanation[:200]}...")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        
    except Exception as exc:
        print(f"\n✗ Error during testing: {exc}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_chatbot_api():
    """Test the chatbot API endpoints (requires running server)."""
    import httpx
    
    print("\n" + "=" * 60)
    print("Testing Feedback Chatbot API Endpoints")
    print("(Make sure the backend server is running)")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test 1: Send message
            print("\n1. Testing POST /api/feedback/chatbot/message...")
            response = await client.post(
                f"{base_url}/api/feedback/chatbot/message",
                json={
                    "message": "Help me write better feedback for my login feature",
                    "itemType": "feature",
                    "context": {
                        "itemTitle": "User Login",
                        "projectName": "My Application"
                    }
                }
            )
            
            if response.status_code != 200:
                print(f"✗ API returned status {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            conversation_id = data["conversationId"]
            print(f"✓ Conversation ID: {conversation_id}")
            print(f"✓ Response: {data['response'][:150]}...")
            
            # Test 2: Continue conversation
            print("\n2. Testing follow-up message...")
            response2 = await client.post(
                f"{base_url}/api/feedback/chatbot/message",
                json={
                    "message": "What about security best practices?",
                    "conversationId": conversation_id
                }
            )
            
            if response2.status_code != 200:
                print(f"✗ API returned status {response2.status_code}")
                return False
            
            data2 = response2.json()
            print(f"✓ Follow-up response: {data2['response'][:150]}...")
            
            # Test 3: Get conversation history
            print("\n3. Testing GET /api/feedback/chatbot/conversation/{id}...")
            response3 = await client.get(
                f"{base_url}/api/feedback/chatbot/conversation/{conversation_id}"
            )
            
            if response3.status_code != 200:
                print(f"✗ API returned status {response3.status_code}")
                return False
            
            history = response3.json()
            print(f"✓ Retrieved {len(history['messages'])} messages")
            
            # Test 4: Suggest improvements
            print("\n4. Testing POST /api/feedback/chatbot/suggest-improvements...")
            response4 = await client.post(
                f"{base_url}/api/feedback/chatbot/suggest-improvements",
                json={
                    "feedback": "Make it better",
                    "itemType": "feature"
                }
            )
            
            if response4.status_code != 200:
                print(f"✗ API returned status {response4.status_code}")
                return False
            
            suggestions = response4.json()
            print(f"✓ Suggestions: {suggestions['suggestions'][:150]}...")
            
            # Test 5: Delete conversation
            print("\n5. Testing DELETE /api/feedback/chatbot/conversation/{id}...")
            response5 = await client.delete(
                f"{base_url}/api/feedback/chatbot/conversation/{conversation_id}"
            )
            
            if response5.status_code != 200:
                print(f"✗ API returned status {response5.status_code}")
                return False
            
            print(f"✓ Conversation deleted successfully")
            
            print("\n" + "=" * 60)
            print("✓ All API tests passed successfully!")
            print("=" * 60)
            
    except httpx.ConnectError:
        print("\n✗ Could not connect to backend server")
        print("Make sure the server is running on http://localhost:8000")
        return False
    except Exception as exc:
        print(f"\n✗ Error during API testing: {exc}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Feedback Chatbot Integration Test Suite")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n✗ ANTHROPIC_API_KEY not found in environment")
        print("Please set your API key in the .env file")
        return
    
    # Test 1: Service tests
    service_success = await test_chatbot_service()
    
    # Test 2: API tests (optional - requires running server)
    print("\n\nWould you like to test the API endpoints?")
    print("This requires the backend server to be running.")
    user_input = input("Test API endpoints? (y/n): ").strip().lower()
    
    if user_input == 'y':
        api_success = await test_chatbot_api()
    else:
        print("\nSkipping API tests.")
        api_success = None
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Service Tests: {'✓ PASSED' if service_success else '✗ FAILED'}")
    if api_success is not None:
        print(f"API Tests: {'✓ PASSED' if api_success else '✗ FAILED'}")
    else:
        print("API Tests: SKIPPED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

