"""AST parser for code structure analysis."""

import ast
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from loguru import logger


@dataclass
class CodeSymbol:
    """Represents a code symbol (function, class, etc)."""
    name: str
    type: str  # 'function', 'class', 'method', 'import'
    file: str
    line: int
    end_line: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    parent: Optional[str] = None  # For methods, the class name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ASTParser:
    """Parse code to extract structure and symbols."""
    
    def __init__(self, workspace_path: str):
        """Initialize AST parser.
        
        Args:
            workspace_path: Path to workspace directory
        """
        self.workspace_path = Path(workspace_path)
        self.symbols_cache: Dict[str, List[CodeSymbol]] = {}
    
    def _parse_python_file(self, file_path: Path) -> List[CodeSymbol]:
        """Parse Python file and extract symbols.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of code symbols
        """
        symbols = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            rel_path = str(file_path.relative_to(self.workspace_path))
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        symbols.append(CodeSymbol(
                            name=alias.name,
                            type='import',
                            file=rel_path,
                            line=node.lineno,
                            end_line=node.lineno
                        ))
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        symbols.append(CodeSymbol(
                            name=f"{module}.{alias.name}" if module else alias.name,
                            type='import',
                            file=rel_path,
                            line=node.lineno,
                            end_line=node.lineno
                        ))
            
            # Extract classes and functions
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    # Get class docstring
                    docstring = ast.get_docstring(node)
                    
                    symbols.append(CodeSymbol(
                        name=node.name,
                        type='class',
                        file=rel_path,
                        line=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        docstring=docstring
                    ))
                    
                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_doc = ast.get_docstring(item)
                            
                            # Build method signature
                            args = []
                            for arg in item.args.args:
                                args.append(arg.arg)
                            signature = f"{item.name}({', '.join(args)})"
                            
                            symbols.append(CodeSymbol(
                                name=item.name,
                                type='method',
                                file=rel_path,
                                line=item.lineno,
                                end_line=item.end_lineno or item.lineno,
                                signature=signature,
                                docstring=method_doc,
                                parent=node.name
                            ))
                
                elif isinstance(node, ast.FunctionDef):
                    # Get function docstring
                    docstring = ast.get_docstring(node)
                    
                    # Build function signature
                    args = []
                    for arg in node.args.args:
                        args.append(arg.arg)
                    signature = f"{node.name}({', '.join(args)})"
                    
                    symbols.append(CodeSymbol(
                        name=node.name,
                        type='function',
                        file=rel_path,
                        line=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        signature=signature,
                        docstring=docstring
                    ))
        
        except SyntaxError as e:
            logger.warning(f"Syntax error parsing {file_path}: {e}")
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
        
        return symbols
    
    def _parse_javascript_file(self, file_path: Path) -> List[CodeSymbol]:
        """Parse JavaScript/TypeScript file (basic pattern matching).
        
        Note: This is a simple regex-based parser. For production,
        consider using proper JS/TS parsers like esprima or typescript compiler.
        
        Args:
            file_path: Path to JS/TS file
            
        Returns:
            List of code symbols
        """
        import re
        
        symbols = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            rel_path = str(file_path.relative_to(self.workspace_path))
            lines = content.split('\n')
            
            # Pattern for function declarations
            func_pattern = re.compile(
                r'^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\('
            )
            
            # Pattern for arrow functions
            arrow_pattern = re.compile(
                r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>'
            )
            
            # Pattern for class declarations
            class_pattern = re.compile(
                r'^\s*(?:export\s+)?class\s+(\w+)'
            )
            
            # Pattern for imports
            import_pattern = re.compile(
                r'^\s*import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
            )
            
            for i, line in enumerate(lines, 1):
                # Check for functions
                func_match = func_pattern.match(line)
                if func_match:
                    symbols.append(CodeSymbol(
                        name=func_match.group(1),
                        type='function',
                        file=rel_path,
                        line=i,
                        end_line=i,
                        signature=func_match.group(0).strip()
                    ))
                
                # Check for arrow functions
                arrow_match = arrow_pattern.match(line)
                if arrow_match:
                    symbols.append(CodeSymbol(
                        name=arrow_match.group(1),
                        type='function',
                        file=rel_path,
                        line=i,
                        end_line=i,
                        signature=arrow_match.group(0).strip()
                    ))
                
                # Check for classes
                class_match = class_pattern.match(line)
                if class_match:
                    symbols.append(CodeSymbol(
                        name=class_match.group(1),
                        type='class',
                        file=rel_path,
                        line=i,
                        end_line=i
                    ))
                
                # Check for imports
                import_match = import_pattern.match(line)
                if import_match:
                    symbols.append(CodeSymbol(
                        name=import_match.group(1),
                        type='import',
                        file=rel_path,
                        line=i,
                        end_line=i
                    ))
        
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
        
        return symbols
    
    def parse_file(self, file_path: Path) -> List[CodeSymbol]:
        """Parse a file and extract symbols.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of code symbols
        """
        if file_path.suffix == '.py':
            return self._parse_python_file(file_path)
        elif file_path.suffix in {'.js', '.ts', '.jsx', '.tsx'}:
            return self._parse_javascript_file(file_path)
        else:
            return []
    
    def parse_workspace(self) -> Dict[str, List[CodeSymbol]]:
        """Parse all code files in workspace.
        
        Returns:
            Dictionary mapping file paths to symbols
        """
        all_symbols = {}
        
        # Patterns to ignore
        ignore_patterns = {
            'node_modules', 'venv', 'env', '__pycache__', '.git',
            'dist', 'build', '.next', 'coverage'
        }
        
        for file_path in self.workspace_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Check ignore patterns
            if any(pattern in file_path.parts for pattern in ignore_patterns):
                continue
            
            # Check if supported file type
            if file_path.suffix not in {'.py', '.js', '.ts', '.jsx', '.tsx'}:
                continue
            
            symbols = self.parse_file(file_path)
            if symbols:
                rel_path = str(file_path.relative_to(self.workspace_path))
                all_symbols[rel_path] = symbols
        
        self.symbols_cache = all_symbols
        return all_symbols
    
    def find_symbol(
        self,
        name: str,
        symbol_type: Optional[str] = None
    ) -> List[CodeSymbol]:
        """Find symbols by name.
        
        Args:
            name: Symbol name to search for
            symbol_type: Optional filter by type ('function', 'class', etc)
            
        Returns:
            List of matching symbols
        """
        if not self.symbols_cache:
            self.parse_workspace()
        
        results = []
        for file_symbols in self.symbols_cache.values():
            for symbol in file_symbols:
                if name.lower() in symbol.name.lower():
                    if symbol_type is None or symbol.type == symbol_type:
                        results.append(symbol)
        
        return results
    
    def find_definitions(self, name: str) -> List[CodeSymbol]:
        """Find where a symbol is defined.
        
        Args:
            name: Symbol name
            
        Returns:
            List of definitions
        """
        if not self.symbols_cache:
            self.parse_workspace()
        
        results = []
        for file_symbols in self.symbols_cache.values():
            for symbol in file_symbols:
                if symbol.name == name and symbol.type in {'function', 'class'}:
                    results.append(symbol)
        
        return results
    
    def find_imports(self, module: str) -> List[CodeSymbol]:
        """Find all imports of a module.
        
        Args:
            module: Module name to search for
            
        Returns:
            List of import symbols
        """
        if not self.symbols_cache:
            self.parse_workspace()
        
        results = []
        for file_symbols in self.symbols_cache.values():
            for symbol in file_symbols:
                if symbol.type == 'import' and module in symbol.name:
                    results.append(symbol)
        
        return results
    
    def get_file_structure(self, file_path: str) -> List[CodeSymbol]:
        """Get structure of a specific file.
        
        Args:
            file_path: Relative path to file
            
        Returns:
            List of symbols in file
        """
        if not self.symbols_cache:
            self.parse_workspace()
        
        return self.symbols_cache.get(file_path, [])
