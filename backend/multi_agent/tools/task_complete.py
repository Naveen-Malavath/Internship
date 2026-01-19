"""Task Completion Tool - Signals when a task is complete"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .base import Tool, ToolParameter

logger = logging.getLogger(__name__)


class TaskCompleteTool(Tool):
    """Tool for signaling task completion."""
    
    name = "task_complete"
    description = """
    Signal that the task is complete. Call this tool when you have:
    1. Created all necessary files
    2. Run all required commands  
    3. Fixed any errors that occurred
    4. Verified the output works as expected
    """
    
    parameters = [
        ToolParameter(
            name="status",
            type="string",
            description="Completion status: 'success' or 'partial' or 'failed'",
            required=True,
            enum=["success", "partial", "failed"]
        ),
        ToolParameter(
            name="summary",
            type="string",
            description="Brief summary of what was accomplished",
            required=True
        ),
        ToolParameter(
            name="files_created",
            type="array",
            description="List of files created during the task",
            required=False
        ),
        ToolParameter(
            name="commands_run",
            type="array",
            description="List of commands executed during the task",
            required=False
        ),
        ToolParameter(
            name="next_steps",
            type="array",
            description="Optional next steps for the user",
            required=False
        ),
        ToolParameter(
            name="issues",
            type="array",
            description="Optional list of issues encountered",
            required=False
        )
    ]
    
    def __init__(self, workspace_path: Optional[Path] = None):
        """Initialize task complete tool."""
        self.workspace_path = workspace_path
    
    async def execute(
        self,
        status: str = "success",
        summary: str = "",
        files_created: Optional[list] = None,
        commands_run: Optional[list] = None,
        next_steps: Optional[list] = None,
        issues: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Signal task completion."""
        logger.info(f"[TASK_COMPLETE] Task completion signaled: {status}")
        
        report = {
            "completed": True,
            "status": status,
            "summary": summary,
            "files_created": files_created or [],
            "commands_run": commands_run or [],
            "next_steps": next_steps or [],
            "issues": issues or []
        }
        
        return report
