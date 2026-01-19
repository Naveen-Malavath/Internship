"""
Quality Assurance Pipeline
Validates generated code before deployment
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from loguru import logger


class QualityLevel(str, Enum):
    """Quality assessment levels"""
    EXCELLENT = "excellent"   # 90%+ score
    GOOD = "good"            # 70-89% score
    ACCEPTABLE = "acceptable" # 50-69% score
    POOR = "poor"            # Below 50%


@dataclass
class QualityIssue:
    """Represents a quality issue"""
    severity: str  # critical, high, medium, low, info
    category: str  # css, jsx, structure, style, functionality
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class QualityReport:
    """Quality assessment report"""
    score: float  # 0-100
    level: QualityLevel
    issues: List[QualityIssue]
    css_validation: Dict[str, Any]
    jsx_validation: Dict[str, Any]
    structure_validation: Dict[str, Any]
    passed: bool
    summary: str


class CSSValidator:
    """Validates CSS files for production quality"""
    
    REQUIRED_VARIABLES = [
        "--color-bg-primary",
        "--color-primary",
        "--color-text-primary",
        "--color-border",
        "--font-family",
        "--spacing",
        "--radius",
        "--shadow",
        "--transition",
    ]
    
    REQUIRED_SELECTORS = [
        "body",
        "*, *::before, *::after",
    ]
    
    @staticmethod
    def validate(css_content: str) -> Dict[str, Any]:
        """Validate CSS content"""
        issues = []
        
        # Check minimum length
        if len(css_content) < 500:
            issues.append(QualityIssue(
                severity="critical",
                category="css",
                message=f"CSS file is too short ({len(css_content)} chars). Minimum 500 chars required.",
                suggestion="Add comprehensive styling including variables, base styles, and component styles."
            ))
        
        # Check for CSS variables
        has_root = ":root" in css_content
        if not has_root:
            issues.append(QualityIssue(
                severity="high",
                category="css",
                message="Missing :root block with CSS variables",
                suggestion="Add :root { } block with color, spacing, and typography variables."
            ))
        
        # Check for required variables
        missing_vars = []
        for var in CSSValidator.REQUIRED_VARIABLES:
            if var not in css_content:
                missing_vars.append(var)
        
        if missing_vars:
            issues.append(QualityIssue(
                severity="medium",
                category="css",
                message=f"Missing CSS variables: {', '.join(missing_vars[:5])}",
                suggestion="Add design tokens for colors, spacing, typography."
            ))
        
        # Check for box-sizing reset
        if "box-sizing: border-box" not in css_content:
            issues.append(QualityIssue(
                severity="medium",
                category="css",
                message="Missing box-sizing reset",
                suggestion="Add '*, *::before, *::after { box-sizing: border-box; }'"
            ))
        
        # Check for hover states
        hover_count = css_content.count(":hover")
        if hover_count < 3:
            issues.append(QualityIssue(
                severity="medium",
                category="css",
                message=f"Too few hover states ({hover_count}). Interactive elements need hover styles.",
                suggestion="Add :hover states for buttons, links, and interactive elements."
            ))
        
        # Check for transitions
        transition_count = css_content.count("transition")
        if transition_count < 3:
            issues.append(QualityIssue(
                severity="medium",
                category="css",
                message=f"Too few transitions ({transition_count}). Add smooth animations.",
                suggestion="Add CSS transitions for color, transform, and opacity changes."
            ))
        
        # Check for responsive design
        has_media_queries = "@media" in css_content
        if not has_media_queries:
            issues.append(QualityIssue(
                severity="medium",
                category="css",
                message="No responsive breakpoints found",
                suggestion="Add @media queries for mobile and tablet views."
            ))
        
        # Check for animations
        has_keyframes = "@keyframes" in css_content
        if not has_keyframes:
            issues.append(QualityIssue(
                severity="low",
                category="css",
                message="No CSS animations defined",
                suggestion="Add @keyframes animations for entrance effects."
            ))
        
        # Check for hardcoded colors
        hardcoded_colors = re.findall(r':\s*#[0-9a-fA-F]{3,8}(?![^{]*var\()', css_content)
        # Filter out colors in :root block
        root_match = re.search(r':root\s*\{[^}]+\}', css_content, re.DOTALL)
        root_colors = len(re.findall(r'#[0-9a-fA-F]{3,8}', root_match.group(0))) if root_match else 0
        non_root_colors = len(hardcoded_colors) - root_colors
        
        if non_root_colors > 10:
            issues.append(QualityIssue(
                severity="info",
                category="css",
                message=f"Many hardcoded colors outside :root ({non_root_colors}). Consider using CSS variables.",
                suggestion="Use var(--color-name) instead of hardcoded hex values."
            ))
        
        # Calculate score
        critical_issues = sum(1 for i in issues if i.severity == "critical")
        high_issues = sum(1 for i in issues if i.severity == "high")
        medium_issues = sum(1 for i in issues if i.severity == "medium")
        low_issues = sum(1 for i in issues if i.severity == "low")
        
        score = 100 - (critical_issues * 30) - (high_issues * 15) - (medium_issues * 5) - (low_issues * 2)
        score = max(0, min(100, score))
        
        return {
            "valid": len([i for i in issues if i.severity in ["critical", "high"]]) == 0,
            "score": score,
            "issues": issues,
            "metrics": {
                "length": len(css_content),
                "variables_count": css_content.count("var(--"),
                "hover_states": hover_count,
                "transitions": transition_count,
                "has_media_queries": has_media_queries,
                "has_animations": has_keyframes,
            }
        }


class JSXValidator:
    """Validates JSX/React files for production quality"""
    
    @staticmethod
    def validate(jsx_content: str) -> Dict[str, Any]:
        """Validate JSX content"""
        issues = []
        
        # Check for key prop in maps
        has_map = ".map(" in jsx_content
        has_key = "key=" in jsx_content
        if has_map and not has_key:
            issues.append(QualityIssue(
                severity="high",
                category="jsx",
                message="Array.map() found without key prop",
                suggestion="Add unique key prop to each item: key={item.id}"
            ))
        
        # Check for console.log
        console_count = jsx_content.count("console.log")
        if console_count > 0:
            issues.append(QualityIssue(
                severity="low",
                category="jsx",
                message=f"Found {console_count} console.log statements",
                suggestion="Remove console.log before production."
            ))
        
        # Check for empty event handlers
        if re.search(r'on\w+\s*=\s*\{\s*\(\)\s*=>\s*\{\s*\}\s*\}', jsx_content):
            issues.append(QualityIssue(
                severity="medium",
                category="jsx",
                message="Empty event handler found",
                suggestion="Implement the event handler or remove it."
            ))
        
        # Check for proper component structure
        if "export default" not in jsx_content:
            issues.append(QualityIssue(
                severity="high",
                category="jsx",
                message="Missing export default",
                suggestion="Add 'export default ComponentName' at the end."
            ))
        
        # Check for CSS import
        if "import" in jsx_content and ".css" not in jsx_content:
            issues.append(QualityIssue(
                severity="medium",
                category="jsx",
                message="No CSS import found",
                suggestion="Import the component's CSS file: import './Component.css'"
            ))
        
        # Check for proper state management
        if "useState" in jsx_content and "const [" not in jsx_content:
            issues.append(QualityIssue(
                severity="medium",
                category="jsx",
                message="useState imported but may not be used correctly",
                suggestion="Use destructuring: const [state, setState] = useState()"
            ))
        
        # Calculate score
        critical_issues = sum(1 for i in issues if i.severity == "critical")
        high_issues = sum(1 for i in issues if i.severity == "high")
        medium_issues = sum(1 for i in issues if i.severity == "medium")
        
        score = 100 - (critical_issues * 30) - (high_issues * 15) - (medium_issues * 5)
        score = max(0, min(100, score))
        
        return {
            "valid": len([i for i in issues if i.severity in ["critical", "high"]]) == 0,
            "score": score,
            "issues": issues,
        }


class CSSClassMatcher:
    """Validates CSS class matching between JSX and CSS"""
    
    @staticmethod
    def extract_jsx_classes(jsx_content: str) -> set:
        """Extract className values from JSX"""
        classes = set()
        
        # className="..."
        for match in re.finditer(r'className\s*=\s*["\']([^"\']+)["\']', jsx_content):
            for cls in match.group(1).split():
                if cls and not cls.startswith('$'):
                    classes.add(cls)
        
        # className={`...`}
        for match in re.finditer(r'className\s*=\s*\{`([^`]+)`\}', jsx_content):
            static_text = re.sub(r'\$\{[^}]+\}', ' ', match.group(1))
            for cls in static_text.split():
                if cls:
                    classes.add(cls)
        
        # className={condition ? 'a' : 'b'}
        for match in re.finditer(r'className\s*=\s*\{[^}]*["\']([^"\']+)["\'][^}]*\}', jsx_content):
            for cls in match.group(1).split():
                if cls:
                    classes.add(cls)
        
        return classes
    
    @staticmethod
    def extract_css_classes(css_content: str) -> set:
        """Extract class definitions from CSS"""
        pattern = r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)'
        matches = re.findall(pattern, css_content)
        return set(matches)
    
    @staticmethod
    def validate(jsx_content: str, css_content: str) -> Dict[str, Any]:
        """Validate CSS class matching"""
        jsx_classes = CSSClassMatcher.extract_jsx_classes(jsx_content)
        css_classes = CSSClassMatcher.extract_css_classes(css_content)
        
        missing = jsx_classes - css_classes
        unused = css_classes - jsx_classes
        
        # Filter utility classes
        utility_prefixes = ['flex', 'grid', 'items-', 'justify-', 'gap-', 'p-', 'm-', 
                          'w-', 'h-', 'text-', 'bg-', 'border-', 'rounded', 'shadow']
        
        filtered_missing = {
            cls for cls in missing 
            if not any(cls.startswith(p) for p in utility_prefixes)
        }
        
        issues = []
        for cls in filtered_missing:
            issues.append(QualityIssue(
                severity="critical",
                category="css",
                message=f"CSS class '{cls}' used in JSX but not defined in CSS",
                suggestion=f"Add '.{cls} {{ }}' to your CSS file with appropriate styles.",
                auto_fixable=True
            ))
        
        return {
            "valid": len(filtered_missing) == 0,
            "missing_classes": list(filtered_missing),
            "unused_classes": list(unused),
            "issues": issues,
            "jsx_classes": list(jsx_classes),
            "css_classes": list(css_classes),
        }
    
    @staticmethod
    def generate_missing_css(missing_classes: List[str]) -> str:
        """Generate CSS for missing classes"""
        if not missing_classes:
            return ""
        
        css_lines = ["\n/* === Auto-generated styles for missing classes === */\n"]
        
        for cls in missing_classes:
            # Generate intelligent defaults based on class name patterns
            if any(x in cls.lower() for x in ['btn', 'button']):
                css_lines.append(f'''.{cls} {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-3) var(--spacing-5);
  font-weight: 600;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}}

.{cls}:hover {{
  transform: translateY(-1px);
}}
''')
            elif any(x in cls.lower() for x in ['input', 'field', 'textbox']):
                css_lines.append(f'''.{cls} {{
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  transition: border-color var(--transition-fast);
}}

.{cls}:focus {{
  outline: none;
  border-color: var(--color-primary);
}}
''')
            elif any(x in cls.lower() for x in ['card', 'box', 'panel']):
                css_lines.append(f'''.{cls} {{
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
}}
''')
            elif any(x in cls.lower() for x in ['list']):
                css_lines.append(f'''.{cls} {{
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}}
''')
            elif any(x in cls.lower() for x in ['item']):
                css_lines.append(f'''.{cls} {{
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}}

.{cls}:hover {{
  border-color: var(--color-border-hover);
}}
''')
            elif any(x in cls.lower() for x in ['header', 'title']):
                css_lines.append(f'''.{cls} {{
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-4);
}}
''')
            elif any(x in cls.lower() for x in ['footer']):
                css_lines.append(f'''.{cls} {{
  margin-top: var(--spacing-6);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--color-border);
}}
''')
            elif any(x in cls.lower() for x in ['section', 'container', 'wrapper']):
                css_lines.append(f'''.{cls} {{
  margin-bottom: var(--spacing-6);
}}
''')
            elif any(x in cls.lower() for x in ['text', 'label']):
                css_lines.append(f'''.{cls} {{
  color: var(--color-text-primary);
}}
''')
            elif any(x in cls.lower() for x in ['checkbox', 'check']):
                css_lines.append(f'''.{cls} {{
  width: 20px;
  height: 20px;
  accent-color: var(--color-primary);
  cursor: pointer;
}}
''')
            elif any(x in cls.lower() for x in ['delete', 'remove', 'close']):
                css_lines.append(f'''.{cls} {{
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: color var(--transition-fast);
}}

.{cls}:hover {{
  color: var(--color-error);
}}
''')
            elif any(x in cls.lower() for x in ['active', 'selected']):
                css_lines.append(f'''.{cls} {{
  background: var(--color-primary);
  color: white;
}}
''')
            elif any(x in cls.lower() for x in ['completed', 'done', 'checked']):
                css_lines.append(f'''.{cls} {{
  opacity: 0.6;
  text-decoration: line-through;
}}
''')
            elif any(x in cls.lower() for x in ['filter', 'tab']):
                css_lines.append(f'''.{cls} {{
  display: flex;
  gap: var(--spacing-2);
}}
''')
            elif any(x in cls.lower() for x in ['count', 'badge', 'counter']):
                css_lines.append(f'''.{cls} {{
  color: var(--color-text-muted);
  font-size: 0.875rem;
}}
''')
            elif any(x in cls.lower() for x in ['empty', 'placeholder']):
                css_lines.append(f'''.{cls} {{
  text-align: center;
  padding: var(--spacing-8);
  color: var(--color-text-muted);
}}
''')
            elif any(x in cls.lower() for x in ['icon']):
                css_lines.append(f'''.{cls} {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
}}
''')
            elif any(x in cls.lower() for x in ['app', 'root', 'main']):
                css_lines.append(f'''.{cls} {{
  min-height: 100vh;
  background: var(--color-bg-primary);
}}
''')
            else:
                css_lines.append(f'''.{cls} {{
  /* Add styles for .{cls} */
}}
''')
        
        return "".join(css_lines)


class QualityAssurancePipeline:
    """
    Complete quality assurance pipeline for generated code
    """
    
    def __init__(self):
        self.css_validator = CSSValidator()
        self.jsx_validator = JSXValidator()
        self.class_matcher = CSSClassMatcher()
    
    def validate_project(
        self,
        files: Dict[str, str]
    ) -> QualityReport:
        """
        Validate an entire project
        
        Args:
            files: Dict of {filepath: content}
            
        Returns:
            QualityReport with assessment
        """
        all_issues = []
        css_results = {}
        jsx_results = {}
        structure_results = {"has_package_json": False, "has_index_html": False}
        
        # Find CSS and JSX files
        css_files = {k: v for k, v in files.items() if k.endswith('.css')}
        jsx_files = {k: v for k, v in files.items() if k.endswith(('.jsx', '.tsx', '.js'))}
        
        # Validate structure
        structure_results["has_package_json"] = any("package.json" in f for f in files)
        structure_results["has_index_html"] = any("index.html" in f for f in files)
        
        if not structure_results["has_package_json"]:
            all_issues.append(QualityIssue(
                severity="critical",
                category="structure",
                message="Missing package.json",
                suggestion="Add package.json with dependencies."
            ))
        
        # Validate each CSS file
        for filepath, content in css_files.items():
            result = self.css_validator.validate(content)
            css_results[filepath] = result
            all_issues.extend(result["issues"])
        
        # Validate each JSX file
        for filepath, content in jsx_files.items():
            result = self.jsx_validator.validate(content)
            jsx_results[filepath] = result
            all_issues.extend(result["issues"])
        
        # Cross-validate CSS classes
        all_jsx = "\n".join(jsx_files.values())
        all_css = "\n".join(css_files.values())
        
        class_validation = self.class_matcher.validate(all_jsx, all_css)
        all_issues.extend(class_validation["issues"])
        
        # Calculate overall score
        critical = sum(1 for i in all_issues if i.severity == "critical")
        high = sum(1 for i in all_issues if i.severity == "high")
        medium = sum(1 for i in all_issues if i.severity == "medium")
        low = sum(1 for i in all_issues if i.severity == "low")
        
        score = 100 - (critical * 25) - (high * 10) - (medium * 3) - (low * 1)
        score = max(0, min(100, score))
        
        # Determine level
        if score >= 90:
            level = QualityLevel.EXCELLENT
        elif score >= 70:
            level = QualityLevel.GOOD
        elif score >= 50:
            level = QualityLevel.ACCEPTABLE
        else:
            level = QualityLevel.POOR
        
        # Generate summary
        summary_parts = []
        if critical > 0:
            summary_parts.append(f"{critical} critical issues")
        if high > 0:
            summary_parts.append(f"{high} high priority issues")
        if medium > 0:
            summary_parts.append(f"{medium} medium issues")
        
        summary = f"Score: {score}/100 ({level.value}). "
        if summary_parts:
            summary += "Found: " + ", ".join(summary_parts) + "."
        else:
            summary += "No major issues found."
        
        return QualityReport(
            score=score,
            level=level,
            issues=all_issues,
            css_validation=css_results,
            jsx_validation=jsx_results,
            structure_validation=structure_results,
            passed=critical == 0 and high == 0,
            summary=summary
        )
    
    def auto_fix(
        self,
        files: Dict[str, str],
        report: QualityReport
    ) -> Dict[str, str]:
        """
        Attempt to auto-fix issues
        
        Args:
            files: Original files
            report: Quality report
            
        Returns:
            Fixed files
        """
        fixed_files = dict(files)
        
        # Fix missing CSS classes
        if report.css_validation:
            all_jsx = "\n".join(v for k, v in files.items() if k.endswith(('.jsx', '.tsx')))
            all_css = "\n".join(v for k, v in files.items() if k.endswith('.css'))
            
            class_match = self.class_matcher.validate(all_jsx, all_css)
            
            if class_match["missing_classes"]:
                # Find the main CSS file
                main_css_path = None
                for path in files:
                    if path.endswith('App.css'):
                        main_css_path = path
                        break
                
                if main_css_path:
                    additional_css = self.class_matcher.generate_missing_css(
                        class_match["missing_classes"]
                    )
                    fixed_files[main_css_path] = files[main_css_path] + additional_css
                    logger.info(f"Auto-fixed {len(class_match['missing_classes'])} missing CSS classes")
        
        return fixed_files
    
    def get_fix_suggestions(self, report: QualityReport) -> List[str]:
        """Get prioritized fix suggestions"""
        suggestions = []
        
        # Sort issues by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_issues = sorted(
            report.issues,
            key=lambda x: severity_order.get(x.severity, 5)
        )
        
        for issue in sorted_issues[:10]:  # Top 10 issues
            if issue.suggestion:
                suggestions.append(f"[{issue.severity.upper()}] {issue.message}: {issue.suggestion}")
        
        return suggestions
