"""
Self-Healing Module
Provides error detection, classification, and automatic fixing capabilities
"""

from .error_detector import ErrorDetector, DetectedError
from .classifier import ErrorClassifier, ErrorCategory
from .fixer import ErrorFixer, FixSuggestion
from .enhanced_error_detector import (
    EnhancedErrorDetector,
    EnhancedDetectedError,
    ErrorSeverity,
    ErrorCategory as EnhancedErrorCategory,
    CSSClassValidator,
    CodeQualityChecker,
    ProductionErrorHandler,
)

__all__ = [
    # Legacy
    "ErrorDetector",
    "DetectedError",
    "ErrorClassifier",
    "ErrorCategory",
    "ErrorFixer",
    "FixSuggestion",
    # Enhanced
    "EnhancedErrorDetector",
    "EnhancedDetectedError",
    "ErrorSeverity",
    "EnhancedErrorCategory",
    "CSSClassValidator",
    "CodeQualityChecker",
    "ProductionErrorHandler",
]
