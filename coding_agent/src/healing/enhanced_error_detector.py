"""
Enhanced Error Detection System
Comprehensive error detection for production-ready code generation
Includes CSS validation, build errors, runtime errors, and code quality checks
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass

from loguru import logger


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    CRITICAL = "critical"    # Blocks execution
    HIGH = "high"            # Major issue, app won't work correctly
    MEDIUM = "medium"        # Noticeable issue, partial functionality
    LOW = "low"              # Minor issue, cosmetic
    WARNING = "warning"      # Suggestion for improvement


class ErrorCategory(str, Enum):
    """Error categories"""
    BUILD = "build"
    RUNTIME = "runtime"
    SYNTAX = "syntax"
    DEPENDENCY = "dependency"
    CSS = "css"
    TYPE = "type"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    CODE_QUALITY = "code_quality"


@dataclass
class EnhancedDetectedError:
    """Comprehensive error representation"""
    error_type: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: str
    
    # Location info
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    
    # Context
    command: Optional[str] = None
    exit_code: Optional[int] = None
    stack_trace: Optional[str] = None
    
    # Fix suggestion
    suggested_fix: Optional[str] = None
    fix_command: Optional[str] = None
    auto_fixable: bool = False


class EnhancedErrorDetector:
    """
    Production-ready error detector with comprehensive pattern matching
    """
    
    # =========================================================================
    # ERROR PATTERNS - Organized by category
    # =========================================================================
    
    BUILD_ERRORS = {
        # Vite/React build errors
        r"Failed to resolve import \"([^\"]+)\"": ("vite_import_error", ErrorSeverity.CRITICAL),
        r"\[vite\] Internal server error: (.+)": ("vite_server_error", ErrorSeverity.CRITICAL),
        r"error during build:": ("build_error", ErrorSeverity.CRITICAL),
        r"Build failed with (\d+) error": ("build_failed", ErrorSeverity.CRITICAL),
        r"Failed to compile": ("compile_error", ErrorSeverity.CRITICAL),
        r"Module build failed": ("module_build_failed", ErrorSeverity.CRITICAL),
        
        # TypeScript errors
        r"TS(\d+): (.+)": ("typescript_error", ErrorSeverity.HIGH),
        r"error TS\d+:": ("typescript_error", ErrorSeverity.HIGH),
        r"Cannot find module '([^']+)'": ("ts_module_not_found", ErrorSeverity.CRITICAL),
        r"Type '([^']+)' is not assignable to type '([^']+)'": ("ts_type_error", ErrorSeverity.HIGH),
        
        # Webpack errors
        r"Module not found: Error: Can't resolve '([^']+)'": ("webpack_module_not_found", ErrorSeverity.CRITICAL),
        r"webpack.*error": ("webpack_error", ErrorSeverity.HIGH),
        
        # ESLint/Linting
        r"(\d+) error[s]? and (\d+) warning[s]?": ("eslint_errors", ErrorSeverity.MEDIUM),
        r"Parsing error: (.+)": ("parsing_error", ErrorSeverity.HIGH),
    }
    
    RUNTIME_ERRORS = {
        # JavaScript runtime
        r"Uncaught ReferenceError: (\w+) is not defined": ("js_reference_error", ErrorSeverity.CRITICAL),
        r"Uncaught TypeError: (.+)": ("js_type_error", ErrorSeverity.CRITICAL),
        r"Uncaught SyntaxError: (.+)": ("js_syntax_error", ErrorSeverity.CRITICAL),
        r"Cannot read propert(?:y|ies) of (?:undefined|null)": ("js_null_error", ErrorSeverity.CRITICAL),
        r"is not a function": ("js_not_function", ErrorSeverity.CRITICAL),
        
        # React specific
        r"React Hook \"(\w+)\" (.+)": ("react_hook_error", ErrorSeverity.HIGH),
        r"Invalid hook call": ("react_invalid_hook", ErrorSeverity.CRITICAL),
        r"Maximum update depth exceeded": ("react_infinite_loop", ErrorSeverity.CRITICAL),
        r"Each child in a list should have a unique \"key\" prop": ("react_key_warning", ErrorSeverity.MEDIUM),
        r"Warning: (.+) is deprecated": ("deprecation_warning", ErrorSeverity.LOW),
        
        # Python runtime
        r"Traceback \(most recent call last\):": ("python_traceback", ErrorSeverity.CRITICAL),
        r"(\w+Error): (.+)": ("python_exception", ErrorSeverity.HIGH),
        r"AttributeError: (.+)": ("python_attribute_error", ErrorSeverity.HIGH),
        r"KeyError: (.+)": ("python_key_error", ErrorSeverity.HIGH),
        r"IndexError: (.+)": ("python_index_error", ErrorSeverity.HIGH),
    }
    
    DEPENDENCY_ERRORS = {
        # npm errors
        r"npm ERR! code E(\d+)": ("npm_error_code", ErrorSeverity.HIGH),
        r"npm ERR! 404 Not Found.*'([^']+)'": ("npm_package_not_found", ErrorSeverity.CRITICAL),
        r"npm ERR! peer dep missing: (.+)": ("npm_peer_dep_missing", ErrorSeverity.MEDIUM),
        r"npm WARN deprecated (.+)": ("npm_deprecated", ErrorSeverity.LOW),
        r"ERESOLVE unable to resolve dependency tree": ("npm_dependency_conflict", ErrorSeverity.HIGH),
        r"npm ERR! ENOENT": ("npm_file_not_found", ErrorSeverity.CRITICAL),
        
        # Python
        r"ModuleNotFoundError: No module named '([^']+)'": ("python_module_not_found", ErrorSeverity.CRITICAL),
        r"ImportError: cannot import name '([^']+)'": ("python_import_error", ErrorSeverity.CRITICAL),
        r"pip.*No matching distribution found for ([^\s]+)": ("pip_package_not_found", ErrorSeverity.CRITICAL),
    }
    
    CSS_ERRORS = {
        # CSS syntax
        r"CssSyntaxError: (.+)": ("css_syntax_error", ErrorSeverity.HIGH),
        r"Unexpected token (.+) in CSS": ("css_unexpected_token", ErrorSeverity.HIGH),
        r"Unknown word": ("css_unknown_word", ErrorSeverity.MEDIUM),
        
        # PostCSS/Tailwind
        r"@apply directive requires (.+)": ("tailwind_apply_error", ErrorSeverity.MEDIUM),
        r"The `(.+)` class does not exist": ("tailwind_class_not_found", ErrorSeverity.MEDIUM),
    }
    
    FILE_SYSTEM_ERRORS = {
        r"ENOENT: no such file or directory(?:, (?:open|stat) '([^']+)')?": ("file_not_found", ErrorSeverity.CRITICAL),
        r"EACCES: permission denied": ("permission_denied", ErrorSeverity.CRITICAL),
        r"EADDRINUSE: address already in use :::?(\d+)": ("port_in_use", ErrorSeverity.HIGH),
        r"ECONNREFUSED": ("connection_refused", ErrorSeverity.HIGH),
        r"ETIMEDOUT": ("connection_timeout", ErrorSeverity.MEDIUM),
    }
    
    COMMAND_ERRORS = {
        r"command not found": ("command_not_found", ErrorSeverity.CRITICAL),
        r"'(\w+)' is not recognized as an internal or external command": ("command_not_recognized", ErrorSeverity.CRITICAL),
        r"bash: (.+): No such file or directory": ("bash_file_not_found", ErrorSeverity.CRITICAL),
        r"which: no (\w+) in": ("command_not_in_path", ErrorSeverity.HIGH),
    }
    
    # Combine all patterns
    ALL_PATTERNS = {
        **BUILD_ERRORS,
        **RUNTIME_ERRORS,
        **DEPENDENCY_ERRORS,
        **CSS_ERRORS,
        **FILE_SYSTEM_ERRORS,
        **COMMAND_ERRORS,
    }
    
    # =========================================================================
    # FIX SUGGESTIONS
    # =========================================================================
    
    FIX_SUGGESTIONS = {
        "npm_package_not_found": {
            "suggestion": "Check package name spelling or verify it exists on npm registry",
            "auto_fixable": False,
        },
        "npm_dependency_conflict": {
            "suggestion": "Try running 'npm install --legacy-peer-deps' or update package versions",
            "command": "npm install --legacy-peer-deps",
            "auto_fixable": True,
        },
        "python_module_not_found": {
            "suggestion": "Install the missing module with pip",
            "command_template": "pip install {module}",
            "auto_fixable": True,
        },
        "port_in_use": {
            "suggestion": "The port is already in use. Kill the process or use a different port",
            "command_template": "npx kill-port {port}",
            "auto_fixable": True,
        },
        "file_not_found": {
            "suggestion": "The file or directory does not exist. Check the path or create it",
            "auto_fixable": False,
        },
        "command_not_found": {
            "suggestion": "The command is not installed or not in PATH",
            "auto_fixable": False,
        },
        "vite_import_error": {
            "suggestion": "Check that the import path is correct and the file exists",
            "auto_fixable": False,
        },
        "react_key_warning": {
            "suggestion": "Add a unique 'key' prop to each item in the list",
            "auto_fixable": False,
        },
        "react_hook_error": {
            "suggestion": "Ensure hooks are called at the top level of function components",
            "auto_fixable": False,
        },
        "typescript_error": {
            "suggestion": "Fix the TypeScript type error as indicated",
            "auto_fixable": False,
        },
        "css_syntax_error": {
            "suggestion": "Fix the CSS syntax error - check for missing brackets, semicolons, or invalid properties",
            "auto_fixable": False,
        },
    }
    
    def __init__(self):
        """Initialize the enhanced error detector"""
        self.detected_errors: List[EnhancedDetectedError] = []
    
    def detect(
        self,
        stdout: str = "",
        stderr: str = "",
        exit_code: int = 0,
        command: Optional[str] = None,
    ) -> Optional[EnhancedDetectedError]:
        """
        Detect the most significant error from command output
        
        Args:
            stdout: Standard output
            stderr: Standard error
            exit_code: Exit code
            command: The command that was executed
            
        Returns:
            The most critical error found, or None
        """
        all_errors = self.detect_all(stdout, stderr, exit_code, command)
        
        if not all_errors:
            return None
        
        # Return the most critical error
        severity_order = [
            ErrorSeverity.CRITICAL,
            ErrorSeverity.HIGH,
            ErrorSeverity.MEDIUM,
            ErrorSeverity.LOW,
            ErrorSeverity.WARNING,
        ]
        
        for severity in severity_order:
            for error in all_errors:
                if error.severity == severity:
                    return error
        
        return all_errors[0]
    
    def detect_all(
        self,
        stdout: str = "",
        stderr: str = "",
        exit_code: int = 0,
        command: Optional[str] = None,
    ) -> List[EnhancedDetectedError]:
        """
        Detect all errors from command output
        
        Returns:
            List of all detected errors
        """
        errors = []
        combined_output = f"{stdout}\n{stderr}"
        
        # Check exit code first
        if exit_code != 0:
            # Try to match patterns
            for pattern, (error_type, severity) in self.ALL_PATTERNS.items():
                match = re.search(pattern, combined_output, re.MULTILINE | re.IGNORECASE)
                if match:
                    error = self._create_error(
                        error_type=error_type,
                        severity=severity,
                        match=match,
                        combined_output=combined_output,
                        exit_code=exit_code,
                        command=command,
                    )
                    errors.append(error)
            
            # If no patterns matched, create generic error
            if not errors:
                errors.append(EnhancedDetectedError(
                    error_type="unknown_error",
                    category=ErrorCategory.RUNTIME,
                    severity=ErrorSeverity.HIGH,
                    message=f"Command failed with exit code {exit_code}",
                    details=combined_output[-1000:],
                    exit_code=exit_code,
                    command=command,
                ))
        
        self.detected_errors.extend(errors)
        return errors
    
    def _create_error(
        self,
        error_type: str,
        severity: ErrorSeverity,
        match: re.Match,
        combined_output: str,
        exit_code: int,
        command: Optional[str],
    ) -> EnhancedDetectedError:
        """Create an error object from a pattern match"""
        
        # Determine category from error type
        category = self._get_category(error_type)
        
        # Get fix suggestion
        fix_info = self.FIX_SUGGESTIONS.get(error_type, {})
        suggested_fix = fix_info.get("suggestion")
        fix_command = fix_info.get("command")
        auto_fixable = fix_info.get("auto_fixable", False)
        
        # Handle command templates
        if "command_template" in fix_info:
            template = fix_info["command_template"]
            if error_type == "python_module_not_found" and match.groups():
                fix_command = template.format(module=match.group(1))
            elif error_type == "port_in_use" and match.groups():
                fix_command = template.format(port=match.group(1))
        
        # Extract file location if present
        file_path, line_number = self._extract_location(combined_output)
        
        # Extract stack trace if present
        stack_trace = self._extract_stack_trace(combined_output)
        
        return EnhancedDetectedError(
            error_type=error_type,
            category=category,
            severity=severity,
            message=match.group(0),
            details=combined_output[-500:],
            file_path=file_path,
            line_number=line_number,
            exit_code=exit_code,
            command=command,
            stack_trace=stack_trace,
            suggested_fix=suggested_fix,
            fix_command=fix_command,
            auto_fixable=auto_fixable,
        )
    
    def _get_category(self, error_type: str) -> ErrorCategory:
        """Determine error category from error type"""
        if error_type in [et[0] for et in self.BUILD_ERRORS.values()]:
            return ErrorCategory.BUILD
        elif error_type in [et[0] for et in self.RUNTIME_ERRORS.values()]:
            return ErrorCategory.RUNTIME
        elif error_type in [et[0] for et in self.DEPENDENCY_ERRORS.values()]:
            return ErrorCategory.DEPENDENCY
        elif error_type in [et[0] for et in self.CSS_ERRORS.values()]:
            return ErrorCategory.CSS
        elif error_type in [et[0] for et in self.FILE_SYSTEM_ERRORS.values()]:
            return ErrorCategory.FILE_SYSTEM
        elif error_type in [et[0] for et in self.COMMAND_ERRORS.values()]:
            return ErrorCategory.CONFIGURATION
        else:
            return ErrorCategory.RUNTIME
    
    def _extract_location(self, text: str) -> tuple:
        """Extract file path and line number from error text"""
        # Python traceback format
        py_match = re.search(r'File "([^"]+)", line (\d+)', text)
        if py_match:
            return py_match.group(1), int(py_match.group(2))
        
        # JavaScript/TypeScript format
        js_match = re.search(r'at (?:\w+\s+)?\(?([^:]+):(\d+)(?::(\d+))?\)?', text)
        if js_match:
            return js_match.group(1), int(js_match.group(2))
        
        # Generic file:line format
        generic_match = re.search(r'([^\s:]+):(\d+)', text)
        if generic_match:
            return generic_match.group(1), int(generic_match.group(2))
        
        return None, None
    
    def _extract_stack_trace(self, text: str) -> Optional[str]:
        """Extract stack trace from error output"""
        # Python traceback
        py_trace = re.search(
            r'(Traceback \(most recent call last\):.*?)(?=\n\n|\Z)',
            text,
            re.DOTALL
        )
        if py_trace:
            return py_trace.group(1)
        
        # JavaScript stack trace
        js_trace = re.search(
            r'((?:Error|TypeError|ReferenceError):.+?(?:\n\s+at .+)+)',
            text,
            re.DOTALL
        )
        if js_trace:
            return js_trace.group(1)
        
        return None


# =============================================================================
# CSS CLASS VALIDATOR
# =============================================================================

class CSSClassValidator:
    """
    Validates CSS class usage between JSX/TSX and CSS files
    Prevents the common issue of mismatched class names
    """
    
    @staticmethod
    def extract_jsx_classes(content: str) -> Set[str]:
        """Extract all className values from JSX/TSX content"""
        classes = set()
        
        # Pattern for className="..." or className='...'
        string_pattern = r'className\s*=\s*["\']([^"\']+)["\']'
        for match in re.finditer(string_pattern, content):
            for cls in match.group(1).split():
                if cls and not cls.startswith('$') and not cls.startswith('{'):
                    classes.add(cls)
        
        # Pattern for className={`...`} template literals
        template_pattern = r'className\s*=\s*\{`([^`]+)`\}'
        for match in re.finditer(template_pattern, content):
            # Extract static parts, ignore ${} expressions
            static_text = re.sub(r'\$\{[^}]+\}', ' ', match.group(1))
            for cls in static_text.split():
                if cls:
                    classes.add(cls)
        
        # Pattern for className={condition ? 'a' : 'b'}
        ternary_pattern = r'className\s*=\s*\{[^}]*["\']([^"\']+)["\'][^}]*\}'
        for match in re.finditer(ternary_pattern, content):
            for cls in match.group(1).split():
                if cls:
                    classes.add(cls)
        
        return classes
    
    @staticmethod
    def extract_css_classes(content: str) -> Set[str]:
        """Extract all class definitions from CSS content"""
        # Pattern for .classname
        pattern = r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)'
        matches = re.findall(pattern, content)
        return set(matches)
    
    @staticmethod
    def validate(jsx_content: str, css_content: str) -> Dict[str, Any]:
        """
        Validate that all classes used in JSX are defined in CSS
        
        Returns:
            Dict with validation results
        """
        jsx_classes = CSSClassValidator.extract_jsx_classes(jsx_content)
        css_classes = CSSClassValidator.extract_css_classes(css_content)
        
        # Classes used but not defined
        missing = jsx_classes - css_classes
        
        # Classes defined but not used
        unused = css_classes - jsx_classes
        
        # Filter out common utility class prefixes (might be from frameworks)
        utility_patterns = [
            r'^flex', r'^grid', r'^items-', r'^justify-', r'^gap-',
            r'^p-', r'^m-', r'^px-', r'^py-', r'^mx-', r'^my-',
            r'^pt-', r'^pb-', r'^pl-', r'^pr-',
            r'^mt-', r'^mb-', r'^ml-', r'^mr-',
            r'^w-', r'^h-', r'^min-', r'^max-',
            r'^text-', r'^font-', r'^bg-', r'^border-',
            r'^rounded', r'^shadow', r'^opacity-',
            r'^transition', r'^transform', r'^animate-',
            r'^cursor-', r'^select-', r'^overflow-',
            r'^z-', r'^top-', r'^right-', r'^bottom-', r'^left-',
            r'^absolute', r'^relative', r'^fixed', r'^sticky',
            r'^hidden', r'^block', r'^inline', r'^visible', r'^invisible',
        ]
        
        filtered_missing = set()
        for cls in missing:
            is_utility = any(re.match(pattern, cls) for pattern in utility_patterns)
            if not is_utility:
                filtered_missing.add(cls)
        
        return {
            'valid': len(filtered_missing) == 0,
            'missing_classes': sorted(list(filtered_missing)),
            'unused_classes': sorted(list(unused)),
            'jsx_classes_count': len(jsx_classes),
            'css_classes_count': len(css_classes),
            'all_jsx_classes': sorted(list(jsx_classes)),
            'all_css_classes': sorted(list(css_classes)),
        }
    
    @staticmethod
    def generate_missing_css(missing_classes: List[str]) -> str:
        """Generate placeholder CSS for missing classes"""
        if not missing_classes:
            return ""
        
        css_lines = ["\n/* Auto-generated styles for missing classes */"]
        
        for cls in missing_classes:
            # Generate intelligent defaults based on class name
            if 'btn' in cls.lower() or 'button' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-3) var(--spacing-5);
  font-weight: 600;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}}""")
            elif 'input' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  transition: border-color var(--transition-fast);
}}

