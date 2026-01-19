"""Database of common error patterns and their fixes"""

from typing import Dict, List, Optional

from pydantic import BaseModel


class ErrorPattern(BaseModel):
    """Represents a known error pattern and its fix"""

    pattern: str  # Error message pattern
    category: str  # 'dependency', 'syntax', 'runtime', 'config'
    fix_command: Optional[str] = None  # Shell command to fix
    fix_description: str = ""  # Human-readable fix description
    code_fix: Optional[str] = None  # Code change to apply
    confidence: float = 1.0  # How confident we are in this fix (0-1)


# Common error patterns with fixes
ERROR_PATTERNS: Dict[str, ErrorPattern] = {
    # Python - Missing modules
    "python_missing_module_pip": ErrorPattern(
        pattern=r"ModuleNotFoundError: No module named '(.+)'",
        category="dependency",
        fix_command="pip install {module}",
        fix_description="Install the missing Python package using pip",
        confidence=0.95,
    ),
    # JavaScript - Missing modules
    "js_missing_module_npm": ErrorPattern(
        pattern=r"Error: Cannot find module '(.+)'",
        category="dependency",
        fix_command="npm install {module}",
        fix_description="Install the missing Node.js package using npm",
        confidence=0.95,
    ),
    # Port already in use
    "port_in_use": ErrorPattern(
        pattern=r"EADDRINUSE.*:(\d+)",
        category="runtime",
        fix_command="lsof -ti:{port} | xargs kill -9",  # Unix/Mac
        fix_description="Kill the process using the port, or use a different port",
        confidence=0.8,
    ),
    # Permission denied
    "permission_denied": ErrorPattern(
        pattern=r"EACCES: permission denied",
        category="config",
        fix_command="chmod +x {file}",
        fix_description="Grant execute permission to the file",
        confidence=0.7,
    ),
    # File not found
    "file_not_found": ErrorPattern(
        pattern=r"ENOENT: no such file or directory, (.+)",
        category="config",
        fix_description="Create the missing file or directory",
        confidence=0.8,
    ),
    # Python syntax error - missing colon
    "python_missing_colon": ErrorPattern(
        pattern=r"SyntaxError: invalid syntax.*expected ':'",
        category="syntax",
        fix_description="Add missing colon at end of statement (if, def, class, etc.)",
        confidence=0.9,
    ),
    # Python indentation error
    "python_indentation": ErrorPattern(
        pattern=r"IndentationError:",
        category="syntax",
        fix_description="Fix indentation - Python requires consistent spacing",
        confidence=0.9,
    ),
    # JavaScript missing semicolon
    "js_missing_semicolon": ErrorPattern(
        pattern=r"SyntaxError: Unexpected token",
        category="syntax",
        fix_description="Check for missing semicolons or brackets",
        confidence=0.6,
    ),
    # Undefined variable
    "undefined_variable": ErrorPattern(
        pattern=r"(NameError|ReferenceError): (.+) is not defined",
        category="runtime",
        fix_description="Define the variable or import it if from another module",
        confidence=0.8,
    ),
    # npm - no package.json
    "npm_no_package_json": ErrorPattern(
        pattern=r"npm ERR!.*ENOENT.*package.json",
        category="config",
        fix_command="npm init -y",
        fix_description="Initialize npm package.json file",
        confidence=0.95,
    ),
    # Git not initialized
    "git_not_initialized": ErrorPattern(
        pattern=r"fatal: not a git repository",
        category="config",
        fix_command="git init",
        fix_description="Initialize git repository",
        confidence=1.0,
    ),
    # Command not found
    "command_not_found": ErrorPattern(
        pattern=r"command not found: (.+)",
        category="dependency",
        fix_description="Install the required command/tool: {command}",
        confidence=0.7,
    ),
    # Python - wrong Python version
    "python_version": ErrorPattern(
        pattern=r"SyntaxError:.*invalid syntax.*:=",
        category="config",
        fix_description="Code uses Python 3.8+ syntax (walrus operator). Upgrade Python version.",
        confidence=0.9,
    ),
    # TypeScript - tsc not found
    "typescript_not_installed": ErrorPattern(
        pattern=r"tsc: command not found",
        category="dependency",
        fix_command="npm install -g typescript",
        fix_description="Install TypeScript compiler globally",
        confidence=0.95,
    ),
    # React - missing dependencies
    "react_missing": ErrorPattern(
        pattern=r"Cannot find module 'react'",
        category="dependency",
        fix_command="npm install react react-dom",
        fix_description="Install React dependencies",
        confidence=1.0,
    ),
    # Express - missing
    "express_missing": ErrorPattern(
        pattern=r"Cannot find module 'express'",
        category="dependency",
        fix_command="npm install express",
        fix_description="Install Express framework",
        confidence=1.0,
    ),
    # Database connection error
    "db_connection_error": ErrorPattern(
        pattern=r"ECONNREFUSED.*\d+",
        category="runtime",
        fix_description="Database server is not running. Start the database service.",
        confidence=0.8,
    ),
    # Environment variable missing
    "env_var_missing": ErrorPattern(
        pattern=r"process\.env\.(\w+) is undefined",
        category="config",
        fix_description="Set the environment variable {var} in .env file",
        confidence=0.85,
    ),
}


def get_fix_for_error(error_message: str) -> Optional[ErrorPattern]:
    """
    Find a fix pattern for an error message
    
    Args:
        error_message: The error message to match
        
    Returns:
        ErrorPattern if found, None otherwise
    """
    import re

    for pattern_name, pattern in ERROR_PATTERNS.items():
        if re.search(pattern.pattern, error_message, re.IGNORECASE):
            return pattern

    return None


def get_dependency_fix(module_name: str, language: str = "python") -> Optional[str]:
    """
    Get the command to install a missing dependency
    
    Args:
        module_name: Name of the missing module
        language: Programming language ('python' or 'javascript')
        
    Returns:
        Installation command or None
    """
    if language == "python":
        # Common package name mappings
        package_map = {
            "PIL": "Pillow",
            "cv2": "opencv-python",
            "sklearn": "scikit-learn",
        }
        package_name = package_map.get(module_name, module_name)
        return f"pip install {package_name}"

    elif language in ["javascript", "js", "node"]:
        return f"npm install {module_name}"

    return None
