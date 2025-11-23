# Feedback Chatbot - API Quick Reference

## 🚀 Endpoints at a Glance

All endpoints are prefixed with: `/api/feedback/chatbot/`

---

## 1️⃣ Send Message

**Endpoint:** `POST /api/feedback/chatbot/message`

**Purpose:** Chat with the AI assistant

**Request:**
```json
{
  "message": "How can I improve this feature?",
  "conversationId": "uuid (optional, for continuing conversation)",
  "projectId": "project-id (optional)",
  "itemId": "item-id (optional)",
  "itemType": "feature|story|visualization (optional)",
  "context": {
    "projectName": "My Project",
    "itemTitle": "Login Feature",
    "itemDescription": "User authentication"
  }
}
```

**Response:**
```json
{
  "conversationId": "conversation-uuid",
  "messageId": "message-uuid",
  "response": "AI response text",
  "timestamp": "2025-11-23T12:00:00Z",
  "metadata": {
    "input_tokens": 150,
    "output_tokens": 200
  }
}
```

**Example (Python):**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/feedback/chatbot/message",
    json={
        "message": "Help me write better feedback",
        "itemType": "feature",
        "context": {"itemTitle": "User Login"}
    }
)
print(response.json()['response'])
```

**Example (JavaScript):**
```javascript
const response = await fetch('/api/feedback/chatbot/message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "Help me write better feedback",
    itemType: "feature"
  })
});
const data = await response.json();
console.log(data.response);
```

---

## 2️⃣ Suggest Improvements

**Endpoint:** `POST /api/feedback/chatbot/suggest-improvements`

**Purpose:** Get AI suggestions to improve feedback

**Request:**
```json
{
  "feedback": "This feature needs work",
  "itemType": "feature|story|visualization",
  "itemContent": {
    "title": "Feature Title",
    "description": "Feature description"
  }
}
```

**Response:**
```json
{
  "suggestions": "AI suggestions text",
  "originalFeedback": "This feature needs work",
  "itemType": "feature",
  "messageId": "message-uuid"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/feedback/chatbot/suggest-improvements \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Make it better",
    "itemType": "feature"
  }'
```

---

## 3️⃣ Explain Regeneration

**Endpoint:** `POST /api/feedback/chatbot/explain-regeneration`

**Purpose:** Understand what changed after content regeneration

**Request:**
```json
{
  "itemType": "feature|story|visualization",
  "originalContent": {
    "title": "Original Title",
    "description": "Original description"
  },
  "regeneratedContent": {
    "title": "New Title",
    "description": "Updated description"
  },
  "feedback": "User feedback that triggered regeneration"
}
```

**Response:**
```json
{
  "explanation": "Detailed explanation of changes",
  "itemType": "feature"
}
```

**Example (Python):**
```python
response = requests.post(
    "http://localhost:8000/api/feedback/chatbot/explain-regeneration",
    json={
        "itemType": "feature",
        "originalContent": {"title": "Login"},
        "regeneratedContent": {"title": "Secure Login with 2FA"},
        "feedback": "Add two-factor authentication"
    }
)
print(response.json()['explanation'])
```

---

## 4️⃣ Get Conversation History

**Endpoint:** `GET /api/feedback/chatbot/conversation/{conversation_id}`

**Purpose:** Retrieve full conversation history

**Response:**
```json
{
  "conversationId": "conversation-uuid",
  "messages": [
    {
      "role": "user|assistant",
      "content": "Message text",
      "timestamp": "2025-11-23T12:00:00Z"
    }
  ],
  "createdAt": "2025-11-23T12:00:00Z",
  "updatedAt": "2025-11-23T12:05:00Z"
}
```

**Example (curl):**
```bash
curl http://localhost:8000/api/feedback/chatbot/conversation/conversation-uuid
```

**Example (JavaScript):**
```javascript
const history = await fetch(`/api/feedback/chatbot/conversation/${conversationId}`);
const data = await history.json();
console.log(`Found ${data.messages.length} messages`);
```

---

## 5️⃣ Delete Conversation

**Endpoint:** `DELETE /api/feedback/chatbot/conversation/{conversation_id}`

**Purpose:** Delete a conversation and its history

**Response:**
```json
{
  "message": "Conversation deleted successfully",
  "conversationId": "conversation-uuid"
}
```

**Example (Python):**
```python
response = requests.delete(
    f"http://localhost:8000/api/feedback/chatbot/conversation/{conversation_id}"
)
print(response.json()['message'])
```

---

## 🔑 Common Patterns

### Pattern 1: Simple Q&A

```python
# Ask one question, get one answer
response = requests.post(
    "/api/feedback/chatbot/message",
    json={"message": "How can I improve this?"}
)
```

### Pattern 2: Multi-turn Conversation

```python
# First message
resp1 = requests.post("/api/feedback/chatbot/message",
    json={"message": "Help me with feedback"})
