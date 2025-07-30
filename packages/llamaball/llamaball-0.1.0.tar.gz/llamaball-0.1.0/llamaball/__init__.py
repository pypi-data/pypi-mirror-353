"""
Llamaball - Accessible Document Chat & RAG System
File Purpose: Package initialization and public API
Primary Functions: Expose core functionality and version info
Inputs: N/A (initialization only)
Outputs: Package version and core functions
"""

__version__ = "0.1.0"

# Import core functionality to make it available at package level
from . import core
from . import cli
from . import utils

# Expose main functions for programmatic use
from .core import (
    ingest_files,
    search_embeddings,
    chat,
    init_db
)

__all__ = [
    '__version__',
    'core',
    'cli', 
    'utils',
    'ingest_files',
    'search_embeddings', 
    'chat',
    'init_db'
] 