"""File operations tool for creating, reading, updating, and deleting files
With production-ready CSS validation"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from loguru import logger

from .base import Tool, ToolParameter


# Minimum CSS requirements for production quality
MIN_CSS_LENGTH = 300  # Minimum characters for CSS files
MIN_CSS_VARIABLES = 5  # Minimum number of CSS variables


class CSSQualityChecker:
    """Lightweight CSS quality checker for file operations"""
    
    @staticmethod
    def check(content: str, file_path: str) -> Dict[str, Any]:
        """Check CSS content quality"""
        warnings = []
        
        # Check length
        if len(content) < MIN_CSS_LENGTH:
            warnings.append(
                f"CSS file is too short ({len(content)} chars). "
                f"Production CSS should be at least {MIN_CSS_LENGTH} chars with proper styling."
            )
        
        # Check for CSS variables
        if ":root" not in content:
            warnings.append(
                "Missing :root block with CSS variables. "
                "Add design tokens for colors, spacing, and typography."
            )
        
        # Check for reset styles
        if "box-sizing: border-box" not in content:
            warnings.append(
                "Missing box-sizing reset. Add '*, *::before, *::after { box-sizing: border-box; }'"
            )
        
        # Check for transitions
        if "transition" not in content:
            warnings.append(
                "No CSS transitions found. Add smooth transitions for hover states."
            )
        
        # Check for hover states
        if ":hover" not in content:
            warnings.append(
                "No :hover states found. Interactive elements need hover styling."
            )
        
        return {
            "passed": len(warnings) == 0,
            "warnings": warnings,
            "length": len(content),
            "has_variables": ":root" in content,
            "has_transitions": "transition" in content,
            "has_hover": ":hover" in content,
        }


class FileOperationsTool(Tool):
    """Tool for file system operations with quality validation"""

    name = "file_operations"
    description = "Create, read, update, delete, and list files and directories. CSS files are validated for production quality."
    parameters = [
        ToolParameter(
            name="operation",
            type="string",
            description="Operation to perform: create, read, update, delete, list",
            required=True,
            enum=["create", "read", "update", "delete", "list"],
        ),
        ToolParameter(
            name="path",
            type="string",
            description="File or directory path",
            required=True,
        ),
        ToolParameter(
            name="content",
            type="string",
            description="File content for create/update operations. For CSS files, include proper styling with variables and transitions.",
            required=False,
        ),
        ToolParameter(
            name="start_line",
            type="number",
            description="Starting line for read operation (1-indexed)",
            required=False,
        ),
        ToolParameter(
            name="end_line",
            type="number",
            description="Ending line for read operation (1-indexed, inclusive)",
            required=False,
        ),
    ]

    def __init__(self, workspace_path: Optional[Path] = None):
        """
        Initialize file operations tool
        
        Args:
            workspace_path: Base workspace directory for operations
        """
        self.workspace_path = workspace_path or Path.cwd()
        self.css_checker = CSSQualityChecker()

    def _resolve_path(self, path: str) -> Path:
        """
        Resolve path relative to workspace
        
        Args:
            path: File path (can be relative or absolute)
            
        Returns:
            Resolved Path object
        """
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = self.workspace_path / path_obj
        return path_obj.resolve()

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute file operation"""
        operation = kwargs.get("operation")
        path = kwargs.get("path")

        if not operation or not path:
            return {
                "success": False,
                "error": "Missing required parameters: operation and path",
            }

        try:
            if operation == "create":
                return await self._create_file(path, kwargs.get("content", ""))
            elif operation == "read":
                return await self._read_file(
                    path, kwargs.get("start_line"), kwargs.get("end_line")
                )
            elif operation == "update":
                return await self._update_file(path, kwargs.get("content", ""))
            elif operation == "delete":
                return await self._delete_file(path)
            elif operation == "list":
                return await self._list_directory(path)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            logger.error(f"File operation error: {e}")
            return {"success": False, "error": str(e)}

    async def _create_file(self, path: str, content: str) -> Dict[str, Any]:
        """Create a new file with content, with CSS quality validation"""
        file_path = self._resolve_path(path)

        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if file_path.exists():
            return {
                "success": False,
                "error": f"File already exists: {file_path}",
            }

        # Validate CSS files for production quality
        css_check = None
        if path.endswith('.css'):
            css_check = self.css_checker.check(content, path)
            if not css_check["passed"]:
                logger.warning(f"CSS quality warnings for {path}: {css_check['warnings']}")

        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)

        logger.info(f"Created file: {file_path}")
        
        result = {
            "success": True,
            "result": f"File created: {file_path}",
            "path": str(file_path),
        }
        
        # Add CSS quality info if applicable
        if css_check:
            result["css_quality"] = css_check
            if not css_check["passed"]:
                result["css_warnings"] = css_check["warnings"]
                result["note"] = "CSS file was created but has quality warnings. Consider adding more comprehensive styling."
        
        return result

    async def _read_file(
        self, path: str, start_line: Optional[int] = None, end_line: Optional[int] = None
    ) -> Dict[str, Any]:
        """Read file content (optionally specific line range)"""
        file_path = self._resolve_path(path)

        if not file_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        if not file_path.is_file():
            return {"success": False, "error": f"Not a file: {file_path}"}

        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()

        # If line range specified, extract those lines
        if start_line is not None or end_line is not None:
            lines = content.splitlines()
            start_idx = (start_line - 1) if start_line else 0
            end_idx = end_line if end_line else len(lines)
            content = "\n".join(lines[start_idx:end_idx])

        logger.info(f"Read file: {file_path}")
        return {
            "success": True,
            "result": content,
            "path": str(file_path),
            "size": file_path.stat().st_size,
        }

    async def _update_file(self, path: str, content: str) -> Dict[str, Any]:
        """Update existing file content with CSS quality validation"""
        file_path = self._resolve_path(path)

        if not file_path.exists():
            # If file doesn't exist, create it instead
            return await self._create_file(path, content)

        # Validate CSS files for production quality
        css_check = None
        if path.endswith('.css'):
            css_check = self.css_checker.check(content, path)
            if not css_check["passed"]:
                logger.warning(f"CSS quality warnings for {path}: {css_check['warnings']}")

        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)

        logger.info(f"Updated file: {file_path}")
        
        result = {
            "success": True,
            "result": f"File updated: {file_path}",
            "path": str(file_path),
        }
        
        # Add CSS quality info if applicable
        if css_check:
            result["css_quality"] = css_check
            if not css_check["passed"]:
                result["css_warnings"] = css_check["warnings"]
                result["note"] = "CSS file was updated but has quality warnings. Consider adding more comprehensive styling."
        
        return result

    async def _delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file"""
        file_path = self._resolve_path(path)

        if not file_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        if file_path.is_file():
            file_path.unlink()
        elif file_path.is_dir():
            # Only delete empty directories
            try:
                file_path.rmdir()
            except OSError:
                return {
                    "success": False,
                    "error": f"Directory not empty: {file_path}",
                }

        logger.info(f"Deleted: {file_path}")
        return {"success": True, "result": f"Deleted: {file_path}", "path": str(file_path)}

    async def _list_directory(self, path: str) -> Dict[str, Any]:
        """List directory contents"""
        dir_path = self._resolve_path(path)

        if not dir_path.exists():
            return {"success": False, "error": f"Directory not found: {dir_path}"}

        if not dir_path.is_dir():
            return {"success": False, "error": f"Not a directory: {dir_path}"}

        items = []
        for item in dir_path.iterdir():
            items.append(
                {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                }
            )

        logger.info(f"Listed directory: {dir_path} ({len(items)} items)")
        return {
            "success": True,
            "result": items,
            "path": str(dir_path),
            "count": len(items),
        }
