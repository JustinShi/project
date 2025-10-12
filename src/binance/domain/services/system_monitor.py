"""系统监控服务"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from binance.domain.entities.alert_rule import (
    AlertRule,
    AlertRuleType,
    SystemAlert,
)
from binance.domain.entities.system_metrics import (
    MetricStatus,
    MetricType,
    SystemMetric,
)


@dataclass
class SystemStatus:
    """系统状态"""

    status: str
    uptime: int  # 运行时间（秒）
    version: str
    environment: str
    last_restart: datetime
    health_score: float


class SystemMonitor:
    """系统监控服务"""

    def __init__(self):
        self._metrics: dict[str, SystemMetric] = {}
        self._alert_rules: dict[int, AlertRule] = {}
        self._active_alerts: list[SystemAlert] = []
        self._performance_history: list[PerformanceMetrics] = []
        self._system_status: SystemStatus | None = None

    def add_metric(self, metric: SystemMetric) -> None:
        """添加系统指标"""
        metric.update_status()
        self._metrics[metric.name] = metric

    def get_metric(self, name: str) -> SystemMetric | None:
        """获取系统指标"""
        return self._metrics.get(name)

    def get_all_metrics(self) -> list[SystemMetric]:
        """获取所有系统指标"""
        return list(self._metrics.values())

    def update_metric(
        self, name: str, value: Decimal, timestamp: datetime | None = None
    ) -> None:
        """更新系统指标"""
        if name in self._metrics:
            metric = self._metrics[name]
            metric.value = value
            if timestamp:
                metric.timestamp = timestamp
            metric.update_status()

            # 检查告警规则
            self._check_alert_rules(metric)

    def get_system_health(self) -> SystemHealth:
        """获取系统健康状态"""
        metrics = self.get_all_metrics()

        healthy_count = sum(1 for m in metrics if m.is_healthy())
        warning_count = sum(1 for m in metrics if m.is_warning())
        critical_count = sum(1 for m in metrics if m.is_critical())
        total_count = len(metrics)

        # 确定整体状态
        if critical_count > 0:
            overall_status = MetricStatus.CRITICAL
        elif warning_count > 0:
            overall_status = MetricStatus.WARNING
        else:
            overall_status = MetricStatus.NORMAL

        return SystemHealth(
            overall_status=overall_status,
            healthy_metrics=healthy_count,
            warning_metrics=warning_count,
            critical_metrics=critical_count,
            total_metrics=total_count,
            last_updated=datetime.now(),
            metrics=metrics,
        )

    def add_alert_rule(self, rule: AlertRule) -> None:
        """添加告警规则"""
        self._alert_rules[rule.id] = rule

    def get_alert_rule(self, rule_id: int) -> AlertRule | None:
        """获取告警规则"""
        return self._alert_rules.get(rule_id)

    def get_all_alert_rules(self) -> list[AlertRule]:
        """获取所有告警规则"""
        return list(self._alert_rules.values())

    def _check_alert_rules(self, metric: SystemMetric) -> None:
        """检查告警规则"""
        for rule in self._alert_rules.values():
            if (
                rule.metric_name == metric.name
                and rule.is_active()
                and rule.should_trigger(metric.value, metric.timestamp)
            ):
                # 创建告警
                alert = SystemAlert(
                    id=len(self._active_alerts) + 1,
                    rule_id=rule.id,
                    metric_name=metric.name,
                    metric_value=metric.value,
                    severity=rule.severity,
                    message=rule.get_alert_message(metric.value),
                    triggered_at=datetime.now(),
                )

                self._active_alerts.append(alert)
                rule.trigger(metric.value, metric.timestamp)

    def get_active_alerts(self) -> list[SystemAlert]:
        """获取活跃告警"""
        return [alert for alert in self._active_alerts if alert.is_active()]

    def acknowledge_alert(self, alert_id: int) -> bool:
        """确认告警"""
        for alert in self._active_alerts:
            if alert.id == alert_id:
                alert.acknowledge()
                return True
        return False

    def resolve_alert(self, alert_id: int) -> bool:
        """解决告警"""
        for alert in self._active_alerts:
            if alert.id == alert_id:
                alert.resolve()
                return True
        return False

    def add_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        """添加性能指标"""
        self._performance_history.append(metrics)

        # 只保留最近24小时的数据
        cutoff_time = datetime.now() - timedelta(hours=24)
        self._performance_history = [
            m for m in self._performance_history if m.timestamp >= cutoff_time
        ]

    def get_performance_metrics(self, hours: int = 1) -> list[PerformanceMetrics]:
        """获取性能指标历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self._performance_history if m.timestamp >= cutoff_time]

    def get_system_status(self) -> SystemStatus:
        """获取系统状态"""
        if self._system_status is None:
            self._system_status = SystemStatus(
                status="RUNNING",
                uptime=0,
                version="1.0.0",
                environment="development",
                last_restart=datetime.now(),
                health_score=100.0,
            )

        # 更新健康分数
        health = self.get_system_health()
        self._system_status.health_score = health.get_health_percentage()

        return self._system_status

    def create_default_metrics(self) -> None:
        """创建默认系统指标"""
        default_metrics = [
            SystemMetric(
                id=1,
                name="api_response_time",
                metric_type=MetricType.TIMER,
                value=Decimal("100.0"),
                unit="ms",
                threshold_warning=Decimal("500.0"),
                threshold_critical=Decimal("1000.0"),
            ),
            SystemMetric(
                id=2,
                name="api_error_rate",
                metric_type=MetricType.GAUGE,
                value=Decimal("0.1"),
                unit="%",
                threshold_warning=Decimal("5.0"),
                threshold_critical=Decimal("10.0"),
            ),
            SystemMetric(
                id=3,
                name="db_connection_pool",
                metric_type=MetricType.GAUGE,
                value=Decimal("5.0"),
                unit="connections",
                threshold_warning=Decimal("80.0"),
                threshold_critical=Decimal("95.0"),
            ),
            SystemMetric(
                id=4,
                name="redis_memory_usage",
                metric_type=MetricType.GAUGE,
                value=Decimal("50.0"),
                unit="%",
                threshold_warning=Decimal("80.0"),
                threshold_critical=Decimal("95.0"),
            ),
            SystemMetric(
                id=5,
                name="websocket_connections",
                metric_type=MetricType.GAUGE,
                value=Decimal("10.0"),
                unit="connections",
                threshold_warning=Decimal("100.0"),
                threshold_critical=Decimal("200.0"),
            ),
            SystemMetric(
                id=6,
                name="cpu_usage",
                metric_type=MetricType.GAUGE,
                value=Decimal("30.0"),
                unit="%",
                threshold_warning=Decimal("80.0"),
                threshold_critical=Decimal("95.0"),
            ),
            SystemMetric(
                id=7,
                name="memory_usage",
                metric_type=MetricType.GAUGE,
                value=Decimal("40.0"),
                unit="%",
                threshold_warning=Decimal("80.0"),
                threshold_critical=Decimal("95.0"),
            ),
            SystemMetric(
                id=8,
                name="active_users",
                metric_type=MetricType.GAUGE,
                value=Decimal("5.0"),
                unit="users",
                threshold_warning=Decimal("100.0"),
                threshold_critical=Decimal("200.0"),
            ),
            SystemMetric(
                id=9,
                name="active_orders",
                metric_type=MetricType.GAUGE,
                value=Decimal("2.0"),
                unit="orders",
                threshold_warning=Decimal("50.0"),
                threshold_critical=Decimal("100.0"),
            ),
            SystemMetric(
                id=10,
                name="order_success_rate",
                metric_type=MetricType.GAUGE,
                value=Decimal("95.0"),
                unit="%",
                threshold_warning=Decimal("90.0"),
                threshold_critical=Decimal("80.0"),
            ),
        ]

        for metric in default_metrics:
            self.add_metric(metric)

    def create_default_alert_rules(self) -> None:
        """创建默认告警规则"""
        default_rules = [
            AlertRule(
                id=1,
                name="API响应时间告警",
                description="API响应时间超过阈值",
                rule_type=AlertRuleType.THRESHOLD,
                metric_name="api_response_time",
                metric_type=MetricType.TIMER,
                threshold_value=Decimal("1000.0"),
                threshold_operator=">",
                severity=MetricStatus.CRITICAL,
            ),
            AlertRule(
                id=2,
                name="API错误率告警",
                description="API错误率超过阈值",
                rule_type=AlertRuleType.THRESHOLD,
                metric_name="api_error_rate",
                metric_type=MetricType.GAUGE,
                threshold_value=Decimal("10.0"),
                threshold_operator=">",
                severity=MetricStatus.CRITICAL,
            ),
            AlertRule(
                id=3,
                name="数据库连接池告警",
                description="数据库连接池使用率过高",
                rule_type=AlertRuleType.THRESHOLD,
                metric_name="db_connection_pool",
                metric_type=MetricType.GAUGE,
                threshold_value=Decimal("90.0"),
                threshold_operator=">",
                severity=MetricStatus.WARNING,
            ),
            AlertRule(
                id=4,
                name="Redis内存使用告警",
                description="Redis内存使用率过高",
                rule_type=AlertRuleType.THRESHOLD,
                metric_name="redis_memory_usage",
                metric_type=MetricType.GAUGE,
                threshold_value=Decimal("90.0"),
                threshold_operator=">",
                severity=MetricStatus.WARNING,
            ),
            AlertRule(
                id=5,
                name="CPU使用率告警",
                description="CPU使用率过高",
                rule_type=AlertRuleType.THRESHOLD,
                metric_name="cpu_usage",
                metric_type=MetricType.GAUGE,
                threshold_value=Decimal("90.0"),
                threshold_operator=">",
                severity=MetricStatus.CRITICAL,
            ),
            AlertRule(
                id=6,
                name="内存使用率告警",
                description="内存使用率过高",
                rule_type=AlertRuleType.THRESHOLD,
                metric_name="memory_usage",
                metric_type=MetricType.GAUGE,
                threshold_value=Decimal("90.0"),
                threshold_operator=">",
                severity=MetricStatus.CRITICAL,
            ),
            AlertRule(
                id=7,
                name="订单成功率告警",
                description="订单成功率过低",
                rule_type=AlertRuleType.THRESHOLD,
                metric_name="order_success_rate",
                metric_type=MetricType.GAUGE,
                threshold_value=Decimal("80.0"),
                threshold_operator="<",
                severity=MetricStatus.WARNING,
            ),
        ]

        for rule in default_rules:
            self.add_alert_rule(rule)

    def get_system_summary(self) -> dict[str, Any]:
        """获取系统摘要"""
        health = self.get_system_health()
        status = self.get_system_status()
        active_alerts = self.get_active_alerts()
        performance_metrics = self.get_performance_metrics(1)

        return {
            "system_status": {
                "status": status.status,
                "uptime": status.uptime,
                "version": status.version,
                "environment": status.environment,
                "health_score": status.health_score,
            },
            "health": health.to_dict(),
            "alerts": {
                "active_count": len(active_alerts),
                "critical_count": len(
                    [a for a in active_alerts if a.severity == MetricStatus.CRITICAL]
                ),
                "warning_count": len(
                    [a for a in active_alerts if a.severity == MetricStatus.WARNING]
                ),
            },
            "performance": {
                "metrics_count": len(performance_metrics),
                "latest_metrics": performance_metrics[-1].to_dict()
                if performance_metrics
                else None,
            },
            "timestamp": datetime.now().isoformat(),
        }
