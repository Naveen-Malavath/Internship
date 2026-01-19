"""Error classification to categorize detected errors"""

import logging
from enum import Enum

from .error_detector import DetectedError

logger = logging.getLogger(__name__)


class ErrorCategory(str, Enum):
    """Categories of errors"""

    DEPENDENCY = "dependency"
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


class ErrorClassifier:
    """Classifies detected errors into categories"""

    @staticmethod
    def classify(error: DetectedError) -> ErrorCategory:
        """Classify an error into a category"""
        error_type = error.error_type.lower()

        if "missing_module" in error_type or "npm_error" in error_type:
            return ErrorCategory.DEPENDENCY

        elif "syntax" in error_type or "indentation" in error_type:
            return ErrorCategory.SYNTAX

        elif "exception" in error_type or "reference" in error_type or "type" in error_type:
            return ErrorCategory.RUNTIME

        elif "not_found" in error_type or "enoent" in error_type:
            return ErrorCategory.CONFIGURATION

        elif "connection" in error_type or "econnrefused" in error_type:
            return ErrorCategory.NETWORK

        elif "permission" in error_type or "eacces" in error_type:
            return ErrorCategory.PERMISSION

        logger.warning(f"[CLASSIFIER] Could not classify error: {error.error_type}")
        return ErrorCategory.UNKNOWN

    @staticmethod
    def is_fixable(error: DetectedError) -> bool:
        """Determine if an error is likely fixable automatically"""
        category = ErrorClassifier.classify(error)

        if category in [ErrorCategory.DEPENDENCY, ErrorCategory.CONFIGURATION]:
            return True

        if category == ErrorCategory.SYNTAX:
            return True

        if category == ErrorCategory.RUNTIME:
            if "not defined" in error.message.lower():
                return True
            return False

        return False

    @staticmethod
    def get_fix_strategy(error: DetectedError) -> str:
        """Get the recommended fix strategy for an error"""
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
