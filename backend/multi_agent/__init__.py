"""Multi-Agent Code Generation System

This module provides a multi-agent architecture for generating full-stack applications.
Migrated from the coding_agent project.
"""

from .orchestrator import CodingAgent
from .tools.base import Tool, ToolRegistry, ToolParameter
from .tools.file_ops import FileOperationsTool
from .tools.terminal import TerminalTool

__all__ = [
    "CodingAgent",
    "Tool",
    "ToolRegistry", 
    "ToolParameter",
    "FileOperationsTool",
    "TerminalTool",
]
