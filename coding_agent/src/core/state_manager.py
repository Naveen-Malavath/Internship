"""State management and conversation memory."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

from loguru import logger


@dataclass
class Checkpoint:
    """Represents a conversation checkpoint."""
    id: str
    timestamp: str
    iteration: int
    messages: List[Dict[str, str]]
    tool_results: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class StateManager:
    """Manages conversation state, checkpoints, and memory."""
    
    def __init__(self, workspace_path: Path, session_id: Optional[str] = None):
        """Initialize state manager.
        
        Args:
            workspace_path: Workspace directory
            session_id: Optional session identifier
        """
        self.workspace_path = Path(workspace_path)
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # State directory
        self.state_dir = self.workspace_path / ".agent_cache" / "sessions"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_file = self.state_dir / f"{self.session_id}.json"
        
        # Current state
        self.messages: List[Dict[str, str]] = []
        self.tool_history: List[Dict[str, Any]] = []
        self.checkpoints: List[Checkpoint] = []
        self.metadata: Dict[str, Any] = {
            'session_id': self.session_id,
            'started_at': datetime.now().isoformat(),
            'workspace': str(workspace_path)
        }
        
        logger.info(f"Initialized StateManager for session: {self.session_id}")
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history.
        
        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
        """
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    
    def add_tool_result(self, tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any]):
        """Add tool execution to history.
        
        Args:
            tool_name: Name of tool
            parameters: Tool parameters
            result: Tool result
        """
        self.tool_history.append({
            'tool': tool_name,
            'parameters': parameters,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
    
    def create_checkpoint(self, iteration: int, metadata: Optional[Dict[str, Any]] = None) -> Checkpoint:
        """Create a checkpoint of current state.
        
        Args:
            iteration: Current iteration number
            metadata: Optional checkpoint metadata
            
        Returns:
            Checkpoint object
        """
        checkpoint = Checkpoint(
            id=f"checkpoint_{len(self.checkpoints) + 1}",
            timestamp=datetime.now().isoformat(),
            iteration=iteration,
            messages=self.messages.copy(),
            tool_results=self.tool_history[-10:],  # Last 10 tool results
            metadata=metadata or {}
        )
        
        self.checkpoints.append(checkpoint)
        logger.debug(f"Created checkpoint {checkpoint.id} at iteration {iteration}")
        
        return checkpoint
    
    def save_session(self):
        """Save current session state to disk."""
        try:
            state = {
                'metadata': self.metadata,
                'messages': self.messages,
                'tool_history': self.tool_history,
                'checkpoints': [cp.to_dict() for cp in self.checkpoints]
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.debug(f"Saved session state to {self.session_file}")
        
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def load_session(self, session_id: str) -> bool:
        """Load a previous session.
        
        Args:
            session_id: Session ID to load
            
        Returns:
            True if session loaded successfully
        """
        try:
            session_file = self.state_dir / f"{session_id}.json"
            
            if not session_file.exists():
                logger.warning(f"Session not found: {session_id}")
                return False
            
            with open(session_file, 'r') as f:
                state = json.load(f)
            
            self.metadata = state.get('metadata', {})
            self.messages = state.get('messages', [])
            self.tool_history = state.get('tool_history', [])
            
            # Load checkpoints
            self.checkpoints = []
            for cp_data in state.get('checkpoints', []):
                checkpoint = Checkpoint(**cp_data)
                self.checkpoints.append(checkpoint)
            
            logger.info(f"Loaded session {session_id}: {len(self.messages)} messages, {len(self.checkpoints)} checkpoints")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation.
        
        Returns:
            Summary string
        """
        user_messages = sum(1 for m in self.messages if m['role'] == 'user')
        assistant_messages = sum(1 for m in self.messages if m['role'] == 'assistant')
        tools_used = len(self.tool_history)
        
        return f"Session {self.session_id}: {user_messages} user messages, {assistant_messages} assistant responses, {tools_used} tool calls"
    
    def get_recent_context(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation context.
        
        Args:
            max_messages: Maximum number of messages to return
            
        Returns:
            List of recent messages
        """
        return self.messages[-max_messages:]
    
    def get_tool_usage_stats(self) -> Dict[str, int]:
        """Get statistics on tool usage.
        
        Returns:
            Dictionary of tool names and usage counts
        """
        stats = {}
        for tool_call in self.tool_history:
            tool_name = tool_call.get('tool', 'unknown')
            stats[tool_name] = stats.get(tool_name, 0) + 1
        return stats
    
    def list_sessions(self) -> List[str]:
        """List all available sessions.
        
        Returns:
            List of session IDs
        """
        if not self.state_dir.exists():
            return []
        
        sessions = []
        for file in self.state_dir.glob("*.json"):
            sessions.append(file.stem)
        
        return sorted(sessions)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            session_file = self.state_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
                logger.info(f"Deleted session: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False
