"""Base Tool class and registry for agent actions"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, Field


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

        logger.debug(f"🛠️ [TOOL] Converting tool '{self.name}' to OpenAI format. Parameters count: {len(self.parameters)}")
        print(f"🛠️ [TOOL] Converting tool '{self.name}' to OpenAI format. Parameters count: {len(self.parameters)}")
        
        for i, param in enumerate(self.parameters):
            logger.debug(f"🛠️ [TOOL] Processing parameter #{i} for tool '{self.name}'. Type: {type(param)}")
            print(f"🛠️ [TOOL] Processing parameter #{i} for tool '{self.name}'. Type: {type(param)}, Value: {repr(param)[:100]}")
            
            # Check if param is a ToolParameter object
            if not isinstance(param, ToolParameter):
                logger.error(f"🔴 [TOOL] ERROR: Tool '{self.name}' has invalid parameter at index {i}. Expected ToolParameter, got {type(param)}. Value: {repr(param)}")
                print(f"🔴 [TOOL] ERROR: Tool '{self.name}' has invalid parameter at index {i}. Expected ToolParameter, got {type(param)}")
                print(f"🔴 [TOOL] Parameter value: {repr(param)}")
                
                # If it's a string, try to convert it or skip it
                if isinstance(param, str):
                    logger.warning(f"⚠️ [TOOL] Parameter at index {i} is a string: {param}. Skipping...")
                    print(f"⚠️ [TOOL] Parameter at index {i} is a string: {param}. Skipping...")
                    continue
                else:
                    # For other types, raise an error with more context
                    raise TypeError(
                        f"Tool '{self.name}' has invalid parameter at index {i}. "
                        f"Expected ToolParameter object, got {type(param).__name__}: {repr(param)[:100]}"
                    )
            
            # Now safely access param attributes
            param_name = getattr(param, 'name', None)
            param_type = getattr(param, 'type', None)
            param_description = getattr(param, 'description', None)
            param_required = getattr(param, 'required', True)
            param_enum = getattr(param, 'enum', None)
            
            if param_name is None:
                logger.error(f"🔴 [TOOL] Tool '{self.name}' parameter at index {i} missing 'name' attribute")
                print(f"🔴 [TOOL] Tool '{self.name}' parameter at index {i} missing 'name' attribute")
                continue
                
            logger.debug(f"🛠️ [TOOL] Adding parameter '{param_name}' (type: {param_type}) to tool '{self.name}'")
            print(f"🛠️ [TOOL] Adding parameter '{param_name}' (type: {param_type}) to tool '{self.name}'")
            
            properties[param_name] = {
                "type": param_type,
                "description": param_description or "",
            }
            if param_enum:
                properties[param_name]["enum"] = param_enum
            if param_required:
                required.append(param_name)

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
    Allows dynamic registration and discovery of tools
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        logger.debug("Initialized ToolRegistry")

    def register(self, tool: Tool) -> None:
        """
        Register a tool
        
        Args:
            tool: Tool instance to register
        """
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def unregister(self, tool_name: str) -> None:
        """
        Unregister a tool
        
        Args:
            tool_name: Name of tool to remove
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.debug(f"Unregistered tool: {tool_name}")

    def get(self, tool_name: str) -> Optional[Tool]:
        """
        Get tool by name
        
        Args:
            tool_name: Name of tool
            
        Returns:
            Tool instance or None
        """
        return self._tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """
        List all registered tool names
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def get_all_tools(self) -> List[Tool]:
        """
        Get all registered tools
        
        Returns:
            List of Tool instances
        """
        return list(self._tools.values())

    def to_openai_tools(self) -> List[Dict[str, Any]]:
        """
        Convert all tools to OpenAI function calling format
        
        Returns:
            List of tool definitions
        """
        return [tool.to_openai_tool() for tool in self._tools.values()]

    async def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name
        
        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        tool = self.get(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found in registry",
            }

        try:
            logger.info(f"Executing tool: {tool_name}")
            result = await tool.execute(**kwargs)
            logger.debug(f"Tool {tool_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return {"success": False, "error": str(e)}

    def __len__(self) -> int:
        return len(self._tools)

    def __repr__(self) -> str:
        return f"<ToolRegistry: {len(self._tools)} tools>"
