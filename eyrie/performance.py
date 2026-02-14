"""
Castle Wyvern Performance Optimizations
Feature 20: Speed and efficiency improvements

Provides:
- Response caching
- Connection pooling
- Lazy loading
- Memory optimization
- Async batching
"""

import os
import json
import time
import functools
import threading
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import OrderedDict
import hashlib


@dataclass
class CacheEntry:
    """A cached response entry."""
    key: str
    value: Any
    timestamp: float
    ttl_seconds: int
    hit_count: int = 0


class ResponseCache:
    """
    LRU cache for AI responses.
    
    Caches responses to avoid redundant API calls.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.Lock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    def _generate_key(self, prompt: str, model: str = "default") -> str:
        """Generate cache key from prompt."""
        content = f"{model}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str = "default") -> Optional[Any]:
        """Get cached response if available and not expired."""
        key = self._generate_key(prompt, model)
        
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if time.time() - entry.timestamp < entry.ttl_seconds:
                    # Move to end (most recently used)
                    self.cache.move_to_end(key)
                    entry.hit_count += 1
                    self.stats["hits"] += 1
                    return entry.value
                else:
                    # Expired, remove
                    del self.cache[key]
            
            self.stats["misses"] += 1
            return None
    
    def set(self, prompt: str, value: Any, model: str = "default", 
            ttl_seconds: int = None):
        """Cache a response."""
        key = self._generate_key(prompt, model)
        
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl
        
        with self._lock:
            # Evict oldest if at capacity
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
                self.stats["evictions"] += 1
            
            self.cache[key] = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                ttl_seconds=ttl_seconds
            )
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries."""
        with self._lock:
            if pattern is None:
                self.cache.clear()
            else:
                # Remove entries matching pattern
                keys_to_remove = [
                    k for k in self.cache.keys()
                    if pattern in self.cache[k].value
                ]
                for k in keys_to_remove:
                    del self.cache[k]
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1%}",
            "evictions": self.stats["evictions"]
        }


class ConnectionPool:
    """
    Manages pooled connections for API clients.
    
    Reduces connection overhead for repeated requests.
    """
    
    def __init__(self, max_connections: int = 10, 
                 connection_factory: Callable = None):
        self.max_connections = max_connections
        self.connection_factory = connection_factory
        self.pool: List[Any] = []
        self.in_use: set = set()
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
    
    def acquire(self, timeout: float = 30) -> Any:
        """Acquire a connection from the pool."""
        with self._condition:
            # Wait for available connection
            wait_start = time.time()
            while len(self.pool) == 0 and len(self.in_use) >= self.max_connections:
                remaining = timeout - (time.time() - wait_start)
                if remaining <= 0:
                    raise TimeoutError("Could not acquire connection")
                self._condition.wait(timeout=remaining)
            
            # Create new connection if needed
            if not self.pool and len(self.in_use) < self.max_connections:
                if self.connection_factory:
                    conn = self.connection_factory()
                    self.pool.append(conn)
            
            if self.pool:
                conn = self.pool.pop()
                self.in_use.add(conn)
                return conn
            else:
                raise RuntimeError("No connections available")
    
    def release(self, conn: Any):
        """Release a connection back to the pool."""
        with self._lock:
            if conn in self.in_use:
                self.in_use.remove(conn)
                self.pool.append(conn)
                self._condition.notify()
    
    def close_all(self):
        """Close all connections."""
        with self._lock:
            for conn in self.pool + list(self.in_use):
                if hasattr(conn, 'close'):
                    conn.close()
            self.pool.clear()
            self.in_use.clear()


class LazyLoader:
    """
    Lazy loading for expensive resources.
    """
    
    def __init__(self, loader: Callable, *args, **kwargs):
        self.loader = loader
        self.args = args
        self.kwargs = kwargs
        self._value = None
        self._loaded = False
        self._lock = threading.Lock()
    
    @property
    def value(self):
        """Get the lazy-loaded value."""
        if not self._loaded:
            with self._lock:
                if not self._loaded:
                    self._value = self.loader(*self.args, **self.kwargs)
                    self._loaded = True
        return self._value
    
    def reset(self):
        """Reset and force reload on next access."""
        with self._lock:
            self._loaded = False
            self._value = None


class MemoryOptimizer:
    """
    Optimizes memory usage.
    """
    
    def __init__(self):
        self.object_pool: Dict[str, Any] = {}
        self.string_intern: Dict[str, str] = {}
    
    def intern_string(self, s: str) -> str:
        """Intern a string to reduce memory."""
        if s not in self.string_intern:
            self.string_intern[s] = s
        return self.string_intern[s]
    
    def get_pooled_object(self, key: str, factory: Callable) -> Any:
        """Get an object from the pool or create new."""
        if key not in self.object_pool:
            self.object_pool[key] = factory()
        return self.object_pool[key]
    
    def clear_pools(self):
        """Clear object pools to free memory."""
        self.object_pool.clear()
        self.string_intern.clear()
    
    def estimate_memory(self, obj: Any) -> int:
        """Estimate memory usage of an object (rough)."""
        return len(json.dumps(obj).encode())


