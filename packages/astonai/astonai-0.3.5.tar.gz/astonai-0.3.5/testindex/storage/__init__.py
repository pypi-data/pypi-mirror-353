"""
Storage utilities for the Test Intelligence Engine.

This package provides utilities for caching and persistent storage.
"""

__version__ = "0.1.0"

# Re-export key classes for easier imports
from testindex.storage.cache import MemoryCache
from testindex.storage.cache.micro_cache import MicroCache, CacheConfig, get_micro_cache
from testindex.storage.cache.graph_loader import GraphDataLoader, load_and_warm_cache
from testindex.storage.persistence import FileStorage 