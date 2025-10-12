"""系统监控API路由"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from binance.api.schemas.monitoring_schema import (
    AlertRuleCreateRequest,
    AlertRuleResponse,
    MetricUpdateRequest,
    MetricUpdateResponse,
    PerformanceHistoryResponse,
    PerformanceMetricsResponse,
    SystemAlertActionRequest,
    SystemAlertActionResponse,
    SystemAlertListResponse,
    SystemAlertResponse,
    SystemDashboardResponse,
    SystemHealthResponse,
    SystemMetricResponse,
    SystemStatusResponse,
    SystemSummaryResponse,
)
from binance.domain.entities.alert_rule import (
    AlertRule,
    AlertRuleType,
)
from binance.domain.entities.system_metrics import (
    MetricStatus,
    MetricType,
)
from binance.domain.services.system_monitor import SystemMonitor
from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# 全局系统监控服务实例
_system_monitor: SystemMonitor | None = None


def get_system_monitor() -> SystemMonitor:
    """获取系统监控服务"""
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = SystemMonitor()
        # 初始化默认指标和告警规则
        _system_monitor.create_default_metrics()
        _system_monitor.create_default_alert_rules()
    return _system_monitor


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    system_monitor: SystemMonitor = Depends(get_system_monitor),
):
    """获取系统健康状态"""
    try:
        health = system_monitor.get_system_health()

        return SystemHealthResponse(
            overall_status=health.overall_status.value,
            healthy_metrics=health.healthy_metrics,
            warning_metrics=health.warning_metrics,
            critical_metrics=health.critical_metrics,
            total_metrics=health.total_metrics,
            health_percentage=health.get_health_percentage(),
            is_system_healthy=health.is_system_healthy(),
            has_critical_issues=health.has_critical_issues(),
            last_updated=health.last_updated,
            metrics=[
                SystemMetricResponse(
                    id=metric.id,
                    name=metric.name,
                    metric_type=metric.metric_type.value,
                    value=metric.value,
                    unit=metric.unit,
                    status=metric.status.value,
                    threshold_warning=metric.threshold_warning,
                    threshold_critical=metric.threshold_critical,
                    tags=metric.tags,
                    timestamp=metric.timestamp,
                    is_healthy=metric.is_healthy(),
                    is_warning=metric.is_warning(),
                    is_critical=metric.is_critical(),
                )
                for metric in health.metrics
            ],
        )

    except Exception as e:
        logger.error(f"获取系统健康状态异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统健康状态失败: {e!s}")


@router.get("/metrics", response_model=list[SystemMetricResponse])
async def get_system_metrics(
    system_monitor: SystemMonitor = Depends(get_system_monitor),
):
    """获取系统指标"""
    try:
        metrics = system_monitor.get_all_metrics()

        return [
            SystemMetricResponse(
                id=metric.id,
                name=metric.name,
                metric_type=metric.metric_type.value,
                value=metric.value,
                unit=metric.unit,
                status=metric.status.value,
                threshold_warning=metric.threshold_warning,
                threshold_critical=metric.threshold_critical,
                tags=metric.tags,
                timestamp=metric.timestamp,
                is_healthy=metric.is_healthy(),
                is_warning=metric.is_warning(),
                is_critical=metric.is_critical(),
            )
            for metric in metrics
        ]

    except Exception as e:
        logger.error(f"获取系统指标异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统指标失败: {e!s}")


@router.post("/metrics/update", response_model=MetricUpdateResponse)
async def update_metric(
    request: MetricUpdateRequest,
    system_monitor: SystemMonitor = Depends(get_system_monitor),
):
    """更新系统指标"""
    try:
        system_monitor.update_metric(
            name=request.name, value=request.value, timestamp=request.timestamp
        )

        metric = system_monitor.get_metric(request.name)
        if metric:
            return MetricUpdateResponse(
                success=True,
                message="指标更新成功",
                metric=SystemMetricResponse(
                    id=metric.id,
                    name=metric.name,
                    metric_type=metric.metric_type.value,
                    value=metric.value,
                    unit=metric.unit,
                    status=metric.status.value,
                    threshold_warning=metric.threshold_warning,
                    threshold_critical=metric.threshold_critical,
                    tags=metric.tags,
                    timestamp=metric.timestamp,
                    is_healthy=metric.is_healthy(),
                    is_warning=metric.is_warning(),
                    is_critical=metric.is_critical(),
                ),
            )
        else:
            return MetricUpdateResponse(
                success=False, message="指标不存在", metric=None
            )

    except Exception as e:
        logger.error(f"更新系统指标异常: {e}")
        raise HTTPException(status_code=500, detail=f"更新系统指标失败: {e!s}")


@router.get("/alerts", response_model=SystemAlertListResponse)
async def get_system_alerts(
    system_monitor: SystemMonitor = Depends(get_system_monitor),
):
    """获取系统告警"""
    try:
        alerts = system_monitor.get_active_alerts()

        alert_responses = []
        for alert in alerts:
            alert_responses.append(
                SystemAlertResponse(
                    id=alert.id,
                    rule_id=alert.rule_id,
                    metric_name=alert.metric_name,
                    metric_value=alert.metric_value,
                    severity=alert.severity.value,
                    message=alert.message,
                    triggered_at=alert.triggered_at,
                    acknowledged_at=alert.acknowledged_at,
                    resolved_at=alert.resolved_at,
                    status=alert.status,
                    duration_seconds=alert.get_duration(),
                    is_active=alert.is_active(),
                )
            )

        active_count = len([a for a in alerts if a.is_active()])
        critical_count = len([a for a in alerts if a.severity == MetricStatus.CRITICAL])
        warning_count = len([a for a in alerts if a.severity == MetricStatus.WARNING])

        return SystemAlertListResponse(
            alerts=alert_responses,
            total=len(alerts),
            active_count=active_count,
            critical_count=critical_count,
            warning_count=warning_count,
        )

    except Exception as e:
        logger.error(f"获取系统告警异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统告警失败: {e!s}")


@router.post("/alerts/acknowledge", response_model=SystemAlertActionResponse)
async def acknowledge_alert(
    request: SystemAlertActionRequest,
    system_monitor: SystemMonitor = Depends(get_system_monitor),
):
    """确认系统告警"""
    try:
        success = system_monitor.acknowledge_alert(request.alert_id)

        if success:
            return SystemAlertActionResponse(success=True, message="告警已确认")
        else:
            return SystemAlertActionResponse(
                success=False, message="告警不存在或已处理"
            )

    except Exception as e:
        logger.error(f"确认系统告警异常: {e}")
        raise HTTPException(status_code=500, detail=f"确认系统告警失败: {e!s}")


@router.post("/alerts/resolve", response_model=SystemAlertActionResponse)
async def resolve_alert(
    request: SystemAlertActionRequest,
    system_monitor: SystemMonitor = Depends(get_system_monitor),
):
    """解决系统告警"""
    try:
        success = system_monitor.resolve_alert(request.alert_id)

        if success:
            return SystemAlertActionResponse(success=True, message="告警已解决")
        else:
            return SystemAlertActionResponse(
                success=False, message="告警不存在或已处理"
            )

    except Exception as e:
        logger.error(f"解决系统告警异常: {e}")
        raise HTTPException(status_code=500, detail=f"解决系统告警失败: {e!s}")


@router.get("/rules", response_model=list[AlertRuleResponse])
async def get_alert_rules(system_monitor: SystemMonitor = Depends(get_system_monitor)):
    """获取告警规则"""
    try:
        rules = system_monitor.get_all_alert_rules()

        return [
            AlertRuleResponse(
                id=rule.id,
                name=rule.name,
                description=rule.description,
                rule_type=rule.rule_type.value,
                metric_name=rule.metric_name,
                metric_type=rule.metric_type.value,
                threshold_value=rule.threshold_value,
                threshold_operator=rule.threshold_operator,
                threshold_duration=rule.threshold_duration,
                rate_threshold=rule.rate_threshold,
                rate_window=rule.rate_window,
                absence_duration=rule.absence_duration,
                anomaly_sensitivity=rule.anomaly_sensitivity,
                anomaly_window=rule.anomaly_window,
                severity=rule.severity.value,
                enabled=rule.enabled,
                status=rule.status.value,
                notification_channels=rule.notification_channels,
                notification_template=rule.notification_template,
                created_at=rule.created_at,
                updated_at=rule.updated_at,
                last_triggered=rule.last_triggered,
                trigger_count=rule.trigger_count,
                is_active=rule.is_active(),
            )
            for rule in rules
        ]

    except Exception as e:
        logger.error(f"获取告警规则异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取告警规则失败: {e!s}")


@router.post("/rules", response_model=AlertRuleResponse)
async def create_alert_rule(
    request: AlertRuleCreateRequest,
    system_monitor: SystemMonitor = Depends(get_system_monitor),
):
    """创建告警规则"""
    try:
        rule = AlertRule(
            id=len(system_monitor.get_all_alert_rules()) + 1,
            name=request.name,
            description=request.description,
            rule_type=AlertRuleType(request.rule_type),
            metric_name=request.metric_name,
            metric_type=MetricType(request.metric_type),
            threshold_value=request.threshold_value,
            threshold_operator=request.threshold_operator,
            threshold_duration=request.threshold_duration,
            rate_threshold=request.rate_threshold,
            rate_window=request.rate_window,
            absence_duration=request.absence_duration,
            anomaly_sensitivity=request.anomaly_sensitivity,
            anomaly_window=request.anomaly_window,
            severity=MetricStatus(request.severity),
            enabled=request.enabled,
            notification_channels=request.notification_channels,
            notification_template=request.notification_template,
        )

        system_monitor.add_alert_rule(rule)

        return AlertRuleResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            rule_type=rule.rule_type.value,
            metric_name=rule.metric_name,
            metric_type=rule.metric_type.value,
            threshold_value=rule.threshold_value,
            threshold_operator=rule.threshold_operator,
            threshold_duration=rule.threshold_duration,
            rate_threshold=rule.rate_threshold,
            rate_window=rule.rate_window,
            absence_duration=rule.absence_duration,
            anomaly_sensitivity=rule.anomaly_sensitivity,
            anomaly_window=rule.anomaly_window,
            severity=rule.severity.value,
            enabled=rule.enabled,
            status=rule.status.value,
            notification_channels=rule.notification_channels,
            notification_template=rule.notification_template,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            last_triggered=rule.last_triggered,
            trigger_count=rule.trigger_count,
            is_active=rule.is_active(),
        )

    except Exception as e:
        logger.error(f"创建告警规则异常: {e}")
        raise HTTPException(status_code=500, detail=f"创建告警规则失败: {e!s}")


@router.get("/performance", response_model=PerformanceHistoryResponse)
async def get_performance_metrics(
    hours: int = Query(1, description="时间范围（小时）"),
    system_monitor: SystemMonitor = Depends(get_system_monitor),
):
    """获取性能指标历史"""
    try:
        metrics = system_monitor.get_performance_metrics(hours)

        return PerformanceHistoryResponse(
            metrics=[
                PerformanceMetricsResponse(
                    api=perf.api,
                    database=perf.database,
                    cache=perf.cache,
                    websocket=perf.websocket,
                    system=perf.system,
                    business=perf.business,
                    timestamp=perf.timestamp,
                )
                for perf in metrics
            ],
            total=len(metrics),
            time_range=f"最近{hours}小时",
        )

    except Exception as e:
        logger.error(f"获取性能指标异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取性能指标失败: {e!s}")


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    system_monitor: SystemMonitor = Depends(get_system_monitor),
):
    """获取系统状态"""
    try:
        status = system_monitor.get_system_status()

        return SystemStatusResponse(
            status=status.status,
            uptime=status.uptime,
            version=status.version,
            environment=status.environment,
            last_restart=status.last_restart,
            health_score=status.health_score,
        )

    except Exception as e:
        logger.error(f"获取系统状态异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统状态失败: {e!s}")


@router.get("/summary", response_model=SystemSummaryResponse)
async def get_system_summary(
    system_monitor: SystemMonitor = Depends(get_system_monitor),
):
    """获取系统摘要"""
    try:
        summary = system_monitor.get_system_summary()

        return SystemSummaryResponse(
            system_status=SystemStatusResponse(
                status=summary["system_status"]["status"],
                uptime=summary["system_status"]["uptime"],
                version=summary["system_status"]["version"],
                environment=summary["system_status"]["environment"],
                last_restart=datetime.fromisoformat(
                    summary["system_status"]["last_restart"]
                ),
                health_score=summary["system_status"]["health_score"],
            ),
            health=SystemHealthResponse(**summary["health"]),
            alerts=summary["alerts"],
            performance=summary["performance"],
            timestamp=datetime.fromisoformat(summary["timestamp"]),
        )

    except Exception as e:
        logger.error(f"获取系统摘要异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统摘要失败: {e!s}")


@router.get("/dashboard", response_model=SystemDashboardResponse)
async def get_system_dashboard(
    system_monitor: SystemMonitor = Depends(get_system_monitor),
):
    """获取系统仪表板"""
    try:
        # 获取系统状态
        status = system_monitor.get_system_status()

        # 获取系统健康
        health = system_monitor.get_system_health()

        # 获取活跃告警
        alerts = system_monitor.get_active_alerts()

        # 获取性能趋势（最近1小时）
        performance_metrics = system_monitor.get_performance_metrics(1)

        # 获取关键指标（按严重程度排序）
        all_metrics = system_monitor.get_all_metrics()
        top_metrics = sorted(
            all_metrics,
            key=lambda m: (m.is_critical(), m.is_warning(), m.value),
            reverse=True,
        )[:10]

        # 获取告警规则
        alert_rules = system_monitor.get_all_alert_rules()

        return SystemDashboardResponse(
            system_status=SystemStatusResponse(
                status=status.status,
                uptime=status.uptime,
                version=status.version,
                environment=status.environment,
                last_restart=status.last_restart,
                health_score=status.health_score,
            ),
            health=SystemHealthResponse(
                overall_status=health.overall_status.value,
                healthy_metrics=health.healthy_metrics,
                warning_metrics=health.warning_metrics,
                critical_metrics=health.critical_metrics,
                total_metrics=health.total_metrics,
                health_percentage=health.get_health_percentage(),
                is_system_healthy=health.is_system_healthy(),
                has_critical_issues=health.has_critical_issues(),
                last_updated=health.last_updated,
                metrics=[
                    SystemMetricResponse(
                        id=metric.id,
                        name=metric.name,
                        metric_type=metric.metric_type.value,
                        value=metric.value,
                        unit=metric.unit,
                        status=metric.status.value,
                        threshold_warning=metric.threshold_warning,
                        threshold_critical=metric.threshold_critical,
                        tags=metric.tags,
                        timestamp=metric.timestamp,
                        is_healthy=metric.is_healthy(),
                        is_warning=metric.is_warning(),
                        is_critical=metric.is_critical(),
                    )
                    for metric in health.metrics
                ],
            ),
            active_alerts=[
                SystemAlertResponse(
                    id=alert.id,
                    rule_id=alert.rule_id,
                    metric_name=alert.metric_name,
                    metric_value=alert.metric_value,
                    severity=alert.severity.value,
                    message=alert.message,
                    triggered_at=alert.triggered_at,
                    acknowledged_at=alert.acknowledged_at,
                    resolved_at=alert.resolved_at,
                    status=alert.status,
                    duration_seconds=alert.get_duration(),
                    is_active=alert.is_active(),
                )
                for alert in alerts
            ],
            performance_trends={
                "api_response_time": [
                    float(m.api_response_time_avg) for m in performance_metrics
                ],
                "cpu_usage": [float(m.cpu_usage) for m in performance_metrics],
                "memory_usage": [float(m.memory_usage) for m in performance_metrics],
            },
            top_metrics=[
                SystemMetricResponse(
                    id=metric.id,
                    name=metric.name,
                    metric_type=metric.metric_type.value,
                    value=metric.value,
                    unit=metric.unit,
                    status=metric.status.value,
                    threshold_warning=metric.threshold_warning,
                    threshold_critical=metric.threshold_critical,
                    tags=metric.tags,
                    timestamp=metric.timestamp,
                    is_healthy=metric.is_healthy(),
                    is_warning=metric.is_warning(),
                    is_critical=metric.is_critical(),
                )
                for metric in top_metrics
            ],
            alert_rules=[
                AlertRuleResponse(
                    id=rule.id,
                    name=rule.name,
                    description=rule.description,
                    rule_type=rule.rule_type.value,
                    metric_name=rule.metric_name,
                    metric_type=rule.metric_type.value,
                    threshold_value=rule.threshold_value,
                    threshold_operator=rule.threshold_operator,
                    threshold_duration=rule.threshold_duration,
                    rate_threshold=rule.rate_threshold,
                    rate_window=rule.rate_window,
                    absence_duration=rule.absence_duration,
                    anomaly_sensitivity=rule.anomaly_sensitivity,
                    anomaly_window=rule.anomaly_window,
                    severity=rule.severity.value,
                    enabled=rule.enabled,
                    status=rule.status.value,
                    notification_channels=rule.notification_channels,
                    notification_template=rule.notification_template,
                    created_at=rule.created_at,
                    updated_at=rule.updated_at,
                    last_triggered=rule.last_triggered,
                    trigger_count=rule.trigger_count,
                    is_active=rule.is_active(),
                )
                for rule in alert_rules
            ],
            last_updated=datetime.now(),
        )

    except Exception as e:
        logger.error(f"获取系统仪表板异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统仪表板失败: {e!s}")
