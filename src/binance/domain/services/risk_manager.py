"""风险管理服务"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from binance.domain.entities.price_data import PriceData
from binance.domain.entities.risk_alert import AlertSeverity, RiskAlert
from binance.domain.entities.risk_profile import RiskFactor, RiskLevel, RiskProfile


@dataclass
class RiskMetrics:
    """风险指标"""
    user_id: int
    current_balance: Decimal
    daily_volume: Decimal
    daily_pnl: Decimal
    consecutive_losses: int
    orders_count_today: int
    orders_count_hour: int
    last_order_time: datetime | None
    price_volatility: Decimal
    position_ratio: Decimal


class RiskManager:
    """风险管理服务"""

    def __init__(self):
        self._risk_profiles: dict[int, RiskProfile] = {}
        self._active_alerts: dict[int, list[RiskAlert]] = {}
        self._risk_metrics: dict[int, RiskMetrics] = {}

    def set_risk_profile(self, profile: RiskProfile) -> None:
        """设置用户风险配置"""
        self._risk_profiles[profile.user_id] = profile

    def get_risk_profile(self, user_id: int) -> RiskProfile | None:
        """获取用户风险配置"""
        return self._risk_profiles.get(user_id)

    def update_risk_metrics(self, user_id: int, metrics: RiskMetrics) -> None:
        """更新风险指标"""
        self._risk_metrics[user_id] = metrics

    def get_risk_metrics(self, user_id: int) -> RiskMetrics | None:
        """获取风险指标"""
        return self._risk_metrics.get(user_id)

    def assess_order_risk(
        self,
        user_id: int,
        symbol: str,
        order_amount: Decimal,
        current_price: PriceData
    ) -> tuple[bool, str, list[RiskAlert]]:
        """评估订单风险"""
        alerts = []

        # 获取用户风险配置
        profile = self.get_risk_profile(user_id)
        if not profile:
            return False, "用户风险配置不存在", []

        # 获取风险指标
        metrics = self.get_risk_metrics(user_id)
        if not metrics:
            return False, "用户风险指标不存在", []

        # 检查交易时间
        if not profile.is_trading_allowed(datetime.now()):
            alert = self._create_alert(
                user_id=user_id,
                title="交易时间限制",
                message="当前时间不允许交易",
                severity=AlertSeverity.WARNING,
                risk_factor=RiskFactor.USER_BEHAVIOR,
                risk_level=RiskLevel.MEDIUM
            )
            alerts.append(alert)
            return False, "交易时间限制", alerts

        # 检查余额风险
        if metrics.current_balance < order_amount:
            alert = self._create_alert(
                user_id=user_id,
                title="余额不足",
                message=f"余额不足，需要 {order_amount} USDT，可用 {metrics.current_balance} USDT",
                severity=AlertSeverity.ERROR,
                risk_factor=RiskFactor.BALANCE_INSUFFICIENT,
                risk_level=RiskLevel.HIGH,
                current_value=metrics.current_balance,
                threshold_value=order_amount
            )
            alerts.append(alert)
            return False, "余额不足", alerts

        # 检查仓位风险
        max_position = profile.get_max_order_amount(metrics.current_balance)
        if order_amount > max_position:
            alert = self._create_alert(
                user_id=user_id,
                title="仓位过大",
                message=f"订单金额 {order_amount} USDT 超过最大仓位 {max_position} USDT",
                severity=AlertSeverity.WARNING,
                risk_factor=RiskFactor.POSITION_SIZE,
                risk_level=RiskLevel.MEDIUM,
                current_value=order_amount,
                threshold_value=max_position
            )
            alerts.append(alert)
            return False, "仓位过大", alerts

        # 检查价格波动风险
        if metrics.price_volatility > profile.max_price_volatility:
            alert = self._create_alert(
                user_id=user_id,
                title="价格波动过大",
                message=f"价格波动 {metrics.price_volatility:.2f}% 超过阈值 {profile.max_price_volatility:.2f}%",
                severity=AlertSeverity.ERROR,
                risk_factor=RiskFactor.PRICE_VOLATILITY,
                risk_level=RiskLevel.HIGH,
                current_value=metrics.price_volatility,
                threshold_value=profile.max_price_volatility
            )
            alerts.append(alert)
            return False, "价格波动过大", alerts

        # 检查订单频率风险
        if metrics.orders_count_hour >= profile.max_orders_per_hour:
            alert = self._create_alert(
                user_id=user_id,
                title="订单频率过高",
                message=f"每小时订单数 {metrics.orders_count_hour} 超过限制 {profile.max_orders_per_hour}",
                severity=AlertSeverity.WARNING,
                risk_factor=RiskFactor.ORDER_FREQUENCY,
                risk_level=RiskLevel.MEDIUM,
                current_value=Decimal(metrics.orders_count_hour),
                threshold_value=Decimal(profile.max_orders_per_hour)
            )
            alerts.append(alert)
            return False, "订单频率过高", alerts

        if metrics.orders_count_today >= profile.max_orders_per_day:
            alert = self._create_alert(
                user_id=user_id,
                title="每日订单数超限",
                message=f"每日订单数 {metrics.orders_count_today} 超过限制 {profile.max_orders_per_day}",
                severity=AlertSeverity.ERROR,
                risk_factor=RiskFactor.ORDER_FREQUENCY,
                risk_level=RiskLevel.HIGH,
                current_value=Decimal(metrics.orders_count_today),
                threshold_value=Decimal(profile.max_orders_per_day)
            )
            alerts.append(alert)
            return False, "每日订单数超限", alerts

        # 检查连续亏损风险
        if profile.should_pause_trading(metrics.consecutive_losses, metrics.daily_pnl):
            alert = self._create_alert(
                user_id=user_id,
                title="交易暂停",
                message=f"连续亏损 {metrics.consecutive_losses} 次或日亏损 {metrics.daily_pnl} USDT 超过限制",
                severity=AlertSeverity.CRITICAL,
                risk_factor=RiskFactor.USER_BEHAVIOR,
                risk_level=RiskLevel.CRITICAL,
                current_value=Decimal(metrics.consecutive_losses),
                threshold_value=Decimal(profile.max_consecutive_losses)
            )
            alerts.append(alert)
            return False, "交易暂停", alerts

        # 检查每日交易量风险
        if metrics.daily_volume + order_amount > profile.max_daily_volume:
            alert = self._create_alert(
                user_id=user_id,
                title="每日交易量超限",
                message=f"每日交易量 {metrics.daily_volume + order_amount} USDT 超过限制 {profile.max_daily_volume} USDT",
                severity=AlertSeverity.WARNING,
                risk_factor=RiskFactor.POSITION_SIZE,
                risk_level=RiskLevel.MEDIUM,
                current_value=metrics.daily_volume + order_amount,
                threshold_value=profile.max_daily_volume
            )
            alerts.append(alert)
            return False, "每日交易量超限", alerts

        return True, "风险检查通过", alerts

    def monitor_price_volatility(
        self,
        user_id: int,
        symbol: str,
        price_data: PriceData,
        price_history: list[PriceData]
    ) -> list[RiskAlert]:
        """监控价格波动"""
        alerts = []

        profile = self.get_risk_profile(user_id)
        if not profile:
            return alerts

        # 计算价格波动
        if len(price_history) < 2:
            return alerts

        # 获取时间窗口内的价格数据
        window_start = datetime.now() - timedelta(minutes=profile.volatility_window_minutes)
        window_prices = [p for p in price_history if p.timestamp >= window_start]

        if len(window_prices) < 2:
            return alerts

        # 计算波动率
        prices = [float(p.price.value) for p in window_prices]
        min_price = min(prices)
        max_price = max(prices)
        volatility = ((max_price - min_price) / min_price) * 100

        if volatility > profile.max_price_volatility:
            alert = self._create_alert(
                user_id=user_id,
                title="价格波动警报",
                message=f"{symbol} 价格波动 {volatility:.2f}% 超过阈值 {profile.max_price_volatility:.2f}%",
                severity=AlertSeverity.ERROR,
                risk_factor=RiskFactor.PRICE_VOLATILITY,
                risk_level=RiskLevel.HIGH,
                current_value=Decimal(volatility),
                threshold_value=profile.max_price_volatility,
                data={"symbol": symbol, "window_minutes": profile.volatility_window_minutes}
            )
            alerts.append(alert)

        return alerts

    def create_risk_profile(
        self,
        user_id: int,
        risk_level: RiskLevel = RiskLevel.MEDIUM
    ) -> RiskProfile:
        """创建默认风险配置"""
        if risk_level == RiskLevel.LOW:
            return RiskProfile(
                id=0,  # 临时ID
                user_id=user_id,
                risk_level=risk_level,
                max_price_volatility=Decimal("3.0"),
                max_position_ratio=Decimal("0.2"),
                max_orders_per_hour=5,
                max_orders_per_day=20,
                max_single_order_amount=Decimal("500.0"),
                max_daily_volume=Decimal("5000.0"),
                max_consecutive_losses=2,
                max_daily_loss=Decimal("200.0")
            )
        elif risk_level == RiskLevel.HIGH:
            return RiskProfile(
                id=0,  # 临时ID
                user_id=user_id,
                risk_level=risk_level,
                max_price_volatility=Decimal("8.0"),
                max_position_ratio=Decimal("0.5"),
                max_orders_per_hour=15,
                max_orders_per_day=100,
                max_single_order_amount=Decimal("2000.0"),
                max_daily_volume=Decimal("20000.0"),
                max_consecutive_losses=5,
                max_daily_loss=Decimal("1000.0")
            )
        else:  # MEDIUM
            return RiskProfile(
                id=0,  # 临时ID
                user_id=user_id,
                risk_level=risk_level,
                max_price_volatility=Decimal("5.0"),
                max_position_ratio=Decimal("0.3"),
                max_orders_per_hour=10,
                max_orders_per_day=50,
                max_single_order_amount=Decimal("1000.0"),
                max_daily_volume=Decimal("10000.0"),
                max_consecutive_losses=3,
                max_daily_loss=Decimal("500.0")
            )

    def _create_alert(
        self,
        user_id: int,
        title: str,
        message: str,
        severity: AlertSeverity,
        risk_factor: RiskFactor,
        risk_level: RiskLevel,
        current_value: Decimal | None = None,
        threshold_value: Decimal | None = None,
        data: dict[str, Any] | None = None
    ) -> RiskAlert:
        """创建风险警报"""
        alert = RiskAlert(
            id=0,  # 临时ID
            user_id=user_id,
            title=title,
            message=message,
            severity=severity,
            risk_factor=risk_factor,
            risk_level=risk_level,
            current_value=current_value,
            threshold_value=threshold_value,
            data=data,
            triggered_at=datetime.now()
        )

        # 添加到活跃警报列表
        if user_id not in self._active_alerts:
            self._active_alerts[user_id] = []
        self._active_alerts[user_id].append(alert)

        return alert

    def get_active_alerts(self, user_id: int) -> list[RiskAlert]:
        """获取用户活跃警报"""
        return self._active_alerts.get(user_id, [])

    def acknowledge_alert(self, user_id: int, alert_id: int) -> bool:
        """确认警报"""
        alerts = self._active_alerts.get(user_id, [])
        for alert in alerts:
            if alert.id == alert_id:
                alert.acknowledge()
                return True
        return False

    def resolve_alert(self, user_id: int, alert_id: int) -> bool:
        """解决警报"""
        alerts = self._active_alerts.get(user_id, [])
        for alert in alerts:
            if alert.id == alert_id:
                alert.resolve()
                return True
        return False

    def get_risk_summary(self, user_id: int) -> dict[str, Any]:
        """获取风险摘要"""
        profile = self.get_risk_profile(user_id)
        metrics = self.get_risk_metrics(user_id)
        alerts = self.get_active_alerts(user_id)

        return {
            "user_id": user_id,
            "risk_level": profile.risk_level.value if profile else "UNKNOWN",
            "active_alerts_count": len(alerts),
            "critical_alerts_count": len([a for a in alerts if a.is_critical()]),
            "current_balance": float(metrics.current_balance) if metrics else 0.0,
            "daily_pnl": float(metrics.daily_pnl) if metrics else 0.0,
            "consecutive_losses": metrics.consecutive_losses if metrics else 0,
            "orders_today": metrics.orders_count_today if metrics else 0,
            "orders_this_hour": metrics.orders_count_hour if metrics else 0,
            "trading_allowed": profile.is_trading_allowed(datetime.now()) if profile else False
        }
