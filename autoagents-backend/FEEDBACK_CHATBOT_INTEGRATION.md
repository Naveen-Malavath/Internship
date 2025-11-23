# Feedback Chatbot Integration

## Overview

The Feedback Chatbot is an AI-powered conversational assistant integrated into the AutoAgents backend. It helps users:

- Provide better feedback on features, stories, and visualizations
- Get suggestions for improving their feedback
- Understand what changed in regenerated content
- Have natural conversations about their projects

## Architecture

The chatbot integration consists of three main components:

1. **FeedbackChatbotService** (`app/services/feedback_chatbot_service.py`)
   - Handles AI interactions using Claude API
   - Generates contextual responses
   - Provides feedback improvement suggestions
   - Explains regeneration changes

2. **Chatbot Schemas** (`app/schemas/feedback.py`)
   - Request/response models for all chatbot endpoints
   - Message and conversation models

3. **Chatbot Endpoints** (`app/routers/feedback.py`)
   - REST API endpoints for chatbot interactions
   - Conversation management (create, read, delete)

## API Endpoints

### 1. Send Message to Chatbot

**POST** `/api/feedback/chatbot/message`

Send a message to the chatbot and get an AI-powered response.

**Request Body:**
```json
{
  "message": "How can I improve the user authentication feature?",
  "conversationId": "optional-conversation-id",
  "projectId": "project-123",
  "itemId": "feature-456",
  "itemType": "feature",
  "context": {
    "itemTitle": "User Authentication",
    "itemDescription": "Implement secure user login",
    "projectName": "My Project"
  }
}
```

**Response:**
```json
{
  "conversationId": "conversation-uuid",
  "messageId": "message-uuid",
  "response": "To improve the user authentication feature, consider...",
  "timestamp": "2025-11-23T12:00:00Z",
  "metadata": {
    "input_tokens": 150,
    "output_tokens": 200
  }
}
```

### 2. Get Feedback Improvement Suggestions

**POST** `/api/feedback/chatbot/suggest-improvements`

Get AI suggestions to make your feedback more actionable.

**Request Body:**
```json
{
  "feedback": "This feature needs improvement",
  "itemType": "feature",
  "itemContent": {
    "title": "User Authentication",
    "description": "Login system for users"
  }
}
```

**Response:**
```json
{
  "suggestions": "Your feedback could be more specific. Consider:\n1. What specific aspects need improvement?\n2. What are the current issues?...",
  "originalFeedback": "This feature needs improvement",
  "itemType": "feature",
  "messageId": "message-uuid"
}
```

### 3. Explain Regeneration Changes

**POST** `/api/feedback/chatbot/explain-regeneration`

Get an explanation of what changed when content was regenerated based on feedback.

**Request Body:**
```json
{
  "itemType": "feature",
  "originalContent": {
    "title": "User Login",
    "description": "Basic login functionality"
  },
  "regeneratedContent": {
    "title": "Secure User Authentication",
    "description": "Multi-factor authentication with OAuth support"
  },
  "feedback": "Add more security features like 2FA"
}
```

**Response:**
```json
{
  "explanation": "Based on your feedback requesting more security features, the regenerated content now includes:\n1. Multi-factor authentication...",
  "itemType": "feature"
}
```

### 4. Get Conversation History

**GET** `/api/feedback/chatbot/conversation/{conversation_id}`

Retrieve the full history of a chatbot conversation.

**Response:**
```json
{
  "conversationId": "conversation-uuid",
  "messages": [
    {
      "role": "user",
      "content": "Help me improve this feature",
      "timestamp": "2025-11-23T12:00:00Z"
    },
    {
      "role": "assistant",
      "content": "I'd be happy to help. What specific aspects...",
      "timestamp": "2025-11-23T12:00:05Z"
    }
  ],
  "createdAt": "2025-11-23T12:00:00Z",
  "updatedAt": "2025-11-23T12:05:00Z"
}
```

### 5. Delete Conversation

**DELETE** `/api/feedback/chatbot/conversation/{conversation_id}`

Delete a chatbot conversation and its history.

**Response:**
```json
{
  "message": "Conversation deleted successfully",
  "conversationId": "conversation-uuid"
}
```

## Usage Examples

### Python Example

```python
import requests

# Base URL of your backend
BASE_URL = "http://localhost:8000"

# 1. Start a conversation
response = requests.post(
    f"{BASE_URL}/api/feedback/chatbot/message",
    json={
        "message": "I need help writing feedback for my login feature",
        "itemType": "feature",
        "context": {
            "itemTitle": "User Login",
            "projectName": "My App"
        }
    }
)
conversation = response.json()
conversation_id = conversation["conversationId"]
print(f"AI: {conversation['response']}")

# 2. Continue the conversation
response = requests.post(
    f"{BASE_URL}/api/feedback/chatbot/message",
    json={
        "message": "I want to add OAuth support",
        "conversationId": conversation_id
    }
)
print(f"AI: {response.json()['response']}")

# 3. Get improvement suggestions
response = requests.post(
    f"{BASE_URL}/api/feedback/chatbot/suggest-improvements",
    json={
        "feedback": "Add OAuth",
        "itemType": "feature"
    }
)
print(f"Suggestions: {response.json()['suggestions']}")
```

