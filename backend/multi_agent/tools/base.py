"""Base Tool class and registry for agent actions"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToolParameter(BaseModel):
    """Tool parameter definition"""

    name: str
    type: str  # 'string', 'number', 'boolean', 'object', 'array'
    description: str
    required: bool = True
    enum: Optional[List[str]] = None


class Tool(ABC):
    """
    Base class for all agent tools
    Tools are actions the agent can perform (create files, run commands, etc.)
    """

    name: str = "base_tool"
    description: str = "Base tool class"
    parameters: List[ToolParameter] = []

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Dict with 'success', 'result', and optional 'error' keys
        """
        pass

    def to_openai_tool(self) -> Dict[str, Any]:
        """
        Convert tool to OpenAI function calling format
        
        Returns:
            Dict in OpenAI tool format
        """
        properties = {}
        required = []

        logger.debug(f"[TOOL] Converting tool '{self.name}' to OpenAI format")
        
        for param in self.parameters:
            if not isinstance(param, ToolParameter):
                logger.error(f"[TOOL] Invalid parameter type: {type(param)}")
                continue
                
            properties[param.name] = {
                "type": param.type,
                "description": param.description or "",
            }
            if param.enum:
                properties[param.name]["enum"] = param.enum
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"


class ToolRegistry:
    """
    Registry for managing available tools
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        logger.debug("Initialized ToolRegistry")

    def register(self, tool: Tool) -> None:
        """Register a tool"""
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def unregister(self, tool_name: str) -> None:
        """Unregister a tool"""
        if tool_name in self._tools:
            del self._tools[tool_name]

    def get(self, tool_name: str) -> Optional[Tool]:
        """Get tool by name"""
        return self._tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())

    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self._tools.values())

    def to_openai_tools(self) -> List[Dict[str, Any]]:
        """Convert all tools to OpenAI function calling format"""
        return [tool.to_openai_tool() for tool in self._tools.values()]

    async def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name"""
        tool = self.get(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found in registry",
            }

        try:
            logger.info(f"Executing tool: {tool_name}")
            result = await tool.execute(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return {"success": False, "error": str(e)}

    def __len__(self) -> int:
        return len(self._tools)

    def __repr__(self) -> str:
        return f"<ToolRegistry: {len(self._tools)} tools>"
