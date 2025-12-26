"""
Redis-based caching service for reference data.
"""
import json
from typing import Optional, List, Dict, Any
from datetime import timedelta
import structlog

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

from app.core.config import settings

logger = structlog.get_logger()

class CacheService:
    """Redis-based caching service."""
    
    def __init__(self):
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis module not available. Caching will be disabled.")
            self.redis_client = None
            return
            
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching will be disabled.")
            self.redis_client = None
    
    def _get_key(self, prefix: str, *args: str) -> str:
        """Generate cache key with prefix."""
        key_parts = [settings.CACHE_PREFIX, prefix] + list(args)
        return ":".join(key_parts)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        if not self.redis_client:
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            if ttl:
                return self.redis_client.setex(key, ttl, serialized_value)
            else:
                return self.redis_client.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False


class ReferenceDataCache:
    """Specialized caching for reference data with language support."""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.default_ttl = 300  # 5 minutes
    
    def get_categories_key(self, language: str, active_only: bool) -> str:
        """Generate cache key for categories."""
        return self.cache._get_key(
            "reference_categories",
            language,
            "active" if active_only else "all"
        )
    
    def get_data_key(self, category_code: str, language: str, active_only: bool, 
                     search: Optional[str] = None, page: int = 1, limit: int = 50) -> str:
        """Generate cache key for reference data."""
        search_key = f"search_{search}" if search else "no_search"
        return self.cache._get_key(
            "reference_data",
            category_code,
            language,
            "active" if active_only else "all",
            search_key,
            f"page_{page}",
            f"limit_{limit}"
        )
    
    def get_categories(self, language: str, active_only: bool) -> Optional[List[Dict[str, Any]]]:
        """Get cached categories."""
        key = self.get_categories_key(language, active_only)
        cached_data = self.cache.get(key)
        
        if cached_data:
            logger.info(
                "Cache hit for categories",
                language=language,
                active_only=active_only,
                key=key
            )
            return cached_data
        
        logger.info(
            "Cache miss for categories",
            language=language,
            active_only=active_only,
            key=key
        )
        return None
    
    def set_categories(self, language: str, active_only: bool, 
                      categories: List[Dict[str, Any]], ttl: Optional[int] = None) -> bool:
        """Cache categories."""
        key = self.get_categories_key(language, active_only)
        success = self.cache.set(key, categories, ttl or self.default_ttl)
        
        if success:
            logger.info(
                "Categories cached",
                language=language,
                active_only=active_only,
                count=len(categories),
                key=key,
                ttl=ttl or self.default_ttl
            )
        
        return success
    
    def get_reference_data(self, category_code: str, language: str, active_only: bool,
                          search: Optional[str] = None, page: int = 1, 
                          limit: int = 50) -> Optional[Dict[str, Any]]:
        """Get cached reference data."""
        key = self.get_data_key(category_code, language, active_only, search, page, limit)
        cached_data = self.cache.get(key)
        
        if cached_data:
            logger.info(
                "Cache hit for reference data",
                category_code=category_code,
                language=language,
                active_only=active_only,
                search=search,
                page=page,
                limit=limit,
                key=key
            )
            return cached_data
        
        logger.info(
            "Cache miss for reference data",
            category_code=category_code,
            language=language,
            active_only=active_only,
            search=search,
            page=page,
            limit=limit,
            key=key
        )
        return None
    
    def set_reference_data(self, category_code: str, language: str, active_only: bool,
                          data: Dict[str, Any], search: Optional[str] = None, 
                          page: int = 1, limit: int = 50, ttl: Optional[int] = None) -> bool:
        """Cache reference data."""
        key = self.get_data_key(category_code, language, active_only, search, page, limit)
        success = self.cache.set(key, data, ttl or self.default_ttl)
        
        if success:
            logger.info(
                "Reference data cached",
                category_code=category_code,
                language=language,
                active_only=active_only,
                search=search,
                page=page,
                limit=limit,
                count=len(data.get('items', [])),
                key=key,
                ttl=ttl or self.default_ttl
            )
        
        return success
    
    def invalidate_categories(self) -> int:
        """Invalidate all cached categories."""
        pattern = self.cache._get_key("reference_categories", "*")
        deleted = self.cache.delete_pattern(pattern)
        
        logger.info(
            "Categories cache invalidated",
            deleted_keys=deleted,
            pattern=pattern
        )
        
        return deleted
    
    def invalidate_category_data(self, category_code: str) -> int:
        """Invalidate cached data for specific category."""
        pattern = self.cache._get_key("reference_data", category_code, "*")
        deleted = self.cache.delete_pattern(pattern)
        
        logger.info(
            "Category data cache invalidated",
            category_code=category_code,
            deleted_keys=deleted,
            pattern=pattern
        )
        
        return deleted
    
    def invalidate_all_reference_data(self) -> int:
        """Invalidate all cached reference data."""
        pattern = self.cache._get_key("reference_data", "*")
        deleted = self.cache.delete_pattern(pattern)
        
        logger.info(
            "All reference data cache invalidated",
            deleted_keys=deleted,
            pattern=pattern
        )
        
        return deleted
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.cache.redis_client:
            return {"status": "disabled"}
        
        try:
            info = self.cache.redis_client.info()
            
            # Count reference data keys
            categories_pattern = self.cache._get_key("reference_categories", "*")
            data_pattern = self.cache._get_key("reference_data", "*")
            
            categories_keys = len(self.cache.redis_client.keys(categories_pattern))
            data_keys = len(self.cache.redis_client.keys(data_pattern))
            
            return {
                "status": "enabled",
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "reference_data_keys": {
                    "categories": categories_keys,
                    "data": data_keys,
                    "total": categories_keys + data_keys
                }
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "error": str(e)}


# Global cache instances
cache_service = CacheService()
reference_data_cache = ReferenceDataCache(cache_service)