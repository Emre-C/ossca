# DeepWiki: A tool for creating queryable knowledge bases from code repositories

from .knowledge_base import KnowledgeBase
from .rag import RAG, RAGAnswer
from .data_pipeline import DatabaseManager

__version__ = "0.1.0"
__all__ = ["KnowledgeBase", "RAG", "RAGAnswer", "DatabaseManager"]