class BatchProcessor:
    """
    Batches requests for efficient processing.
    """
    
    def __init__(self, batch_size: int = 10, max_wait_ms: float = 100):
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.pending: List[Tuple[Any, Callable]] = []
        self._lock = threading.Lock()
        self._timer: Optional[threading.Timer] = None
    
    def add(self, item: Any, callback: Callable):
        """Add an item to the batch."""
        with self._lock:
            self.pending.append((item, callback))
            
            if len(self.pending) >= self.batch_size:
                self._flush()
            elif self._timer is None:
                # Start timer for max wait
                self._timer = threading.Timer(
                    self.max_wait_ms / 1000,
                    self._flush
                )
                self._timer.start()
    
    def _flush(self):
        """Process all pending items."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None
            
            batch = self.pending.copy()
            self.pending.clear()
        
        if batch:
            # Process batch
            for item, callback in batch:
                try:
                    result = self._process_item(item)
                    callback(result)
                except Exception as e:
                    callback(None, error=e)
    
    def _process_item(self, item: Any) -> Any:
        """Process a single item. Override in subclass."""
        return item
    
    def flush(self):
        """Force immediate flush."""
        self._flush()


class PerformanceProfiler:
    """
    Profiles performance of operations.
    """
    
    def __init__(self):
        self.measurements: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
    
    def measure(self, name: str):
        """Decorator to measure function execution time."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                elapsed = (time.time() - start) * 1000  # ms
                
                with self._lock:
                    if name not in self.measurements:
                        self.measurements[name] = []
                    self.measurements[name].append(elapsed)
                
                return result
            return wrapper
        return decorator
    
    def get_stats(self, name: str = None) -> Dict:
        """Get performance statistics."""
        with self._lock:
            if name:
                if name not in self.measurements:
                    return {}
                times = self.measurements[name]
                return {
                    "count": len(times),
                    "avg_ms": sum(times) / len(times),
                    "min_ms": min(times),
                    "max_ms": max(times)
                }
            else:
                return {
                    name: self.get_stats(name)
                    for name in self.measurements.keys()
                }


class PerformanceManager:
    """
    Central manager for performance optimizations.
    """
    
    def __init__(self):
        self.cache = ResponseCache()
        self.connection_pool: Optional[ConnectionPool] = None
        self.memory = MemoryOptimizer()
        self.batch_processor = BatchProcessor()
        self.profiler = PerformanceProfiler()
        self.lazy_loaders: Dict[str, LazyLoader] = {}
        
        # Performance tracking
        self.start_time = time.time()
        self.request_count = 0
    
    def setup_connection_pool(self, factory: Callable, max_connections: int = 10):
        """Setup connection pooling."""
        self.connection_pool = ConnectionPool(max_connections, factory)
    
    def get_cached_or_compute(self, prompt: str, compute_fn: Callable, 
                              model: str = "default") -> Any:
        """Get cached response or compute and cache."""
        # Check cache
        cached = self.cache.get(prompt, model)
        if cached is not None:
            return cached
        
        # Compute
        self.request_count += 1
        result = compute_fn()
        
        # Cache result
        self.cache.set(prompt, result, model)
        
        return result
    
    def lazy_load(self, name: str, loader: Callable, *args, **kwargs) -> Any:
        """Lazy load a resource."""
        if name not in self.lazy_loaders:
            self.lazy_loaders[name] = LazyLoader(loader, *args, **kwargs)
        return self.lazy_loaders[name].value
    
    def profile(self, name: str):
        """Get profiling decorator."""
        return self.profiler.measure(name)
    
    def get_stats(self) -> Dict:
        """Get comprehensive performance statistics."""
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": int(uptime),
            "total_requests": self.request_count,
            "cache": self.cache.get_stats(),
            "profiler": self.profiler.get_stats(),
            "lazy_loaders": len(self.lazy_loaders),
            "requests_per_minute": (self.request_count / (uptime / 60)) if uptime > 0 else 0
        }
    
    def optimize_memory(self):
        """Run memory optimization."""
        self.memory.clear_pools()
        self.cache.invalidate()  # Clear old cache entries
        
        return {
            "cache_cleared": True,
            "pools_cleared": True
        }


# Standalone test
if __name__ == "__main__":
    print("🏰 Castle Wyvern Performance Optimizations Test")
    print("=" * 50)
    
    perf = PerformanceManager()
    
    # Test caching
    print("\n1. Testing response cache...")
    prompt = "What is Python?"
    
    # First call (miss)
    result = perf.get_cached_or_compute(
        prompt,
        lambda: "Python is a programming language."
    )
    print(f"   First call: {result[:30]}...")
    
    # Second call (hit)
    result = perf.get_cached_or_compute(
        prompt,
        lambda: "This should not be called"
    )
    print(f"   Second call (cached): {result[:30]}...")
    print(f"   Cache stats: {perf.cache.get_stats()}")
    
    # Test lazy loading
    print("\n2. Testing lazy loading...")
    def expensive_load():
        print("   [Performing expensive load...]")
        return {"data": "expensive", "timestamp": time.time()}
    
    lazy_data = perf.lazy_load("test_data", expensive_load)
    print(f"   First access: {lazy_data['data']}")
    lazy_data2 = perf.lazy_load("test_data", expensive_load)
    print(f"   Second access: {lazy_data2['data']} (no reload)")
    
    # Test profiling
    print("\n3. Testing performance profiler...")
    
    @perf.profile("test_operation")
    def test_operation():
        time.sleep(0.01)  # 10ms
        return "done"
    
    for _ in range(5):
        test_operation()
    
    print(f"   Profile stats: {perf.profiler.get_stats('test_operation')}")
    
    # Overall stats
    print("\n4. Overall performance stats:")
    print(f"   {perf.get_stats()}")
    
    print("\n✅ Performance optimizations ready!")
