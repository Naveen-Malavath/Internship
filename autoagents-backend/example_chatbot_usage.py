"""
Example usage of the Feedback Chatbot API.

This demonstrates how to interact with the chatbot endpoints from a Python client.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Update if your backend runs on a different port


def example_1_simple_conversation():
    """Example 1: Simple chatbot conversation."""
    print("\n" + "=" * 60)
    print("Example 1: Simple Chatbot Conversation")
    print("=" * 60)
    
    # Send first message
    print("\n📤 User: How can I write better feedback for my authentication feature?")
    
    response = requests.post(
        f"{BASE_URL}/api/feedback/chatbot/message",
        json={
            "message": "How can I write better feedback for my authentication feature?",
            "itemType": "feature",
            "context": {
                "itemTitle": "User Authentication",
                "projectName": "My Application"
            }
        }
    )
    
    data = response.json()
    conversation_id = data["conversationId"]
    
    print(f"🤖 AI: {data['response']}\n")
    print(f"📊 Conversation ID: {conversation_id}")
    
    # Continue conversation
    print("\n📤 User: What about security considerations?")
    
    response = requests.post(
        f"{BASE_URL}/api/feedback/chatbot/message",
        json={
            "message": "What about security considerations?",
            "conversationId": conversation_id
        }
    )
    
    print(f"🤖 AI: {response.json()['response']}\n")
    
    return conversation_id


def example_2_feedback_improvements():
    """Example 2: Get suggestions to improve feedback."""
    print("\n" + "=" * 60)
    print("Example 2: Improve Your Feedback")
    print("=" * 60)
    
    original_feedback = "The login page needs to be better"
    
    print(f"\n📝 Original Feedback: '{original_feedback}'")
    print("\n🔍 Asking AI for improvement suggestions...")
    
    response = requests.post(
        f"{BASE_URL}/api/feedback/chatbot/suggest-improvements",
        json={
            "feedback": original_feedback,
            "itemType": "feature",
            "itemContent": {
                "title": "Login Page",
                "description": "User authentication interface"
            }
        }
    )
    
    suggestions = response.json()
    print(f"\n💡 AI Suggestions:\n{suggestions['suggestions']}\n")


def example_3_explain_regeneration():
    """Example 3: Understand what changed in regenerated content."""
    print("\n" + "=" * 60)
    print("Example 3: Explain Regeneration Changes")
    print("=" * 60)
    
    print("\n📋 Scenario: You provided feedback and the feature was regenerated")
    
    response = requests.post(
        f"{BASE_URL}/api/feedback/chatbot/explain-regeneration",
        json={
            "itemType": "feature",
            "originalContent": {
                "title": "Basic Login",
                "description": "Simple username and password login",
                "acceptanceCriteria": [
                    "User can enter credentials",
                    "System validates credentials"
                ]
            },
            "regeneratedContent": {
                "title": "Secure Multi-Factor Authentication",
                "description": "Advanced authentication with MFA and OAuth2 support",
                "acceptanceCriteria": [
                    "User can login with username/password",
                    "System supports 2FA via SMS or authenticator app",
                    "OAuth2 integration with Google and GitHub",
                    "Rate limiting and brute force protection"
                ]
            },
            "feedback": "Add two-factor authentication and OAuth support for better security"
        }
    )
    
    explanation = response.json()
    print(f"\n🔍 AI Explanation:\n{explanation['explanation']}\n")


def example_4_conversation_history():
    """Example 4: Retrieve and manage conversation history."""
    print("\n" + "=" * 60)
    print("Example 4: Conversation History Management")
    print("=" * 60)
    
    # Create a conversation
    print("\n📤 Creating a new conversation...")
    
    response = requests.post(
        f"{BASE_URL}/api/feedback/chatbot/message",
        json={
            "message": "Help me understand user stories better",
            "itemType": "story"
        }
    )
    
    conversation_id = response.json()["conversationId"]
    print(f"✓ Conversation created: {conversation_id}")
    
    # Add another message
    requests.post(
        f"{BASE_URL}/api/feedback/chatbot/message",
        json={
            "message": "What's the difference between a user story and a feature?",
            "conversationId": conversation_id
        }
    )
    
    # Get history
    print(f"\n📜 Retrieving conversation history...")
    
    response = requests.get(
        f"{BASE_URL}/api/feedback/chatbot/conversation/{conversation_id}"
    )
    
    history = response.json()
    print(f"\n✓ Found {len(history['messages'])} messages:")
    
    for i, msg in enumerate(history['messages'], 1):
        role = "👤 User" if msg['role'] == 'user' else "🤖 AI"
        print(f"\n{i}. {role}: {msg['content'][:100]}...")
    
    # Delete conversation
    print(f"\n🗑️  Deleting conversation...")
    
    response = requests.delete(
        f"{BASE_URL}/api/feedback/chatbot/conversation/{conversation_id}"
    )
    
    print(f"✓ {response.json()['message']}\n")


def example_5_contextual_chat():
    """Example 5: Using context for better responses."""
    print("\n" + "=" * 60)
    print("Example 5: Contextual Conversations")
    print("=" * 60)
    
    # Rich context for better responses
    context = {
        "itemType": "feature",
        "itemId": "feature-123",
        "projectId": "project-456",
        "context": {
            "projectName": "E-commerce Platform",
            "itemTitle": "Shopping Cart",
            "itemDescription": "Allow users to add items and checkout",
            "industry": "Retail"
        }
    }
    
    print(f"\n📋 Context: {json.dumps(context['context'], indent=2)}")
    print("\n📤 User: What feedback should I provide for this feature?")
    
    response = requests.post(
        f"{BASE_URL}/api/feedback/chatbot/message",
        json={
            "message": "What feedback should I provide for this shopping cart feature?",
            **context
        }
    )
    
    print(f"\n🤖 AI: {response.json()['response']}\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print(" 🤖 Feedback Chatbot API - Usage Examples")
    print("=" * 70)
    print("\n⚠️  Make sure the backend server is running on", BASE_URL)
    print("\nPress Enter to continue...")
    input()
    
    try:
        # Run examples
        conversation_id = example_1_simple_conversation()
        example_2_feedback_improvements()
        example_3_explain_regeneration()
        example_4_conversation_history()
        example_5_contextual_chat()
        
        print("\n" + "=" * 70)
        print("✓ All examples completed successfully!")
        print("=" * 70)
        print("\n📚 For more information, see FEEDBACK_CHATBOT_INTEGRATION.md")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the backend server")
        print(f"Please make sure the server is running on {BASE_URL}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

