"""
End-to-end test for DeepWiki.

This test validates the complete workflow:
1. Clone a small public repository
2. Build the knowledge base
3. Query and assert non-empty answer
4. Test with streaming disabled for speed
"""

import pytest
import tempfile
import shutil
import os
import logging
from pathlib import Path

# Test is marked as e2e for filtering
pytestmark = pytest.mark.e2e

# Configure test timeout
pytest_timeout = 60  # 60 seconds max


@pytest.fixture
def test_repo_url():
    """Use a tiny public repository for testing."""
    return "https://github.com/octocat/Hello-World"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test isolation."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_internet_connectivity():
    """Check if internet is available for the test."""
    import requests
    try:
        response = requests.get("https://github.com", timeout=5)
        return response.status_code == 200
    except:
        return False


@pytest.mark.skipif(not test_internet_connectivity(), reason="Internet not available")
def test_e2e_small_repo_workflow(test_repo_url, temp_dir):
    """
    Test the complete end-to-end workflow with a small repository.
    
    Steps:
    1. Clone https://github.com/octocat/Hello-World (tiny repo)
    2. Build knowledge base (force rebuild, no streaming for speed) 
    3. Query "What does this repository do?"
    4. Assert answer contains the word "Hello"
    """
    from deepwiki import KnowledgeBase
    from deepwiki.exceptions import SchemaMismatchError
    
    # Set up logging for test visibility
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting e2e test with repository: {test_repo_url}")
    
    # Step 1: Initialize knowledge base
    kb = KnowledgeBase(provider="google")  # Use default provider
    
    # Step 2: Build knowledge base (force rebuild for clean test)
    logger.info("Building knowledge base...")
    success = kb.build(
        repo_url_or_path=test_repo_url,
        repo_type="github",
        force_rebuild=True  # Force rebuild to ensure clean test
    )
    
    assert success, "Failed to build knowledge base"
    assert kb.is_ready, "Knowledge base should be ready after successful build"
    
    # Step 3: Query the repository (non-streaming for speed and simplicity)
    logger.info("Querying the repository...")
    question = "What does this repository do?"
    
    answer, retrieved_docs = kb.query(question)
    
    # Step 4: Validate the response
    assert answer, "Answer should not be empty"
    assert isinstance(answer, str), "Answer should be a string"
    assert len(answer) > 0, "Answer should have content"
    
    # Check that the answer contains "Hello" (case-insensitive)
    assert "hello" in answer.lower(), f"Answer should mention 'Hello', got: {answer}"
    
    # Validate that documents were retrieved
    assert retrieved_docs is not None, "Retrieved documents should not be None"
    logger.info(f"Successfully retrieved {len(retrieved_docs)} documents")
    
    # Test conversation history
    kb.add_conversation_turn(question, answer)
    
    # Test clearing conversation
    kb.clear_conversation()
    
    logger.info("End-to-end test completed successfully")


@pytest.mark.skipif(not test_internet_connectivity(), reason="Internet not available")
def test_e2e_streaming_functionality(test_repo_url):
    """
    Test the streaming functionality separately.
    """
    from deepwiki import KnowledgeBase
    
    logger = logging.getLogger(__name__)
    logger.info("Testing streaming functionality...")
    
    # Initialize and build (reuse if exists)
    kb = KnowledgeBase(provider="google")
    
    # Load existing or build if needed
    if not kb.is_built(test_repo_url):
        success = kb.build(repo_url_or_path=test_repo_url, repo_type="github")
        assert success, "Failed to build knowledge base for streaming test"
    else:
        success = kb.load(repo_url_or_path=test_repo_url, repo_type="github")
        assert success, "Failed to load existing knowledge base for streaming test"
    
    # Test streaming
    question = "What programming language is used?"
    chunks = []
    
    for chunk in kb.query_stream(question):
        chunks.append(chunk)
        if len(chunks) > 10:  # Prevent infinite loops in tests
            break
    
    # Validate streaming response
    assert len(chunks) > 0, "Should receive at least one chunk"
    
    full_answer = "".join(chunks)
    assert len(full_answer) > 0, "Combined chunks should form a non-empty answer"
    
    logger.info(f"Streaming test completed, received {len(chunks)} chunks")


def test_schema_versioning():
    """
    Test database schema versioning functionality.
    """
    from deepwiki.database_versioning import (
        save_state_with_version, 
        load_state_with_version, 
        check_database_version,
        CURRENT_SCHEMA_VERSION
    )
    from deepwiki.exceptions import SchemaMismatchError
    import tempfile
    
    # Test saving and loading with correct version
    test_data = {"test": "data", "numbers": [1, 2, 3]}
    
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        filepath = f.name
    
    try:
        # Save data with version
        save_state_with_version(test_data, filepath)
        
        # Load data and verify
        loaded_data = load_state_with_version(filepath)
        assert loaded_data == test_data, "Data should match after save/load cycle"
        
        # Test version checking
        assert check_database_version(filepath), "Version check should pass for current version"
        
        # Test loading old format (simulate by saving without version)
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(test_data, f)  # Save without version wrapper
        
        # Should raise SchemaMismatchError for old format
        with pytest.raises(SchemaMismatchError) as exc_info:
            load_state_with_version(filepath)
        
        assert "unknown" in str(exc_info.value), "Should indicate unknown version"
        assert CURRENT_SCHEMA_VERSION in str(exc_info.value), "Should mention current version"
        
    finally:
        # Cleanup
        if os.path.exists(filepath):
            os.unlink(filepath)


def test_logging_simplification():
    """
    Test the simplified logging configuration.
    """
    import logging
    from deepwiki.logging_config import setup_logging
    
    # Test with different log levels
    for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]:
        setup_logging(level)
        
        # Verify the level was set
        root_logger = logging.getLogger()
        assert root_logger.level == level, f"Log level should be set to {level}"


if __name__ == "__main__":
    # Allow running the test directly
    pytest.main([__file__, "-v", "-s"]) 