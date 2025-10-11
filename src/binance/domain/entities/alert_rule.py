"""告警规则实体"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from binance.domain.entities.system_metrics import MetricStatus, MetricType


class AlertRuleType(str, Enum):
    """告警规则类型"""
    THRESHOLD = "THRESHOLD"           # 阈值告警
    RATE_CHANGE = "RATE_CHANGE"       # 变化率告警
    ABSENCE = "ABSENCE"               # 缺失告警
    ANOMALY = "ANOMALY"               # 异常告警


class AlertRuleStatus(str, Enum):
    """告警规则状态"""
    ACTIVE = "ACTIVE"                 # 活跃
    INACTIVE = "INACTIVE"            # 非活跃
    DISABLED = "DISABLED"             # 禁用


@dataclass
class AlertRule:
    """告警规则"""

    id: int
    name: str
    description: str
    rule_type: AlertRuleType
    metric_name: str
    metric_type: MetricType

    # 阈值配置
    threshold_value: Decimal | None = None
    threshold_operator: str = ">"  # >, <, >=, <=, ==, !=
    threshold_duration: int = 300  # 持续时间（秒）

    # 变化率配置
    rate_threshold: Decimal | None = None
    rate_window: int = 600  # 时间窗口（秒）

    # 缺失配置
    absence_duration: int = 300  # 缺失持续时间（秒）

    # 异常检测配置
    anomaly_sensitivity: Decimal = Decimal("2.0")  # 异常敏感度
    anomaly_window: int = 3600  # 异常检测窗口（秒）

    # 告警配置
    severity: MetricStatus = MetricStatus.WARNING
    enabled: bool = True
    status: AlertRuleStatus = AlertRuleStatus.ACTIVE

    # 通知配置
    notification_channels: list[str] = None
    notification_template: str | None = None

    # 元数据
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_triggered: datetime | None = None
    trigger_count: int = 0

    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ["email", "webhook"]
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def is_active(self) -> bool:
        """检查规则是否活跃"""
        return self.status == AlertRuleStatus.ACTIVE and self.enabled

    def should_trigger(self, metric_value: Decimal, timestamp: datetime) -> bool:
        """检查是否应该触发告警"""
        if not self.is_active():
            return False

        if self.rule_type == AlertRuleType.THRESHOLD:
            return self._check_threshold(metric_value)
        elif self.rule_type == AlertRuleType.RATE_CHANGE:
            return self._check_rate_change(metric_value, timestamp)
        elif self.rule_type == AlertRuleType.ABSENCE:
            return self._check_absence(timestamp)
        elif self.rule_type == AlertRuleType.ANOMALY:
            return self._check_anomaly(metric_value, timestamp)

        return False

    def _check_threshold(self, metric_value: Decimal) -> bool:
        """检查阈值告警"""
        if self.threshold_value is None:
            return False

        if self.threshold_operator == ">":
            return metric_value > self.threshold_value
        elif self.threshold_operator == "<":
            return metric_value < self.threshold_value
        elif self.threshold_operator == ">=":
            return metric_value >= self.threshold_value
        elif self.threshold_operator == "<=":
            return metric_value <= self.threshold_value
        elif self.threshold_operator == "==":
            return metric_value == self.threshold_value
        elif self.threshold_operator == "!=":
            return metric_value != self.threshold_value

        return False

    def _check_rate_change(self, metric_value: Decimal, timestamp: datetime) -> bool:
        """检查变化率告警"""
        # 这里需要历史数据来计算变化率
        # 暂时返回False，实际实现需要访问历史数据
        return False

    def _check_absence(self, timestamp: datetime) -> bool:
        """检查缺失告警"""
        if self.last_triggered is None:
            return False

        time_since_last = timestamp - self.last_triggered
        return time_since_last.total_seconds() > self.absence_duration

    def _check_anomaly(self, metric_value: Decimal, timestamp: datetime) -> bool:
        """检查异常告警"""
        # 这里需要历史数据来进行异常检测
        # 暂时返回False，实际实现需要访问历史数据
        return False

    def trigger(self, metric_value: Decimal, timestamp: datetime) -> None:
        """触发告警"""
        self.last_triggered = timestamp
        self.trigger_count += 1
        self.updated_at = timestamp

    def get_alert_message(self, metric_value: Decimal) -> str:
        """获取告警消息"""
        if self.notification_template:
            return self.notification_template.format(
                metric_name=self.metric_name,
                metric_value=metric_value,
                threshold_value=self.threshold_value,
                severity=self.severity.value
            )

        if self.rule_type == AlertRuleType.THRESHOLD:
            return f"{self.metric_name} {self.threshold_operator} {self.threshold_value} (当前值: {metric_value})"
        elif self.rule_type == AlertRuleType.RATE_CHANGE:
            return f"{self.metric_name} 变化率超过阈值 {self.rate_threshold}% (当前值: {metric_value})"
        elif self.rule_type == AlertRuleType.ABSENCE:
            return f"{self.metric_name} 超过 {self.absence_duration} 秒未更新"
        elif self.rule_type == AlertRuleType.ANOMALY:
            return f"{self.metric_name} 检测到异常值: {metric_value}"

        return f"{self.metric_name} 触发告警: {metric_value}"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rule_type": self.rule_type.value,
            "metric_name": self.metric_name,
            "metric_type": self.metric_type.value,
            "threshold_value": float(self.threshold_value) if self.threshold_value else None,
            "threshold_operator": self.threshold_operator,
            "threshold_duration": self.threshold_duration,
            "rate_threshold": float(self.rate_threshold) if self.rate_threshold else None,
            "rate_window": self.rate_window,
            "absence_duration": self.absence_duration,
            "anomaly_sensitivity": float(self.anomaly_sensitivity),
            "anomaly_window": self.anomaly_window,
            "severity": self.severity.value,
            "enabled": self.enabled,
            "status": self.status.value,
            "notification_channels": self.notification_channels,
            "notification_template": self.notification_template,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "trigger_count": self.trigger_count,
            "is_active": self.is_active()
        }


@dataclass
class SystemAlert:
    """系统告警"""

    id: int
    rule_id: int
    metric_name: str
    metric_value: Decimal
    severity: MetricStatus
    message: str
    triggered_at: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    status: str = "ACTIVE"  # ACTIVE, ACKNOWLEDGED, RESOLVED

    def acknowledge(self) -> None:
        """确认告警"""
        self.status = "ACKNOWLEDGED"
        self.acknowledged_at = datetime.now()

    def resolve(self) -> None:
        """解决告警"""
        self.status = "RESOLVED"
        self.resolved_at = datetime.now()

    def is_active(self) -> bool:
        """检查告警是否活跃"""
        return self.status == "ACTIVE"

    def get_duration(self) -> int:
        """获取告警持续时间（秒）"""
        if self.resolved_at:
            return int((self.resolved_at - self.triggered_at).total_seconds())
        elif self.status in ["ACTIVE", "ACKNOWLEDGED"]:
            return int((datetime.now() - self.triggered_at).total_seconds())
        return 0

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "metric_name": self.metric_name,
            "metric_value": float(self.metric_value),
            "severity": self.severity.value,
            "message": self.message,
            "triggered_at": self.triggered_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "status": self.status,
            "duration_seconds": self.get_duration(),
            "is_active": self.is_active()
        }
