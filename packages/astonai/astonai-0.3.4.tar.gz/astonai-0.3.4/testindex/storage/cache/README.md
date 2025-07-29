# Micro Cache Layer for AstonAI

## Overview

The Micro Cache Layer provides sub-300ms graph data access for AstonAI analysis commands, enabling fast NL-router and L-series prototypes. It intelligently caches nodes, edges, and pre-computed criticality metrics with automatic performance monitoring.

## Quick Start

### Basic Usage

```python
from testindex.storage.cache import get_micro_cache, CacheConfig

# Configure cache for optimal performance
config = CacheConfig(
    target_latency_ms=300,
    enable_criticality_precompute=True
)

# Get cache instance
cache = get_micro_cache(config)

# Warm up with your graph data
cache.warm_up_cache(nodes, edges)

# Fast data access
node = cache.get_node_fast("node_id")  # < 10ms typical
outgoing, incoming = cache.get_node_relationships_fast("node_id")  # < 50ms
file_nodes = cache.get_nodes_by_file_fast("src/module.py")  # < 50ms
```

### CLI Commands

```bash
# Warm up the cache
aston cache warm-up --progress

# Check cache status and performance
aston cache status

# Clear cache
aston cache clear --confirm
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Micro Cache Layer                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  GraphDataCache │  │  MetricsCache   │  │ Performance  │ │
│  │                 │  │                 │  │ Monitoring   │ │
│  │ • Nodes         │  │ • Criticality   │  │              │ │
│  │ • Edges         │  │ • Hash-based    │  │ • Sub-300ms  │ │
│  │ • File Indexes  │  │   Invalidation  │  │ • Hit Ratios │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Graph Loader    │  │ Command         │  │ CLI Commands │ │
│  │                 │  │ Integration     │  │              │ │
│  │ • JSON Source   │  │ • Decorators    │  │ • aston cache│ │
│  │ • Offline Mode  │  │ • Enhancements  │  │ • Status     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 🚀 Performance Targets
- **Sub-300ms latency** for all analysis operations
- **Criticality pre-computation** for frequently accessed metrics
- **File-based indexing** for fast file-based queries
- **Memory-efficient** caching with 256MB default limit

### 📊 Caching Strategies
- **Node Caching**: Fast lookup by ID with file-path indexing
- **Edge Caching**: Indexed by source and target nodes
- **Metrics Caching**: Hash-based invalidation for computed results
- **Relationship Caching**: Optimized for graph traversal operations

### 🔧 Smart Features
- **Automatic Cache Warming**: Pre-loads frequently accessed data
- **Intelligent Invalidation**: File-based clearing
- **Performance Monitoring**: Real-time latency tracking and statistics
- **Command Integration**: Transparent enhancement of existing CLI commands

## Configuration

### CacheConfig Options

```python
config = CacheConfig(
    # Performance targets
    target_latency_ms=300,        # Sub-300ms target
    precompute_threshold=100,     # Pre-compute for graphs > 100 nodes
    
    # Memory management
    default_ttl_seconds=3600,     # 1 hour cache TTL
    max_memory_mb=256,            # 256MB memory limit
    
    # Feature toggles
    enable_criticality_precompute=True,
    
    # Monitoring
    log_slow_queries=True,
    slow_query_threshold_ms=100,
    enable_performance_monitoring=True
)
```

## Data Sources

### Offline JSON Files
```python
from testindex.storage.cache.graph_loader import GraphDataLoader

loader = GraphDataLoader()
nodes, edges = loader.load_from_offline_json(".testindex/knowledge_graph")
```

## Integration with AstonAI Commands

### Enhanced Command Decorators
```python
from testindex.storage.cache.command_integration import with_micro_cache

@with_micro_cache(warm_up=True)
def my_analysis_command(*args, **kwargs):
    # Your command automatically gets cache enhancement
    cache = kwargs.get('_micro_cache')
    # Now uses sub-300ms data access
    pass
```

### Context Manager for Enhanced Execution
```python
from testindex.storage.cache.command_integration import CacheEnhancedExecution

with CacheEnhancedExecution(config) as enhanced:
    cache = enhanced.get_cache()
    
    # All operations in this context use caching
    nodes = get_analysis_nodes()
    relationships = get_node_relationships()
    scores = compute_criticality_scores()
    
# Automatic performance reporting on exit
```

## Monitoring and Diagnostics

### Performance Statistics
```python
stats = cache.get_cache_statistics()
print(f"Hit Ratio: {stats['performance']['hit_ratio']:.1%}")
print(f"Avg Latency: {stats['performance']['avg_response_time_ms']:.2f}ms")
print(f"Target Met: {stats['latency_target_met']}")
```

### Real-time Monitoring
```bash
# Status check
aston cache status

# Continuous monitoring
aston cache status --json cache_stats.json
watch -n 5 "cat cache_stats.json | jq '.performance'"
```

## Global Instance Management

The micro cache maintains a global instance that persists across commands:

```python
from testindex.storage.cache import get_micro_cache, clear_global_cache

# Get or create global instance
cache1 = get_micro_cache()
cache2 = get_micro_cache()  # Same instance

assert cache1 is cache2  # True - same global instance

# Clear when needed
clear_global_cache()
```

## Testing and Validation

### Unit Tests
```bash
# Run micro cache tests
python -m pytest tests/unit/storage/cache/test_micro_cache.py -v
```

### Integration Validation
```bash
# End-to-end testing with real data
aston cache warm-up --progress
aston coverage --critical-path  # Should be sub-300ms
```

## Future Extensions

The core implementation is designed for extension. Advanced features are planned for future releases:

- **Distributed Caching**: Redis backend for multi-node setups
- **Neo4j Integration**: Direct database loading
- **Advanced Metrics**: Centrality and coverage pre-computation
- **Performance Tooling**: Comprehensive benchmarking and profiling

---

For more information, see the [AstonAI documentation](../../../README.md) or run `aston cache --help`. 