"""Error classification to categorize detected errors"""

from enum import Enum
from typing import Optional

from loguru import logger

from .error_detector import DetectedError
from .error_patterns import get_fix_for_error


class ErrorCategory(str, Enum):
    """Categories of errors"""

    DEPENDENCY = "dependency"  # Missing packages/modules
    SYNTAX = "syntax"  # Syntax errors in code
    RUNTIME = "runtime"  # Runtime errors (undefined vars, null refs, etc.)
    CONFIGURATION = "configuration"  # Config issues (env vars, paths, etc.)
    NETWORK = "network"  # Network/connection errors
    PERMISSION = "permission"  # Permission/access errors
    UNKNOWN = "unknown"  # Unclassified errors


class ErrorClassifier:
    """
    Classifies detected errors into categories
    Helps determine the appropriate fix strategy
    """

    @staticmethod
    def classify(error: DetectedError) -> ErrorCategory:
        """
        Classify an error into a category
        
        Args:
            error: Detected error
            
        Returns:
            ErrorCategory
        """
        # Check if we have a pattern match
        pattern = get_fix_for_error(error.message)
        if pattern:
            category_map = {
                "dependency": ErrorCategory.DEPENDENCY,
                "syntax": ErrorCategory.SYNTAX,
                "runtime": ErrorCategory.RUNTIME,
                "config": ErrorCategory.CONFIGURATION,
                "network": ErrorCategory.NETWORK,
                "permission": ErrorCategory.PERMISSION,
            }
            return category_map.get(pattern.category, ErrorCategory.UNKNOWN)

        # Fallback to error type analysis
        error_type = error.error_type.lower()

        if "missing_module" in error_type or "npm_error" in error_type:
            return ErrorCategory.DEPENDENCY

        elif "syntax" in error_type or "indentation" in error_type:
            return ErrorCategory.SYNTAX

        elif (
            "exception" in error_type
            or "reference" in error_type
            or "type" in error_type
        ):
            return ErrorCategory.RUNTIME

        elif "not_found" in error_type or "enoent" in error_type:
            return ErrorCategory.CONFIGURATION

        elif "connection" in error_type or "econnrefused" in error_type:
            return ErrorCategory.NETWORK

        elif "permission" in error_type or "eacces" in error_type:
            return ErrorCategory.PERMISSION

        logger.warning(f"Could not classify error: {error.error_type}")
        return ErrorCategory.UNKNOWN

    @staticmethod
    def is_fixable(error: DetectedError) -> bool:
        """
        Determine if an error is likely fixable automatically
        
        Args:
            error: Detected error
            
        Returns:
            True if likely fixable
        """
        category = ErrorClassifier.classify(error)

        # Dependency and config errors are usually fixable
        if category in [ErrorCategory.DEPENDENCY, ErrorCategory.CONFIGURATION]:
            return True

        # Syntax errors might be fixable with LLM
        if category == ErrorCategory.SYNTAX:
            return True

        # Some runtime errors are fixable
        if category == ErrorCategory.RUNTIME:
            # Check if it's a simple undefined variable
            if "not defined" in error.message.lower():
                return True
            return False

        return False

    @staticmethod
    def get_fix_strategy(error: DetectedError) -> str:
        """
        Get the recommended fix strategy for an error
        
        Args:
            error: Detected error
            
        Returns:
            Fix strategy name
        """
        category = ErrorClassifier.classify(error)

        strategy_map = {
            ErrorCategory.DEPENDENCY: "install_dependency",
            ErrorCategory.SYNTAX: "fix_syntax",
            ErrorCategory.RUNTIME: "fix_runtime",
            ErrorCategory.CONFIGURATION: "fix_config",
            ErrorCategory.NETWORK: "check_services",
            ErrorCategory.PERMISSION: "fix_permissions",
            ErrorCategory.UNKNOWN: "llm_analysis",
        }

        return strategy_map.get(category, "llm_analysis")
