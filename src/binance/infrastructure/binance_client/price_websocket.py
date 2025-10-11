"""价格WebSocket连接器"""

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import Any

from binance.domain.entities.price_data import PriceData
from binance.domain.value_objects.price import Price
from binance.infrastructure.binance_client.websocket_client import (
    BinanceWebSocketClient,
)
from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)


class PriceWebSocketConnector:
    """价格WebSocket连接器

    负责连接币安价格流，解析价格数据，触发价格更新事件
    """

    def __init__(
        self,
        symbol: str,
        on_price_update: Callable[[PriceData], None] | None = None,
        on_connection_event: Callable[[str, dict[str, Any]], None] | None = None,
    ):
        """初始化价格WebSocket连接器

        Args:
            symbol: 代币符号（如 "koge_usdt"）
            on_price_update: 价格更新回调函数
            on_connection_event: 连接事件回调函数
        """
        self._symbol = symbol
        self._on_price_update = on_price_update
        self._on_connection_event = on_connection_event
        self._websocket_client = BinanceWebSocketClient()
        self._is_running = False

    async def start(self) -> None:
        """启动价格WebSocket连接"""
        if self._is_running:
            logger.warning("价格WebSocket已在运行")
            return

        # 注册消息处理器
        self._websocket_client.register_message_handler("aggTrade", self._handle_agg_trade)

        # 注册连接事件处理器
        self._websocket_client.register_connection_handler("connected", self._on_connected)
        self._websocket_client.register_connection_handler("disconnected", self._on_disconnected)
        self._websocket_client.register_connection_handler("connection_failed", self._on_connection_failed)

        # 构建流名称
        stream_name = f"{self._symbol}@aggTrade"

        try:
            await self._websocket_client.connect(stream_name)
            self._is_running = True

            # 开始监听消息
            await self._websocket_client.listen()

        except Exception as e:
            logger.error(f"启动价格WebSocket失败: {e}")
            await self._trigger_connection_event("start_failed", error=str(e))
            raise

    async def stop(self) -> None:
        """停止价格WebSocket连接"""
        if not self._is_running:
            return

        self._is_running = False
        await self._websocket_client.disconnect()
        logger.info("价格WebSocket已停止")

    async def _handle_agg_trade(self, data: dict[str, Any]) -> None:
        """处理聚合交易消息

        Args:
            data: 聚合交易数据
        """
        try:
            # 解析价格数据
            price_data = self._parse_agg_trade_data(data)

            if price_data and self._on_price_update:
                await self._on_price_update(price_data)

        except Exception as e:
            logger.error(f"处理聚合交易消息失败: {e}")

    def _parse_agg_trade_data(self, data: dict[str, Any]) -> PriceData | None:
        """解析聚合交易数据

        Args:
            data: 原始数据

        Returns:
            价格数据实体
        """
        try:
            # 提取必要字段
            symbol = data.get("s", "").lower()
            price_str = data.get("p", "0")
            volume_str = data.get("q", "0")
            timestamp_ms = data.get("T", 0)

            # 验证符号匹配
            if symbol != self._symbol:
                return None

            # 创建价格和数量
            price = Price(price_str, precision=8)
            volume = Decimal(volume_str)

            # 转换时间戳
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000)

            # 创建价格数据实体
            price_data = PriceData(
                symbol=symbol,
                price=price,
                volume=volume,
                timestamp=timestamp,
            )

            return price_data

        except Exception as e:
            logger.error(f"解析聚合交易数据失败: {e}")
            return None

    async def _on_connected(self) -> None:
        """连接成功事件处理"""
        logger.info(f"价格WebSocket连接成功: {self._symbol}")
        await self._trigger_connection_event("connected")

    async def _on_disconnected(self) -> None:
        """连接断开事件处理"""
        logger.info(f"价格WebSocket连接断开: {self._symbol}")
        await self._trigger_connection_event("disconnected")

    async def _on_connection_failed(self, error: str) -> None:
        """连接失败事件处理"""
        logger.error(f"价格WebSocket连接失败: {self._symbol}, 错误: {error}")
        await self._trigger_connection_event("connection_failed", error=error)

    async def _trigger_connection_event(self, event_type: str, **kwargs) -> None:
        """触发连接事件

        Args:
            event_type: 事件类型
            **kwargs: 额外参数
        """
        if self._on_connection_event:
            try:
                await self._on_connection_event(event_type, kwargs)
            except Exception as e:
                logger.error(f"处理连接事件失败: {event_type}, 错误: {e}")

    @property
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._is_running and self._websocket_client.is_connected

    @property
    def symbol(self) -> str:
        """获取代币符号"""
        return self._symbol

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.stop()
