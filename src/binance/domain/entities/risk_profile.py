"""风险配置文件实体"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any


class RiskLevel(str, Enum):
    """风险等级"""

    LOW = "LOW"  # 低风险
    MEDIUM = "MEDIUM"  # 中等风险
    HIGH = "HIGH"  # 高风险
    CRITICAL = "CRITICAL"  # 极高风险


class RiskFactor(str, Enum):
    """风险因子"""

    PRICE_VOLATILITY = "PRICE_VOLATILITY"  # 价格波动
    BALANCE_INSUFFICIENT = "BALANCE_INSUFFICIENT"  # 余额不足
    ORDER_FREQUENCY = "ORDER_FREQUENCY"  # 订单频率
    POSITION_SIZE = "POSITION_SIZE"  # 仓位大小
    MARKET_CONDITIONS = "MARKET_CONDITIONS"  # 市场条件
    USER_BEHAVIOR = "USER_BEHAVIOR"  # 用户行为


@dataclass
class RiskProfile:
    """风险配置文件"""

    id: int
    user_id: int

    # 风险等级
    risk_level: RiskLevel = RiskLevel.MEDIUM

    # 价格波动风险控制
    max_price_volatility: Decimal = Decimal("5.0")  # 最大价格波动百分比
    volatility_window_minutes: int = 10  # 波动计算窗口（分钟）

    # 余额风险控制
    min_balance_ratio: Decimal = Decimal("0.1")  # 最小余额比例（10%）
    max_position_ratio: Decimal = Decimal("0.3")  # 最大仓位比例（30%）

    # 订单频率控制
    max_orders_per_hour: int = 10  # 每小时最大订单数
    max_orders_per_day: int = 50  # 每天最大订单数

    # 仓位大小控制
    max_single_order_amount: Decimal = Decimal("1000.0")  # 单笔订单最大金额
    max_daily_volume: Decimal = Decimal("10000.0")  # 每日最大交易量

    # 市场条件控制
    trading_hours_start: int = 9  # 交易开始时间（小时）
    trading_hours_end: int = 21  # 交易结束时间（小时）
    weekend_trading: bool = False  # 是否允许周末交易

    # 用户行为控制
    max_consecutive_losses: int = 3  # 最大连续亏损次数
    max_daily_loss: Decimal = Decimal("500.0")  # 每日最大亏损

    # 元数据
    created_at: datetime | None = None
    updated_at: datetime | None = None
    is_active: bool = True

    def validate(self) -> tuple[bool, str]:
        """验证风险配置"""
        if self.max_price_volatility <= 0:
            return False, "最大价格波动必须大于0"

        if self.min_balance_ratio <= 0 or self.min_balance_ratio >= 1:
            return False, "最小余额比例必须在0-1之间"

        if self.max_position_ratio <= 0 or self.max_position_ratio >= 1:
            return False, "最大仓位比例必须在0-1之间"

        if self.max_orders_per_hour <= 0:
            return False, "每小时最大订单数必须大于0"

        if self.max_orders_per_day <= 0:
            return False, "每天最大订单数必须大于0"

        if self.max_single_order_amount <= 0:
            return False, "单笔订单最大金额必须大于0"

        if self.max_daily_volume <= 0:
            return False, "每日最大交易量必须大于0"

        if self.trading_hours_start < 0 or self.trading_hours_start >= 24:
            return False, "交易开始时间必须在0-23之间"

        if self.trading_hours_end < 0 or self.trading_hours_end >= 24:
            return False, "交易结束时间必须在0-23之间"

        if self.trading_hours_start >= self.trading_hours_end:
            return False, "交易开始时间必须早于结束时间"

        if self.max_consecutive_losses < 0:
            return False, "最大连续亏损次数不能为负数"

        if self.max_daily_loss < 0:
            return False, "每日最大亏损不能为负数"

        return True, "风险配置验证通过"

    def is_trading_allowed(self, current_time: datetime) -> bool:
        """检查是否允许交易"""
        if not self.is_active:
            return False

        # 检查交易时间
        current_hour = current_time.hour
        if not self.weekend_trading and current_time.weekday() >= 5:  # 周末
            return False

        return not (
            current_hour < self.trading_hours_start
            or current_hour >= self.trading_hours_end
        )

    def get_max_order_amount(self, current_balance: Decimal) -> Decimal:
        """获取最大订单金额"""
        # 基于余额和仓位比例计算
        max_by_balance = current_balance * self.max_position_ratio
        return min(max_by_balance, self.max_single_order_amount)

    def should_pause_trading(
        self, consecutive_losses: int, daily_loss: Decimal
    ) -> bool:
        """检查是否应该暂停交易"""
        if consecutive_losses >= self.max_consecutive_losses:
            return True

        return daily_loss >= self.max_daily_loss

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "risk_level": self.risk_level.value,
            "max_price_volatility": float(self.max_price_volatility),
            "volatility_window_minutes": self.volatility_window_minutes,
            "min_balance_ratio": float(self.min_balance_ratio),
            "max_position_ratio": float(self.max_position_ratio),
            "max_orders_per_hour": self.max_orders_per_hour,
            "max_orders_per_day": self.max_orders_per_day,
            "max_single_order_amount": float(self.max_single_order_amount),
            "max_daily_volume": float(self.max_daily_volume),
            "trading_hours_start": self.trading_hours_start,
            "trading_hours_end": self.trading_hours_end,
            "weekend_trading": self.weekend_trading,
            "max_consecutive_losses": self.max_consecutive_losses,
            "max_daily_loss": float(self.max_daily_loss),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
