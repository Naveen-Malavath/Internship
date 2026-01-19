"""
FastAPI Web Server for AI Coding Agent
Streams all agent interactions in real-time via WebSocket
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from uuid import uuid4
import sys
import platform

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi import Request as FastAPIRequest
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

from ..core.orchestrator import CodingAgent

# CRITICAL: Set Windows event loop policy for subprocess support
# This must be done BEFORE any asyncio operations
if sys.platform == "win32":
    try:
        # Use ProactorEventLoopPolicy on Windows for proper subprocess support
        if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
            policy = asyncio.WindowsProactorEventLoopPolicy()
            asyncio.set_event_loop_policy(policy)
            logger.info("✅ Set WindowsProactorEventLoopPolicy for subprocess support")
        else:
            # Fallback for older Python versions
            logger.warning("⚠️ WindowsProactorEventLoopPolicy not available, using default policy")
    except Exception as e:
        logger.warning(f"⚠️ Could not set Windows event loop policy: {e}")
        # Continue anyway - the terminal tool has a fallback mechanism

# Configure console logging for debugging
# On Windows, use stderr with UTF-8 encoding to handle Unicode properly
import io
if sys.platform == "win32":
    # Configure stdout to use UTF-8 on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except:
            pass
    
logger.remove()
# Use stderr on Windows to avoid encoding issues, stdout otherwise
log_stream = sys.stderr if sys.platform == "win32" else sys.stdout
logger.add(log_stream, level="DEBUG", colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", enqueue=True)

app = FastAPI(title="AI Coding Agent Web UI")

# Debug logging middleware
class DebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        origin = request.headers.get("origin", "NO ORIGIN")
        method = request.method
        path = request.url.path
        logger.debug(f"REQUEST: {method} {path} | Origin: {origin}")
        logger.debug(f"Headers: {dict(request.headers)}")
        
        response = await call_next(request)
        
        cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
        logger.debug(f"RESPONSE: {response.status_code} | CORS Headers: {cors_headers}")
        logger.debug(f"All Response Headers: {dict(response.headers)}")
        
        return response

# Configure CORS - MUST be added FIRST (executes LAST in reverse order)
logger.info("Configuring CORS middleware...")
logger.info("   allow_origins: ['http://localhost:5173', 'http://127.0.0.1:5173']")
logger.info("   allow_credentials: True")
logger.info("   allow_methods: ['*']")
logger.info("   allow_headers: ['*']")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add debug middleware AFTER CORS (executes FIRST)
app.add_middleware(DebugMiddleware)

logger.info("CORS middleware configured!")


class RunRequest(BaseModel):
    """Request to run the agent"""
    prompt: str
    max_iterations: int = 150
    workspace_path: Optional[str] = None
    client_id: Optional[str] = None  # WebSocket client ID


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
    
    async def send_event(self, client_id: str, event: Dict[str, Any]):
        """Send event to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(event)
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
                self.disconnect(client_id)


manager = ConnectionManager()


