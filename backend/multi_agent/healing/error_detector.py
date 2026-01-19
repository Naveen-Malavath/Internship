"""Error detection from command output, stderr, and exit codes"""

import re
import logging
from typing import Dict, Optional, Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DetectedError(BaseModel):
    """Represents a detected error"""

    error_type: str
    message: str
    details: str
    exit_code: Optional[int] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    command: Optional[str] = None


class ErrorDetector:
    """Detects errors from command execution output"""

    ERROR_PATTERNS = {
        # Python
        r"ModuleNotFoundError: No module named '([^']+)'": "python_missing_module",
        r"ImportError: (.+)": "python_import",
        r"SyntaxError: (.+)": "python_syntax",
        r"File \"([^\"]+)\", line (\d+)": "python_traceback",
        
        # JavaScript/Node
        r"Error: Cannot find module '([^']+)'": "js_missing_module",
        r"SyntaxError: (.+)": "js_syntax",
        r"ReferenceError: (.+)": "js_reference",
        r"TypeError: (.+)": "js_type",
        
        # npm
        r"npm ERR! (.+)": "npm_error",
        r"ENOENT: no such file or directory": "file_not_found",
        r"EADDRINUSE: address already in use": "port_in_use",
        
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
        """Detect errors from command output"""
        
        if exit_code == 0:
            return None

        combined_output = f"{stdout}\n{stderr}"
        error_info = self._match_patterns(combined_output)

        if error_info:
            logger.info(f"[ERROR_DETECTOR] Detected: {error_info['type']}")
            return DetectedError(
                error_type=error_info["type"],
                message=error_info["message"],
                details=combined_output.strip()[-500:],
                exit_code=exit_code,
                file_path=error_info.get("file_path"),
                line_number=error_info.get("line_number"),
                command=command,
            )

        # Generic error
        return DetectedError(
            error_type="unknown_error",
            message=f"Command failed with exit code {exit_code}",
            details=combined_output.strip()[-500:],
            exit_code=exit_code,
            command=command,
        )

    def _match_patterns(self, text: str) -> Optional[Dict[str, Any]]:
        """Match text against known error patterns"""
        for pattern, error_type in self.ERROR_PATTERNS.items():
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                result = {
                    "type": error_type,
                    "message": match.group(0),
                }

                if error_type == "python_traceback":
                    result["file_path"] = match.group(1)
                    result["line_number"] = int(match.group(2))
                elif "missing_module" in error_type:
                    result["module_name"] = match.group(1)

                return result

        return None

    def is_dependency_error(self, error: DetectedError) -> bool:
        """Check if error is related to missing dependencies"""
        return error.error_type in [
            "python_missing_module",
            "js_missing_module",
            "npm_error",
        ]

    def is_syntax_error(self, error: DetectedError) -> bool:
        """Check if error is a syntax error"""
        return "syntax" in error.error_type.lower()
