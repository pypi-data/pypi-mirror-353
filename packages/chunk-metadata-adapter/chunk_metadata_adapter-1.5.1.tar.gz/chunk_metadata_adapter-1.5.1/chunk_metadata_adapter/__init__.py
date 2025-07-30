"""
Chunk Metadata Adapter - A package for managing metadata for chunked content.

This package provides tools for creating, managing, and converting metadata 
for chunks of content in various systems, including RAG pipelines, document 
processing, and machine learning training datasets.
"""

from .metadata_builder import ChunkMetadataBuilder
from .models import (
    SemanticChunk,
    ChunkType,
    ChunkRole,
    ChunkStatus,
    ChunkMetrics,
    FeedbackMetrics
)
from chunk_metadata_adapter.flat_chunk import FlatSemanticChunk

__version__ = "1.5.0"
__all__ = [
    "ChunkMetadataBuilder",
    "SemanticChunk",
    "FlatSemanticChunk",
    "ChunkType",
    "ChunkRole",
    "ChunkStatus",
    "ChunkMetrics",
    "FeedbackMetrics",
]
