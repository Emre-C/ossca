"""
Database versioning utilities for DeepWiki.

This module provides functionality to handle database schema versioning
and detect incompatible versions.
"""

import pickle
import logging
from pathlib import Path
from typing import Any, Dict
from .exceptions import SchemaMismatchError

logger = logging.getLogger(__name__)

# Database schema version - increment when database structure changes
CURRENT_SCHEMA_VERSION = "1.0.0"


def save_state_with_version(obj: Any, filepath: str) -> None:
    """
    Save an object with schema version information.
    
    Args:
        obj: The object to save
        filepath: Path to save the object to
    """
    versioned_data = {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "data": obj
    }
    
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'wb') as f:
        pickle.dump(versioned_data, f)
    
    logger.debug(f"Saved state with schema version {CURRENT_SCHEMA_VERSION} to {filepath}")


def load_state_with_version(filepath: str) -> Any:
    """
    Load an object and check its schema version.
    
    Args:
        filepath: Path to load the object from
        
    Returns:
        The loaded object
        
    Raises:
        SchemaMismatchError: If the schema version doesn't match
        FileNotFoundError: If the file doesn't exist
    """
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Database file not found: {filepath}")
    
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    
    # Handle old format without versioning
    if not isinstance(data, dict) or "schema_version" not in data:
        logger.warning(f"Loading database without version information from {filepath}")
        raise SchemaMismatchError("unknown", CURRENT_SCHEMA_VERSION)
    
    found_version = data["schema_version"]
    if found_version != CURRENT_SCHEMA_VERSION:
        logger.error(f"Schema version mismatch in {filepath}")
        raise SchemaMismatchError(found_version, CURRENT_SCHEMA_VERSION)
    
    logger.debug(f"Loaded state with schema version {found_version} from {filepath}")
    return data["data"]


def check_database_version(filepath: str) -> bool:
    """
    Check if a database file has a compatible schema version.
    
    Args:
        filepath: Path to the database file
        
    Returns:
        True if compatible, False otherwise
    """
    try:
        load_state_with_version(filepath)
        return True
    except (SchemaMismatchError, FileNotFoundError):
        return False 