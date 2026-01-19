"""Error fixer - generates fixes for detected errors"""

import re
import logging
from typing import Dict, List, Optional, Any

from .error_detector import DetectedError
from .classifier import ErrorClassifier, ErrorCategory

logger = logging.getLogger(__name__)


class FixSuggestion:
    """Represents a suggested fix for an error"""

    def __init__(
        self,
        fix_type: str,
        description: str,
        command: Optional[str] = None,
        file_path: Optional[str] = None,
        confidence: float = 0.5,
    ):
        self.fix_type = fix_type
        self.description = description
        self.command = command
        self.file_path = file_path
        self.confidence = confidence

    def __repr__(self) -> str:
        return f"<FixSuggestion: {self.description} (confidence: {self.confidence})>"


# Common package mappings for Python
PYTHON_PACKAGE_MAP = {
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
}


class ErrorFixer:
    """Generates fixes for detected errors"""

    def __init__(self):
        self.fix_history: List[Dict[str, Any]] = []

    def suggest_fix(self, error: DetectedError) -> Optional[FixSuggestion]:
        """Suggest a fix for an error"""
        logger.info(f"[FIXER] Analyzing error: {error.error_type}")

        category = ErrorClassifier.classify(error)

        if category == ErrorCategory.DEPENDENCY:
            return self._fix_dependency_error(error)
        elif category == ErrorCategory.SYNTAX:
            return self._suggest_syntax_fix(error)
        elif category == ErrorCategory.RUNTIME:
            return self._suggest_runtime_fix(error)
        elif category == ErrorCategory.CONFIGURATION:
            return self._suggest_config_fix(error)

        return None

    def _fix_dependency_error(self, error: DetectedError) -> Optional[FixSuggestion]:
        """Fix missing dependency errors"""
        module_match = re.search(
            r"(?:No module named|Cannot find module) '([^']+)'",
            error.message,
        )

        if module_match:
            module_name = module_match.group(1)

            if "python" in error.error_type.lower():
                package_name = PYTHON_PACKAGE_MAP.get(module_name, module_name)
                command = f"pip install {package_name}"
            else:
                command = f"npm install {module_name}"

            return FixSuggestion(
                fix_type="install_dependency",
                description=f"Install missing module: {module_name}",
                command=command,
                confidence=0.9,
            )

        return None

    def _suggest_syntax_fix(self, error: DetectedError) -> Optional[FixSuggestion]:
        """Suggest fix for syntax errors"""
        return FixSuggestion(
            fix_type="syntax_fix",
            description="Syntax error detected. Review the code for issues.",
            file_path=error.file_path,
            confidence=0.5,
        )

    def _suggest_runtime_fix(self, error: DetectedError) -> Optional[FixSuggestion]:
        """Suggest fix for runtime errors"""
        if "not defined" in error.message.lower():
            var_match = re.search(r"'?(\w+)'? is not defined", error.message)
            if var_match:
                var_name = var_match.group(1)
                return FixSuggestion(
                    fix_type="runtime_fix",
                    description=f"Define variable '{var_name}' or import it",
                    file_path=error.file_path,
                    confidence=0.7,
                )

        elif "address already in use" in error.message.lower():
            return FixSuggestion(
                fix_type="runtime_fix",
                description="Port is in use. Use a different port.",
                confidence=0.8,
            )

        return None

    def _suggest_config_fix(self, error: DetectedError) -> Optional[FixSuggestion]:
        """Suggest fix for configuration errors"""
        if "no such file or directory" in error.message.lower():
            return FixSuggestion(
                fix_type="config_fix",
                description="Create missing file or directory",
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

    def track_fix(self, error: DetectedError, fix: FixSuggestion, success: bool):
        """Track fix attempts for learning"""
        self.fix_history.append({
            "error_type": error.error_type,
            "fix_type": fix.fix_type,
            "success": success,
        })
        logger.info(f"[FIXER] Fix {'SUCCESS' if success else 'FAILED'}: {fix.description}")
