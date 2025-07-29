"""
Micro cache system for AstonAI graph data with sub-300ms latency targets.

This module provides intelligent caching of nodes, edges, and pre-computed
metrics to enable fast analysis command execution.
"""

from testindex.storage.cache.memory_cache import MemoryCache
from testindex.storage.cache.micro_cache import (
    MicroCache, CacheConfig, CacheStats, 
    get_micro_cache, clear_global_cache, warm_up_global_cache
)
from testindex.storage.cache.graph_loader import (
    GraphDataLoader, load_and_warm_cache, get_cache_with_data
)
from testindex.storage.cache.command_integration import (
    with_micro_cache, CacheEnhancedExecution, CachedAnalysisHelper
)

__all__ = [
    # Legacy
    'MemoryCache',
    
    # Core classes
    'MicroCache',
    'CacheConfig',
    'CacheStats',
    
    # Global functions
    'get_micro_cache',
    'clear_global_cache', 
    'warm_up_global_cache',
    
    # Data loading
    'GraphDataLoader',
    'load_and_warm_cache',
    'get_cache_with_data',
    
    # Command integration
    'with_micro_cache',
    'CacheEnhancedExecution', 
    'CachedAnalysisHelper'
] 