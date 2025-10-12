"""系统指标实体"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any


class MetricType(str, Enum):
    """指标类型"""

    COUNTER = "COUNTER"  # 计数器
    GAUGE = "GAUGE"  # 仪表盘
    HISTOGRAM = "HISTOGRAM"  # 直方图
    TIMER = "TIMER"  # 计时器


class MetricStatus(str, Enum):
    """指标状态"""

    NORMAL = "NORMAL"  # 正常
    WARNING = "WARNING"  # 警告
    CRITICAL = "CRITICAL"  # 严重
    UNKNOWN = "UNKNOWN"  # 未知


@dataclass
class SystemMetric:
    """系统指标"""

    id: int
    name: str
    metric_type: MetricType
    value: Decimal
    unit: str
    status: MetricStatus = MetricStatus.NORMAL
    threshold_warning: Decimal | None = None
    threshold_critical: Decimal | None = None
    tags: dict[str, str] | None = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def is_healthy(self) -> bool:
        """检查指标是否健康"""
        return self.status == MetricStatus.NORMAL

    def is_warning(self) -> bool:
        """检查是否处于警告状态"""
        return self.status == MetricStatus.WARNING

    def is_critical(self) -> bool:
        """检查是否处于严重状态"""
        return self.status == MetricStatus.CRITICAL

    def update_status(self) -> None:
        """更新指标状态"""
        if (
            self.threshold_critical is not None
            and self.value >= self.threshold_critical
        ):
            self.status = MetricStatus.CRITICAL
        elif (
            self.threshold_warning is not None and self.value >= self.threshold_warning
        ):
            self.status = MetricStatus.WARNING
        else:
            self.status = MetricStatus.NORMAL

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "metric_type": self.metric_type.value,
            "value": float(self.value),
            "unit": self.unit,
            "status": self.status.value,
            "threshold_warning": float(self.threshold_warning)
            if self.threshold_warning
            else None,
            "threshold_critical": float(self.threshold_critical)
            if self.threshold_critical
            else None,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat(),
            "is_healthy": self.is_healthy(),
            "is_warning": self.is_warning(),
            "is_critical": self.is_critical(),
        }


@dataclass
class SystemHealth:
    """系统健康状态"""

    overall_status: MetricStatus
    healthy_metrics: int
    warning_metrics: int
    critical_metrics: int
    total_metrics: int
    last_updated: datetime
    metrics: list[SystemMetric]

    def get_health_percentage(self) -> float:
        """获取健康百分比"""
        if self.total_metrics == 0:
            return 100.0
        return (self.healthy_metrics / self.total_metrics) * 100.0

    def is_system_healthy(self) -> bool:
        """检查系统是否健康"""
        return self.overall_status == MetricStatus.NORMAL

    def has_critical_issues(self) -> bool:
        """检查是否有严重问题"""
        return self.critical_metrics > 0

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "overall_status": self.overall_status.value,
            "healthy_metrics": self.healthy_metrics,
            "warning_metrics": self.warning_metrics,
            "critical_metrics": self.critical_metrics,
            "total_metrics": self.total_metrics,
            "health_percentage": self.get_health_percentage(),
            "is_system_healthy": self.is_system_healthy(),
            "has_critical_issues": self.has_critical_issues(),
            "last_updated": self.last_updated.isoformat(),
            "metrics": [metric.to_dict() for metric in self.metrics],
        }


@dataclass
class PerformanceMetrics:
    """性能指标"""

    # API性能
    api_response_time_avg: Decimal
    api_response_time_p95: Decimal
    api_response_time_p99: Decimal
    api_requests_per_second: Decimal
    api_error_rate: Decimal

    # 数据库性能
    db_connection_pool_size: int
    db_connection_pool_used: int
    db_query_time_avg: Decimal
    db_query_time_p95: Decimal
    db_transactions_per_second: Decimal

    # 缓存性能
    redis_hit_rate: Decimal
    redis_memory_usage: Decimal
    redis_operations_per_second: Decimal

    # WebSocket性能
    websocket_connections: int
    websocket_messages_per_second: Decimal
    websocket_reconnect_rate: Decimal

    # 系统资源
    cpu_usage: Decimal
    memory_usage: Decimal
    disk_usage: Decimal
    network_io: Decimal

    # 业务指标
    active_users: int
    active_orders: int
    orders_per_minute: Decimal
    successful_orders: int
    failed_orders: int

    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def get_success_rate(self) -> Decimal:
        """获取成功率"""
        total_orders = self.successful_orders + self.failed_orders
        if total_orders == 0:
            return Decimal("0")
        return (self.successful_orders / total_orders) * Decimal("100")

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "api": {
                "response_time_avg": float(self.api_response_time_avg),
                "response_time_p95": float(self.api_response_time_p95),
                "response_time_p99": float(self.api_response_time_p99),
                "requests_per_second": float(self.api_requests_per_second),
                "error_rate": float(self.api_error_rate),
            },
            "database": {
                "connection_pool_size": self.db_connection_pool_size,
                "connection_pool_used": self.db_connection_pool_used,
                "query_time_avg": float(self.db_query_time_avg),
                "query_time_p95": float(self.db_query_time_p95),
                "transactions_per_second": float(self.db_transactions_per_second),
            },
            "cache": {
                "redis_hit_rate": float(self.redis_hit_rate),
                "redis_memory_usage": float(self.redis_memory_usage),
                "redis_operations_per_second": float(self.redis_operations_per_second),
            },
            "websocket": {
                "connections": self.websocket_connections,
                "messages_per_second": float(self.websocket_messages_per_second),
                "reconnect_rate": float(self.websocket_reconnect_rate),
            },
            "system": {
                "cpu_usage": float(self.cpu_usage),
                "memory_usage": float(self.memory_usage),
                "disk_usage": float(self.disk_usage),
                "network_io": float(self.network_io),
            },
            "business": {
                "active_users": self.active_users,
                "active_orders": self.active_orders,
                "orders_per_minute": float(self.orders_per_minute),
                "successful_orders": self.successful_orders,
                "failed_orders": self.failed_orders,
                "success_rate": float(self.get_success_rate()),
            },
            "timestamp": self.timestamp.isoformat(),
        }
