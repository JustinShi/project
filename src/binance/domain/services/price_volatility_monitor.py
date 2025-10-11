"""价格波动监控领域服务"""

from collections import deque
from datetime import datetime, timedelta
from decimal import Decimal

from binance.domain.entities.price_data import PriceData


class PriceVolatilityMonitor:
    """价格波动监控领域服务

    使用滑动窗口算法监控价格波动，检测异常波动
    """

    def __init__(self, window_size: int = 60, threshold_percentage: Decimal = Decimal("2.0")):
        """初始化价格波动监控器

        Args:
            window_size: 滑动窗口大小（秒）
            threshold_percentage: 波动阈值（百分比）
        """
        self._window_size = window_size
        self._threshold_percentage = threshold_percentage
        self._price_history: deque[PriceData] = deque(maxlen=window_size)
        self._last_check_time: datetime | None = None

    def add_price_data(self, price_data: PriceData) -> bool:
        """添加价格数据并检查波动

        Args:
            price_data: 价格数据

        Returns:
            是否触发波动警报
        """
        self._price_history.append(price_data)
        self._last_check_time = price_data.timestamp

        # 如果历史数据不足，不进行波动检查
        if len(self._price_history) < 2:
            return False

        return self._check_volatility()

    def _check_volatility(self) -> bool:
        """检查价格波动是否超过阈值

        Returns:
            是否超过波动阈值
        """
        if len(self._price_history) < 2:
            return False

        # 获取窗口内的价格范围
        prices = [data.price.value for data in self._price_history]
        min_price = min(prices)
        max_price = max(prices)

        # 计算波动百分比
        if min_price == 0:
            return False

        volatility = ((max_price - min_price) / min_price) * Decimal("100")

        return volatility >= self._threshold_percentage

    def get_volatility_info(self) -> dict:
        """获取波动信息

        Returns:
            波动信息字典
        """
        if len(self._price_history) < 2:
            return {
                "volatility_percentage": Decimal("0"),
                "is_volatile": False,
                "price_range": {"min": Decimal("0"), "max": Decimal("0")},
                "window_size": len(self._price_history),
            }

        prices = [data.price.value for data in self._price_history]
        min_price = min(prices)
        max_price = max(prices)

        volatility = Decimal("0")
        if min_price > 0:
            volatility = ((max_price - min_price) / min_price) * Decimal("100")

        return {
            "volatility_percentage": volatility,
            "is_volatile": volatility >= self._threshold_percentage,
            "price_range": {"min": min_price, "max": max_price},
            "window_size": len(self._price_history),
            "threshold": self._threshold_percentage,
        }

    def get_recent_prices(self, count: int = 10) -> list[PriceData]:
        """获取最近的价格数据

        Args:
            count: 返回数量

        Returns:
            最近的价格数据列表
        """
        return list(self._price_history)[-count:]

    def clear_history(self) -> None:
        """清空价格历史"""
        self._price_history.clear()
        self._last_check_time = None

    def is_window_full(self) -> bool:
        """检查滑动窗口是否已满

        Returns:
            是否已满
        """
        return len(self._price_history) == self._window_size

    def get_window_utilization(self) -> float:
        """获取窗口利用率

        Returns:
            利用率（0.0-1.0）
        """
        return len(self._price_history) / self._window_size

    def should_check_volatility(self, current_time: datetime) -> bool:
        """检查是否应该进行波动检查

        Args:
            current_time: 当前时间

        Returns:
            是否应该检查
        """
        if self._last_check_time is None:
            return True

        # 每分钟检查一次
        time_diff = current_time - self._last_check_time
        return time_diff >= timedelta(minutes=1)

    def __str__(self) -> str:
        return (
            f"PriceVolatilityMonitor(window_size={self._window_size}, "
            f"threshold={self._threshold_percentage}%, "
            f"history_count={len(self._price_history)})"
        )
