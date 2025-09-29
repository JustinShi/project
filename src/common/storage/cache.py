"""
通用缓存接口
提供统一的缓存操作接口，支持多种后端
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from loguru import logger


class Cache(ABC):
    """缓存接口抽象基类"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存项"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存项"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存项"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查缓存项是否存在"""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """清空所有缓存"""
        pass

    @abstractmethod
    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键列表"""
        pass

    @abstractmethod
    async def size(self) -> int:
        """获取缓存大小"""
        pass


class MemoryCache(Cache):
    """内存缓存实现"""

    def __init__(self, max_size: int = 1000):
        """
        初始化内存缓存

        Args:
            max_size: 最大缓存项数量
        """
        self._cache: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}
        self._max_size = max_size
        self._access_order: List[str] = []

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存项"""
        if key not in self._cache:
            return None

        # 检查是否过期
        if key in self._ttl and self._ttl[key] < asyncio.get_event_loop().time():
            await self.delete(key)
            return None

        # 更新访问顺序
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        return self._cache[key]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存项"""
        try:
            # 如果缓存已满，删除最旧的项
            if len(self._cache) >= self._max_size and key not in self._cache:
                await self._evict_oldest()

            self._cache[key] = value

            # 设置过期时间
            if ttl:
                self._ttl[key] = asyncio.get_event_loop().time() + ttl

            # 更新访问顺序
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)

            return True

        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存项"""
        try:
            if key in self._cache:
                del self._cache[key]
            if key in self._ttl:
                del self._ttl[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return True

        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查缓存项是否存在"""
        if key not in self._cache:
            return False

        # 检查是否过期
        if key in self._ttl and self._ttl[key] < asyncio.get_event_loop().time():
            await self.delete(key)
            return False

        return True

    async def clear(self) -> bool:
        """清空所有缓存"""
        try:
            self._cache.clear()
            self._ttl.clear()
            self._access_order.clear()
            return True

        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False

    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键列表"""
        if pattern == "*":
            return list(self._cache.keys())

        # 简单的模式匹配
        import fnmatch

        return [key for key in self._cache if fnmatch.fnmatch(key, pattern)]

    async def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)

    async def _evict_oldest(self) -> None:
        """删除最旧的缓存项"""
        if self._access_order:
            oldest_key = self._access_order[0]
            await self.delete(oldest_key)


class RedisCache(Cache):
    """Redis 缓存实现"""

    def __init__(self, redis_client=None):
        """
        初始化 Redis 缓存

        Args:
            redis_client: Redis 客户端实例
        """
        self._redis = redis_client
        self._prefix = "cache:"

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存项"""
        try:
            if not self._redis:
                return None

            full_key = f"{self._prefix}{key}"
            value = await self._redis.get(full_key)

            if value is None:
                return None

            # 尝试解析 JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存项"""
        try:
            if not self._redis:
                return False

            full_key = f"{self._prefix}{key}"

            # 序列化值
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif not isinstance(value, (str, int, float, bool)):
                value = str(value)

            if ttl:
                await self._redis.setex(full_key, ttl, value)
            else:
                await self._redis.set(full_key, value)

            return True

        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存项"""
        try:
            if not self._redis:
                return False

            full_key = f"{self._prefix}{key}"
            result = await self._redis.delete(full_key)
            return result > 0

        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查缓存项是否存在"""
        try:
            if not self._redis:
                return False

            full_key = f"{self._prefix}{key}"
            result = await self._redis.exists(full_key)
            return result > 0

        except Exception as e:
            logger.error(f"检查缓存存在性失败: {e}")
            return False

    async def clear(self) -> bool:
        """清空所有缓存"""
        try:
            if not self._redis:
                return False

            pattern = f"{self._prefix}*"
            keys = await self._redis.keys(pattern)

            if keys:
                await self._redis.delete(*keys)

            return True

        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False

    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键列表"""
        try:
            if not self._redis:
                return []

            full_pattern = f"{self._prefix}{pattern}"
            keys = await self._redis.keys(full_pattern)

            # 移除前缀
            return [key.decode().replace(self._prefix, "") for key in keys]

        except Exception as e:
            logger.error(f"获取键列表失败: {e}")
            return []

    async def size(self) -> int:
        """获取缓存大小"""
        try:
            if not self._redis:
                return 0

            pattern = f"{self._prefix}*"
            keys = await self._redis.keys(pattern)
            return len(keys)

        except Exception as e:
            logger.error(f"获取缓存大小失败: {e}")
            return 0


class CacheManager:
    """缓存管理器"""

    def __init__(self, default_cache: Optional[Cache] = None):
        """
        初始化缓存管理器

        Args:
            default_cache: 默认缓存实例
        """
        self._caches: Dict[str, Cache] = {}
        self._default_cache = default_cache

    def register_cache(self, name: str, cache: Cache) -> None:
        """
        注册缓存实例

        Args:
            name: 缓存名称
            cache: 缓存实例
        """
        self._caches[name] = cache

    def get_cache(self, name: Optional[str] = None) -> Optional[Cache]:
        """
        获取缓存实例

        Args:
            name: 缓存名称，None 时返回默认缓存

        Returns:
            缓存实例或 None
        """
        if name is None:
            return self._default_cache
        return self._caches.get(name)

    async def get(self, key: str, cache_name: Optional[str] = None) -> Optional[Any]:
        """获取缓存项"""
        cache = self.get_cache(cache_name)
        if cache:
            return await cache.get(key)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        cache_name: Optional[str] = None,
    ) -> bool:
        """设置缓存项"""
        cache = self.get_cache(cache_name)
        if cache:
            return await cache.set(key, value, ttl)
        return False

    async def delete(self, key: str, cache_name: Optional[str] = None) -> bool:
        """删除缓存项"""
        cache = self.get_cache(cache_name)
        if cache:
            return await cache.delete(key)
        return False

    async def exists(self, key: str, cache_name: Optional[str] = None) -> bool:
        """检查缓存项是否存在"""
        cache = self.get_cache(cache_name)
        if cache:
            return await cache.exists(key)
        return False

    async def clear(self, cache_name: Optional[str] = None) -> bool:
        """清空缓存"""
        cache = self.get_cache(cache_name)
        if cache:
            return await cache.clear()
        return False

    def list_caches(self) -> List[str]:
        """获取所有缓存名称"""
        return list(self._caches.keys())

    def get_cache_info(self, cache_name: Optional[str] = None) -> Dict[str, Any]:
        """获取缓存信息"""
        cache = self.get_cache(cache_name)
        if not cache:
            return {}

        return {
            "name": cache_name or "default",
            "type": type(cache).__name__,
            "size": 0,  # 需要异步获取，这里简化处理
        }
