"""
Custom exceptions for DeepWiki.
"""


class SchemaMismatchError(Exception):
    """
    Raised when the database schema version doesn't match the expected version.
    
    This typically happens when the database was created with an older version
    of DeepWiki and needs to be rebuilt.
    """
    
    def __init__(self, found_version: str, expected_version: str):
        self.found_version = found_version
        self.expected_version = expected_version
        super().__init__(
            f"Database schema version mismatch. Found: {found_version}, "
            f"Expected: {expected_version}. Please rebuild the knowledge base."
        ) 