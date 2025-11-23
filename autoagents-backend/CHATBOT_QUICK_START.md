# Feedback Chatbot - Quick Start Guide

## What Was Added

Your AutoAgents backend now has a fully integrated AI-powered feedback chatbot! 🎉

### New Components

1. **`app/services/feedback_chatbot_service.py`** - AI chatbot service using Claude
2. **Updated `app/schemas/feedback.py`** - New chatbot request/response models
3. **Updated `app/routers/feedback.py`** - 5 new chatbot API endpoints
4. **`FEEDBACK_CHATBOT_INTEGRATION.md`** - Complete documentation
5. **`test_chatbot.py`** - Automated test suite
6. **`example_chatbot_usage.py`** - Working examples

## Setup (2 Minutes)

### 1. Your API key should already be in `.env` file

Your `.env` file should already have:
```env
ANTHROPIC_API_KEY=your-api-key-here
CLAUDE_MODEL=claude-sonnet-4-20250514  # Optional, has default
```

If not, add your Anthropic API key to the `.env` file in the `autoagents-backend` directory.

### 2. No new dependencies needed!

All required packages (anthropic, etc.) should already be installed since you're using the other agents.

### 3. Start your backend server (if not running)

```powershell
cd autoagents-backend
.\start_backend.ps1
```

Or manually:
```powershell
python -m uvicorn app.main:app --reload --port 8000
```

## Test It Out (1 Minute)

### Option 1: Quick API Test

Open a new terminal and run:

```powershell
cd autoagents-backend
python example_chatbot_usage.py
```

This will demonstrate all chatbot features with interactive examples.

### Option 2: Manual Test with curl

```powershell
# Send a message to the chatbot
curl -X POST http://localhost:8000/api/feedback/chatbot/message `
  -H "Content-Type: application/json" `
  -d '{
    "message": "How can I improve feedback for my login feature?",
    "itemType": "feature",
    "context": {
      "itemTitle": "User Login",
      "projectName": "My App"
    }
  }'
```

### Option 3: Python Quick Test

```python
import requests

response = requests.post(
    "http://localhost:8000/api/feedback/chatbot/message",
    json={
        "message": "Help me write better feedback",
        "itemType": "feature"
    }
)

print(response.json()['response'])
```

## Available Endpoints

All endpoints are under `/api/feedback/chatbot/`:

1. **POST** `/message` - Chat with the AI assistant
2. **POST** `/suggest-improvements` - Get feedback improvement suggestions
3. **POST** `/explain-regeneration` - Understand what changed after regeneration
4. **GET** `/conversation/{id}` - Get conversation history
5. **DELETE** `/conversation/{id}` - Delete a conversation

## Use Cases

### 1. **Interactive Feedback Assistant**
Users can chat with AI to refine their feedback before submitting it.

```javascript
// In your frontend
const response = await fetch('/api/feedback/chatbot/message', {
  method: 'POST',
  body: JSON.stringify({
    message: "How should I provide feedback on this feature?",
    itemId: featureId,
    itemType: 'feature',
    context: { itemTitle, projectName }
  })
});
```

### 2. **Feedback Improvement**
Automatically suggest better wording for user feedback.

```javascript
const suggestions = await fetch('/api/feedback/chatbot/suggest-improvements', {
  method: 'POST',
  body: JSON.stringify({
    feedback: userFeedback,
    itemType: 'story',
    itemContent: currentStory
  })
});
```

### 3. **Change Explanations**
Help users understand what changed when content is regenerated.

```javascript
const explanation = await fetch('/api/feedback/chatbot/explain-regeneration', {
  method: 'POST',
  body: JSON.stringify({
    itemType: 'feature',
    originalContent: originalFeature,
    regeneratedContent: newFeature,
    feedback: userProvidedFeedback
  })
});
```

## Frontend Integration Ideas

### React Chat Component

```typescript
import { useState } from 'react';

export const FeedbackChatbot = ({ itemId, itemType }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState(null);

  const sendMessage = async () => {
    const response = await fetch('/api/feedback/chatbot/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: input,
        conversationId,
        itemId,
        itemType
      })
    });
    
    const data = await response.json();
    
    if (!conversationId) setConversationId(data.conversationId);
    
    setMessages([
      ...messages,
      { role: 'user', content: input },
      { role: 'assistant', content: data.response }
    ]);
    
    setInput('');
  };

  return (
    <div className="chatbot">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role}>
            {msg.content}
          </div>
        ))}
      </div>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
};
```

## Database

The chatbot uses a new MongoDB collection:

**Collection:** `chatbot_conversations`

Stores conversation history, automatically created when first used.

## Monitoring

Check chatbot usage in your logs:

```powershell
# Watch backend logs for chatbot activity
Get-Content -Path "path/to/logs" -Wait | Select-String "FeedbackChatbot"
```

## Troubleshooting

### ❌ "ANTHROPIC_API_KEY not found"
**Solution:** Add your API key to the `.env` file in `autoagents-backend/`

### ❌ "Connection refused"
**Solution:** Make sure your backend server is running on port 8000

### ❌ "500 Internal Server Error"
**Solution:** Check backend logs for details. Common issues:
- Invalid API key
- API rate limits exceeded
- MongoDB connection issues

## Next Steps

1. **Integrate with your frontend** - Add chatbot UI components
2. **Customize prompts** - Edit `feedback_chatbot_service.py` to customize AI behavior
3. **Add analytics** - Track which features users need help with
4. **Extend functionality** - Add suggested questions, templates, etc.

## Documentation

- **Full Documentation:** `FEEDBACK_CHATBOT_INTEGRATION.md`
- **Code Examples:** `example_chatbot_usage.py`
- **Test Suite:** `test_chatbot.py`

## Support

For questions or issues:
1. Check `FEEDBACK_CHATBOT_INTEGRATION.md` for detailed docs
2. Review `example_chatbot_usage.py` for working examples
3. Run `test_chatbot.py` to verify your setup

---

**Enjoy your new AI-powered feedback chatbot! 🚀**

