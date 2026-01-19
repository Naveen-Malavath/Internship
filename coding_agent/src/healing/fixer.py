"""Error fixer - generates and applies fixes for detected errors"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any

from loguru import logger

from .error_detector import DetectedError
from .error_patterns import get_fix_for_error, get_dependency_fix
from .classifier import ErrorClassifier, ErrorCategory


class FixSuggestion:
    """Represents a suggested fix for an error"""

    def __init__(
        self,
        fix_type: str,
        description: str,
        command: Optional[str] = None,
        file_path: Optional[str] = None,
        code_change: Optional[str] = None,
        confidence: float = 0.5,
    ):
        self.fix_type = fix_type
        self.description = description
        self.command = command
        self.file_path = file_path
        self.code_change = code_change
        self.confidence = confidence

    def __repr__(self) -> str:
        return f"<FixSuggestion: {self.description} (confidence: {self.confidence})>"


class ErrorFixer:
    """
    Generates fixes for detected errors
    Can suggest commands to run or code changes to make
    """

    def __init__(self):
        self.fix_history: List[Dict[str, Any]] = []

    def suggest_fix(self, error: DetectedError) -> Optional[FixSuggestion]:
        """
        Suggest a fix for an error
        
        Args:
            error: Detected error
            
        Returns:
            FixSuggestion or None
        """
        logger.info(f"Analyzing error for fix: {error.error_type}")

        # Try pattern-based fix first
        pattern = get_fix_for_error(error.message)
        if pattern and pattern.fix_command:
            # Extract variables from error message
            fix_command = self._interpolate_fix_command(
                pattern.fix_command, error.message, pattern.pattern
            )

            return FixSuggestion(
                fix_type="command",
                description=pattern.fix_description,
                command=fix_command,
                confidence=pattern.confidence,
            )

        # Category-based fixes
        category = ErrorClassifier.classify(error)

        if category == ErrorCategory.DEPENDENCY:
            return self._fix_dependency_error(error)

        elif category == ErrorCategory.SYNTAX:
            return self._suggest_syntax_fix(error)

        elif category == ErrorCategory.RUNTIME:
            return self._suggest_runtime_fix(error)

        elif category == ErrorCategory.CONFIGURATION:
            return self._suggest_config_fix(error)

        logger.warning(f"No fix suggestion found for error: {error.error_type}")
        return None

    def _fix_dependency_error(self, error: DetectedError) -> Optional[FixSuggestion]:
        """Fix missing dependency errors"""
        # Extract module name
        module_match = re.search(
            r"(?:No module named|Cannot find module) '([^']+)'",
            error.message,
        )

        if module_match:
            module_name = module_match.group(1)

            # Determine language
            if "python" in error.error_type.lower():
                command = get_dependency_fix(module_name, "python")
            elif "js" in error.error_type.lower() or "npm" in error.error_type.lower():
                command = get_dependency_fix(module_name, "javascript")
            else:
                command = f"pip install {module_name}"  # Default to Python

            return FixSuggestion(
                fix_type="install_dependency",
                description=f"Install missing module: {module_name}",
                command=command,
                confidence=0.9,
            )

        return None

    def _suggest_syntax_fix(self, error: DetectedError) -> Optional[FixSuggestion]:
        """Suggest fix for syntax errors"""
        if not error.file_path or not error.line_number:
            return FixSuggestion(
                fix_type="syntax_fix",
                description="Syntax error detected. Review the code for missing punctuation, brackets, or indentation issues.",
                confidence=0.5,
            )

        # Specific syntax error patterns
        if "expected ':'" in error.message.lower():
            return FixSuggestion(
                fix_type="syntax_fix",
                description=f"Add missing colon at line {error.line_number} in {error.file_path}",
                file_path=error.file_path,
                confidence=0.8,
            )

        elif "indentationerror" in error.message.lower():
            return FixSuggestion(
                fix_type="syntax_fix",
                description=f"Fix indentation at line {error.line_number} in {error.file_path}",
                file_path=error.file_path,
                confidence=0.8,
            )

        return FixSuggestion(
            fix_type="syntax_fix",
            description=f"Fix syntax error at line {error.line_number} in {error.file_path}",
            file_path=error.file_path,
            confidence=0.6,
        )

    def _suggest_runtime_fix(self, error: DetectedError) -> Optional[FixSuggestion]:
        """Suggest fix for runtime errors"""
        if "not defined" in error.message.lower():
            # Extract variable name
            var_match = re.search(r"'?(\w+)'? is not defined", error.message)
            if var_match:
                var_name = var_match.group(1)
                return FixSuggestion(
                    fix_type="runtime_fix",
                    description=f"Define variable '{var_name}' or import it if from another module",
                    file_path=error.file_path,
                    confidence=0.7,
                )

        elif "address already in use" in error.message.lower():
            # Extract port number
            port_match = re.search(r":(\d+)", error.message)
            if port_match:
                port = port_match.group(1)
                return FixSuggestion(
                    fix_type="runtime_fix",
                    description=f"Port {port} is in use. Change to a different port or stop the process using it.",
                    confidence=0.8,
                )

        return FixSuggestion(
            fix_type="runtime_fix",
            description="Runtime error detected. Check variable definitions and data types.",
            confidence=0.5,
        )

    def _suggest_config_fix(self, error: DetectedError) -> Optional[FixSuggestion]:
        """Suggest fix for configuration errors"""
        if "no such file or directory" in error.message.lower():
            return FixSuggestion(
                fix_type="config_fix",
                description="Create missing file or directory, or check the path is correct",
                confidence=0.7,
            )

        elif "package.json" in error.message.lower():
            return FixSuggestion(
                fix_type="config_fix",
                description="Initialize npm project",
                command="npm init -y",
                confidence=0.95,
            )

        return None

    def _interpolate_fix_command(
        self, command_template: str, error_message: str, pattern: str
    ) -> str:
        """
        Interpolate variables in fix command from error message
        
        Args:
            command_template: Command with {placeholders}
            error_message: Error message to extract values from
            pattern: Regex pattern to match
            
        Returns:
            Interpolated command
        """
        match = re.search(pattern, error_message, re.IGNORECASE)
        if not match:
            return command_template

        # Replace {module} with captured group
        if "{module}" in command_template and match.groups():
            module = match.group(1)
            return command_template.replace("{module}", module)

        # Replace {port} with captured port number
        if "{port}" in command_template:
            port_match = re.search(r":(\d+)", error_message)
            if port_match:
                return command_template.replace("{port}", port_match.group(1))

        return command_template

    def track_fix(self, error: DetectedError, fix: FixSuggestion, success: bool):
        """
        Track fix attempts for learning
        
        Args:
            error: The error that was fixed
            fix: The fix that was applied
            success: Whether the fix worked
        """
        self.fix_history.append(
            {
                "error_type": error.error_type,
                "error_message": error.message,
                "fix_type": fix.fix_type,
                "fix_description": fix.description,
                "success": success,
            }
        )

        logger.info(f"Tracked fix: {fix.description} - {'SUCCESS' if success else 'FAILED'}")

    def get_fix_success_rate(self, error_type: str) -> float:
        """
        Get success rate for fixes of a specific error type
        
        Args:
            error_type: Type of error
            
        Returns:
            Success rate (0-1)
        """
        relevant_fixes = [
            f for f in self.fix_history if f["error_type"] == error_type
        ]

        if not relevant_fixes:
            return 0.0

        successful = sum(1 for f in relevant_fixes if f["success"])
        return successful / len(relevant_fixes)
