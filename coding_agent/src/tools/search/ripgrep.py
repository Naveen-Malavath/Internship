"""Fast text search using ripgrep or grep."""

import subprocess
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from loguru import logger


@dataclass
class SearchMatch:
    """Represents a search match."""
    file: str
    line: int
    column: int
    text: str
    match: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'file': self.file,
            'line': self.line,
            'column': self.column,
            'text': self.text,
            'match': self.match
        }


class RipgrepSearch:
    """Fast text search using ripgrep or fallback to Python grep."""
    
    def __init__(self, workspace_path: str):
        """Initialize ripgrep search.
        
        Args:
            workspace_path: Path to workspace directory
        """
        self.workspace_path = Path(workspace_path)
        self.has_ripgrep = self._check_ripgrep()
        
        if not self.has_ripgrep:
            logger.info("ripgrep not found, using Python fallback for text search")
    
    def _check_ripgrep(self) -> bool:
        """Check if ripgrep is available."""
        try:
            subprocess.run(
                ['rg', '--version'],
                capture_output=True,
                timeout=1
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _search_with_ripgrep(
        self,
        pattern: str,
        is_regex: bool = False,
        case_sensitive: bool = False,
        file_pattern: Optional[str] = None,
        max_results: int = 100
    ) -> List[SearchMatch]:
        """Search using ripgrep.
        
        Args:
            pattern: Search pattern
            is_regex: Whether pattern is a regex
            case_sensitive: Whether search is case sensitive
            file_pattern: Optional glob pattern for files to search
            max_results: Maximum number of results
            
        Returns:
            List of search matches
        """
        cmd = ['rg', '--json', '--line-number', '--column']
        
        if not case_sensitive:
            cmd.append('--ignore-case')
        
        if not is_regex:
            cmd.append('--fixed-strings')
        
        if file_pattern:
            cmd.extend(['--glob', file_pattern])
        
        # Add max count
        cmd.extend(['--max-count', str(max_results)])
        
        cmd.append(pattern)
        cmd.append(str(self.workspace_path))
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            matches = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                try:
                    import json
                    data = json.loads(line)
                    
                    if data.get('type') == 'match':
                        match_data = data['data']
                        path_data = match_data['path']
                        
                        # Get relative path
                        abs_path = Path(path_data['text'])
                        try:
                            rel_path = str(abs_path.relative_to(self.workspace_path))
                        except ValueError:
                            rel_path = str(abs_path)
                        
                        line_num = match_data['line_number']
                        lines_text = match_data['lines']['text'].rstrip('\n')
                        
                        # Get match info
                        submatch = match_data['submatches'][0] if match_data['submatches'] else {}
                        match_text = submatch.get('match', {}).get('text', '')
                        col = submatch.get('start', 0) + 1
                        
                        matches.append(SearchMatch(
                            file=rel_path,
                            line=line_num,
                            column=col,
                            text=lines_text,
                            match=match_text
                        ))
                        
                        if len(matches) >= max_results:
                            break
                
                except (json.JSONDecodeError, KeyError) as e:
                    logger.debug(f"Failed to parse ripgrep output: {e}")
                    continue
            
            return matches
        
        except subprocess.TimeoutExpired:
            logger.warning("Ripgrep search timed out")
            return []
        except Exception as e:
            logger.error(f"Ripgrep search failed: {e}")
            return []
    
    def _search_with_python(
        self,
        pattern: str,
        is_regex: bool = False,
        case_sensitive: bool = False,
        file_pattern: Optional[str] = None,
        max_results: int = 100
    ) -> List[SearchMatch]:
        """Fallback Python-based search.
        
        Args:
            pattern: Search pattern
            is_regex: Whether pattern is a regex
            case_sensitive: Whether search is case sensitive
            file_pattern: Optional glob pattern for files
            max_results: Maximum number of results
            
        Returns:
            List of search matches
        """
        matches = []
        
        # Compile pattern
        flags = 0 if case_sensitive else re.IGNORECASE
        if is_regex:
            try:
                regex = re.compile(pattern, flags)
            except re.error:
                logger.error(f"Invalid regex pattern: {pattern}")
                return []
        else:
            # Escape special characters for literal search
            escaped = re.escape(pattern)
            regex = re.compile(escaped, flags)
        
        # Determine which files to search
        if file_pattern:
            files = self.workspace_path.glob(file_pattern)
        else:
            files = self.workspace_path.rglob('*')
        
        # Ignore patterns
        ignore_patterns = {
            'node_modules', 'venv', 'env', '__pycache__', '.git',
            'dist', 'build', '.next', 'coverage', '.agent_cache'
        }
        
        for file_path in files:
            if not file_path.is_file():
                continue
            
            # Check ignore patterns
            if any(pattern in file_path.parts for pattern in ignore_patterns):
                continue
            
            # Skip binary files (simple heuristic)
            if file_path.suffix in {'.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe'}:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        for match in regex.finditer(line):
                            rel_path = str(file_path.relative_to(self.workspace_path))
                            
                            matches.append(SearchMatch(
                                file=rel_path,
                                line=line_num,
                                column=match.start() + 1,
                                text=line.rstrip('\n'),
                                match=match.group(0)
                            ))
                            
                            if len(matches) >= max_results:
                                return matches
            
            except Exception as e:
                logger.debug(f"Failed to search {file_path}: {e}")
                continue
        
        return matches
    
    def search(
        self,
        pattern: str,
        is_regex: bool = False,
        case_sensitive: bool = False,
        file_pattern: Optional[str] = None,
        max_results: int = 100
    ) -> List[SearchMatch]:
        """Search for pattern in workspace.
        
        Args:
            pattern: Search pattern (literal string or regex)
            is_regex: Whether pattern is a regex
            case_sensitive: Whether search is case sensitive
            file_pattern: Optional glob pattern for files (e.g., '*.py')
            max_results: Maximum number of results to return
            
        Returns:
            List of search matches
        """
        if self.has_ripgrep:
            return self._search_with_ripgrep(
                pattern, is_regex, case_sensitive, file_pattern, max_results
            )
        else:
            return self._search_with_python(
                pattern, is_regex, case_sensitive, file_pattern, max_results
            )
    
    def search_in_file(
        self,
        file_path: str,
        pattern: str,
        is_regex: bool = False,
        case_sensitive: bool = False
    ) -> List[SearchMatch]:
        """Search for pattern in a specific file.
        
        Args:
            file_path: Path to file (relative to workspace)
            pattern: Search pattern
            is_regex: Whether pattern is a regex
            case_sensitive: Whether search is case sensitive
            
        Returns:
            List of search matches
        """
        abs_path = self.workspace_path / file_path
        
        if not abs_path.exists() or not abs_path.is_file():
            return []
        
        matches = []
        
        # Compile pattern
        flags = 0 if case_sensitive else re.IGNORECASE
        if is_regex:
            try:
                regex = re.compile(pattern, flags)
            except re.error:
                logger.error(f"Invalid regex pattern: {pattern}")
                return []
        else:
            escaped = re.escape(pattern)
            regex = re.compile(escaped, flags)
        
        try:
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    for match in regex.finditer(line):
                        matches.append(SearchMatch(
                            file=file_path,
                            line=line_num,
                            column=match.start() + 1,
                            text=line.rstrip('\n'),
                            match=match.group(0)
                        ))
        
        except Exception as e:
            logger.error(f"Failed to search file {file_path}: {e}")
        
        return matches
