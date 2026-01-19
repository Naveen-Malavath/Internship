"""Error detection from command output, stderr, and exit codes"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any

from loguru import logger
from pydantic import BaseModel


class DetectedError(BaseModel):
    """Represents a detected error"""

    error_type: str  # 'command_failure', 'parse_error', 'runtime_error', etc.
    message: str
    details: str
    exit_code: Optional[int] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    stack_trace: Optional[str] = None
    command: Optional[str] = None


class ErrorDetector:
    """
    Detects errors from command execution output
    Parses stderr, exit codes, and common error patterns
    """

    # Common error patterns across languages
    ERROR_PATTERNS = {
        # Python
        r"File \"([^\"]+)\", line (\d+)": "python_traceback",
        r"(\w+Error): (.+)": "python_exception",
        r"SyntaxError: (.+)": "python_syntax",
        r"ModuleNotFoundError: No module named '([^']+)'": "python_missing_module",
        r"ImportError: (.+)": "python_import",
        
        # JavaScript/Node
        r"Error: Cannot find module '([^']+)'": "js_missing_module",
        r"SyntaxError: (.+)": "js_syntax",
        r"ReferenceError: (.+)": "js_reference",
        r"TypeError: (.+)": "js_type",
        r"at (.+):(\d+):(\d+)": "js_stack_trace",
        
        # npm/package managers
        r"npm ERR! (.+)": "npm_error",
        r"ENOENT: no such file or directory": "file_not_found",
        r"EADDRINUSE: address already in use": "port_in_use",
        r"EACCES: permission denied": "permission_denied",
        
        # Git
        r"fatal: (.+)": "git_error",
        
        # Compilation errors
        r"error: (.+)": "compilation_error",
        r"warning: (.+)": "compilation_warning",
        
        # General
        r"command not found": "command_not_found",
        r"No such file or directory": "file_not_found",
    }

    def detect(
        self,
        stdout: str = "",
        stderr: str = "",
        exit_code: int = 0,
        command: Optional[str] = None,
    ) -> Optional[DetectedError]:
        """
        Detect errors from command execution output
        
        Args:
            stdout: Standard output
            stderr: Standard error output
            exit_code: Command exit code
            command: The command that was executed
            
        Returns:
            DetectedError if error found, None otherwise
        """
        # Exit code 0 typically means success
        if exit_code == 0:
            return None

        # Combine output for analysis
        combined_output = f"{stdout}\n{stderr}"

        # Try to match error patterns
        error_info = self._match_patterns(combined_output)

        if error_info:
            logger.info(f"Detected error type: {error_info['type']}")
            return DetectedError(
                error_type=error_info["type"],
                message=error_info["message"],
                details=combined_output.strip()[-500:],  # Last 500 chars
                exit_code=exit_code,
                file_path=error_info.get("file_path"),
                line_number=error_info.get("line_number"),
                stack_trace=error_info.get("stack_trace"),
                command=command,
            )

        # Generic error if no pattern matched
        return DetectedError(
            error_type="unknown_error",
            message=f"Command failed with exit code {exit_code}",
            details=combined_output.strip()[-500:],
            exit_code=exit_code,
            command=command,
        )

    def _match_patterns(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Match text against known error patterns
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with error information or None
        """
        for pattern, error_type in self.ERROR_PATTERNS.items():
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                result = {
                    "type": error_type,
                    "message": match.group(0),
                }

                # Extract file and line if available
                if error_type == "python_traceback":
                    result["file_path"] = match.group(1)
                    result["line_number"] = int(match.group(2))

                # Extract module name for missing imports
                elif "missing_module" in error_type:
                    result["module_name"] = match.group(1)

                return result

        return None

    def extract_stack_trace(self, text: str) -> Optional[str]:
        """
        Extract stack trace from error output
        
        Args:
            text: Error output
            
        Returns:
            Stack trace string or None
        """
        # Python traceback
        traceback_match = re.search(
            r"Traceback \(most recent call last\):.*?(?=\n\n|\Z)",
            text,
            re.DOTALL,
        )
        if traceback_match:
            return traceback_match.group(0)

        # JavaScript stack trace
        stack_match = re.search(
            r"Error:.*?(?:\n    at .*?)+",
            text,
            re.DOTALL,
        )
        if stack_match:
            return stack_match.group(0)

        return None

    def is_dependency_error(self, error: DetectedError) -> bool:
        """Check if error is related to missing dependencies"""
        dependency_types = [
            "python_missing_module",
            "js_missing_module",
            "npm_error",
        ]
        return error.error_type in dependency_types

    def is_syntax_error(self, error: DetectedError) -> bool:
        """Check if error is a syntax error"""
        syntax_types = ["python_syntax", "js_syntax", "compilation_error"]
        return error.error_type in syntax_types

    def is_runtime_error(self, error: DetectedError) -> bool:
        """Check if error is a runtime error"""
        runtime_types = [
            "python_exception",
            "js_reference",
            "js_type",
            "port_in_use",
        ]
        return error.error_type in runtime_types
