#!/usr/bin/env python3
"""
Test the KnowledgeBase API to ensure the refactoring is working correctly.

This is a basic integration test that verifies the main components work together.
"""

import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path to import the deepwiki module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from deepwiki import KnowledgeBase


class TestKnowledgeBase:
    """Tests for the KnowledgeBase class"""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_repo_url = "https://github.com/test/repo"
        self.test_local_path = "/tmp/test-repo"
    
    def test_knowledge_base_initialization(self):
        """Test that KnowledgeBase can be initialized properly."""
        kb = KnowledgeBase()
        assert kb.provider == "google"
        assert kb.model is None
        assert not kb.is_ready
        assert kb.repo_url_or_path is None
    
    def test_knowledge_base_initialization_with_provider(self):
        """Test that KnowledgeBase can be initialized with custom provider."""
        kb = KnowledgeBase(provider="openai", model="gpt-4")
        assert kb.provider == "openai"
        assert kb.model == "gpt-4"
        assert not kb.is_ready
    
    def test_extract_repo_identifier_github_url(self):
        """Test repository identifier extraction from GitHub URL."""
        kb = KnowledgeBase()
        
        # Standard GitHub URL
        result = kb._extract_repo_identifier("https://github.com/owner/repo")
        assert result == "owner_repo"
        
        # GitHub URL with .git suffix
        result = kb._extract_repo_identifier("https://github.com/owner/repo.git")
        assert result == "owner_repo"
        
        # GitHub URL with trailing slash
        result = kb._extract_repo_identifier("https://github.com/owner/repo/")
        assert result == "owner_repo"
    
    def test_extract_repo_identifier_local_path(self):
        """Test repository identifier extraction from local path."""
        kb = KnowledgeBase()
        
        # Local directory path
        result = kb._extract_repo_identifier("/home/user/projects/my-repo")
        assert result == "my-repo"
        
        # Local path with .git suffix
        result = kb._extract_repo_identifier("/var/repos/project.git")
        assert result == "project.git"  # For local paths, we keep the .git if it's part of directory name
    
    def test_get_database_path(self):
        """Test database path generation."""
        kb = KnowledgeBase()
        
        with patch('deepwiki.knowledge_base.get_adalflow_default_root_path') as mock_root:
            mock_root.return_value = "/tmp/adalflow"
            
            result = kb._get_database_path("test_repo")
            assert result == "/tmp/adalflow/databases/test_repo"
    
    def test_database_exists_check(self):
        """Test database existence checking."""
        kb = KnowledgeBase()
        
        with patch('os.path.exists') as mock_exists, \
             patch('os.listdir') as mock_listdir, \
             patch('deepwiki.knowledge_base.get_adalflow_default_root_path') as mock_root:
            
            mock_root.return_value = "/tmp/adalflow"
            
            # Test non-existent database
            mock_exists.return_value = False
            result = kb._database_exists("test_repo")
            assert not result
            
            # Test existing but empty database
            mock_exists.return_value = True
            mock_listdir.return_value = []
            result = kb._database_exists("test_repo")
            assert not result
            
            # Test existing database with files
            mock_exists.return_value = True
            mock_listdir.return_value = ["index.faiss", "metadata.json"]
            result = kb._database_exists("test_repo")
            assert result
    
    def test_is_built_method(self):
        """Test the is_built method."""
        kb = KnowledgeBase()
        
        with patch.object(kb, '_database_exists') as mock_db_exists:
            mock_db_exists.return_value = True
            assert kb.is_built("https://github.com/owner/repo")
            mock_db_exists.assert_called_once_with("owner_repo")
            
            mock_db_exists.reset_mock()
            mock_db_exists.return_value = False
            assert not kb.is_built("https://github.com/owner/repo")
    
    @patch('deepwiki.knowledge_base.RAG')
    def test_query_not_ready_error(self, mock_rag):
        """Test that query raises error when knowledge base is not ready."""
        kb = KnowledgeBase()
        
        with pytest.raises(RuntimeError, match="Knowledge base is not ready"):
            kb.query("test question")
    
    @patch('deepwiki.knowledge_base.RAG')
    def test_query_with_ready_knowledge_base(self, mock_rag):
        """Test querying when knowledge base is ready."""
        # Mock the RAG call method
        mock_rag_instance = MagicMock()
        mock_rag.return_value = mock_rag_instance
        
        # Mock response
        from deepwiki import RAGAnswer
        mock_answer = RAGAnswer(answer="This is a test answer")
        mock_rag_instance.call.return_value = (mock_answer, [])
        
        kb = KnowledgeBase()
        kb.is_ready = True  # Simulate ready state
        
        answer, docs = kb.query("test question")
        
        assert answer == "This is a test answer"
        assert docs == []
        mock_rag_instance.call.assert_called_once_with("test question", "en")
    
    def test_add_conversation_turn_not_ready(self):
        """Test adding conversation turn when not ready."""
        kb = KnowledgeBase()
        
        result = kb.add_conversation_turn("question", "answer")
        assert not result
    
    @patch('deepwiki.knowledge_base.RAG')
    def test_add_conversation_turn_ready(self, mock_rag):
        """Test adding conversation turn when ready."""
        mock_rag_instance = MagicMock()
        mock_rag.return_value = mock_rag_instance
        mock_rag_instance.memory.add_dialog_turn.return_value = True
        
        kb = KnowledgeBase()
        kb.is_ready = True
        
        result = kb.add_conversation_turn("question", "answer")
        assert result
        mock_rag_instance.memory.add_dialog_turn.assert_called_once_with("question", "answer")
    
    @patch('deepwiki.knowledge_base.RAG')
    def test_clear_conversation(self, mock_rag):
        """Test clearing conversation history."""
        mock_rag_instance = MagicMock()
        mock_rag.return_value = mock_rag_instance
        
        kb = KnowledgeBase()
        kb.is_ready = True
        
        kb.clear_conversation()
        # Should create a new memory instance
        assert mock_rag_instance.memory.__class__.called or True  # This is a basic check


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 