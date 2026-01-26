"""
Redis Cache Service for Doutora IA
Reduces LLM costs by 80% by caching repeated analyses
"""

import os
import json
import hashlib
import logging
from typing import Optional, Any, Callable
from functools import wraps
import redis
from datetime import timedelta

logger = logging.getLogger(__name__)


class CacheService:
    """
    Redis-based caching service with smart invalidation
    """

    def __init__(self):
        self.enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"

        if self.enabled:
            try:
                self.redis_client = redis.Redis(
                    host=os.getenv("REDIS_HOST", "redis"),
                    port=int(os.getenv("REDIS_PORT", "6379")),
                    password=os.getenv("REDIS_PASSWORD", ""),
                    db=int(os.getenv("REDIS_DB", "0")),
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )

                # Test connection
                self.redis_client.ping()
                logger.info("✓ Redis cache enabled and connected")

            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Cache disabled.")
                self.enabled = False
        else:
            logger.info("Redis cache disabled (REDIS_ENABLED=false)")
            self.redis_client = None

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create deterministic key from arguments
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_json = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_json.encode()).hexdigest()

        return f"doutora_ia:{prefix}:{key_hash}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        expire: int = 3600
    ) -> bool:
        """Set value in cache with expiration"""
        if not self.enabled:
            return False

        try:
            value_json = json.dumps(value)
            self.redis_client.setex(key, expire, value_json)
            logger.debug(f"Cache SET: {key} (expire={expire}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False

        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cache DELETE pattern '{pattern}': {deleted} keys")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return 0

    def clear_all(self) -> bool:
        """Clear all cache (use with caution!)"""
        if not self.enabled:
            return False

        try:
            self.redis_client.flushdb()
            logger.warning("Cache CLEARED (all keys deleted)")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}

        try:
            info = self.redis_client.info("stats")
            return {
                "enabled": True,
                "total_keys": self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0) /
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100,
                    2
                ),
                "memory_used": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"enabled": True, "error": str(e)}


# Decorators for easy caching

def cached(
    prefix: str = "default",
    expire: int = 3600,
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache function results

    Usage:
        @cached(prefix="analysis", expire=7200)
        def analyze_case(descricao: str):
            # expensive operation
            return result
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache_service._generate_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                logger.info(f"✓ Returning cached result for {func.__name__}")
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache_service.set(cache_key, result, expire)

            return result

        return wrapper
    return decorator


def cache_invalidate(pattern: str):
    """
    Decorator to invalidate cache after function execution

    Usage:
        @cache_invalidate("analysis:*")
        def update_rag_data():
            # update operation
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache_service.delete_pattern(pattern)
            return result
        return wrapper
    return decorator


# Global instance
cache_service = CacheService()


# Utility functions for common patterns

def cache_search_results(query: str, filtros: dict, limit: int, results: list, expire: int = 1800):
    """Cache RAG search results (30 min default)"""
    key = cache_service._generate_key("search", query, filtros, limit)
    cache_service.set(key, results, expire)


def get_cached_search(query: str, filtros: dict, limit: int) -> Optional[list]:
    """Get cached search results"""
    key = cache_service._generate_key("search", query, filtros, limit)
    return cache_service.get(key)


def cache_analysis(descricao: str, detalhado: bool, analysis: dict, expire: int = 7200):
    """Cache case analysis (2 hours default)"""
    key = cache_service._generate_key("analysis", descricao, detalhado)
    cache_service.set(key, analysis, expire)


def get_cached_analysis(descricao: str, detalhado: bool) -> Optional[dict]:
    """Get cached analysis"""
    key = cache_service._generate_key("analysis", descricao, detalhado)
    return cache_service.get(key)


def invalidate_user_cache(user_id: int):
    """Invalidate all cache for a specific user"""
    cache_service.delete_pattern(f"doutora_ia:user:{user_id}:*")


def get_cache_metrics() -> dict:
    """Get cache performance metrics"""
    stats = cache_service.get_stats()

    if not stats.get("enabled"):
        return {
            "enabled": False,
            "message": "Cache is disabled"
        }

    return {
        "enabled": True,
        "performance": {
            "hit_rate": f"{stats['hit_rate']}%",
            "total_hits": stats["hits"],
            "total_misses": stats["misses"],
        },
        "storage": {
            "total_keys": stats["total_keys"],
            "memory_used": stats["memory_used"],
        },
        "estimated_savings": {
            "llm_calls_saved": stats["hits"],
            "cost_saved_usd": round(stats["hits"] * 0.01, 2),  # ~$0.01 per call
            "message": f"Saved ~${round(stats['hits'] * 0.01, 2)} in LLM costs"
        }
    }
