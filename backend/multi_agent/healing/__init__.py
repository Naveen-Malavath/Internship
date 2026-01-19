"""Self-healing error detection and fixing system."""

from .error_detector import ErrorDetector, DetectedError
from .classifier import ErrorClassifier, ErrorCategory
from .fixer import ErrorFixer, FixSuggestion

__all__ = [
    "ErrorDetector",
    "DetectedError",
    "ErrorClassifier", 
    "ErrorCategory",
    "ErrorFixer",
    "FixSuggestion",
]
