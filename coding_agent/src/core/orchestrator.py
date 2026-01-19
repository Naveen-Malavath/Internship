"""Main orchestrator - the brain of the coding agent"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout

from .config import get_config
from .llm import LLMProvider, LLMResponse
from .parallel_executor import ParallelExecutor
from .state_manager import StateManager
from ..tools.base import ToolRegistry
from ..tools.file_ops import FileOperationsTool
from ..tools.terminal import TerminalTool
from ..tools.code_gen import CodeGenTool
from ..tools.search_tool import SearchTool
from ..tools.task_complete import TaskCompleteTool
from ..healing.error_detector import ErrorDetector
from ..healing.classifier import ErrorClassifier
from ..healing.fixer import ErrorFixer, FixSuggestion


class CodingAgent:
    """
    Main AI Coding Agent orchestrator
    Coordinates LLM, tools, and execution flow
    """

    def __init__(
        self,
        workspace_path: Optional[Path] = None,
        llm_provider: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize the coding agent
        
        Args:
            workspace_path: Working directory for the agent
            llm_provider: LLM provider ('openai' or 'anthropic')
            model: Model name to use
        """
        self.config = get_config()
        self.workspace_path = workspace_path or self.config.workspace_path

        # Initialize LLM
        self.llm = LLMProvider(
            provider=llm_provider,
            model=model,
        )
        logger.info(f"Initialized CodingAgent with workspace: {self.workspace_path}")

        # Event callback for Web UI streaming (must be set before registering tools)
        self.event_callback = None

        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        self._register_default_tools()

        # Initialize self-healing components
        self.error_detector = ErrorDetector()
        self.error_fixer = ErrorFixer()
        
        # Initialize Phase 5 components
        self.parallel_executor = ParallelExecutor()
        self.state_manager = StateManager(self.workspace_path)
        self.console = Console()

        # Conversation history
        self.messages: List[Dict[str, str]] = []
        self.system_prompt = self._create_system_prompt()
    
    async def _emit_event(self, event_type: str, source: str, target: str, data: Any, metadata: Optional[Dict] = None):
        """Emit event to callback if registered"""
        if self.event_callback:
            from datetime import datetime
            event = {
                "type": event_type,
                "source": source,
                "target": target,
                "data": data,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
            await self.event_callback(event)

    def _register_default_tools(self):
        """Register default tools"""
        file_tool = FileOperationsTool(workspace_path=self.workspace_path)
        # Pass event_callback to terminal tool for real-time streaming
        terminal_tool = TerminalTool(workspace_path=self.workspace_path, event_callback=self.event_callback)
        code_gen_tool = CodeGenTool(workspace_path=self.workspace_path)
        search_tool = SearchTool(workspace_path=self.workspace_path)
        task_complete_tool = TaskCompleteTool(workspace_path=self.workspace_path)

        self.tool_registry.register(file_tool)
        self.tool_registry.register(terminal_tool)
        self.tool_registry.register(code_gen_tool)
        self.tool_registry.register(search_tool)
        self.tool_registry.register(task_complete_tool)

        logger.info(
            f"Registered {len(self.tool_registry)} default tools: {self.tool_registry.list_tools()}"
        )
    
    def set_event_callback(self, callback):
        """Set event callback and update terminal tool if already registered"""
        self.event_callback = callback
        # Update terminal tool's event callback if it's already registered
        terminal_tool = self.tool_registry.get("terminal")
        if terminal_tool:
            terminal_tool.event_callback = callback
            logger.info("✅ Updated terminal tool event_callback for real-time streaming")
            print(f"[OK] [ORCHESTRATOR] Updated terminal tool event_callback for real-time streaming")

    def _create_system_prompt(self) -> str:
        """Create system prompt for the agent"""
        return """You are an ELITE AI coding agent that generates PRODUCTION-READY, BEAUTIFUL applications autonomously.

## YOUR CAPABILITIES
1. Create, read, update, delete files with file_operations tool
2. Execute terminal commands with terminal tool  
3. Generate full-stack applications with generate_code tool
4. Search code with search_code tool
5. Signal completion with task_complete tool

## CRITICAL: BULLETPROOF CODE QUALITY

### DESIGN SYSTEM - USE THESE EXACT CSS VARIABLES
Every CSS file MUST start with these variables:

```css
:root {
  /* Colors - Dark Theme */
  --color-bg-primary: #0a0a0f;
  --color-bg-secondary: #12121a;
  --color-bg-card: #16161f;
  --color-bg-hover: #1e1e28;
  
  --color-primary: #6366f1;
  --color-primary-hover: #818cf8;
  --color-primary-glow: rgba(99, 102, 241, 0.3);
  
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  
  --color-text-primary: #f8fafc;
  --color-text-secondary: #94a3b8;
  --color-text-muted: #64748b;
  
  --color-border: #2d2d3a;
  --color-border-hover: #3d3d4a;
  
  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  
  /* Spacing (8px grid) */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  
  /* Border Radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
  
  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 200ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### CSS CLASS MATCHING - CRITICAL
**EVERY className in JSX MUST have a matching CSS class definition!**

WRONG (classes don't match):
```jsx
// App.jsx
<div className="input-section">  // Uses "input-section"
```
```css
/* App.css */
.todo-input-container { }  // Defines "todo-input-container" - MISMATCH!
```

CORRECT (classes match exactly):
```jsx
// App.jsx  
<div className="todo-input-section">
```
```css
/* App.css */
.todo-input-section { padding: var(--spacing-4); }  // MATCHES!
```

### MINIMUM CSS REQUIREMENTS
Every CSS file MUST include (minimum 200+ lines):
1. CSS variables (:root block)
2. Reset styles (*, html, body)
3. Component styles for EVERY className used
4. Hover states and transitions
5. Responsive breakpoints (@media queries)
6. Animations (@keyframes)

### BUTTON STYLES - Always include:
```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-3) var(--spacing-5);
  font-weight: 600;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, #8b5cf6 100%);
  color: white;
  box-shadow: 0 0 20px var(--color-primary-glow);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 30px var(--color-primary-glow);
}
```

### INPUT STYLES - Always include:
```css
.input, input[type="text"] {
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  font-family: var(--font-family);
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast);
}

.input:focus, input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}
```

### CARD STYLES - Always include:
```css
.card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
  transition: all var(--transition-normal);
}

.card:hover {
  border-color: var(--color-border-hover);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}
```

### ANIMATIONS - Always include:
```css
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

## TOOL USAGE RULES - MANDATORY

1. **ALWAYS USE TOOLS** - Never describe actions, EXECUTE them
2. **NO TEXT-ONLY RESPONSES** - Every response needs tool calls
3. **VALIDATE CSS CLASSES** - Ensure JSX classNames match CSS definitions
4. **INSTALL DEPENDENCIES** - Run `npm install` after creating package.json
5. **START THE APP** - Run `npm run dev` to launch the application
6. **COMPLETE THE TASK** - Only call task_complete when app is RUNNING

## EXECUTION PROTOCOL

1. Create all files using file_operations
2. Verify CSS classes match JSX classNames  
3. Run `npm install` using terminal tool
4. Run `npm run dev` using terminal tool (background mode)
5. Verify app is running
6. Call task_complete with status="success"

## FORBIDDEN ACTIONS
- ❌ Empty or minimal CSS files
- ❌ Mismatched CSS class names
- ❌ Text-only responses without tools
- ❌ Manual installation guides
- ❌ Calling task_complete with failed commands
- ❌ Using generic/ugly browser default styles

## REQUIRED QUALITY
- ✅ 200+ lines of CSS minimum
- ✅ Dark theme with gradients
- ✅ Smooth hover animations
- ✅ Responsive design
- ✅ All CSS classes defined
- ✅ App running successfully
- Body and html base styles
- Component-specific styles with proper selectors
- Hover states and transitions
- Responsive breakpoints
- At least 100+ lines of meaningful CSS per major component

**Backend Quality Requirements:**
1. Proper error handling and validation
2. CORS configuration for frontend integration
3. Clean API structure with RESTful endpoints
4. Database models with proper relationships
5. Input validation using Pydantic or equivalent

**DO NOT:**
- Create skeleton/placeholder code
- Leave CSS files empty or minimal
- Skip styling in favor of "getting it working"
- Create ugly, unstyled interfaces
- Use default browser styles

**REMEMBER: A task is NOT complete if the UI looks ugly or unstyled. Beautiful design is REQUIRED.**

When given a task:
1. Break it down into clear steps
2. **MANDATORY: ALWAYS USE TOOLS** - You MUST call tools, never just describe actions
3. **FORBIDDEN**: Never respond with only text like "Let me create..." or "Now let me update..." - these are INVALID responses
4. **FORBIDDEN**: Never add descriptive prefatory text like "Let me check...", "There's a critical issue...", "I'll create..." - JUST CALL THE TOOLS DIRECTLY
5. **REQUIRED**: Every response MUST include tool calls. If you want to create a file → call file_operations tool. If you want to run a command → call terminal tool.
6. **REQUIRED**: Call tools IMMEDIATELY without explaining what you're about to do - the tool calls themselves are self-explanatory
7. If you encounter errors, analyze them and try to fix them using tools
8. Generate complete, working code using tools
9. Be proactive - don't ask for permission, just execute using tools
10. **CRITICAL**: When the task is complete, call the 'task_complete' tool to signal completion
11. **VALID RESPONSE**: Tool calls only (file_operations, terminal, generate_code, etc.) - no descriptive text needed
12. **INVALID RESPONSE**: Text-only responses OR responses with descriptive text like "Let me check the backend...", "There's a critical issue...", "I'll create a comprehensive report..." - these will be rejected or ignored

Available tools:
- file_operations: Create, read, update, delete, list files and directories
- terminal: **EXECUTE commands** - Install dependencies (npm install, pip install), run servers (npm run dev, uvicorn), execute any command. **USE THIS TOOL** to actually run commands, not just describe them.
- generate_code: Generate complete projects from templates (react, express, fastapi, fullstack-react-express, fullstack-react-fastapi)
- search_code: Search code semantically, find symbols/functions/classes, text search with regex
- task_complete: **Signal when task is done** (status: success/partial/failed, summary, files created, commands run)

**CRITICAL TOOL USAGE RULES:**
1. When you need to install dependencies → **CALL terminal tool** with command="npm install" (don't just say "install dependencies")
2. When you need to run a server → **CALL terminal tool** with command="npm run dev" (don't just describe it)
3. When you need to check versions → **CALL terminal tool** with command="npm --version" (don't just ask user)
4. **NEVER** respond with text saying "you should install" or "run this command" - **ALWAYS CALL THE TOOL INSTEAD**

Code Navigation Tips:
- Use semantic search to find code by meaning ("authentication logic", "database queries")
- Use symbol search to find functions/classes by name
- Use text search for exact matches or regex patterns
- Use definition search to find where symbols are defined
- Use references search to find imports/usages

**CRITICAL: Application Setup and Launch Protocol**:
When creating or generating any application (React, Express, FastAPI, Node.js, Python, etc.):
1. **ALWAYS** install dependencies using the terminal tool:
   - For Node.js projects: Run `cd <project_dir> && npm install` or `npm install --prefix <project_dir>`
   - For Python projects: Run `cd <project_dir> && pip install -r requirements.txt` or create virtual environment if needed
   - For other package managers: Use the appropriate install command
2. **ALWAYS** verify installation succeeded before proceeding
3. **ALWAYS** launch/run the application to verify it works:
   - For React/Vite: Run `npm run dev` (usually runs on http://localhost:5173)
   - For Express: Run `npm start` or `node server.js` (usually runs on http://localhost:3000)
   - For FastAPI: Run `uvicorn main:app --reload` (usually runs on http://localhost:8000)
   - Check the output to confirm the server started successfully
4. If errors occur during installation or launch:
   - Use the error detection and self-healing capabilities
   - Try to fix the issues automatically (check PATH, install missing tools, fix configurations)
   - **KEEP TRYING** until commands succeed - do NOT give up after one failure
   - Diagnose the root cause (e.g., Node.js not installed, PATH not configured, permissions issue)
   - Fix the root cause, then retry the command
   - **NEVER** call task_complete if critical commands (npm install, npm run dev) FAILED
5. **DO NOT** just create files and stop - running the application is part of the task completion
6. **FORBIDDEN**: Do NOT provide "next_steps" telling the user to run commands manually - YOU must run them yourself
7. **FORBIDDEN**: Do NOT call task_complete with failed commands listed in commands_run - commands must SUCCEED

**Task Completion Protocol - CRITICAL RULES**:
**YOU CANNOT MARK A TASK AS COMPLETE IF COMMANDS FAILED!**

When you have completed the task:
1. Verify all files are created
2. Verify dependencies are installed **AND SUCCEEDED** (commands must return success=True)
3. Verify the application runs successfully **AND SUCCEEDED** (launch commands must return success=True)
4. **ONLY THEN** call task_complete with status="success"
5. Include list of files_created and ALL **SUCCESSFUL** commands_run
6. **DO NOT** list failed commands - if commands failed, you MUST fix them first, then retry

**REJECTION CRITERIA - Your task_complete will be REJECTED if:**
- ❌ You list failed commands (e.g., "npm install (failed)") - commands MUST succeed
- ❌ You provide "next_steps" for commands you should run - YOU must run them
- ❌ Critical commands (npm install, npm run dev) failed - you MUST fix and retry
- ❌ Dependencies installed but app not launched - you MUST launch the app

**VALID task_complete example:**
- ✅ status="success"
- ✅ commands_run=["npm install", "npm run dev"] (both succeeded)
- ✅ No next_steps about running commands (you already ran them)

**INVALID task_complete example (will be REJECTED):**
- ❌ commands_run=["npm install (failed)", "npm run dev (failed)"]
- ❌ next_steps=["Run npm install", "Run npm run dev"]
- ❌ Listing failed commands and saying "user should run them"

**Remember: The task is ONLY complete when commands actually SUCCEED, not when they fail!**

When generating full applications, prefer using generate_code tool for faster results, but REMEMBER to install dependencies and launch the app afterward.
Work efficiently and aim to complete tasks fully on the first attempt. Execution is just as important as file creation."""

    async def run(self, user_prompt: str, max_iterations: int = 150) -> Dict[str, Any]:
        """
        Run the agent with a user prompt
        
        Args:
            user_prompt: User's request/prompt
            max_iterations: Maximum tool execution iterations
            
        Returns:
            Dict with results and conversation history
        """
        logger.info(f"Starting agent with prompt: {user_prompt[:100]}...")

        # Initialize conversation
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        iterations = 0
        final_response = ""
        task_completed = False
        completion_report = None
        
        # Track files and commands for validation
        self._created_files_tracker = []
        self._executed_commands_tracker = []

        try:
            while iterations < max_iterations and not task_completed:
                iterations += 1
                logger.info(f"Iteration {iterations}/{max_iterations}")
                
                # Emit iteration start
                await self._emit_event(
                    "iteration_start",
                    "agent",
                    "system",
                    {"iteration": iterations, "max_iterations": max_iterations},
                    {"iteration": iterations}
                )

                # Get LLM response
                await self._emit_event(
                    "llm_request",
                    "agent",
                    "llm",
                    {
                        "messages": self.messages,
                        "tools_available": len(self.tool_registry.to_openai_tools())
                    },
                    {"iteration": iterations}
                )
                
                logger.info(f"🔄 [ORCHESTRATOR] About to call llm.chat() in iteration {iterations}")
                print(f"🔄 [ORCHESTRATOR] About to call llm.chat() in iteration {iterations}")
                logger.info(f"🔄 [ORCHESTRATOR] Provider: {self.llm.provider}")
                print(f"🔄 [ORCHESTRATOR] Provider: {self.llm.provider}")
                
                try:
                    response = self.llm.chat(
                        messages=self.messages,
                        tools=self.tool_registry.to_openai_tools(),
                        temperature=0.7,
                    )
                    logger.info(f"✅ [ORCHESTRATOR] llm.chat() completed successfully")
                    print(f"✅ [ORCHESTRATOR] llm.chat() completed successfully")
                except Exception as e:
                    logger.error(f"🔴 [ORCHESTRATOR] ERROR in llm.chat(): {e}", exc_info=True)
                    print(f"🔴 [ORCHESTRATOR] ERROR in llm.chat(): {e}")
                    import traceback
                    traceback.print_exc()
                    raise
                
                await self._emit_event(
                    "llm_response",
                    "llm",
                    "agent",
                    {
                        "content": response.content,
                        "tool_calls": len(response.tool_calls) if response.tool_calls else 0
                    },
                    {"iteration": iterations}
                )

                # If no tool calls, REJECT immediately - don't add text to history
                if not response.tool_calls:
                    logger.error(f"🔴 [ORCHESTRATOR] REJECTED: Agent responded with text but NO TOOL CALLS. This is INVALID.")
                    print(f"🔴 [ORCHESTRATOR] REJECTED: Agent responded with text but NO TOOL CALLS. This is INVALID.")
                    print(f"🔴 [ORCHESTRATOR] Response content: {response.content[:200] if response.content else 'None'}")
                    
                    # DO NOT add the assistant's text-only response to history - it's rejected
                    # This prevents the agent from thinking text-only responses are acceptable
                    
                    # Add STRONG error message with examples
                    error_message = f"""ERROR: Your response was REJECTED because it contained NO TOOL CALLS.

Your invalid response: "{response.content[:150] if response.content else 'Empty response'}..."

**THIS IS FORBIDDEN.** You MUST call tools, not describe actions.

**EXAMPLES OF INVALID RESPONSES (DO NOT DO THIS):**
- "Now let me update the CSS..." ❌
- "Let me create a standalone HTML version..." ❌  
- "I'll install the dependencies..." ❌
- Any text without tool calls ❌

**EXAMPLES OF VALID RESPONSES (DO THIS):**
- Call file_operations tool with operation="update", path="file.css", content="..." ✅
- Call terminal tool with command="npm install" ✅
- Call generate_code tool with project_type="react" ✅

**YOU MUST CALL A TOOL NOW.** Respond with tool calls only, no explanatory text."""
                    
                    self.messages.append({
                        "role": "user",
                        "content": error_message
                    })
                    
                    logger.warning(f"⚠️ [ORCHESTRATOR] Rejected text-only response. Forcing agent to call tools.")
                    print(f"⚠️ [ORCHESTRATOR] Rejected text-only response. Forcing agent to call tools.")
                    continue  # Continue loop - agent MUST call tools
                
                # Check for descriptive prefatory text (even with tool calls) - this is also bad
                if response.content and response.tool_calls:
                    # Check if content contains descriptive phrases that indicate describing actions instead of doing them
                    descriptive_phrases = [
                        "let me", "i'll", "i will", "now let me", "let me check",
                        "i should", "i need to", "i'm going to", "i will now",
                        "let me create", "let me update", "let me check",
                        "i'll check", "i'll create", "i'll update", "i'll run",
                        "there's a", "there is a", "it seems", "it appears",
                        "critical issue", "comprehensive status", "status report"
                    ]
                    
                    content_lower = response.content.lower()
                    has_descriptive_text = any(phrase in content_lower for phrase in descriptive_phrases)
                    
                    if has_descriptive_text:
                        logger.warning(f"⚠️ [ORCHESTRATOR] Agent used descriptive prefatory text with tool calls")
                        print(f"⚠️ [ORCHESTRATOR] Agent used descriptive prefatory text: {response.content[:100]}")
                        
                        # Strip the descriptive text and only keep tool calls
                        # Don't add the descriptive content to history - it's unnecessary
                        # The tool calls themselves are sufficient
                        logger.info(f"✅ [ORCHESTRATOR] Accepting tool calls but ignoring descriptive text")
                        # Don't add the content to history - just execute the tools
                        response.content = ""  # Clear descriptive text
                
                # Only add assistant message to history if there's non-descriptive content
                # Most of the time, tool calls alone are sufficient
                if response.content and response.content.strip():
                    # Only add if it's not descriptive prefatory text
                    self.messages.append(
                        {"role": "assistant", "content": response.content}
                    )
                elif response.tool_calls:
                    # If only tool calls, we can optionally add a minimal message
                    # But it's better to just let the tool calls speak for themselves
                    # Tools will be added to history automatically when executed
                    pass

                # Execute tool calls (with parallel execution for independent calls)
                tool_call_dicts = [
                    {'name': tc.name, 'parameters': tc.arguments, 'id': tc.id}
                    for tc in response.tool_calls
                ]
                
                # Group calls for parallel execution
                batches = self.parallel_executor.group_independent_calls(tool_call_dicts)
                
                await self._emit_event(
                    "parallel_batch_start",
                    "agent",
                    "tools",
                    {
                        "total_tools": len(response.tool_calls),
                        "batches": len(batches),
                        "batch_sizes": [len(b) for b in batches]
                    },
                    {"iteration": iterations}
                )
                
                self.console.print(f"\n[bold blue]→ Executing {len(response.tool_calls)} tools in {len(batches)} batch(es)[/bold blue]")
                
                all_results = []
                for batch_idx, batch in enumerate(batches, 1):
                    if len(batch) > 1:
                        self.console.print(f"  [cyan]Batch {batch_idx}: {len(batch)} tools in parallel[/cyan]")
                        # Execute in parallel
                        results = await self.parallel_executor.execute_parallel(
                            batch, self.tool_registry, show_progress=True
                        )
                    else:
                        self.console.print(f"  [yellow]Batch {batch_idx}: 1 tool sequentially[/yellow]")
                        # Execute single tool
                        results = await self.parallel_executor.execute_sequential(
                            batch, self.tool_registry
                        )
                    
                    all_results.extend(results)
                
                # Process results and add to conversation
                # Safety check: ensure we have matching tool calls and results
                if len(all_results) != len(response.tool_calls):
                    logger.error(f"🔴 [ORCHESTRATOR] Mismatch: {len(response.tool_calls)} tool calls but {len(all_results)} results")
                    print(f"🔴 [ORCHESTRATOR] Mismatch: {len(response.tool_calls)} tool calls but {len(all_results)} results")
                    # Use the minimum to avoid index errors
                    min_len = min(len(all_results), len(response.tool_calls))
                    all_results = all_results[:min_len]
                    response.tool_calls = response.tool_calls[:min_len]
                
                for i, exec_result in enumerate(all_results):
                    if i >= len(response.tool_calls):
                        logger.error(f"🔴 [ORCHESTRATOR] Index {i} out of range for tool_calls (length: {len(response.tool_calls)})")
                        print(f"🔴 [ORCHESTRATOR] Index {i} out of range for tool_calls")
                        break
                    
                    tool_call = response.tool_calls[i]
                    result = exec_result.result
                    
                    # CRITICAL DIAGNOSTIC: Log what we're about to process
                    logger.info(f"🔍 [ORCHESTRATOR] Processing tool result {i}: tool={tool_call.name}, exec_result.success={exec_result.success}")
                    print(f"[DEBUG] [ORCHESTRATOR] Processing tool result {i}: tool={tool_call.name}, exec_result.success={exec_result.success}")
                    if isinstance(result, dict):
                        logger.info(f"🔍 [ORCHESTRATOR] Result dict: success={result.get('success')}, error={repr(result.get('error', ''))[:100]}")
                        print(f"[DEBUG] [ORCHESTRATOR] Result dict: success={result.get('success')}, error={repr(result.get('error', ''))[:100]}")
                    else:
                        logger.warning(f"⚠️ [ORCHESTRATOR] Result is not a dict: {type(result)}")
                        print(f"[WARNING] [ORCHESTRATOR] Result is not a dict: {type(result)}")
                    
                    # Safety check: ensure tool_call has required attributes
                    if not hasattr(tool_call, 'name'):
                        logger.error(f"🔴 [ORCHESTRATOR] tool_call at index {i} missing 'name' attribute: {type(tool_call)}")
                        print(f"🔴 [ORCHESTRATOR] tool_call at index {i} missing 'name' attribute")
                        continue
                    
                    # Emit tool call event
                    await self._emit_event(
                        "tool_call",
                        "agent",
                        "tool",
                        {
                            "tool_name": tool_call.name,
                            "parameters": tool_call.arguments
                        },
                        {"iteration": iterations, "tool_index": i}
                    )
                    
                    # CRITICAL: Ensure result dict has all required fields for terminal commands
                    if tool_call.name == "terminal":
                        # Force include success and exit_code in result if missing
                        if "success" not in result:
                            result["success"] = result.get("exit_code", 0) == 0
                            logger.warning(f"⚠️ [ORCHESTRATOR] result missing 'success' field, derived from exit_code")
                        if "exit_code" not in result:
                            result["exit_code"] = -1
                            logger.warning(f"⚠️ [ORCHESTRATOR] result missing 'exit_code' field, defaulting to -1")
                        if "error" not in result:
                            result["error"] = "" if result.get("success") else "Unknown error"
                            logger.warning(f"⚠️ [ORCHESTRATOR] result missing 'error' field, defaulting")
                        if "command" not in result:
                            result["command"] = tool_call.arguments.get("command", "")
                            logger.warning(f"⚠️ [ORCHESTRATOR] result missing 'command' field, using from arguments")
                        # CRITICAL: Also ensure stdout, stderr, and cwd are present (even if empty)
                        if "stdout" not in result:
                            result["stdout"] = ""
                            logger.warning(f"⚠️ [ORCHESTRATOR] result missing 'stdout' field, defaulting to empty string")
                        if "stderr" not in result:
                            result["stderr"] = ""
                            logger.warning(f"⚠️ [ORCHESTRATOR] result missing 'stderr' field, defaulting to empty string")
                        if "cwd" not in result:
                            result["cwd"] = tool_call.arguments.get("cwd", "")
                            logger.warning(f"⚠️ [ORCHESTRATOR] result missing 'cwd' field, using from arguments")
                    
                    # CRITICAL: For terminal commands, log the complete result before emitting
                    if tool_call.name == "terminal" and isinstance(result, dict):
                        logger.info(f"🔍 [ORCHESTRATOR] Terminal result FULL structure: {json.dumps({k: str(v)[:200] for k, v in result.items()})}")
                        print(f"[DEBUG] [ORCHESTRATOR] Terminal result FULL structure:")
                        print(f"[DEBUG] [ORCHESTRATOR]   success: {result.get('success')}")
                        print(f"[DEBUG] [ORCHESTRATOR]   exit_code: {result.get('exit_code')}")
                        print(f"[DEBUG] [ORCHESTRATOR]   command: {result.get('command')}")
                        print(f"[DEBUG] [ORCHESTRATOR]   stdout length: {len(result.get('stdout', ''))}")
                        print(f"[DEBUG] [ORCHESTRATOR]   stderr length: {len(result.get('stderr', ''))}")
                        print(f"[DEBUG] [ORCHESTRATOR]   error length: {len(result.get('error', ''))}")
                        print(f"[DEBUG] [ORCHESTRATOR]   stdout preview: {repr(result.get('stdout', '')[:200])}")
                        print(f"[DEBUG] [ORCHESTRATOR]   stderr preview: {repr(result.get('stderr', '')[:200])}")
                        print(f"[DEBUG] [ORCHESTRATOR]   error preview: {repr(result.get('error', '')[:200])}")
                    
                    # Emit tool result event with FULL result
                    await self._emit_event(
                        "tool_result",
                        "tool",
                        "agent",
                        {
                            "tool_name": tool_call.name,
                            "result": result,  # Full result dict
                            "success": result.get("success", True),
                            # CRITICAL: For terminal commands, explicitly include all fields
                            "exit_code": result.get("exit_code") if tool_call.name == "terminal" else None,
                            "error": result.get("error") if tool_call.name == "terminal" else None,
                            "command": result.get("command") if tool_call.name == "terminal" else None,
                            "stdout": result.get("stdout") if tool_call.name == "terminal" else None,
                            "stderr": result.get("stderr") if tool_call.name == "terminal" else None,
                        },
                        {"iteration": iterations, "tool_index": i}
                    )
                    
                    # Auto-execute commands after code generation
                    if tool_call.name == "generate_code" and result.get("success"):
                        suggested_commands = result.get("suggested_commands", [])
                        if suggested_commands:
                            logger.info(f"🔄 [ORCHESTRATOR] Auto-executing suggested commands after code generation")
                            print(f"🔄 [ORCHESTRATOR] Auto-executing {len(suggested_commands)} suggested commands")
                            
                            terminal_tool = self.tool_registry.get("terminal")
                            if terminal_tool:
                                executed_commands = []
                                for cmd in suggested_commands:
                                    logger.info(f"🔄 [ORCHESTRATOR] Auto-running: {cmd}")
                                    print(f"🔄 [ORCHESTRATOR] Auto-running: {cmd}")
                                    
                                    # Extract project directory if it's a cd command
                                    cwd = None
                                    actual_cmd = cmd
                                    
                                    if cmd.startswith("cd "):
                                        parts = cmd.split(" && ", 1)
                                        if len(parts) == 2:
                                            cwd_part = parts[0].replace("cd ", "").strip()
                                            actual_cmd = parts[1]
                                            # Resolve path relative to workspace
                                            cwd_path = Path(cwd_part)
                                            if not cwd_path.is_absolute():
                                                cwd = self.workspace_path / cwd_path
                                            else:
                                                cwd = Path(cwd_part)
                                            cwd = str(cwd.resolve())
                                            
                                            logger.info(f"🔄 [ORCHESTRATOR] Extracted cwd: {cwd} from command: {cmd}")
                                            print(f"🔄 [ORCHESTRATOR] Extracted cwd: {cwd} from command: {cmd}")
                                            
                                            # Verify directory exists
                                            if not Path(cwd).exists():
                                                logger.error(f"🔴 [ORCHESTRATOR] Directory does not exist: {cwd}")
                                                print(f"🔴 [ORCHESTRATOR] Directory does not exist: {cwd}")
                                                # Add error to conversation
                                                error_msg = f"Directory does not exist: {cwd}. The project may not have been created yet."
                                                if self.llm.provider.value == "anthropic":
                                                    self.messages.append({
                                                        "role": "user",
                                                        "content": f"Error: {error_msg}\n\nPlease create the directory first or wait for file creation to complete."
                                                    })
                                                else:
                                                    self.messages.append({
                                                        "role": "tool",
                                                        "content": json.dumps({
                                                            "success": False,
                                                            "error": error_msg,
                                                            "command": actual_cmd,
                                                            "cwd": cwd
                                                        }),
                                                        "tool_call_id": f"auto_exec_{iterations}_{i}",
                                                        "name": "terminal"
                                                    })
                                                continue
                                        else:
                                            actual_cmd = cmd
                                    
                                    # CRITICAL: Auto-detect dev server commands and run them in background
                                    # Dev servers run indefinitely, so they must run in background
                                    is_dev_server = any(keyword in actual_cmd.lower() for keyword in [
                                        "npm run dev", "npm start", "npm run start", 
                                        "uvicorn", "flask run", "python -m http.server"
                                    ])
                                    
                                    if is_dev_server:
                                        logger.info(f"🔄 [ORCHESTRATOR] Auto-detected dev server command: {actual_cmd}. Running in background mode.")
                                        print(f"[INFO] [ORCHESTRATOR] Auto-detected dev server command: {actual_cmd}. Running in background...")
                                        
                                    logger.info(f"🔄 [ORCHESTRATOR] Running command: {actual_cmd} in cwd: {cwd}, background: {is_dev_server}")
                                    print(f"🔄 [ORCHESTRATOR] Running command: {actual_cmd} in cwd: {cwd}, background: {is_dev_server}")
                                    
                                    try:
                                        cmd_result = await terminal_tool.execute(
                                            command=actual_cmd,
                                            cwd=str(cwd) if cwd else None,
                                            timeout=300 if is_dev_server else 60,
                                            background=is_dev_server  # CRITICAL: Run dev servers in background
                                        )
                                        
                                        executed_commands.append(cmd)
                                        
                                        # Track command execution
                                        if not hasattr(self, '_executed_commands_tracker'):
                                            self._executed_commands_tracker = []
                                        self._executed_commands_tracker.append(cmd)
                                        
                                        # Emit events for auto-executed commands so agent can see them
                                        await self._emit_event(
                                            "tool_call",
                                            "system",
                                            "terminal",
                                            {
                                                "tool_name": "terminal",
                                                "parameters": {"command": actual_cmd, "cwd": str(cwd) if cwd else None}
                                            },
                                            {"iteration": iterations, "auto_executed": True}
                                        )
                                        
                                        await self._emit_event(
                                            "tool_result",
                                            "terminal",
                                            "agent",
                                            {
                                                "tool_name": "terminal",
                                                "result": cmd_result,
                                                "success": cmd_result.get("success", False),
                                                "command": actual_cmd
                                            },
                                            {"iteration": iterations, "auto_executed": True}
                                        )
                                        
                                        if not cmd_result.get("success"):
                                            logger.warning(f"⚠️ [ORCHESTRATOR] Auto-executed command failed: {cmd}")
                                            print(f"⚠️ [ORCHESTRATOR] Auto-executed command failed: {cmd}")
                                            
                                            # Try to heal
                                            healed = await self._try_heal_error(
                                                cmd_result, {"command": actual_cmd, "cwd": str(cwd) if cwd else None}
                                            )
                                            if healed:
                                                logger.info(f"✅ [ORCHESTRATOR] Auto-healed command: {cmd}")
                                                print(f"✅ [ORCHESTRATOR] Auto-healed command: {cmd}")
                                            else:
                                                # If healing failed, add error to conversation so agent can fix it
                                                error_msg = cmd_result.get("error", "Unknown error")
                                                stdout = cmd_result.get("stdout", "")
                                                stderr = cmd_result.get("stderr", "")
                                                
                                                error_details = f"Command failed: {actual_cmd}\n"
                                                if error_msg:
                                                    error_details += f"Error: {error_msg}\n"
                                                if stderr:
                                                    error_details += f"STDERR: {stderr}\n"
                                                if stdout:
                                                    error_details += f"STDOUT: {stdout}"
                                                
                                                # Format terminal result explicitly for LLM to see ALL output
                                                success = cmd_result.get("success", False)
                                                stdout = cmd_result.get("stdout", "")
                                                stderr = cmd_result.get("stderr", "")
                                                exit_code = cmd_result.get("exit_code", -1)
                                                error = cmd_result.get("error", "")
                                                
                                                formatted_error_result = (
                                                    f"❌ Auto-executed command FAILED:\n"
                                                    f"Command: {actual_cmd}\n"
                                                    f"Exit Code: {exit_code}\n"
                                                    f"Error: {error if error else 'No error message'}\n"
                                                    f"STDOUT:\n{stdout if stdout.strip() else '(no output)'}\n"
                                                    f"STDERR:\n{stderr if stderr.strip() else '(no output)'}\n\n"
                                                    f"Full result: {json.dumps(cmd_result)}\n\n"
                                                    f"⚠️ The auto-executed command '{actual_cmd}' failed. Please analyze the error above and fix it. Error details:\n{error_details}"
                                                )
                                                
                                                # Add tool result to conversation so agent can see the error
                                                # Handle Anthropic vs OpenAI format
                                                if self.llm.provider.value == "anthropic":
                                                    self.messages.append({
                                                        "role": "user",
                                                        "content": f"Tool 'terminal' result:\n{formatted_error_result}"
                                                    })
                                                else:
                                                    self.messages.append({
                                                        "role": "tool",
                                                        "content": formatted_error_result,
                                                        "tool_call_id": f"auto_exec_{iterations}_{i}",
                                                        "name": "terminal"
                                                    })
                                                    # Add user message to prompt agent to fix
                                                    self.messages.append({
                                                        "role": "user",
                                                        "content": f"⚠️ The auto-executed command '{actual_cmd}' failed. Please analyze the tool result above and fix the issue."
                                                    })
                                                
                                                logger.info(f"🔄 [ORCHESTRATOR] Added error to conversation for agent to fix")
                                                print(f"🔄 [ORCHESTRATOR] Added error to conversation for agent to fix")
                                        else:
                                            # Add successful command result to conversation
                                            # Format terminal results explicitly for LLM
                                            success = cmd_result.get("success", False)
                                            stdout = cmd_result.get("stdout", "")
                                            stderr = cmd_result.get("stderr", "")
                                            exit_code = cmd_result.get("exit_code", -1)
                                            error = cmd_result.get("error", "")
                                            command = cmd_result.get("command", "")
                                            
                                            if success:
                                                formatted_cmd_result = (
                                                    f"✅ Auto-executed command SUCCEEDED:\n"
                                                    f"Command: {command}\n"
                                                    f"Exit Code: {exit_code}\n"
                                                    f"STDOUT:\n{stdout if stdout.strip() else '(no output)'}\n"
                                                    f"{f'STDERR:\n{stderr}' if stderr.strip() else ''}"
                                                )
                                            else:
                                                formatted_cmd_result = (
                                                    f"❌ Auto-executed command FAILED:\n"
                                                    f"Command: {command}\n"
                                                    f"Exit Code: {exit_code}\n"
                                                    f"Error: {error if error else 'No error message'}\n"
                                                    f"STDOUT:\n{stdout if stdout.strip() else '(no output)'}\n"
                                                    f"STDERR:\n{stderr if stderr.strip() else '(no output)'}\n\n"
                                                    f"Full result: {json.dumps(cmd_result)}"
                                                )
                                            
                                            # Handle Anthropic vs OpenAI format
                                            if self.llm.provider.value == "anthropic":
                                                self.messages.append({
                                                    "role": "user",
                                                    "content": f"Tool 'terminal' result:\n{formatted_cmd_result}"
                                                })
                                            else:
                                                self.messages.append({
                                                    "role": "tool",
                                                    "content": formatted_cmd_result,
                                                    "tool_call_id": f"auto_exec_{iterations}_{i}",
                                                    "name": "terminal"
                                                })
                                    except Exception as e:
                                        logger.error(f"🔴 [ORCHESTRATOR] Error auto-executing command {cmd}: {e}")
                                        print(f"🔴 [ORCHESTRATOR] Error auto-executing command {cmd}: {e}")
                                        
                                        # Add exception to conversation
                                        error_result = {
                                            "success": False,
                                            "error": str(e),
                                            "command": actual_cmd
                                        }
                                        # Handle Anthropic vs OpenAI format
                                        if self.llm.provider.value == "anthropic":
                                            self.messages.append({
                                                "role": "user",
                                                "content": f"Tool 'terminal' result: {json.dumps(error_result)}"
                                            })
                                        else:
                                            self.messages.append({
                                                "role": "tool",
                                                "content": json.dumps(error_result),
                                                "tool_call_id": f"auto_exec_{iterations}_{i}",
                                                "name": "terminal"
                                            })
                                
                                if executed_commands:
                                    # Add summary message about auto-executed commands
                                    self.messages.append({
                                        "role": "assistant",
                                        "content": f"I have automatically executed the following commands: {', '.join(executed_commands)}. Please check the tool results above and verify the application is running correctly."
                                    })
                    
                    # Track created files and executed commands across all tool calls
                    if tool_call.name == "file_operations" and result.get("success"):
                        operation = tool_call.arguments.get("operation")
                        if operation == "create" or operation == "update":
                            file_path = tool_call.arguments.get("path", "")
                            content = tool_call.arguments.get("content", "")
                            
                            # REJECT manual installation guides and next_steps files
                            if any(keyword in file_path.lower() for keyword in ["installation_guide", "manual_install", "next_steps", "setup_guide", "install_guide"]):
                                logger.error(f"🔴 [ORCHESTRATOR] REJECTED: Agent created manual installation guide: {file_path}")
                                print(f"🔴 [ORCHESTRATOR] REJECTED: Agent created manual installation guide: {file_path}")
                                
                                # Check if content contains manual installation instructions
                                content_lower = content.lower()
                                manual_keywords = ["manual installation", "open a new command prompt", "run manually", "follow these steps", "you should install", "user should run"]
                                if any(keyword in content_lower for keyword in manual_keywords):
                                    # Reject this file operation
                                    self.messages.append({
                                        "role": "user",
                                        "content": f"""🚫 ERROR: You created a manual installation guide at {file_path}. This is FORBIDDEN.

**YOU MUST RUN COMMANDS YOURSELF, NOT CREATE INSTRUCTIONS FOR THE USER.**

Delete this file and actually execute the commands using the terminal tool:
- Call terminal tool with command="npm install" (don't create a guide telling user to do it)
- Call terminal tool with command="npm run dev" (don't create instructions)

**DO NOT create INSTALLATION_GUIDE.md, MANUAL_INSTALL.md, or any files with manual steps.**
**YOU must execute the commands yourself using the terminal tool.**"""
                                    })
                                    
                                    # Delete the file if it was created
                                    try:
                                        file_full_path = self.workspace_path / file_path
                                        if file_full_path.exists():
                                            file_full_path.unlink()
                                            logger.info(f"🗑️ [ORCHESTRATOR] Deleted rejected installation guide: {file_path}")
                                            print(f"🗑️ [ORCHESTRATOR] Deleted rejected installation guide: {file_path}")
                                    except Exception as e:
                                        logger.error(f"Failed to delete file: {e}")
                                    
                                    continue  # Skip tracking this file
                            
                            # Track created files for validation (only if not rejected)
                            if operation == "create":
                                if not hasattr(self, '_created_files_tracker'):
                                    self._created_files_tracker = []
                                self._created_files_tracker.append(file_path)
                    
                    # Track terminal commands - both successful and failed
                    if tool_call.name == "terminal":
                        command = tool_call.arguments.get("command", "")
                        success = result.get("success", False)
                        
                        # Track all executed commands
                        if not hasattr(self, '_executed_commands_tracker'):
                            self._executed_commands_tracker = []
                        self._executed_commands_tracker.append(command)
                        
                        # Track successful commands separately
                        if not hasattr(self, '_successful_commands_tracker'):
                            self._successful_commands_tracker = []
                        if not hasattr(self, '_failed_commands_tracker'):
                            self._failed_commands_tracker = []
                        
                        if success:
                            self._successful_commands_tracker.append(command)
                            logger.info(f"✅ [ORCHESTRATOR] Command succeeded: {command}")
                        else:
                            self._failed_commands_tracker.append(command)
                            logger.warning(f"❌ [ORCHESTRATOR] Command failed: {command}")
                    
                    # Check if task_complete was called
                    if tool_call.name == "task_complete":
                        commands_run = result.get("commands_run", [])
                        files_created = result.get("files_created", [])
                        
                        # Also check tracked files if files_created is empty or incomplete
                        if not files_created and hasattr(self, '_created_files_tracker'):
                            files_created = self._created_files_tracker.copy()
                        
                        # Also check tracked commands if commands_run is empty
                        if not commands_run and hasattr(self, '_executed_commands_tracker'):
                            commands_run = self._executed_commands_tracker.copy()
                        
                        # Validate: if this is an app creation (has package.json, requirements.txt, etc.)
                        is_app_creation = any(
                            "package.json" in str(f) or 
                            "requirements.txt" in str(f) or 
                            "pom.xml" in str(f) or
                            "Cargo.toml" in str(f) or
                            "go.mod" in str(f)
                            for f in files_created
                        )
                        
                        # Get successful and failed commands
                        successful_commands = getattr(self, '_successful_commands_tracker', [])
                        failed_commands = getattr(self, '_failed_commands_tracker', [])
                        
                        # Check for critical commands that MUST succeed
                        critical_commands = ["npm install", "pip install", "npm run dev", "npm start", "uvicorn", "flask run"]
                        has_critical_success = any(
                            any(crit in cmd for crit in critical_commands) 
                            for cmd in successful_commands
                        )
                        has_critical_failure = any(
                            any(crit in cmd for crit in critical_commands)
                            for cmd in failed_commands
                        )
                        
                        # Check for manual installation steps (FORBIDDEN)
                        next_steps = result.get("next_steps", [])
                        manual_keywords = ["npm install", "pip install", "run manually", "open terminal", "command prompt"]
                        has_manual_steps = any(
                            any(keyword.lower() in str(step).lower() for keyword in manual_keywords)
                            for step in next_steps
                        ) if next_steps else False
                        
                        # Validate app creation requirements
                        if is_app_creation:
                            # Check 1: No commands run at all
                            if not commands_run:
                                logger.warning(f"⚠️ [ORCHESTRATOR] Task marked complete but no commands were run for app creation!")
                                print(f"⚠️ [ORCHESTRATOR] Task marked complete but no commands were run for app creation!")
                                
                                self.messages.append({
                                    "role": "user",
                                    "content": """🚫 ERROR: You called task_complete without running ANY commands. 

For application creation, you MUST:
1. Install dependencies (e.g., npm install, pip install -r requirements.txt)
2. Launch the application (e.g., npm run dev, uvicorn main:app --reload)

The task is NOT complete until the application is installed and running. 
Please use the terminal tool to install dependencies and launch the application, then call task_complete again with the commands_run field populated."""
                                })
                                
                                task_completed = False
                                logger.info(f"🔄 [ORCHESTRATOR] REJECTED: No commands run")
                                print(f"🔄 [ORCHESTRATOR] REJECTED: No commands run")
                                continue
                            
                            # Check 2: Critical commands failed
                            if has_critical_failure and not has_critical_success:
                                logger.error(f"🔴 [ORCHESTRATOR] Task marked complete but CRITICAL commands FAILED!")
                                print(f"🔴 [ORCHESTRATOR] Task marked complete but CRITICAL commands FAILED!")
                                print(f"🔴 [ORCHESTRATOR] Failed commands: {failed_commands}")
                                
                                failed_list = "\n".join([f"  ❌ {cmd}" for cmd in failed_commands if any(crit in cmd for crit in critical_commands)])
                                
                                self.messages.append({
                                    "role": "user",
                                    "content": f"""🚫 CRITICAL ERROR: You called task_complete, but CRITICAL commands FAILED:

{failed_list}

**YOU CANNOT MARK THE TASK AS COMPLETE WHEN COMMANDS FAIL!**

You MUST:
1. Diagnose WHY the commands failed (check PATH, Node.js installation, etc.)
2. Fix the underlying issue (install Node.js, fix PATH, etc.)
3. Retry the commands until they SUCCEED
4. Only then call task_complete

**DO NOT give up. DO NOT provide "next_steps". FIX THE ERRORS AND RETRY UNTIL IT WORKS.**

The task is NOT complete until:
- ✅ npm install succeeds (not fails!)
- ✅ npm run dev/start succeeds (not fails!)

**Analyze the error messages from the failed commands and fix them. Keep trying until the commands succeed.**"""
                                })
                                
                                task_completed = False
                                logger.error(f"🔄 [ORCHESTRATOR] REJECTED: Critical commands failed")
                                print(f"🔄 [ORCHESTRATOR] REJECTED: Critical commands failed")
                                continue
                            
                            # Check 3: Agent provided manual installation steps (FORBIDDEN)
                            if has_manual_steps:
                                logger.error(f"🔴 [ORCHESTRATOR] Task marked complete but provides MANUAL INSTALLATION STEPS!")
                                print(f"🔴 [ORCHESTRATOR] Task marked complete but provides MANUAL INSTALLATION STEPS!")
                                
                                self.messages.append({
                                    "role": "user",
                                    "content": f"""🚫 CRITICAL ERROR: You called task_complete with next_steps containing manual installation instructions. This is FORBIDDEN.

Your next_steps: {next_steps[:3]}

**YOU CANNOT PROVIDE MANUAL STEPS. YOU MUST EXECUTE COMMANDS YOURSELF.**

**REQUIRED ACTIONS:**
1. Delete any INSTALLATION_GUIDE.md or manual instruction files you created
2. Execute commands using terminal tool:
   - Call terminal tool with command="npm install"
   - Call terminal tool with command="npm run dev"
3. Only call task_complete AFTER commands succeed

**DO NOT provide next_steps telling the user to run commands. YOU must run them.**"""
                                })
                                
                                task_completed = False
                                logger.error(f"🔄 [ORCHESTRATOR] REJECTED: Manual steps provided")
                                print(f"🔄 [ORCHESTRATOR] REJECTED: Manual steps provided")
                                continue
                            
                            # Check 4: Dependencies installed but app not running
                            has_install_success = any(
                                ("npm install" in cmd or "pip install" in cmd) and cmd in successful_commands
                                for cmd in successful_commands
                            )
                            has_run_success = any(
                                ("npm run dev" in cmd or "npm start" in cmd or "uvicorn" in cmd or "flask run" in cmd) and cmd in successful_commands
                                for cmd in successful_commands
                            )
                            
                            if has_install_success and not has_run_success:
                                logger.warning(f"⚠️ [ORCHESTRATOR] Dependencies installed but application not launched")
                                print(f"⚠️ [ORCHESTRATOR] Dependencies installed but application not launched")
                                
                                self.messages.append({
                                    "role": "user",
                                    "content": """⚠️ WARNING: Dependencies were installed successfully, but the application has not been launched.

You MUST launch the application before calling task_complete:
- For React/Node: npm run dev or npm start
- For Python: uvicorn main:app --reload or flask run

Please launch the application now, then call task_complete."""
                                })
                                
                                task_completed = False
                                logger.info(f"🔄 [ORCHESTRATOR] REJECTED: App not launched")
                                print(f"🔄 [ORCHESTRATOR] REJECTED: App not launched")
                                continue
                        
                        task_completed = True
                        completion_report = result
                        logger.info(f"Task completed: {result.get('status')}")
                        
                        await self._emit_event(
                            "task_complete",
                            "agent",
                            "user",
                            result,
                            {"iteration": iterations}
                        )
                    
                    # Store in state
                    self.state_manager.add_tool_result(
                        tool_call.name, tool_call.arguments, result
                    )
                    
                    # Check if terminal command failed and try to heal
                    if tool_call.name == "terminal" and not result.get("success"):
                        await self._emit_event(
                            "error_detected",
                            "agent",
                            "self_healing",
                            {
                                "error": result.get("error"),
                                "command": tool_call.arguments.get("command")
                            },
                            {"iteration": iterations}
                        )
                        
                        healed_result = await self._try_heal_error(result, tool_call.arguments)
                        if healed_result:
                            result = healed_result
                            
                            await self._emit_event(
                                "self_healing_success",
                                "self_healing",
                                "agent",
                                {"healed_result": healed_result},
                                {"iteration": iterations}
                            )

                    # Format tool result for LLM - especially important for terminal results
                    if tool_call.name == "terminal":
                        # For terminal results, format explicitly so LLM sees ALL output
                        success = result.get("success", False)
                        stdout = result.get("stdout", "")
                        stderr = result.get("stderr", "")
                        exit_code = result.get("exit_code", -1)
                        error = result.get("error", "")
                        command = result.get("command", "")
                        
                        # CRITICAL: If command failed but error is empty, generate error message
                        # AND update the result dict itself so frontend receives it
                        if not success and (not error or error.strip() == ""):
                            logger.error(f"🔴 [ORCHESTRATOR] Command failed but error is empty! Exit code: {exit_code}")
                            print(f"[ERROR] [ORCHESTRATOR] Command failed but error is empty! Exit code: {exit_code}")
                            # Generate error message based on exit code
                            if exit_code == 1 or exit_code == 9009 or exit_code == -1:
                                error = f"Command not found or failed to execute: '{command}'. Exit code: {exit_code}. The program may not be installed or not in PATH."
                                if "npm" in command.lower() or "node" in command.lower():
                                    error += " Node.js/npm may not be installed. Please install Node.js from https://nodejs.org/"
                            elif exit_code == 2:
                                error = f"Command syntax error or file not found: '{command}'. Exit code: {exit_code}"
                            else:
                                error = f"Command '{command}' failed with exit code {exit_code}. STDOUT: {stdout[:200] if stdout else '(empty)'}, STDERR: {stderr[:200] if stderr else '(empty)'}"
                            
                            # CRITICAL: Update the result dict itself, not just the local variable
                            result["error"] = error
                            logger.info(f"🔴 [ORCHESTRATOR] Updated result['error'] with generated message: {error[:200]}")
                            print(f"[ERROR] [ORCHESTRATOR] Updated result['error'] with generated message: {error[:200]}")
                        
                        # Create a detailed, explicit message for the LLM
                        # CRITICAL: Include ALL output, but summarize very long outputs
                        # For npm install and similar commands, we need to see success/failure clearly
                        stdout_preview = stdout if len(stdout) < 2000 else stdout[:2000] + f"\n... (truncated, total {len(stdout)} chars)"
                        stderr_preview = stderr if len(stderr) < 2000 else stderr[:2000] + f"\n... (truncated, total {len(stderr)} chars)"
                        
                        if success:
                            # For successful commands, show summary + key output
                            formatted_result = (
                                f"✅ Command executed SUCCESSFULLY:\n"
                                f"Command: {command}\n"
                                f"Exit Code: {exit_code}\n"
                                f"Working Directory: {result.get('cwd', 'unknown')}\n"
                                f"STDOUT ({len(stdout)} chars):\n{stdout_preview if stdout.strip() else '(no output)'}\n"
                                f"{f'STDERR ({len(stderr)} chars):\n{stderr_preview}' if stderr.strip() else ''}"
                            )
                            # CRITICAL: Add explicit next-step instructions for the LLM
                            if "npm install" in command.lower():
                                formatted_result += (
                                    "\n\n"
                                    "✅ npm install completed successfully!\n"
                                    "**NEXT STEP REQUIRED**: You MUST run the next command to start the application.\n"
                                    "For React/Vite projects: Use terminal tool with command='npm run dev' (cwd='todo-list')\n"
                                    "For Express projects: Use terminal tool with command='npm start' (cwd='todo-list')\n"
                                    "Do NOT call task_complete yet - you must start the application first!"
                                )
                            elif "npm run dev" in command.lower() or "npm start" in command.lower():
                                formatted_result += (
                                    "\n\n"
                                    "✅ Development server is running!\n"
                                    "The application should be available at the URL shown in the output above.\n"
                                    "Now you can call task_complete to signal that the application is running."
                                )
                        else:
                            formatted_result = (
                                f"❌ Command FAILED:\n"
                                f"Command: {command}\n"
                                f"Exit Code: {exit_code}\n"
                                f"Working Directory: {result.get('cwd', 'unknown')}\n"
                                f"Error: {error}\n"
                                f"STDOUT ({len(stdout)} chars):\n{stdout_preview if stdout.strip() else '(no output)'}\n"
                                f"STDERR ({len(stderr)} chars):\n{stderr_preview if stderr.strip() else '(no output)'}\n\n"
                                f"You need to fix this error before proceeding."
                            )
                        
                        logger.info(f"📤 [ORCHESTRATOR] Sending terminal result to LLM (stdout: {len(stdout)} chars, stderr: {len(stderr)} chars)")
                        print(f"[DEBUG] [ORCHESTRATOR] Sending terminal result to LLM (stdout: {len(stdout)} chars, stderr: {len(stderr)} chars)")
                        logger.info(f"📤 [ORCHESTRATOR] Formatted result preview: {formatted_result[:500]}")
                        print(f"[DEBUG] [ORCHESTRATOR] Formatted result preview: {formatted_result[:500]}")
                    else:
                        # For other tools, use JSON format
                        formatted_result = json.dumps(result)
                    
                    # Add tool result to conversation
                    tool_message = {
                        "role": "tool",
                        "content": formatted_result,
                        "tool_call_id": tool_call.id,
                        "name": tool_call.name,
                    }

                    # For anthropic compatibility
                    if self.llm.provider.value == "anthropic":
                        # Anthropic handles tool results differently
                        if tool_call.name == "terminal":
                            # Use the formatted result for terminal
                            self.messages.append(
                                {
                                    "role": "user",
                                    "content": f"Tool 'terminal' result:\n{formatted_result}",
                                }
                            )
                        else:
                            self.messages.append(
                                {
                                    "role": "user",
                                    "content": f"Tool '{tool_call.name}' result: {json.dumps(result)}",
                                }
                            )
                    else:
                        self.messages.append(tool_message)

                    logger.debug(f"Tool {tool_call.name} result: {result}")
                    logger.info(f"📤 [ORCHESTRATOR] Added tool result to conversation. Total messages: {len(self.messages)}")
                    print(f"[DEBUG] [ORCHESTRATOR] Added tool result to conversation. Total messages: {len(self.messages)}")
                
                # Create checkpoint after each iteration
                self.state_manager.create_checkpoint(iterations, {
                    'tool_calls': len(response.tool_calls),
                    'batches': len(batches)
                })

                # CRITICAL: Log that we're continuing to next iteration
                logger.info(f"🔄 [ORCHESTRATOR] Completed iteration {iterations}. Total messages: {len(self.messages)}. LLM will see all tool results and decide next action.")
                print(f"[INFO] [ORCHESTRATOR] ════════════════════════════════════════════════════")
                print(f"[INFO] [ORCHESTRATOR] Completed iteration {iterations}")
                print(f"[INFO] [ORCHESTRATOR] Total messages in conversation: {len(self.messages)}")
                print(f"[INFO] [ORCHESTRATOR] Continuing to next iteration - LLM will be called again...")
                print(f"[INFO] [ORCHESTRATOR] ════════════════════════════════════════════════════")
                
                # Check if we should continue
                if iterations >= max_iterations:
                    logger.warning("Reached maximum iterations")
                    break
                
                # Continue to next iteration - the while loop will continue automatically
                # LLM will see all tool results and decide next action
                # The loop will automatically go to the next iteration and call llm.chat() again

            logger.info(f"Agent completed in {iterations} iterations")
            
            # Save final state
            self.state_manager.save_session()
            
            # Display session summary
            self._display_summary(iterations)

            return {
                "success": True,
                "completed": task_completed,
                "completion_report": completion_report,
                "response": final_response,
                "iterations": iterations,
                "messages": self.messages,
                "session_id": self.state_manager.session_id,
                "tool_stats": self.state_manager.get_tool_usage_stats()
            }

        except Exception as e:
            logger.error(f"🔴 [ORCHESTRATOR] Agent execution error: {e}", exc_info=True)
            print(f"🔴 [ORCHESTRATOR] Agent execution error: {e}")
            import traceback
            print(f"🔴 [ORCHESTRATOR] Full traceback:")
            traceback.print_exc()
            return {
                "success": False,
                "completed": None,
                "completion_report": None,
                "error": str(e),
                "error_type": type(e).__name__,
                "response": final_response,
                "iterations": iterations,
                "session_id": self.state_manager.session_id if hasattr(self, 'state_manager') else None,
            }

    async def chat(self, user_message: str) -> str:
        """
        Continue conversation with the agent
        
        Args:
            user_message: User's message
            
        Returns:
            Agent's response
        """
        self.messages.append({"role": "user", "content": user_message})

        response = self.llm.chat(
            messages=self.messages,
            tools=self.tool_registry.to_openai_tools(),
        )

        if response.content:
            self.messages.append({"role": "assistant", "content": response.content})
            return response.content

        return ""

    def reset(self):
        """Reset conversation history"""
        self.messages = []
        logger.info("Agent conversation reset")

    async def _try_heal_error(
        self, failed_result: Dict[str, Any], command_args: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Try to heal an error from a failed command
        
        Args:
            failed_result: The failed command result
            command_args: Arguments that were passed to the command
            
        Returns:
            Healed result if successful, None otherwise
        """
        max_heal_attempts = self.config.max_retries

        # Detect error
        error = self.error_detector.detect(
            stdout=failed_result.get("stdout", ""),
            stderr=failed_result.get("stderr", ""),
            exit_code=failed_result.get("exit_code", 1),
            command=command_args.get("command"),
        )

        if not error:
            logger.warning("Failed to detect specific error")
            return None

        logger.info(f"Detected error: {error.error_type} - {error.message}")

        # Check if fixable
        if not ErrorClassifier.is_fixable(error):
            logger.warning("Error is not automatically fixable")
            return None

        # Get fix suggestion
        fix = self.error_fixer.suggest_fix(error)
        if not fix:
            logger.warning("No fix suggestion available")
            return None

        logger.info(f"Attempting fix: {fix.description}")

        # Apply fix
        for attempt in range(max_heal_attempts):
            logger.info(f"Heal attempt {attempt + 1}/{max_heal_attempts}")

            if fix.command:
                # Execute fix command
                terminal_tool = self.tool_registry.get("terminal")
                if terminal_tool:
                    fix_result = await terminal_tool.execute(
                        command=fix.command,
                        cwd=command_args.get("cwd"),
                        timeout=command_args.get("timeout", 60),
                    )

                    if fix_result.get("success"):
                        logger.info("Fix command executed successfully")

                        # Retry original command
                        retry_result = await terminal_tool.execute(**command_args)

                        if retry_result.get("success"):
                            logger.info("✓ Self-healing successful!")
                            self.error_fixer.track_fix(error, fix, True)
                            return retry_result
                        else:
                            logger.warning(f"Retry failed, attempt {attempt + 1}")
                    else:
                        logger.warning("Fix command failed")

            # If we get here, healing didn't work this attempt
            await asyncio.sleep(2 ** attempt)  # Exponential backoff

        # All attempts failed
        logger.error("Self-healing failed after all attempts")
        self.error_fixer.track_fix(error, fix, False)
        return None
    
    def _display_summary(self, iterations: int):
        """Display execution summary.
        
        Args:
            iterations: Number of iterations completed
        """
        table = Table(title="🎯 Execution Summary", show_header=True)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        # Get tool stats
        tool_stats = self.state_manager.get_tool_usage_stats()
        
        table.add_row("Iterations", str(iterations))
        table.add_row("Messages", str(len(self.messages)))
        table.add_row("Tool Calls", str(len(self.state_manager.tool_history)))
        table.add_row("Checkpoints", str(len(self.state_manager.checkpoints)))
        table.add_row("Session ID", self.state_manager.session_id)
        
        self.console.print()
        self.console.print(table)
        
        # Tool usage breakdown
        if tool_stats:
            tool_table = Table(title="🔧 Tool Usage", show_header=True)
            tool_table.add_column("Tool", style="yellow")
            tool_table.add_column("Calls", justify="right", style="cyan")
            
            for tool_name, count in sorted(tool_stats.items(), key=lambda x: x[1], reverse=True):
                tool_table.add_row(tool_name, str(count))
            
            self.console.print()
            self.console.print(tool_table)
