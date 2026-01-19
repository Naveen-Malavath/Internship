"""Main Orchestrator - The brain of the multi-agent code generation system"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from .llm_provider import LLMProvider, LLMResponse
from .tools.base import ToolRegistry
from .tools.file_ops import FileOperationsTool
from .tools.terminal import TerminalTool
from .tools.task_complete import TaskCompleteTool
from .healing.error_detector import ErrorDetector
from .healing.classifier import ErrorClassifier
from .healing.fixer import ErrorFixer

logger = logging.getLogger(__name__)


class CodingAgent:
    """
    Main AI Coding Agent orchestrator
    Coordinates LLM, tools, and execution flow with self-healing
    """

    def __init__(
        self,
        workspace_path: Optional[Path] = None,
        model: Optional[str] = None,
        event_callback: Optional[Callable] = None,
    ):
        """
        Initialize the coding agent
        
        Args:
            workspace_path: Working directory for the agent
            model: Model name to use
            event_callback: Async callback for streaming events
        """
        self.workspace_path = workspace_path or Path.cwd()
        self.event_callback = event_callback

        # Initialize LLM
        self.llm = LLMProvider(model=model)
        logger.info(f"[AGENT] Initialized with workspace: {self.workspace_path}")

        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        self._register_tools()

        # Initialize self-healing components
        self.error_detector = ErrorDetector()
        self.error_fixer = ErrorFixer()

        # Conversation history
        self.messages: List[Dict[str, str]] = []
        self.system_prompt = self._create_system_prompt()

    def _register_tools(self):
        """Register default tools"""
        self.tool_registry.register(FileOperationsTool(workspace_path=self.workspace_path))
        self.tool_registry.register(TerminalTool(
            workspace_path=self.workspace_path, 
            event_callback=self.event_callback
        ))
        self.tool_registry.register(TaskCompleteTool(workspace_path=self.workspace_path))

        logger.info(f"[AGENT] Registered tools: {self.tool_registry.list_tools()}")

    def _create_system_prompt(self) -> str:
        """Create system prompt for the agent"""
        return """You are an expert AI coding agent that generates PRODUCTION-READY, FULLY FUNCTIONAL applications.

## CRITICAL REQUIREMENT: PRODUCTION-READY CODE
Every application you generate must be:
1. FULLY FUNCTIONAL - All buttons, forms, and interactions must work
2. CONNECTED - Frontend must call backend APIs (never use hardcoded mock data)
3. PERSISTENT - Data must persist (localStorage for frontend-only, or real API calls)
4. ERROR HANDLED - Include try/catch, loading states, error messages
5. RESPONSIVE - Works on mobile and desktop

## TOOLS
- file_operations: create/read/update/delete files
- terminal: run shell commands
- task_complete: signal completion

## RULES
1. Always use tools - never just describe what to do
2. Create complete files with full content
3. EVERY feature must be implemented and working, not placeholder code
4. Run npm install and npm run dev to start the app
5. Only call task_complete when app is FULLY running and TESTED

## FULL-STACK APPLICATION REQUIREMENTS

### Backend (FastAPI)
Create a proper backend with:
1. All CRUD endpoints for each entity
2. Proper Pydantic models for validation
3. In-memory storage (list/dict) with seed data (5-10 items)
4. CORS middleware enabled for frontend access
5. Health check endpoint at GET /health
6. Error handling with appropriate status codes
7. NO AUTHENTICATION for simple demos - all endpoints should be public
8. Seed the database with sample data so the app works immediately

### CRITICAL: SIMPLE REST API PATTERN (MUST FOLLOW)

For demo apps WITHOUT authentication, use these EXACT endpoint patterns:

```
GET  /api/{entity}          → Returns ALL items (no user_id needed!)
POST /api/{entity}          → Creates new item
GET  /api/{entity}/{id}     → Returns single item by id
PUT  /api/{entity}/{id}     → Updates item by id
DELETE /api/{entity}/{id}   → Deletes item by id
```

