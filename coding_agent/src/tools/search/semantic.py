"""Semantic code search using embeddings."""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import hashlib

from openai import OpenAI
from loguru import logger


class SemanticSearch:
    """Semantic code search using OpenAI embeddings."""
    
    def __init__(self, workspace_path: str, openai_api_key: Optional[str] = None):
        """Initialize semantic search.
        
        Args:
            workspace_path: Path to workspace directory
            openai_api_key: Optional OpenAI API key. If not provided, reads from env
        """
        self.workspace_path = Path(workspace_path)
        
        # Get API key from parameter or environment
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.embeddings_cache_path = self.workspace_path / ".agent_cache" / "embeddings.json"
        self.embeddings_cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()
        
        # File patterns to index
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', 
            '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt', '.scala',
            '.sh', '.bash', '.yaml', '.yml', '.json', '.md', '.txt'
        }
        
        # Patterns to ignore
        self.ignore_patterns = {
            'node_modules', 'venv', 'env', '__pycache__', '.git', 
            'dist', 'build', '.next', 'coverage', '.pytest_cache',
            '.agent_cache', 'package-lock.json', 'yarn.lock'
        }
    
    def _load_cache(self):
        """Load embeddings cache from disk."""
        if self.embeddings_cache_path.exists():
            try:
                with open(self.embeddings_cache_path, 'r') as f:
                    self.embeddings_cache = json.load(f)
                logger.info(f"Loaded {len(self.embeddings_cache)} cached embeddings")
            except Exception as e:
                logger.warning(f"Failed to load embeddings cache: {e}")
                self.embeddings_cache = {}
    
    def _save_cache(self):
        """Save embeddings cache to disk."""
        try:
            self.embeddings_cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.embeddings_cache_path, 'w') as f:
                json.dump(self.embeddings_cache, f)
            logger.debug("Saved embeddings cache")
        except Exception as e:
            logger.warning(f"Failed to save embeddings cache: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get hash of file content for cache validation."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _should_index_file(self, file_path: Path) -> bool:
        """Check if file should be indexed."""
        # Check extension
        if file_path.suffix not in self.code_extensions:
            return False
        
        # Check ignore patterns
        parts = file_path.parts
        for pattern in self.ignore_patterns:
            if pattern in parts:
                return False
        
        # Check file size (skip files > 100KB)
        try:
            if file_path.stat().st_size > 100_000:
                return False
        except Exception:
            return False
        
        return True
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text using OpenAI API."""
        if not self.client:
            logger.warning("OpenAI API key not configured, semantic search disabled")
            return None
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def index_workspace(self, force_reindex: bool = False) -> int:
        """Index all code files in workspace.
        
        Args:
            force_reindex: Force re-indexing even if cache exists
            
        Returns:
            Number of files indexed
        """
        if not self.client:
            logger.warning("OpenAI API not configured, skipping indexing")
            return 0
        
        indexed_count = 0
        
        for file_path in self.workspace_path.rglob('*'):
            if not file_path.is_file() or not self._should_index_file(file_path):
                continue
            
            try:
                # Check cache
                rel_path = str(file_path.relative_to(self.workspace_path))
                file_hash = self._get_file_hash(file_path)
                
                if not force_reindex and rel_path in self.embeddings_cache:
                    cached = self.embeddings_cache[rel_path]
                    if cached.get('hash') == file_hash:
                        continue  # Already cached and unchanged
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Skip empty files
                if not content.strip():
                    continue
                
                # Create searchable text (file path + content)
                searchable_text = f"File: {rel_path}\n\n{content}"
                
                # Get embedding
                embedding = self._get_embedding(searchable_text)
                if embedding:
                    self.embeddings_cache[rel_path] = {
                        'hash': file_hash,
                        'embedding': embedding,
                        'preview': content[:200]  # Store preview for results
                    }
                    indexed_count += 1
                    
                    if indexed_count % 10 == 0:
                        logger.info(f"Indexed {indexed_count} files...")
            
            except Exception as e:
                logger.warning(f"Failed to index {file_path}: {e}")
                continue
        
        # Save cache
        if indexed_count > 0:
            self._save_cache()
            logger.info(f"Indexed {indexed_count} new/modified files")
        
        return indexed_count
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Search for code matching query semantically.
        
        Args:
            query: Search query
            top_k: Maximum number of results to return
            min_score: Minimum similarity score (0-1)
            
        Returns:
            List of search results with file path, score, and preview
        """
        if not self.client:
            logger.warning("OpenAI API not configured, semantic search disabled")
            return []
        
        # Auto-index if cache is empty
        if not self.embeddings_cache:
            logger.info("No embeddings cached, indexing workspace...")
            self.index_workspace()
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        if not query_embedding:
            return []
        
        # Calculate similarities
        results = []
        for file_path, data in self.embeddings_cache.items():
            embedding = data.get('embedding')
            if not embedding:
                continue
            
            score = self._cosine_similarity(query_embedding, embedding)
            if score >= min_score:
                results.append({
                    'file': file_path,
                    'score': score,
                    'preview': data.get('preview', '')
                })
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def search_files(
        self,
        query: str,
        file_paths: List[str],
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Search within specific files only.
        
        Args:
            query: Search query
            file_paths: List of file paths to search within
            min_score: Minimum similarity score
            
        Returns:
            List of search results
        """
        if not self.client:
            return []
        
        query_embedding = self._get_embedding(query)
        if not query_embedding:
            return []
        
        results = []
        for file_path in file_paths:
            if file_path not in self.embeddings_cache:
                continue
            
            data = self.embeddings_cache[file_path]
            embedding = data.get('embedding')
            if not embedding:
                continue
            
            score = self._cosine_similarity(query_embedding, embedding)
            if score >= min_score:
                results.append({
                    'file': file_path,
                    'score': score,
                    'preview': data.get('preview', '')
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
