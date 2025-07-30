# ./src/embedkit/classes.py

"""Core types and enums for the EmbedKit library.

This module provides the main types and enums that users should interact with:
- EmbeddingResult: The result type returned by embedding operations
- EmbeddingError: Exception type for embedding operations
- Model: Enum of supported embedding models
- CohereInputType: Enum for Cohere's input types
"""

from . import EmbeddingResponse, EmbeddingError
from .models import Model
from .providers.cohere import CohereInputType
from .providers.snowflake import SnowflakeInputType

__all__ = ["EmbeddingResponse", "EmbeddingError", "Model", "CohereInputType", "SnowflakeInputType"]