Example for an e-commerce app:
```
GET  /api/products     → Returns all products
POST /api/products     → Creates a product
GET  /api/products/1   → Returns product with id 1

GET  /api/orders       → Returns ALL orders (not /api/orders/{user_id})
POST /api/orders       → Creates an order
GET  /api/orders/1     → Returns order with id 1

GET  /api/cart         → Returns cart items
POST /api/cart         → Adds item to cart
DELETE /api/cart/{id}  → Removes item from cart
```

⚠️ WRONG PATTERNS - DO NOT USE:
- `/api/orders/{user_id}` - Don't put user_id in path for list endpoints
- `/api/cart/{user_id}` - Don't require user_id for cart
- `/api/admin/orders` - Keep it simple, just use `/api/orders`

### CRITICAL: Frontend-Backend Sync CHECKLIST

Before writing frontend code, LIST your backend endpoints:
1. Write down each endpoint: method + path
2. Check frontend ONLY calls those EXACT endpoints
3. If frontend needs `/api/orders`, backend MUST have `GET /api/orders`

VALIDATION CHECKLIST:
- [ ] Frontend calls `/api/products` → Backend has `@app.get("/api/products")`
- [ ] Frontend calls `/api/orders` → Backend has `@app.get("/api/orders")`  
- [ ] Frontend POSTs to `/api/orders` → Backend has `@app.post("/api/orders")`
- [ ] NO endpoint mismatches between frontend and backend

### Frontend (React + Vite)
Create a frontend that:
1. CALLS THE BACKEND APIs using fetch() - NEVER use hardcoded data
2. Uses useState for local state, useEffect for API calls
3. Shows loading spinners during API calls
4. Displays error messages when API fails
5. Updates UI immediately after actions (optimistic updates)
6. Includes proper form validation
7. ONLY calls endpoints that exist in your backend - no /api/users unless backend has it
8. NO authentication tokens needed - backend endpoints are all public

### API Integration Pattern (REQUIRED)

CRITICAL: Use RELATIVE URLs (like '/api/products') NOT absolute URLs (like 'http://localhost:8000/api/products')
This ensures the Vite proxy correctly forwards requests to the backend.

```javascript
// CORRECT - Uses RELATIVE URLs (Vite proxy handles routing to backend)
const [products, setProducts] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  fetch('/api/products')  // RELATIVE URL - no localhost!
    .then(res => {
      if (!res.ok) throw new Error('Failed to fetch');
      return res.json();
    })
    .then(data => setProducts(data))
    .catch(err => setError(err.message))
    .finally(() => setLoading(false));
}, []);

const addProduct = async (product) => {
  try {
    const res = await fetch('/api/products', {  // RELATIVE URL
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(product)
    });
    if (res.ok) {
      const newProduct = await res.json();
      setProducts([...products, newProduct]);
    }
  } catch (err) {
    setError(err.message);
  }
};
```

### WRONG (DO NOT DO THIS):
```javascript
// WRONG - Absolute URL causes CORS errors!
fetch('http://localhost:8000/api/products')  // NEVER DO THIS

// WRONG - Hardcoded mock data
const products = [
  { id: 1, name: 'Item 1', price: 10 },
  { id: 2, name: 'Item 2', price: 20 }
];
```

## LAYOUT REQUIREMENTS (CRITICAL)

1. App container MUST use min-h-screen to fill viewport height:
   ```jsx
   <div className="min-h-screen bg-slate-900 text-white">
   ```

2. Main content area should flex-grow to fill space:
   ```jsx
   <div className="flex flex-col min-h-screen">
     <nav>...</nav>
     <main className="flex-1 p-6">...</main>
     <footer>...</footer>
   </div>
   ```

3. Always show content - never leave main area empty:
   - Show loading spinner while fetching
   - Show error message if fetch fails
   - Show "No items found" if data is empty array
   - Show actual data when loaded

## CSS REQUIREMENTS

