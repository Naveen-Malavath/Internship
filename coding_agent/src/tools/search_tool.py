"""Unified search tool combining semantic, AST, and text search."""

from pathlib import Path
from typing import Dict, Any, List, Optional

from src.tools.base import Tool
from src.tools.search.semantic import SemanticSearch
from src.tools.search.ast_parser import ASTParser
from src.tools.search.ripgrep import RipgrepSearch
from loguru import logger


class SearchTool(Tool):
    """Unified search tool for code navigation and context gathering."""
    
    # Class attributes for Tool base class
    name = "search_code"
    description = "Search and navigate code in the workspace. Supports semantic search, AST-based symbol search, and fast text search."
    
    def __init__(self, workspace_path: str):
        """Initialize search tool.
        
        Args:
            workspace_path: Path to workspace directory
        """
        self.workspace_path = Path(workspace_path)
        self.semantic = SemanticSearch(workspace_path)
        self.ast_parser = ASTParser(workspace_path)
        self.ripgrep = RipgrepSearch(workspace_path)
        
        logger.info(f"Initialized SearchTool for {workspace_path}")
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_type": {
                            "type": "string",
                            "enum": ["semantic", "symbol", "text", "definition", "references"],
                            "description": (
                                "Type of search: "
                                "'semantic' - Find code by meaning/intent using embeddings, "
                                "'symbol' - Find functions/classes by name, "
                                "'text' - Fast text/regex search, "
                                "'definition' - Find where a symbol is defined, "
                                "'references' - Find where a symbol is used/imported"
                            )
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query or pattern"
                        },
                        "file_pattern": {
                            "type": "string",
                            "description": "Optional glob pattern to filter files (e.g., '*.py', 'src/**/*.ts')"
                        },
                        "is_regex": {
                            "type": "boolean",
                            "description": "Whether query is a regex pattern (for text search only)",
                            "default": False
                        },
                        "case_sensitive": {
                            "type": "boolean",
                            "description": "Whether search is case sensitive (for text search only)",
                            "default": False
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10
                        }
                    },
                    "required": ["search_type", "query"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute search based on search type.
        
        Args:
            search_type: Type of search to perform
            query: Search query
            file_pattern: Optional file pattern filter
            is_regex: Whether query is regex (text search only)
            case_sensitive: Whether search is case sensitive (text search only)
            max_results: Maximum results to return
            
        Returns:
            Search results with success status
        """
        search_type = kwargs.get('search_type')
        query = kwargs.get('query', '')
        file_pattern = kwargs.get('file_pattern')
        is_regex = kwargs.get('is_regex', False)
        case_sensitive = kwargs.get('case_sensitive', False)
        max_results = kwargs.get('max_results', 10)
        
        logger.info(f"Searching: type={search_type}, query='{query}'")
        
        try:
            if search_type == 'semantic':
                return self._semantic_search(query, max_results)
            
            elif search_type == 'symbol':
                return self._symbol_search(query, max_results)
            
            elif search_type == 'text':
                return self._text_search(
                    query, file_pattern, is_regex, case_sensitive, max_results
                )
            
            elif search_type == 'definition':
                return self._find_definition(query)
            
            elif search_type == 'references':
                return self._find_references(query)
            
            else:
                return {
                    'success': False,
                    'error': f"Unknown search type: {search_type}"
                }
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _semantic_search(self, query: str, max_results: int) -> Dict[str, Any]:
        """Perform semantic search.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            Search results
        """
        results = self.semantic.search(query, top_k=max_results)
        
        if not results:
            return {
                'success': True,
                'results': [],
                'message': 'No semantic matches found. Tip: Semantic search requires OpenAI API key.',
                'count': 0
            }
        
        # Format results
        formatted = []
        for r in results:
            formatted.append({
                'file': r['file'],
                'score': round(r['score'], 3),
                'preview': r['preview'][:150] + '...' if len(r['preview']) > 150 else r['preview']
            })
        
        return {
            'success': True,
            'results': formatted,
            'count': len(formatted),
            'message': f"Found {len(formatted)} semantic matches"
        }
    
    def _symbol_search(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search for symbols (functions, classes).
        
        Args:
            query: Symbol name pattern
            max_results: Maximum results
            
        Returns:
            Search results
        """
        symbols = self.ast_parser.find_symbol(query)
        
        if not symbols:
            return {
                'success': True,
                'results': [],
                'message': 'No symbols found',
                'count': 0
            }
        
        # Limit results
        symbols = symbols[:max_results]
        
        # Format results
        formatted = []
        for sym in symbols:
            result = {
                'name': sym.name,
                'type': sym.type,
                'file': sym.file,
                'line': sym.line
            }
            
            if sym.signature:
                result['signature'] = sym.signature
            if sym.docstring:
                result['docstring'] = sym.docstring[:100] + '...' if len(sym.docstring) > 100 else sym.docstring
            if sym.parent:
                result['parent'] = sym.parent
            
            formatted.append(result)
        
        return {
            'success': True,
            'results': formatted,
            'count': len(formatted),
            'message': f"Found {len(formatted)} symbols matching '{query}'"
        }
    
    def _text_search(
        self,
        query: str,
        file_pattern: Optional[str],
        is_regex: bool,
        case_sensitive: bool,
        max_results: int
    ) -> Dict[str, Any]:
        """Perform text search.
        
        Args:
            query: Search pattern
            file_pattern: Optional file filter
            is_regex: Whether query is regex
            case_sensitive: Case sensitivity
            max_results: Maximum results
            
        Returns:
            Search results
        """
        matches = self.ripgrep.search(
            query,
            is_regex=is_regex,
            case_sensitive=case_sensitive,
            file_pattern=file_pattern,
            max_results=max_results
        )
        
        if not matches:
            return {
                'success': True,
                'results': [],
                'message': f"No matches found for '{query}'",
                'count': 0
            }
        
        # Format results
        formatted = []
        for match in matches:
            formatted.append({
                'file': match.file,
                'line': match.line,
                'column': match.column,
                'text': match.text,
                'match': match.match
            })
        
        return {
            'success': True,
            'results': formatted,
            'count': len(formatted),
            'message': f"Found {len(formatted)} matches"
        }
    
    def _find_definition(self, name: str) -> Dict[str, Any]:
        """Find where a symbol is defined.
        
        Args:
            name: Symbol name
            
        Returns:
            Definition results
        """
        definitions = self.ast_parser.find_definitions(name)
        
        if not definitions:
            return {
                'success': True,
                'results': [],
                'message': f"No definition found for '{name}'",
                'count': 0
            }
        
        # Format results
        formatted = []
        for defn in definitions:
            result = {
                'name': defn.name,
                'type': defn.type,
                'file': defn.file,
                'line': defn.line,
                'end_line': defn.end_line
            }
            
            if defn.signature:
                result['signature'] = defn.signature
            if defn.docstring:
                result['docstring'] = defn.docstring
            
            formatted.append(result)
        
        return {
            'success': True,
            'results': formatted,
            'count': len(formatted),
            'message': f"Found {len(formatted)} definitions"
        }
    
    def _find_references(self, name: str) -> Dict[str, Any]:
        """Find where a symbol is referenced/imported.
        
        Args:
            name: Symbol/module name
            
        Returns:
            Reference results
        """
        imports = self.ast_parser.find_imports(name)
        
        if not imports:
            return {
                'success': True,
                'results': [],
                'message': f"No imports found for '{name}'",
                'count': 0
            }
        
        # Format results
        formatted = []
        for imp in imports:
            formatted.append({
                'name': imp.name,
                'file': imp.file,
                'line': imp.line
            })
        
        return {
            'success': True,
            'results': formatted,
            'count': len(formatted),
            'message': f"Found {len(formatted)} references"
        }
