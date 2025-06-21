"""
Knowledge Base API for DeepWiki

This module provides a high-level interface for creating and querying knowledge bases
from code repositories.
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from .rag import RAG, RAGAnswer
from .data_pipeline import DatabaseManager

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    High-level interface for creating and querying knowledge bases from code repositories.
    
    This class manages the entire lifecycle:
    - Repository cloning and processing
    - Building and saving search indexes
    - Loading existing indexes
    - Answering questions using RAG
    """
    
    def __init__(self, provider: str = "google", model: Optional[str] = None):
        """
        Initialize the Knowledge Base.
        
        Args:
            provider: Model provider to use (google, openai, openrouter, ollama)
            model: Model name to use with the provider
        """
        self.provider = provider
        self.model = model
        self.rag = RAG(provider=provider, model=model)
        self.repo_url_or_path = None
        self.is_ready = False
        
    def _extract_repo_identifier(self, repo_url_or_path: str) -> str:
        """
        Extract a unique identifier from a repository URL or path for storage.
        
        Args:
            repo_url_or_path: Repository URL or local path
            
        Returns:
            Unique identifier for the repository
        """
        if os.path.isdir(repo_url_or_path):
            # Local path - use directory name
            return Path(repo_url_or_path).name
        else:
            # URL - extract owner/repo format
            parsed = urlparse(repo_url_or_path)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2:
                owner, repo = path_parts[0], path_parts[1]
                # Remove .git suffix if present
                repo = repo.replace('.git', '')
                return f"{owner}_{repo}"
            elif len(path_parts) == 1:
                repo = path_parts[0].replace('.git', '')
                return repo
            else:
                # Fallback to last part of URL
                return parsed.path.split('/')[-1] or "unknown_repo"
    
    def _get_database_path(self, repo_identifier: str) -> str:
        """
        Get the database path for a repository.
        
        Args:
            repo_identifier: Unique identifier for the repository
            
        Returns:
            Path to the database directory
        """
        from adalflow.utils import get_adalflow_default_root_path
        return os.path.join(get_adalflow_default_root_path(), "databases", repo_identifier)
    
    def _database_exists(self, repo_identifier: str) -> bool:
        """
        Check if a database already exists for the repository.
        
        Args:
            repo_identifier: Unique identifier for the repository
            
        Returns:
            True if database exists, False otherwise
        """
        db_path = self._get_database_path(repo_identifier)
        return os.path.exists(db_path) and os.listdir(db_path)
    
    def build(self, repo_url_or_path: str, 
              repo_type: str = "github",
              access_token: Optional[str] = None,
              excluded_dirs: Optional[List[str]] = None,
              excluded_files: Optional[List[str]] = None,
              included_dirs: Optional[List[str]] = None,
              included_files: Optional[List[str]] = None,
              force_rebuild: bool = False) -> bool:
        """
        Build the knowledge base from a repository.
        
        Args:
            repo_url_or_path: Repository URL or local path
            repo_type: Type of repository ("github", "gitlab", "bitbucket", "local")
            access_token: Optional access token for private repositories
            excluded_dirs: List of directories to exclude from processing
            excluded_files: List of file patterns to exclude from processing
            included_dirs: List of directories to include exclusively
            included_files: List of file patterns to include exclusively
            force_rebuild: Force rebuild even if database exists
            
        Returns:
            True if build was successful, False otherwise
        """
        try:
            self.repo_url_or_path = repo_url_or_path
            repo_identifier = self._extract_repo_identifier(repo_url_or_path)
            
            # Check if database already exists
            if not force_rebuild and self._database_exists(repo_identifier):
                logger.info(f"Database already exists for {repo_identifier}. Use force_rebuild=True to rebuild.")
                return self.load(repo_url_or_path, repo_type, access_token)
            
            logger.info(f"Building knowledge base for {repo_url_or_path}")
            
            # Prepare the retriever (this will build the database)
            self.rag.prepare_retriever(
                repo_url_or_path=repo_url_or_path,
                type=repo_type,
                access_token=access_token,
                excluded_dirs=excluded_dirs,
                excluded_files=excluded_files,
                included_dirs=included_dirs,
                included_files=included_files
            )
            
            self.is_ready = True
            logger.info("Knowledge base built successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build knowledge base: {str(e)}")
            return False
    
    def load(self, repo_url_or_path: str,
             repo_type: str = "github", 
             access_token: Optional[str] = None) -> bool:
        """
        Load an existing knowledge base.
        
        Args:
            repo_url_or_path: Repository URL or local path
            repo_type: Type of repository ("github", "gitlab", "bitbucket", "local")
            access_token: Optional access token for private repositories
            
        Returns:
            True if load was successful, False otherwise
        """
        try:
            self.repo_url_or_path = repo_url_or_path
            repo_identifier = self._extract_repo_identifier(repo_url_or_path)
            
            if not self._database_exists(repo_identifier):
                logger.warning(f"No existing database found for {repo_identifier}")
                return False
            
            logger.info(f"Loading existing knowledge base for {repo_identifier}")
            
            # Load the existing database
            self.rag.prepare_retriever(
                repo_url_or_path=repo_url_or_path,
                type=repo_type,
                access_token=access_token
            )
            
            self.is_ready = True
            logger.info("Knowledge base loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {str(e)}")
            return False
    
    def is_built(self, repo_url_or_path: str) -> bool:
        """
        Check if a knowledge base is already built for the repository.
        
        Args:
            repo_url_or_path: Repository URL or local path
            
        Returns:
            True if knowledge base exists, False otherwise
        """
        repo_identifier = self._extract_repo_identifier(repo_url_or_path)
        return self._database_exists(repo_identifier)
    
    def query(self, question: str, language: str = "en") -> Tuple[str, List]:
        """
        Query the knowledge base with a question.
        
        Args:
            question: The question to ask
            language: Language for the response
            
        Returns:
            Tuple of (answer, retrieved_documents)
        """
        if not self.is_ready:
            raise RuntimeError("Knowledge base is not ready. Call build() or load() first.")
        
        try:
            result = self.rag.call(question, language)
            
            if isinstance(result, tuple) and len(result) == 2:
                rag_answer, retrieved_docs = result
                if isinstance(rag_answer, RAGAnswer):
                    return rag_answer.answer, retrieved_docs
                else:
                    return str(rag_answer), retrieved_docs
            else:
                return str(result), []
                
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}", []
    
    def add_conversation_turn(self, question: str, answer: str) -> bool:
        """
        Add a question-answer pair to the conversation history.
        
        Args:
            question: The user's question
            answer: The assistant's answer
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_ready:
            return False
        
        try:
            return self.rag.memory.add_dialog_turn(question, answer)
        except Exception as e:
            logger.error(f"Error adding conversation turn: {str(e)}")
            return False
    
    def clear_conversation(self):
        """Clear the conversation history."""
        if self.is_ready:
            self.rag.memory = self.rag.memory.__class__() 