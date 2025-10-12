"""价格监控应用服务"""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal

from binance.domain.entities.price_data import PriceData
from binance.domain.services.price_volatility_monitor import PriceVolatilityMonitor
from binance.infrastructure.binance_client.price_websocket import (
    PriceWebSocketConnector,
)
from binance.infrastructure.cache.cache_manager import CacheManager


logger = logging.getLogger(__name__)


class PriceMonitorService:
    """价格监控应用服务

    负责启动价格WebSocket连接，监控价格波动，触发暂停交易事件
    """

    def __init__(
        self,
        cache_manager: CacheManager,
        on_volatility_alert: Callable[[str, dict], None] | None = None,
        on_price_update: Callable[[PriceData], None] | None = None,
    ):
        """初始化价格监控服务

        Args:
            cache_manager: 缓存管理器
            on_volatility_alert: 波动警报回调函数
            on_price_update: 价格更新回调函数
        """
        self._cache_manager = cache_manager
        self._on_volatility_alert = on_volatility_alert
        self._on_price_update = on_price_update

        # 价格监控器字典，按代币符号存储
        self._monitors: dict[str, PriceVolatilityMonitor] = {}
        self._connectors: dict[str, PriceWebSocketConnector] = {}
        self._is_running = False

    async def start_monitoring(
        self, symbols: list[str], volatility_threshold: Decimal = Decimal("2.0")
    ) -> None:
        """启动价格监控

        Args:
            symbols: 要监控的代币符号列表
            volatility_threshold: 波动阈值（百分比）
        """
        if self._is_running:
            logger.warning("价格监控已在运行")
            return

        self._is_running = True

        # 为每个代币创建监控器
        for symbol in symbols:
            await self._create_monitor(symbol, volatility_threshold)
            await self._create_connector(symbol)

        logger.info(f"价格监控已启动，监控代币: {symbols}")

    async def stop_monitoring(self) -> None:
        """停止价格监控"""
        if not self._is_running:
            return

        # 停止所有连接器
        for connector in self._connectors.values():
            await connector.stop()

        self._connectors.clear()
        self._monitors.clear()
        self._is_running = False

        logger.info("价格监控已停止")

    async def add_symbol(
        self, symbol: str, volatility_threshold: Decimal = Decimal("2.0")
    ) -> None:
        """添加监控代币

        Args:
            symbol: 代币符号
            volatility_threshold: 波动阈值
        """
        if symbol in self._monitors:
            logger.warning(f"代币 {symbol} 已在监控中")
            return

        await self._create_monitor(symbol, volatility_threshold)
        await self._create_connector(symbol)

        logger.info(f"已添加监控代币: {symbol}")

    async def remove_symbol(self, symbol: str) -> None:
        """移除监控代币

        Args:
            symbol: 代币符号
        """
        if symbol not in self._monitors:
            logger.warning(f"代币 {symbol} 不在监控中")
            return

        # 停止连接器
        if symbol in self._connectors:
            await self._connectors[symbol].stop()
            del self._connectors[symbol]

        # 移除监控器
        del self._monitors[symbol]

        logger.info(f"已移除监控代币: {symbol}")

    async def _create_monitor(self, symbol: str, volatility_threshold: Decimal) -> None:
        """创建价格波动监控器

        Args:
            symbol: 代币符号
            volatility_threshold: 波动阈值
        """
        monitor = PriceVolatilityMonitor(
            window_size=60,  # 1分钟窗口
            threshold_percentage=volatility_threshold,
        )
        self._monitors[symbol] = monitor

    async def _create_connector(self, symbol: str) -> None:
        """创建价格WebSocket连接器

        Args:
            symbol: 代币符号
        """
        connector = PriceWebSocketConnector(
            symbol=symbol,
            on_price_update=self._handle_price_update,
            on_connection_event=self._handle_connection_event,
        )

        self._connectors[symbol] = connector

        # 启动连接器（在后台运行）
        asyncio.create_task(connector.start())

    async def _handle_price_update(self, price_data: PriceData) -> None:
        """处理价格更新

        Args:
            price_data: 价格数据
        """
        symbol = price_data.symbol

        # 更新缓存
        await self._cache_manager.add_price_to_history(
            symbol=symbol,
            price=float(price_data.price.value),
            timestamp=price_data.timestamp,
        )

        # 检查波动
        if symbol in self._monitors:
            monitor = self._monitors[symbol]
            is_volatile = monitor.add_price_data(price_data)

            if is_volatile:
                await self._handle_volatility_alert(symbol, monitor)

        # 触发价格更新回调
        if self._on_price_update:
            try:
                await self._on_price_update(price_data)
            except Exception as e:
                logger.error(f"价格更新回调失败: {e}")

    async def _handle_volatility_alert(
        self, symbol: str, monitor: PriceVolatilityMonitor
    ) -> None:
        """处理波动警报

        Args:
            symbol: 代币符号
            monitor: 监控器
        """
        volatility_info = monitor.get_volatility_info()

        alert_data = {
            "symbol": symbol,
            "volatility_percentage": float(volatility_info["volatility_percentage"]),
            "threshold": float(monitor._threshold_percentage),
            "price_range": {
                "min": float(volatility_info["price_range"]["min"]),
                "max": float(volatility_info["price_range"]["max"]),
            },
            "window_size": volatility_info["window_size"],
            "timestamp": datetime.now().isoformat(),
        }

        logger.warning(
            f"价格波动警报: {symbol}, 波动率: {alert_data['volatility_percentage']:.2f}%"
        )

        # 触发波动警报回调
        if self._on_volatility_alert:
            try:
                await self._on_volatility_alert(symbol, alert_data)
            except Exception as e:
                logger.error(f"波动警报回调失败: {e}")

    async def _handle_connection_event(self, event_type: str, data: dict) -> None:
        """处理连接事件

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        logger.info(f"WebSocket连接事件: {event_type}, 数据: {data}")

    async def get_price_statistics(self, symbol: str, minutes: int = 1) -> dict:
        """获取价格统计信息

        Args:
            symbol: 代币符号
            minutes: 统计时间范围（分钟）

        Returns:
            价格统计信息
        """
        return await self._cache_manager.get_price_history(symbol, minutes * 60)

    async def get_latest_price(self, symbol: str) -> dict | None:
        """获取最新价格

        Args:
            symbol: 代币符号

        Returns:
            最新价格数据
        """
        history = await self._cache_manager.get_price_history(symbol, 60)  # 最近1分钟
        if history:
            return history[-1]  # 返回最新的价格数据
        return None

    async def is_symbol_monitored(self, symbol: str) -> bool:
        """检查代币是否在监控中

        Args:
            symbol: 代币符号

        Returns:
            是否在监控中
        """
        return symbol in self._monitors

    async def get_monitored_symbols(self) -> list[str]:
        """获取正在监控的代币列表

        Returns:
            监控的代币符号列表
        """
        return list(self._monitors.keys())

    @property
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._is_running