.{cls}:focus {{
  outline: none;
  border-color: var(--color-primary);
}}""")
            elif 'card' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
}}""")
            elif 'list' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  list-style: none;
  padding: 0;
  margin: 0;
}}""")
            elif 'item' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--color-border);
}}

.{cls}:last-child {{
  border-bottom: none;
}}""")
            elif 'header' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  margin-bottom: var(--spacing-6);
}}""")
            elif 'footer' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  margin-top: var(--spacing-6);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--color-border);
}}""")
            elif 'section' in cls.lower() or 'container' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  margin-bottom: var(--spacing-6);
}}""")
            elif 'text' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  color: var(--color-text-primary);
}}""")
            elif 'title' in cls.lower() or 'heading' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  font-family: var(--font-heading);
  font-weight: 700;
  color: var(--color-text-primary);
}}""")
            elif 'checkbox' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  width: 20px;
  height: 20px;
  accent-color: var(--color-primary);
  cursor: pointer;
}}""")
            elif 'delete' in cls.lower() or 'remove' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color var(--transition-fast);
}}

.{cls}:hover {{
  color: var(--color-error);
}}""")
            elif 'active' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  background: var(--color-primary);
  color: white;
}}""")
            elif 'completed' in cls.lower() or 'done' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  opacity: 0.6;
  text-decoration: line-through;
}}""")
            elif 'filter' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  display: flex;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-4);
}}""")
            elif 'count' in cls.lower() or 'counter' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  color: var(--color-text-muted);
  font-size: 0.875rem;
}}""")
            elif 'clear' in cls.lower():
                css_lines.append(f"""