### JavaScript/TypeScript Example

```typescript
// 1. Send a message to the chatbot
const sendMessage = async (message: string, conversationId?: string) => {
  const response = await fetch('/api/feedback/chatbot/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      conversationId,
      itemType: 'feature',
      context: {
        itemTitle: 'User Authentication',
        projectName: 'My Project'
      }
    })
  });
  return await response.json();
};

// 2. Get feedback suggestions
const getSuggestions = async (feedback: string) => {
  const response = await fetch('/api/feedback/chatbot/suggest-improvements', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      feedback,
      itemType: 'feature'
    })
  });
  return await response.json();
};

// Usage
const conversation = await sendMessage("Help me improve this feature");
console.log('AI:', conversation.response);

const suggestions = await getSuggestions("This needs improvement");
console.log('Suggestions:', suggestions.suggestions);
```

## Features

### Contextual Conversations
- Maintains conversation history across multiple messages
- Uses context from projects, features, stories, and visualizations
- Provides relevant suggestions based on item type

### Feedback Improvement
- Analyzes user feedback and suggests improvements
- Asks clarifying questions
- Helps make feedback more actionable

### Regeneration Explanations
- Explains what changed between original and regenerated content
- Shows how feedback was incorporated
- Identifies potential concerns

### Persistent Storage
- Conversations are stored in MongoDB
- Retrieve conversation history at any time
- Delete conversations when no longer needed

## Database Collections

### `chatbot_conversations`
Stores chatbot conversation history.

**Schema:**
```javascript
{
  _id: "conversation-uuid",
  messages: [
    {
      role: "user" | "assistant",
      content: "message text",
      timestamp: "ISO timestamp"
    }
  ],
  project_id: "optional-project-id",
  item_id: "optional-item-id",
  item_type: "feature | story | visualization",
  created_at: "ISO timestamp",
  updated_at: "ISO timestamp"
}
```

## Configuration

The chatbot service requires the following environment variables:

- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude
- `CLAUDE_MODEL` (optional): Claude model to use (default: `claude-sonnet-4-20250514`)

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful operation
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Conversation/resource not found
- `500 Internal Server Error`: Server or AI service error

Example error response:
```json
{
  "detail": "Failed to process chatbot message: API error"
}
```

## Best Practices

1. **Use Context**: Provide as much context as possible (project info, item details) for better responses
2. **Maintain Conversations**: Reuse `conversationId` for follow-up questions to maintain context
3. **Clear Conversations**: Delete old conversations to keep the database clean
4. **Handle Errors**: Always handle potential API errors gracefully
5. **Token Usage**: Monitor `metadata.input_tokens` and `metadata.output_tokens` to track API usage

## Integration with Frontend

### Example React Integration

```typescript
// hooks/useChatbot.ts
import { useState } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export const useChatbot = () => {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (message: string, context?: any) => {
    setLoading(true);
    try {
      const response = await fetch('/api/feedback/chatbot/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          conversationId,
          ...context
        })
      });
      
      const data = await response.json();
      
      if (!conversationId) {
        setConversationId(data.conversationId);
      }
      
      setMessages(prev => [
        ...prev,
        { role: 'user', content: message, timestamp: new Date().toISOString() },
        { role: 'assistant', content: data.response, timestamp: data.timestamp }
      ]);
      
      return data;
    } catch (error) {
      console.error('Chatbot error:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const clearConversation = () => {
    setConversationId(null);
    setMessages([]);
  };

  return { sendMessage, messages, loading, clearConversation };
};
```

## Troubleshooting

### Chatbot not responding
- Check that `ANTHROPIC_API_KEY` is set correctly
- Verify Claude API quota and limits
- Check backend logs for error details

### Conversations not persisting
- Ensure MongoDB is running and connected
- Verify database permissions
- Check that `chatbot_conversations` collection exists

### Context not working
- Ensure you're passing `conversationId` for follow-up messages
- Verify that context data is properly formatted
- Check that conversation exists in database

## Future Enhancements

Potential improvements for the chatbot:

- [ ] Voice input/output support
- [ ] Multi-language support
- [ ] Suggested prompts/quick replies
- [ ] Feedback templates
- [ ] Integration with other agents (Agent1, Agent2, Agent3)
- [ ] Conversation summaries
- [ ] Export conversation history
- [ ] Chatbot analytics and insights

