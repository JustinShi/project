"""Redis客户端管理"""

from functools import lru_cache
from typing import Optional

from redis.asyncio import Redis

from binance.config import get_settings

_redis_client: Optional[Redis] = None


async def init_redis() -> Redis:
    """初始化Redis客户端

    Returns:
        Redis异步客户端实例
    """
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    settings = get_settings()

    _redis_client = Redis.from_url(
        str(settings.redis_url),
        encoding="utf-8",
        decode_responses=True,
        password=settings.redis_password if settings.redis_password else None,
        db=settings.redis_db,
        socket_connect_timeout=5,
        socket_keepalive=True,
        health_check_interval=30,
    )

    # 测试连接
    await _redis_client.ping()

    return _redis_client


@lru_cache
def get_redis_client() -> Redis:
    """获取Redis客户端（同步访问）

    注意：这个函数返回的是全局单例，需要先调用init_redis()初始化

    Returns:
        Redis异步客户端实例

    Example:
        # 在应用启动时
        await init_redis()

        # 在依赖注入中
        redis = get_redis_client()
        await redis.set("key", "value")
    """
    if _redis_client is None:
        raise RuntimeError(
            "Redis client not initialized. Call init_redis() first."
        )
    return _redis_client


async def close_redis() -> None:
    """关闭Redis连接"""
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None