.{cls} {{
  color: var(--color-text-muted);
  background: none;
  border: none;
  cursor: pointer;
}}

.{cls}:hover {{
  color: var(--color-error);
}}""")
            else:
                # Generic fallback
                css_lines.append(f"""
.{cls} {{
  /* TODO: Add styles for .{cls} */
}}""")
        
        return "\n".join(css_lines)


# =============================================================================
# CODE QUALITY CHECKER
# =============================================================================

class CodeQualityChecker:
    """
    Checks generated code for common quality issues
    """
    
    @staticmethod
    def check_jsx(content: str) -> List[Dict[str, Any]]:
        """Check JSX content for common issues"""
        issues = []
        
        # Check for missing key prop in map
        if '.map(' in content and 'key=' not in content:
            issues.append({
                'type': 'missing_key_prop',
                'severity': 'warning',
                'message': 'Array.map() found without key prop - add key prop to list items',
            })
        
        # Check for console.log in production code
        if 'console.log' in content:
            issues.append({
                'type': 'console_log',
                'severity': 'warning',
                'message': 'console.log found - remove before production',
            })
        
        # Check for TODO comments
        todo_count = len(re.findall(r'//\s*TODO', content, re.IGNORECASE))
        if todo_count > 0:
            issues.append({
                'type': 'todo_comments',
                'severity': 'info',
                'message': f'{todo_count} TODO comment(s) found',
            })
        
        # Check for empty event handlers
        if re.search(r'on\w+\s*=\s*\{\s*\(\)\s*=>\s*\{\s*\}\s*\}', content):
            issues.append({
                'type': 'empty_handler',
                'severity': 'warning',
                'message': 'Empty event handler found',
            })
        
        # Check for inline styles (prefer CSS)
        inline_style_count = len(re.findall(r'style\s*=\s*\{\{', content))
        if inline_style_count > 5:
            issues.append({
                'type': 'too_many_inline_styles',
                'severity': 'info',
                'message': f'{inline_style_count} inline styles found - consider moving to CSS',
            })
        
        return issues
    
    @staticmethod
    def check_css(content: str) -> List[Dict[str, Any]]:
        """Check CSS content for common issues"""
        issues = []
        
        # Check for !important abuse
        important_count = content.count('!important')
        if important_count > 3:
            issues.append({
                'type': 'important_abuse',
                'severity': 'warning',
                'message': f'{important_count} uses of !important found - consider refactoring',
            })
        
        # Check for missing semicolons (common CSS error)
        # This is a simple heuristic
        lines = content.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.endswith(('{', '}', ';', '*/', '/*', '@')) and ':' in stripped:
                if not stripped.startswith(('@', '/*', '*', '//')):
                    issues.append({
                        'type': 'possibly_missing_semicolon',
                        'severity': 'warning',
                        'message': f'Line {i+1} may be missing semicolon',
                        'line': i + 1,
                    })
        
        # Check for hardcoded colors instead of variables
        hardcoded_colors = re.findall(r':\s*(#[0-9a-fA-F]{3,8}|rgb\([^)]+\))', content)
        if len(hardcoded_colors) > 10:
            issues.append({
                'type': 'hardcoded_colors',
                'severity': 'info',
                'message': f'{len(hardcoded_colors)} hardcoded colors found - consider using CSS variables',
            })
        
        # Check for very short CSS (likely incomplete)
        if len(content) < 200:
            issues.append({
                'type': 'minimal_css',
                'severity': 'warning',
                'message': 'CSS file is very short - may be incomplete',
            })
        
        return issues


# =============================================================================
# UNIFIED ERROR HANDLER
# =============================================================================

class ProductionErrorHandler:
    """
    Unified error handling for production-ready code generation
    Combines error detection, CSS validation, and code quality checks
    """
    
    def __init__(self):
        self.error_detector = EnhancedErrorDetector()
        self.css_validator = CSSClassValidator()
        self.quality_checker = CodeQualityChecker()
    
    def analyze_command_output(
        self,
        stdout: str,
        stderr: str,
        exit_code: int,
        command: str,
    ) -> Dict[str, Any]:
        """Analyze command output for errors"""
        error = self.error_detector.detect(stdout, stderr, exit_code, command)
        
        return {
            'has_error': error is not None,
            'error': error,
            'all_errors': self.error_detector.detected_errors,
        }
    
    def validate_generated_code(
        self,
        jsx_content: str,
        css_content: str,
    ) -> Dict[str, Any]:
        """Validate generated JSX and CSS"""
        # CSS class validation
        css_validation = self.css_validator.validate(jsx_content, css_content)
        
        # Code quality checks
        jsx_issues = self.quality_checker.check_jsx(jsx_content)
        css_issues = self.quality_checker.check_css(css_content)
        
        # Generate fix for missing CSS classes
        missing_css = ""
        if css_validation['missing_classes']:
            missing_css = self.css_validator.generate_missing_css(
                css_validation['missing_classes']
            )
        
        return {
            'css_valid': css_validation['valid'],
            'css_validation': css_validation,
            'jsx_issues': jsx_issues,
            'css_issues': css_issues,
            'generated_css_fix': missing_css,
            'total_issues': len(jsx_issues) + len(css_issues) + len(css_validation['missing_classes']),
        }
    
    def get_fix_suggestions(self, error: EnhancedDetectedError) -> Dict[str, Any]:
        """Get fix suggestions for an error"""
        return {
            'error_type': error.error_type,
            'suggested_fix': error.suggested_fix,
            'fix_command': error.fix_command,
            'auto_fixable': error.auto_fixable,
        }