def create_event(
    event_type: str,
    source: str,
    target: str,
    data: Any,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """Create a standardized event"""
    return {
        "type": event_type,
        "source": source,
        "target": target,
        "data": data,
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root(http_request: FastAPIRequest):
    """Health check"""
    origin = http_request.headers.get("origin", "NO ORIGIN")
    logger.info(f"🏥 Health check - Origin: {origin}")
    return {"status": "ok", "service": "AI Coding Agent Web UI"}


@app.options("/api/run")
async def options_run(request: FastAPIRequest):
    """Handle OPTIONS preflight request"""
    origin = request.headers.get("origin", "NO ORIGIN")
    logger.info(f"🔍 OPTIONS preflight request for /api/run - Origin: {origin}")
    return JSONResponse(
        content={"status": "ok"},
        headers={
            "Access-Control-Allow-Origin": origin if origin in ["http://localhost:5173", "http://127.0.0.1:5173"] else "http://localhost:5173",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Credentials": "true",
        }
    )


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time event streaming"""
    origin = websocket.headers.get("origin", "NO ORIGIN")
    logger.info(f"🔌 WebSocket connection attempt - Client: {client_id}, Origin: {origin}")
    logger.debug(f"   WebSocket headers: {dict(websocket.headers)}")
    try:
        await manager.connect(client_id, websocket)
        logger.info(f"WebSocket connected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket connection failed: {e}")
        raise
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(client_id)


@app.post("/api/run")
async def run_agent(request: RunRequest, http_request: FastAPIRequest):
    """
    Run the agent and stream all interactions via WebSocket
    """
    origin = http_request.headers.get("origin", "NO ORIGIN")
    logger.info(f"POST /api/run - Origin: {origin}")
    logger.debug(f"   Request body: {request.dict()}")
    
    client_id = request.client_id or str(uuid4())
    
    # Validate workspace path
    try:
        if request.workspace_path:
            workspace_path = Path(request.workspace_path).resolve()
            # Ensure the path exists and is a directory
            if not workspace_path.exists():
                raise HTTPException(status_code=400, detail=f"Workspace path does not exist: {workspace_path}")
            if not workspace_path.is_dir():
                raise HTTPException(status_code=400, detail=f"Workspace path is not a directory: {workspace_path}")
        else:
            workspace_path = Path.cwd().resolve()
    except (OSError, ValueError) as e:
        logger.error(f"Invalid workspace path: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid workspace path: {str(e)}")
    
    # Send initial event
    await manager.send_event(
        client_id,
        create_event(
            "session_start",
            "system",
            "ui",
            {
                "client_id": client_id,
                "prompt": request.prompt,
                "max_iterations": request.max_iterations,
                "workspace": str(workspace_path)
            }
        )
    )
    
    # Create event callback for orchestrator
    async def event_callback(event: Dict[str, Any]):
        """Callback to stream events from agent"""
        await manager.send_event(client_id, event)
    
    try:
        # Initialize agent
        agent = CodingAgent(workspace_path=workspace_path)
        # Set event callback (this will also update the terminal tool)
        agent.set_event_callback(event_callback)
        
        # Send user message event
        await event_callback(
            create_event(
                "user_message",
                "user",
                "agent",
                {"message": request.prompt},
                {"iteration": 0}
            )
        )
        
        # Run agent
        result = await agent.run(
            user_prompt=request.prompt,
            max_iterations=request.max_iterations
        )
        
        # Send completion event
        completion_data = {
            "success": result.get("success"),
            "completed": result.get("completed"),
            "completion_report": result.get("completion_report"),
            "iterations": result.get("iterations"),
            "session_id": result.get("session_id")
        }
        
        # Include error if present
        if not result.get("success") and result.get("error"):
            completion_data["error"] = result.get("error")
            completion_data["error_type"] = result.get("error_type")
            # Also send a separate error event
            await event_callback(
                create_event(
                    "error",
                    "agent",
                    "user",
                    {
                        "error": result.get("error"),
                        "error_type": result.get("error_type"),
                        "type": "execution_error"
                    }
                )
            )
        
        await event_callback(
            create_event(
                "session_complete",
                "agent",
                "user",
                completion_data
            )
        )
        
        return {
            "success": True,
            "client_id": client_id,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=True)
        
        # Send error event with full details
        error_detail = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": str(e.__traceback__) if hasattr(e, '__traceback__') else None
        }
        await manager.send_event(
            client_id,
            create_event(
                "error",
                "system",
                "user",
                error_detail
            )
        )
        
        # Return error in response instead of raising
        return {
            "success": False,
            "client_id": client_id,
            "error": str(e),
            "error_type": type(e).__name__,
            "result": {
                "success": False,
                "completed": None,
                "completion_report": None,
                "iterations": 0,
                "error": str(e)
            }
        }


@app.get("/api/sessions")
async def list_sessions():
    """List all saved sessions"""
    try:
        cache_dir = Path.cwd().resolve() / ".agent_cache" / "sessions"
        
        if not cache_dir.exists():
            return {"sessions": []}
        
        sessions = []
        for session_file in cache_dir.glob("*.json"):
            try:
                # Use explicit encoding and error handling for Windows
                with open(session_file, 'r', encoding='utf-8', errors='replace') as f:
                    session_data = json.load(f)
                    sessions.append({
                        "session_id": session_data.get("session_id"),
                        "created_at": session_data.get("created_at"),
                        "iterations": session_data.get("iterations"),
                        "tool_calls": len(session_data.get("tool_history", []))
                    })
            except (OSError, IOError, json.JSONDecodeError) as e:
                logger.error(f"Error reading session {session_file}: {e}")
                continue
        
        return {"sessions": sorted(sessions, key=lambda x: x.get("created_at", ""), reverse=True)}
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return {"sessions": [], "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
