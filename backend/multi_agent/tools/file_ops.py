"""File operations tool for creating, reading, updating, and deleting files
With automatic CSS validation and injection for React apps"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Set, List

import aiofiles

from .base import Tool, ToolParameter

logger = logging.getLogger(__name__)


# =============================================================================
# PRODUCTION CSS TEMPLATES - Injected when LLM CSS is insufficient
# =============================================================================

BASE_CSS_TEMPLATE = '''/* ============================================
   AUTO-INJECTED PRODUCTION STYLES
   ============================================ */

:root {
  --color-bg-primary: #0a0a0f;
  --color-bg-secondary: #12121a;
  --color-bg-card: #16161f;
  --color-bg-hover: #1e1e28;
  
  --color-primary: #6366f1;
  --color-primary-hover: #818cf8;
  --color-primary-glow: rgba(99, 102, 241, 0.3);
  
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  
  --color-text-primary: #f8fafc;
  --color-text-secondary: #94a3b8;
  --color-text-muted: #64748b;
  
  --color-border: #2d2d3a;
  --color-border-hover: #3d3d4a;
  
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
  
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
}

*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  line-height: 1.6;
  min-height: 100vh;
}

h1, h2, h3, h4, h5, h6 {
  color: var(--color-text-primary);
  font-weight: 700;
}

button {
  font-family: var(--font-family);
  cursor: pointer;
}

input {
  font-family: var(--font-family);
}

/* App Container */
.App, .app {
  min-height: 100vh;
  padding: var(--spacing-8);
  background: radial-gradient(ellipse at top, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
              var(--color-bg-primary);
}

'''

# CSS class patterns for common component types
CSS_CLASS_PATTERNS = {
    'container': '''
.{cls} {{
  max-width: 600px;
  margin: 0 auto;
  padding: var(--spacing-6);
}}
''',
    'input': '''
.{cls} {{
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  font-size: 1rem;
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  outline: none;
  transition: all var(--transition-fast);
}}

.{cls}:focus {{
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}}

.{cls}::placeholder {{
  color: var(--color-text-muted);
}}
''',
    'button': '''
.{cls} {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-3) var(--spacing-5);
  font-size: 0.9375rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, var(--color-primary) 0%, #8b5cf6 100%);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 0 20px var(--color-primary-glow);
}}

.{cls}:hover {{
  transform: translateY(-2px);
  box-shadow: 0 0 30px var(--color-primary-glow);
}}
''',
    'section': '''
.{cls} {{
  display: flex;
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-6);
}}
''',
    'list': '''
.{cls} {{
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}}
''',
    'item': '''
.{cls} {{
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}}

.{cls}:hover {{
  border-color: var(--color-border-hover);
  transform: translateX(4px);
}}
''',
    'checkbox': '''
.{cls} {{
  width: 20px;
  height: 20px;
  accent-color: var(--color-primary);
  cursor: pointer;
}}
''',
    'text': '''
.{cls} {{
  flex: 1;
  font-size: 1rem;
  color: var(--color-text-primary);
}}
''',
    'delete': '''
.{cls} {{
  padding: var(--spacing-2);
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  opacity: 0.5;
}}

.{cls}:hover {{
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
  opacity: 1;
}}
''',
    'filter': '''
.{cls} {{
  display: flex;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-2);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
}}

.{cls} button {{
  flex: 1;
  padding: var(--spacing-3);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}}

.{cls} button:hover {{
  color: var(--color-text-primary);
}}

.{cls} button.active {{
  background: var(--color-bg-card);
  color: var(--color-primary);
  box-shadow: var(--shadow-md);
}}
''',
    'footer': '''
.{cls} {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-6);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--color-border);
  color: var(--color-text-muted);
  font-size: 0.875rem;
}}
''',
    'count': '''
.{cls} {{
  color: var(--color-text-muted);
  font-size: 0.875rem;
}}
''',
    'clear': '''
.{cls} {{
  padding: var(--spacing-2) var(--spacing-3);
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}}

.{cls}:hover {{
  color: var(--color-error);
  background: rgba(239, 68, 68, 0.1);
}}
''',
    'completed': '''
.completed, .{cls}.completed {{
  opacity: 0.6;
}}

.completed .todo-text, .{cls} .todo-text {{
  text-decoration: line-through;
  color: var(--color-text-muted);
}}
''',
    'active': '''
.active, .{cls}.active {{
  background: var(--color-bg-card);
  color: var(--color-primary);
}}
''',
    'default': '''
.{cls} {{
  /* Auto-generated style for {cls} */
}}
'''
}


class CSSInjector:
    """Automatically validates and injects CSS for React components"""
    
    @staticmethod
    def extract_jsx_classes(jsx_content: str) -> Set[str]:
        """Extract all className values from JSX"""
        classes = set()
        
        # className="..."
        for match in re.finditer(r'className\s*=\s*["\']([^"\']+)["\']', jsx_content):
            for cls in match.group(1).split():
                if cls and not cls.startswith('$'):
                    classes.add(cls)
        
        # className={`...`} template literals
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
    def extract_css_classes(css_content: str) -> Set[str]:
        """Extract all class definitions from CSS"""
        pattern = r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)'
        return set(re.findall(pattern, css_content))
    
    @staticmethod
    def get_class_type(class_name: str) -> str:
        """Determine the type of component based on class name"""
        name_lower = class_name.lower()
        
        if any(x in name_lower for x in ['input', 'field', 'textbox']):
            return 'input'
        elif any(x in name_lower for x in ['btn', 'button']):
            return 'button'
        elif any(x in name_lower for x in ['container', 'wrapper', 'box']):
            return 'container'
        elif any(x in name_lower for x in ['section', 'row', 'group']):
            return 'section'
        elif any(x in name_lower for x in ['list', 'items']):
            return 'list'
        elif any(x in name_lower for x in ['item', 'card', 'entry']):
            return 'item'
        elif any(x in name_lower for x in ['checkbox', 'check', 'toggle']):
            return 'checkbox'
        elif any(x in name_lower for x in ['text', 'label', 'title']):
            return 'text'
        elif any(x in name_lower for x in ['delete', 'remove', 'close']):
            return 'delete'
        elif any(x in name_lower for x in ['filter', 'tab', 'nav']):
            return 'filter'
        elif any(x in name_lower for x in ['footer', 'bottom']):
            return 'footer'
        elif any(x in name_lower for x in ['count', 'counter', 'badge']):
            return 'count'
        elif any(x in name_lower for x in ['clear', 'reset']):
            return 'clear'
        elif 'completed' in name_lower or 'done' in name_lower:
            return 'completed'
        elif 'active' in name_lower or 'selected' in name_lower:
            return 'active'
        else:
            return 'default'
    
    @staticmethod
    def generate_css_for_class(class_name: str) -> str:
        """Generate CSS for a specific class name"""
        class_type = CSSInjector.get_class_type(class_name)
        template = CSS_CLASS_PATTERNS.get(class_type, CSS_CLASS_PATTERNS['default'])
        return template.format(cls=class_name)
    
    @staticmethod
    def inject_missing_styles(css_content: str, jsx_content: str) -> str:
        """Inject missing CSS styles based on JSX classNames"""
        jsx_classes = CSSInjector.extract_jsx_classes(jsx_content)
        css_classes = CSSInjector.extract_css_classes(css_content)
        
        missing_classes = jsx_classes - css_classes
        
        if not missing_classes:
            return css_content
        
        logger.info(f"[CSS_INJECTOR] Found {len(missing_classes)} missing classes: {missing_classes}")
        
        # Generate CSS for missing classes
        injected_css = "\n\n/* ============================================\n"
        injected_css += "   AUTO-INJECTED STYLES FOR MISSING CLASSES\n"
        injected_css += "   ============================================ */\n"
        
        for cls in sorted(missing_classes):
            injected_css += CSSInjector.generate_css_for_class(cls)
        
        return css_content + injected_css
    
    @staticmethod
    def ensure_base_styles(css_content: str) -> str:
        """Ensure CSS has base styles and variables"""
        # Check if CSS has minimum requirements
        has_root = ':root' in css_content
        has_reset = 'box-sizing' in css_content
        has_body = 'body {' in css_content or 'body{' in css_content
        
        if has_root and has_reset and has_body and len(css_content) > 500:
            return css_content
        
        # Inject base template
        logger.info("[CSS_INJECTOR] Injecting base CSS template")
        return BASE_CSS_TEMPLATE + "\n" + css_content


class FileOperationsTool(Tool):
    """Tool for file system operations"""

    name = "file_operations"
    description = "Create, read, update, delete, and list files and directories"
    parameters = [
        ToolParameter(
            name="operation",
            type="string",
            description="Operation to perform: create, read, update, delete, list",
            required=True,
            enum=["create", "read", "update", "delete", "list"],
        ),
        ToolParameter(
            name="path",
            type="string",
            description="File or directory path",
            required=True,
        ),
        ToolParameter(
            name="content",
            type="string",
            description="File content for create/update operations",
            required=False,
        ),
    ]

    def __init__(self, workspace_path: Optional[Path] = None):
        """Initialize file operations tool"""
        self.workspace_path = workspace_path or Path.cwd()
        logger.info(f"[FILE_OPS] Initialized with workspace: {self.workspace_path}")

    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to workspace"""
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = self.workspace_path / path_obj
        return path_obj.resolve()

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute file operation"""
        operation = kwargs.get("operation")
        path = kwargs.get("path")

        if not operation or not path:
            return {
                "success": False,
                "error": "Missing required parameters: operation and path",
            }

        logger.info(f"[FILE_OPS] {operation} on {path}")

        try:
            if operation == "create":
                return await self._create_file(path, kwargs.get("content", ""))
            elif operation == "read":
                return await self._read_file(path)
            elif operation == "update":
                return await self._update_file(path, kwargs.get("content", ""))
            elif operation == "delete":
                return await self._delete_file(path)
            elif operation == "list":
                return await self._list_directory(path)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            logger.error(f"[FILE_OPS] Error: {e}")
            return {"success": False, "error": str(e)}

    async def _create_file(self, path: str, content: str) -> Dict[str, Any]:
        """Create a new file with content"""
        file_path = self._resolve_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)

        logger.info(f"[FILE_OPS] Created: {file_path}")
        
        result = {
            "success": True,
            "result": f"File created: {file_path}",
            "path": str(file_path),
        }
        
        # For JSX/TSX files, extract and include classNames so LLM remembers them for CSS
        if path.endswith(('.jsx', '.tsx', '.js')):
            import re
            classes = set()
            for match in re.finditer(r'className\s*=\s*["\']([^"\']+)["\']', content):
                for cls in match.group(1).split():
                    classes.add(cls)
            if classes:
                result["classNames_used"] = sorted(list(classes))
                result["css_reminder"] = f"IMPORTANT: When creating the CSS file, you MUST include styles for these classes: {', '.join(sorted(classes))}"
        
        # For CSS files, check if corresponding JSX exists and validate class coverage
        if path.endswith('.css'):
            import re
            # Find corresponding JSX file
            jsx_path = path.replace('.css', '.jsx')
            jsx_file = self._resolve_path(jsx_path)
            
            if jsx_file.exists():
                try:
                    jsx_content = jsx_file.read_text(encoding='utf-8')
                    
                    # Extract classes from JSX
                    jsx_classes = set()
                    for match in re.finditer(r'className\s*=\s*["\']([^"\']+)["\']', jsx_content):
                        for cls in match.group(1).split():
                            jsx_classes.add(cls)
                    
                    # Extract classes from CSS
                    css_classes = set(re.findall(r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)', content))
                    
                    # Find missing classes
                    missing = jsx_classes - css_classes
                    
                    if missing:
                        result["warning"] = f"MISSING CSS CLASSES! The following classes are used in {jsx_path} but NOT defined in CSS: {', '.join(sorted(missing))}. Please UPDATE the CSS file to include styles for ALL these classes."
                        result["missing_classes"] = sorted(list(missing))
                        logger.warning(f"[FILE_OPS] CSS missing classes: {missing}")
                    
                    # Check CSS quality
                    if len(content) < 500:
                        result["quality_warning"] = f"CSS file is too short ({len(content)} chars). Production CSS should have comprehensive styles with :root variables, resets, and component styles."
                        
                except Exception as e:
                    logger.error(f"[FILE_OPS] Error checking CSS: {e}")
        
        return result

    async def _read_file(self, path: str) -> Dict[str, Any]:
        """Read file content"""
        file_path = self._resolve_path(path)

        if not file_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()

        return {
            "success": True,
            "result": content,
            "path": str(file_path),
        }

    async def _update_file(self, path: str, content: str) -> Dict[str, Any]:
        """Update existing file content"""
        file_path = self._resolve_path(path)

        # Create if doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)

        logger.info(f"[FILE_OPS] Updated: {file_path}")
        return {
            "success": True,
            "result": f"File updated: {file_path}",
            "path": str(file_path),
        }

    async def _delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file"""
        file_path = self._resolve_path(path)

        if not file_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        if file_path.is_file():
            file_path.unlink()
        elif file_path.is_dir():
            try:
                file_path.rmdir()
            except OSError:
                return {
                    "success": False,
                    "error": f"Directory not empty: {file_path}",
                }

        return {"success": True, "result": f"Deleted: {file_path}"}

    async def _list_directory(self, path: str) -> Dict[str, Any]:
        """List directory contents"""
        dir_path = self._resolve_path(path)

        if not dir_path.exists():
            return {"success": False, "error": f"Directory not found: {dir_path}"}

        if not dir_path.is_dir():
            return {"success": False, "error": f"Not a directory: {dir_path}"}

        items = []
        for item in dir_path.iterdir():
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0,
            })

        return {
            "success": True,
            "result": items,
            "path": str(dir_path),
            "count": len(items),
        }