Use a dark theme with these colors:
- Background: #0a0a0f (main), #16161f (cards)
- Primary: #6366f1 (buttons, accents)
- Text: #f8fafc (primary), #64748b (muted)
- Border: #2d2d3a

Include:
1. :root with CSS variables
2. Reset (* { margin: 0; box-sizing: border-box; })
3. html, body, #root { min-height: 100vh; }
4. body { background: #0a0a0f; color: #f8fafc; font-family: Inter, sans-serif; }
5. Styles for EVERY className used in JSX
6. Hover states and transitions
7. Loading spinner animation
8. Error state styles (red border, error message)
9. Empty state styles ("No items found")

## VITE CONFIG (CRITICAL FOR API PROXY)

Create frontend/vite.config.js with proxy to avoid CORS:
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:8000',  // 'backend' is Docker service name
        changeOrigin: true
      }
    }
  }
})
```

## BACKEND CORS (REQUIRED)

Always include CORS middleware in FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## DOCKER COMPOSE FOR FULL-STACK

Create docker-compose.yml that runs BOTH frontend and backend:
```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 5s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      backend:
        condition: service_healthy
    environment:
      - VITE_API_URL=http://backend:8000
```

## INDEX.HTML TEMPLATE (CRITICAL FOR FULL HEIGHT)

frontend/index.html MUST include these styles to fill viewport:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>App</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
      html, body, #root {
        height: 100%;
        min-height: 100vh;
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

## WORKFLOW
1. Create backend/main.py with FastAPI app and ALL endpoints
2. Create backend/requirements.txt (fastapi, uvicorn)
3. Create backend/Dockerfile
4. Create frontend/package.json with vite and react
5. Create frontend/index.html - MUST include height: 100% styles!
6. Create frontend/src/main.jsx
7. Create frontend/src/App.jsx - MUST use min-h-screen and call backend APIs
8. Create frontend/src/App.css
9. Create frontend/vite.config.js with proxy to backend
10. Create frontend/Dockerfile
11. Create docker-compose.yml
12. Run: docker-compose up --build
13. Verify app works at http://localhost:3000
14. Call task_complete with verification results"""

    async def _emit_event(self, event_type: str, data: Any, metadata: Optional[Dict] = None):
        """Emit event to callback if registered"""
        if self.event_callback:
            event = {
                "type": event_type,
                "data": data,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
            await self.event_callback(event)

    async def run(self, user_prompt: str, max_iterations: int = 50) -> Dict[str, Any]:
        """
        Run the agent with a user prompt
        
        Args:
            user_prompt: User's request
            max_iterations: Maximum tool execution iterations
            
        Returns:
            Dict with results
        """
        logger.info(f"[AGENT] Starting with prompt: {user_prompt[:100]}...")

        # Initialize conversation
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        iterations = 0
        task_completed = False
        completion_report = None
        files_created = []
        commands_run = []

        try:
            while iterations < max_iterations and not task_completed:
                iterations += 1
                logger.info(f"[AGENT] Iteration {iterations}/{max_iterations}")

                await self._emit_event("iteration_start", {
                    "iteration": iterations,
                    "max_iterations": max_iterations
                })

                # Get LLM response
                response = self.llm.chat(
                    messages=self.messages,
                    tools=self.tool_registry.to_openai_tools(),
                    temperature=0.7,
                )

                await self._emit_event("llm_response", {
                    "content": response.content,
                    "tool_calls": len(response.tool_calls) if response.tool_calls else 0
                })

                # If no tool calls, prompt for tool usage
                if not response.tool_calls:
                    logger.warning("[AGENT] No tool calls in response")
                    self.messages.append({
                        "role": "user",
                        "content": "ERROR: You must use tools to complete the task. Call file_operations to create files, terminal to run commands, or task_complete when done."
                    })
                    continue

                # Add assistant message
                if response.content:
                    self.messages.append({"role": "assistant", "content": response.content})

                # Execute tool calls
                for tool_call in response.tool_calls:
                    tool_name = tool_call.name
                    parameters = tool_call.arguments

                    logger.info(f"[AGENT] Executing tool: {tool_name}")

                    await self._emit_event("tool_call", {
                        "tool_name": tool_name,
                        "parameters": parameters
                    })

                    # Execute tool
                    result = await self.tool_registry.execute(tool_name, **parameters)

                    await self._emit_event("tool_result", {
                        "tool_name": tool_name,
                        "result": result,
                        "success": result.get("success", False)
                    })

                    # Track files and commands
                    if tool_name == "file_operations" and result.get("success"):
                        if parameters.get("operation") in ["create", "update"]:
                            files_created.append(parameters.get("path"))

                    if tool_name == "terminal":
                        commands_run.append(parameters.get("command"))
                        
                        # Try to heal errors
                        if not result.get("success"):
                            healed = await self._try_heal_error(result, parameters)
                            if healed:
                                result = healed

                    # Check for task completion
                    if tool_name == "task_complete":
                        task_completed = True
                        completion_report = result
                        logger.info(f"[AGENT] Task completed: {result.get('status')}")
                        
                        await self._emit_event("task_complete", result)
                        break

                    # Add tool result to conversation
                    if tool_name == "terminal":
                        # Format terminal output explicitly
                        success = result.get("success", False)
                        stdout = result.get("stdout", "")
                        stderr = result.get("stderr", "")
                        exit_code = result.get("exit_code", -1)
                        error = result.get("error", "")

                        if success:
                            formatted = f"✅ Command succeeded:\n{stdout[:2000]}"
                        else:
                            formatted = f"❌ Command failed (exit {exit_code}):\nError: {error}\nStdout: {stdout[:1000]}\nStderr: {stderr[:1000]}"
                        
                        self.messages.append({
                            "role": "user",
                            "content": f"Tool 'terminal' result:\n{formatted}"
                        })
                    else:
                        self.messages.append({
                            "role": "user", 
                            "content": f"Tool '{tool_name}' result: {json.dumps(result)}"
                        })

            logger.info(f"[AGENT] Completed in {iterations} iterations")

            return {
                "success": True,
                "completed": task_completed,
                "completion_report": completion_report,
                "iterations": iterations,
                "files_created": files_created,
                "commands_run": commands_run,
            }

        except Exception as e:
            logger.error(f"[AGENT] Error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "iterations": iterations,
                "files_created": files_created,
                "commands_run": commands_run,
            }

    async def _try_heal_error(
        self, failed_result: Dict[str, Any], command_args: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Try to heal an error from a failed command"""
        
        # Detect error
        error = self.error_detector.detect(
            stdout=failed_result.get("stdout", ""),
            stderr=failed_result.get("stderr", ""),
            exit_code=failed_result.get("exit_code", 1),
            command=command_args.get("command"),
        )

        if not error:
            return None

        logger.info(f"[AGENT] Detected error: {error.error_type}")

        if not ErrorClassifier.is_fixable(error):
            return None

        # Get fix suggestion
        fix = self.error_fixer.suggest_fix(error)
        if not fix or not fix.command:
            return None

        logger.info(f"[AGENT] Attempting fix: {fix.description}")

        # Execute fix command
        terminal_tool = self.tool_registry.get("terminal")
        if terminal_tool:
            fix_result = await terminal_tool.execute(
                command=fix.command,
                cwd=command_args.get("cwd"),
            )

            if fix_result.get("success"):
                logger.info("[AGENT] Fix command succeeded, retrying original")

                # Retry original command
                retry_result = await terminal_tool.execute(**command_args)
                
                if retry_result.get("success"):
                    logger.info("[AGENT] ✓ Self-healing successful!")
                    self.error_fixer.track_fix(error, fix, True)
                    return retry_result

        self.error_fixer.track_fix(error, fix, False)
        return None

    def reset(self):
        """Reset conversation history"""
        self.messages = []
        logger.info("[AGENT] Reset conversation")
