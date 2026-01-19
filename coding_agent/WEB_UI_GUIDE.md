# 🤖 AI Coding Agent - Web UI Guide

## 🚀 Quick Start

### Option 1: Using Batch Script (Windows - Easiest)
```cmd
start.bat
```
This will:
1. Start the backend API server
2. Start the React frontend
3. Open your browser automatically

### Option 2: Manual Start
```cmd
# Terminal 1 - Backend
env\Scripts\python.exe -m uvicorn src.web.server:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Then open: http://localhost:5173

---

## 📊 What You'll See

The Web UI shows **EVERY interaction** in the agent's "conversation":

### 👤 USER → 🤖 AGENT
Your prompt is sent to the agent

### 🤖 AGENT → 🧠 LLM (Claude)
Agent asks Claude what to do, including:
- Full system prompt
- Available tools
- Conversation history

### 🧠 LLM → 🤖 AGENT  
Claude responds with:
- Reasoning/thinking
- Tool calls to execute

### 🤖 AGENT → 🔧 TOOLS
Agent executes tools in parallel:
- `file_operations` - Create/read/update files
- `terminal` - Run commands
- `generate_code` - Use templates
- `task_complete` - Signal done

### 🔧 TOOL → 🤖 AGENT
Tools return results:
- Success/failure status
- Output data
- Error messages (if any)

### 🔄 Loop until 🎯 TASK COMPLETE

---

## 🎨 UI Features

### Color Coding
- 🔵 **Blue** - User messages
- 🟣 **Purple** - Agent orchestration
- 🟠 **Orange** - LLM (Claude) responses
- 🟢 **Teal** - Tool executions
- 🟢 **Green** - Task completed
- 🔴 **Red** - Errors
- 🟡 **Yellow** - Self-healing attempts

### Event Types
- `user_message` - Your prompt
- `iteration_start` - New iteration begins
- `llm_request` - Sending to Claude
- `llm_response` - Claude's reply
- `parallel_batch_start` - Multiple tools executing
- `tool_call` - Individual tool execution
- `tool_result` - Tool finished
- `error_detected` - Error found
- `self_healing_success` - Error fixed
- `task_complete` - Job done!
- `session_complete` - All finished

---

## 💡 Example Prompts

### Simple (1-2 iterations)
```
Create a Python file called hello.py that prints Hello World
```

### Medium (5-10 iterations)
```
Create a todo app with:
- React frontend with useState
- Add/remove/toggle todos
- LocalStorage persistence
```

### Complex (15-30 iterations)
```
Build a FastAPI microservice with:
- User authentication (JWT)
- CRUD for products
- PostgreSQL database
- Docker setup
- API documentation
```

### Full-Stack (30-50 iterations)
```
Create a blog platform with:
- Next.js frontend
- Express backend
- MongoDB database
- User authentication
- Post creation/editing
- Comments system
- Responsive design
```

---

## 🔍 Reading the Conversation

### Iteration Flow
Each iteration shows:
1. **Iteration X/50** - Current progress
2. **LLM Request** - What agent asked Claude
3. **LLM Response** - Claude's plan
4. **Parallel Batch** - Tools being run (2-8 at once!)
5. **Tool Results** - What happened
6. **Next Iteration** - Agent continues or completes

### Parallel Execution
Watch for:
```
parallel_batch_start
  Total Tools: 5
  Batches: 2
  Batch Sizes: 3, 2
```
This means:
- 5 tools total
- Split into 2 batches
- Batch 1: 3 tools in parallel
- Batch 2: 2 tools in parallel

### Task Completion
When you see:
```
task_complete
  status: success
  files_created: [...]
  commands_run: [...]
```
The agent is DONE! ✅

---

## 🐛 Troubleshooting

### "Failed to fetch" Error
1. Check backend is running: http://localhost:8000
2. Check frontend is running: http://localhost:5173
3. Restart both servers

### Backend Won't Start
```cmd
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <process_id> /F

# Restart
env\Scripts\python.exe -m uvicorn src.web.server:app --reload --port 8000
```

### Frontend Won't Start
```cmd
cd frontend
npm install  # Reinstall dependencies
npm run dev
```

### WebSocket Not Connecting
- Make sure backend started BEFORE frontend
- Check browser console for errors (F12)
- Try refreshing the page

---

## 🎯 What Makes This Special

### Full Transparency
Unlike other AI coding tools, you see:
- Exactly what the agent is thinking
- How it breaks down tasks
- Which tools it chooses
- Why it makes decisions
- When it runs things in parallel
- How it handles errors

### Real-Time Streaming
- Events appear as they happen
- No waiting for completion
- See progress live
- Cancel if needed (Ctrl+C in terminals)

### Learning Tool
Perfect for understanding:
- How AI agents work
- Prompt engineering
- Tool selection strategies
- Parallel execution optimization
- Error recovery patterns

---

## 📁 Project Structure

```
coding_agent/
├── src/
│   ├── web/
│   │   ├── server.py          # FastAPI backend
│   │   └── __init__.py
│   ├── core/
│   │   └── orchestrator.py    # Event emission
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # React UI
│   │   └── App.css           # Styles
│   └── package.json
├── start.bat                  # Windows startup
└── start_web_ui.py           # Python startup
```

---

## 🎉 Enjoy!

You're now watching an AI agent "think" in real-time!

Try different prompts and watch how it:
- Plans the solution
- Breaks it into steps
- Executes in parallel
- Handles errors
- Knows when it's done

**It's like seeing inside the mind of an AI!** 🧠✨
