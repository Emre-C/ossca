"""
Core API for DeepWiki.

This module provides the stable public interface for DeepWiki functionality.
"""

from ..knowledge_base import KnowledgeBase
from ..rag import RAG, RAGAnswer
from ..data_pipeline import DatabaseManager
from ..exceptions import SchemaMismatchError

__all__ = [
    "KnowledgeBase",
    "RAG", 
    "RAGAnswer",
    "DatabaseManager",
    "SchemaMismatchError"
] 