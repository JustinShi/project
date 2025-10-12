"""缓存管理器（代币精度和符号映射缓存逻辑）"""

import json
from datetime import datetime, timedelta
from functools import lru_cache

from redis.asyncio import Redis

from binance.config import get_settings
from binance.config.constants import CACHE_TTL_TOKEN_INFO, CacheKeyPrefix
from binance.infrastructure.logging import get_logger


logger = get_logger(__name__)


class CacheManager:
    """缓存管理器（处理代币信息缓存）"""

    def __init__(self, redis_client: Redis):
        """初始化缓存管理器

        Args:
            redis_client: Redis异步客户端
        """
        self._redis = redis_client
        self._settings = get_settings()

    async def get_token_precision(self, symbol_short: str) -> tuple[int, int] | None:
        """从缓存获取代币精度

        Args:
            symbol_short: 代币简称（如KOGE）

        Returns:
            (trade_decimal, token_decimal) 或 None（如果缓存不存在）

        Example:
            precision = await cache.get_token_precision("KOGE")
            if precision:
                trade_decimal, token_decimal = precision
        """
        key = f"{CacheKeyPrefix.TOKEN_PRECISION.value}{symbol_short}"

        try:
            data = await self._redis.get(key)
            if data:
                parsed = json.loads(data)
                logger.debug(
                    "token_precision_cache_hit",
                    symbol=symbol_short,
                    precision=parsed,
                )
                return (parsed["trade_decimal"], parsed["token_decimal"])

            logger.debug("token_precision_cache_miss", symbol=symbol_short)
            return None
        except Exception as e:
            logger.error(
                "token_precision_cache_error",
                symbol=symbol_short,
                error=str(e),
            )
            return None

    async def set_token_precision(
        self, symbol_short: str, trade_decimal: int, token_decimal: int
    ) -> bool:
        """设置代币精度到缓存

        Args:
            symbol_short: 代币简称
            trade_decimal: 交易精度
            token_decimal: 代币精度

        Returns:
            是否设置成功
        """
        key = f"{CacheKeyPrefix.TOKEN_PRECISION.value}{symbol_short}"
        data = json.dumps(
            {
                "trade_decimal": trade_decimal,
                "token_decimal": token_decimal,
                "cached_at": datetime.now().isoformat(),
            }
        )

        try:
            await self._redis.setex(key, CACHE_TTL_TOKEN_INFO, data)
            logger.info(
                "token_precision_cached",
                symbol=symbol_short,
                trade_decimal=trade_decimal,
                token_decimal=token_decimal,
                ttl=CACHE_TTL_TOKEN_INFO,
            )
            return True
        except Exception as e:
            logger.error(
                "token_precision_cache_set_error",
                symbol=symbol_short,
                error=str(e),
            )
            return False

    async def get_token_mapping(self, symbol_short: str) -> dict[str, str] | None:
        """从缓存获取代币符号映射

        Args:
            symbol_short: 代币简称

        Returns:
            包含order_api_symbol和websocket_symbol的字典，或None
        """
        key = f"{CacheKeyPrefix.TOKEN_MAPPING.value}{symbol_short}"

        try:
            data = await self._redis.get(key)
            if data:
                mapping = json.loads(data)
                logger.debug(
                    "token_mapping_cache_hit",
                    symbol=symbol_short,
                    mapping=mapping,
                )
                return mapping

            logger.debug("token_mapping_cache_miss", symbol=symbol_short)
            return None
        except Exception as e:
            logger.error(
                "token_mapping_cache_error",
                symbol=symbol_short,
                error=str(e),
            )
            return None

    async def set_token_mapping(
        self,
        symbol_short: str,
        order_api_symbol: str,
        websocket_symbol: str,
        alpha_id: str | None = None,
    ) -> bool:
        """设置代币符号映射到缓存

        Args:
            symbol_short: 代币简称
            order_api_symbol: 订单API符号
            websocket_symbol: WebSocket符号
            alpha_id: Alpha ID（可选）

        Returns:
            是否设置成功
        """
        key = f"{CacheKeyPrefix.TOKEN_MAPPING.value}{symbol_short}"
        data = json.dumps(
            {
                "order_api_symbol": order_api_symbol,
                "websocket_symbol": websocket_symbol,
                "alpha_id": alpha_id,
                "cached_at": datetime.now().isoformat(),
            }
        )

        try:
            await self._redis.setex(key, CACHE_TTL_TOKEN_INFO, data)
            logger.info(
                "token_mapping_cached",
                symbol=symbol_short,
                order_api_symbol=order_api_symbol,
                websocket_symbol=websocket_symbol,
                ttl=CACHE_TTL_TOKEN_INFO,
            )
            return True
        except Exception as e:
            logger.error(
                "token_mapping_cache_set_error",
                symbol=symbol_short,
                error=str(e),
            )
            return False

    async def add_price_to_history(
        self, symbol: str, price: float, timestamp: datetime | None = None
    ) -> bool:
        """添加价格到历史记录（用于波动监控）

        Args:
            symbol: 代币符号
            price: 价格
            timestamp: 时间戳（默认为当前时间）

        Returns:
            是否添加成功
        """
        if timestamp is None:
            timestamp = datetime.now()

        key = f"{CacheKeyPrefix.PRICE_HISTORY.value}{symbol}"
        score = timestamp.timestamp()
        member = json.dumps({"price": price, "timestamp": timestamp.isoformat()})

        try:
            # 添加到有序集合
            await self._redis.zadd(key, {member: score})

            # 删除超过监控窗口的数据
            cutoff_time = datetime.now() - timedelta(
                seconds=self._settings.price_volatility_window
            )
            await self._redis.zremrangebyscore(key, "-inf", cutoff_time.timestamp())

            # 设置键的过期时间（2倍监控窗口）
            await self._redis.expire(key, self._settings.price_volatility_window * 2)

            return True
        except Exception as e:
            logger.error(
                "price_history_add_error",
                symbol=symbol,
                price=price,
                error=str(e),
            )
            return False

    async def get_price_history(
        self, symbol: str, window_seconds: int | None = None
    ) -> list[dict]:
        """获取价格历史记录

        Args:
            symbol: 代币符号
            window_seconds: 时间窗口（秒），默认使用配置的波动监控窗口

        Returns:
            价格历史记录列表，按时间升序排列
        """
        if window_seconds is None:
            window_seconds = self._settings.price_volatility_window

        key = f"{CacheKeyPrefix.PRICE_HISTORY.value}{symbol}"
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)

        try:
            # 获取时间窗口内的所有价格
            members = await self._redis.zrangebyscore(
                key, cutoff_time.timestamp(), "+inf"
            )

            history = []
            for member in members:
                data = json.loads(member)
                history.append(data)

            logger.debug(
                "price_history_retrieved",
                symbol=symbol,
                count=len(history),
                window_seconds=window_seconds,
            )
            return history
        except Exception as e:
            logger.error(
                "price_history_get_error",
                symbol=symbol,
                error=str(e),
            )
            return []


@lru_cache
def get_cache_manager() -> CacheManager:
    """获取缓存管理器单例（需要先初始化Redis）

    Returns:
        CacheManager实例
    """
    from .redis_client import get_redis_client

    redis = get_redis_client()
    return CacheManager(redis)
