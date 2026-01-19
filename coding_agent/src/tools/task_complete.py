"""
Task Completion Tool

Allows the LLM to explicitly signal when a task is complete.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from src.tools.base import Tool, ToolParameter
from loguru import logger


class TaskCompleteTool(Tool):
    """Tool for signaling task completion."""
    
    name = "task_complete"
    description = """
    Signal that the task is complete. Call this tool when you have:
    1. Created all necessary files
    2. Run all required commands
    3. Fixed any errors that occurred
    4. Verified the output works as expected
    
    Parameters:
    - status: "success" or "partial" or "failed"
    - summary: Brief summary of what was accomplished
    - files_created: List of files created
    - commands_run: List of commands executed
    - next_steps: Optional steps the user should take (e.g., "Run 'npm install'")
    - issues: Optional list of issues encountered
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
            description="Optional next steps for the user (e.g., ['Run npm install', 'Start the server'])",
            required=False
        ),
        ToolParameter(
            name="issues",
            type="array",
            description="Optional list of issues encountered during the task",
            required=False
        )
    ]
    
    def __init__(self, workspace_path: Optional[Path] = None):
        """Initialize task complete tool.
        
        Args:
            workspace_path: Optional workspace path (not used, but kept for consistency with other tools)
        """
        self.workspace_path = workspace_path
    
    async def execute(
        self,
        status: str,
        summary: str,
        files_created: Optional[list] = None,
        commands_run: Optional[list] = None,
        next_steps: Optional[list] = None,
        issues: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Signal task completion.
        
        Args:
            status: Completion status (success/partial/failed)
            summary: Summary of accomplishments
            files_created: Files created during task
            commands_run: Commands executed
            next_steps: Steps user should take
            issues: Issues encountered
            
        Returns:
            Completion report
        """
        logger.info(f"Task completion signaled: {status}")
        
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