conv_id = resp1.json()['conversationId']

# Continue conversation
resp2 = requests.post("/api/feedback/chatbot/message",
    json={"message": "What about security?", "conversationId": conv_id})
```

### Pattern 3: Context-aware Chat

```python
# Provide rich context for better responses
response = requests.post("/api/feedback/chatbot/message", json={
    "message": "What should I focus on?",
    "itemType": "feature",
    "itemId": "feature-123",
    "context": {
        "projectName": "E-commerce App",
        "itemTitle": "Shopping Cart",
        "itemDescription": "Add items and checkout"
    }
})
```

---

## 🎯 HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `400` | Bad request (invalid parameters) |
| `404` | Conversation not found |
| `500` | Server or AI service error |

---

## 🔧 Common Parameters

### `itemType`
Valid values: `"feature"`, `"story"`, `"visualization"`

### `context` (optional but recommended)
```json
{
  "projectName": "string",
  "itemTitle": "string",
  "itemDescription": "string",
  "industry": "string"
}
```

---

## 💻 Complete Integration Example

### React Component

```typescript
import { useState } from 'react';

export const ChatWidget = ({ itemId, itemType }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [convId, setConvId] = useState(null);
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim()) return;
    
    setLoading(true);
    try {
      const res = await fetch('/api/feedback/chatbot/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          conversationId: convId,
          itemId,
          itemType
        })
      });
      
      const data = await res.json();
      
      if (!convId) setConvId(data.conversationId);
      
      setMessages([
        ...messages,
        { role: 'user', content: input },
        { role: 'assistant', content: data.response }
      ]);
      
      setInput('');
    } catch (err) {
      console.error('Chat error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-widget">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      
      <div className="input-area">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && send()}
          placeholder="Ask for help with feedback..."
          disabled={loading}
        />
        <button onClick={send} disabled={loading}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
};
```

---

## 📱 Mobile/Native Example

### React Native

```typescript
const sendMessage = async (message: string) => {
  const response = await fetch('http://your-api.com/api/feedback/chatbot/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  
  const data = await response.json();
  return data.response;
};
```

---

## 🐛 Error Handling

```typescript
try {
  const response = await fetch('/api/feedback/chatbot/message', {
    method: 'POST',
    body: JSON.stringify({ message: userInput })
  });
  
  if (!response.ok) {
    const error = await response.json();
    console.error('API Error:', error.detail);
    // Show user-friendly error message
    return;
  }
  
  const data = await response.json();
  // Process successful response
  
} catch (error) {
  console.error('Network error:', error);
  // Handle connection issues
}
```

---

## 📊 Rate Limiting & Performance

- **Claude API:** Subject to Anthropic rate limits
- **Conversation storage:** Unlimited (MongoDB)
- **Recommended:** Add rate limiting middleware for production
- **Average response time:** 1-3 seconds (depends on Claude API)

---

## 🔒 Security Best Practices

1. **Validate input:** Sanitize user messages before sending
2. **Add authentication:** Protect endpoints with user auth
3. **Rate limiting:** Prevent abuse
4. **Monitor usage:** Track API costs
5. **Secure API keys:** Never expose in frontend code

---

## 🎨 Styling Tips

### Suggested Message Bubble Classes

```css
.message.user {
  background: #007bff;
  color: white;
  align-self: flex-end;
}

.message.assistant {
  background: #f1f3f4;
  color: #333;
  align-self: flex-start;
}
```

---

## 📖 More Resources

- **Full Documentation:** `FEEDBACK_CHATBOT_INTEGRATION.md`
- **Quick Start:** `CHATBOT_QUICK_START.md`
- **Integration Summary:** `INTEGRATION_SUMMARY.md`
- **Working Examples:** `example_chatbot_usage.py`
- **Test Suite:** `test_chatbot.py`

---

**Happy Coding! 🚀**

