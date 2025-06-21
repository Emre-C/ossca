"""
Embedder utilities for DeepWiki
"""

import adalflow as adal
from deepwiki.config import configs


def get_embedder() -> adal.Embedder:
    """Get the configured embedder instance."""
    embedder_config = configs["embedder"]

    # --- Initialize Embedder ---
    model_client_class = embedder_config["model_client"]
    if "initialize_kwargs" in embedder_config:
        model_client = model_client_class(**embedder_config["initialize_kwargs"])
    else:
        model_client = model_client_class()
    embedder = adal.Embedder(
        model_client=model_client,
        model_kwargs=embedder_config["model_kwargs"],
    )
    return embedder 