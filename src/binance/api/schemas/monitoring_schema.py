"""系统监控相关API模式"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class SystemMetricResponse(BaseModel):
    """系统指标响应"""
    id: int = Field(..., description="指标ID")
    name: str = Field(..., description="指标名称")
    metric_type: str = Field(..., description="指标类型")
    value: Decimal = Field(..., description="指标值")
    unit: str = Field(..., description="单位")
    status: str = Field(..., description="状态")
    threshold_warning: Decimal | None = Field(None, description="警告阈值")
    threshold_critical: Decimal | None = Field(None, description="严重阈值")
    tags: dict[str, str] | None = Field(None, description="标签")
    timestamp: datetime = Field(..., description="时间戳")
    is_healthy: bool = Field(..., description="是否健康")
    is_warning: bool = Field(..., description="是否警告")
    is_critical: bool = Field(..., description="是否严重")


class SystemHealthResponse(BaseModel):
    """系统健康响应"""
    overall_status: str = Field(..., description="整体状态")
    healthy_metrics: int = Field(..., description="健康指标数")
    warning_metrics: int = Field(..., description="警告指标数")
    critical_metrics: int = Field(..., description="严重指标数")
    total_metrics: int = Field(..., description="总指标数")
    health_percentage: float = Field(..., description="健康百分比")
    is_system_healthy: bool = Field(..., description="系统是否健康")
    has_critical_issues: bool = Field(..., description="是否有严重问题")
    last_updated: datetime = Field(..., description="最后更新时间")
    metrics: list[SystemMetricResponse] = Field(..., description="指标列表")


class PerformanceMetricsResponse(BaseModel):
    """性能指标响应"""
    api: dict[str, float] = Field(..., description="API性能指标")
    database: dict[str, Any] = Field(..., description="数据库性能指标")
    cache: dict[str, float] = Field(..., description="缓存性能指标")
    websocket: dict[str, Any] = Field(..., description="WebSocket性能指标")
    system: dict[str, float] = Field(..., description="系统资源指标")
    business: dict[str, Any] = Field(..., description="业务指标")
    timestamp: datetime = Field(..., description="时间戳")


class AlertRuleResponse(BaseModel):
    """告警规则响应"""
    id: int = Field(..., description="规则ID")
    name: str = Field(..., description="规则名称")
    description: str = Field(..., description="规则描述")
    rule_type: str = Field(..., description="规则类型")
    metric_name: str = Field(..., description="指标名称")
    metric_type: str = Field(..., description="指标类型")
    threshold_value: Decimal | None = Field(None, description="阈值")
    threshold_operator: str = Field(..., description="阈值操作符")
    threshold_duration: int = Field(..., description="阈值持续时间")
    rate_threshold: Decimal | None = Field(None, description="变化率阈值")
    rate_window: int = Field(..., description="变化率窗口")
    absence_duration: int = Field(..., description="缺失持续时间")
    anomaly_sensitivity: Decimal = Field(..., description="异常敏感度")
    anomaly_window: int = Field(..., description="异常检测窗口")
    severity: str = Field(..., description="严重程度")
    enabled: bool = Field(..., description="是否启用")
    status: str = Field(..., description="状态")
    notification_channels: list[str] = Field(..., description="通知渠道")
    notification_template: str | None = Field(None, description="通知模板")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")
    last_triggered: datetime | None = Field(None, description="最后触发时间")
    trigger_count: int = Field(..., description="触发次数")
    is_active: bool = Field(..., description="是否活跃")


class AlertRuleCreateRequest(BaseModel):
    """创建告警规则请求"""
    name: str = Field(..., description="规则名称")
    description: str = Field(..., description="规则描述")
    rule_type: str = Field(..., description="规则类型")
    metric_name: str = Field(..., description="指标名称")
    metric_type: str = Field(..., description="指标类型")
    threshold_value: Decimal | None = Field(None, description="阈值")
    threshold_operator: str = Field(">", description="阈值操作符")
    threshold_duration: int = Field(300, description="阈值持续时间")
    rate_threshold: Decimal | None = Field(None, description="变化率阈值")
    rate_window: int = Field(600, description="变化率窗口")
    absence_duration: int = Field(300, description="缺失持续时间")
    anomaly_sensitivity: Decimal = Field(Decimal("2.0"), description="异常敏感度")
    anomaly_window: int = Field(3600, description="异常检测窗口")
    severity: str = Field("WARNING", description="严重程度")
    enabled: bool = Field(True, description="是否启用")
    notification_channels: list[str] = Field(["email", "webhook"], description="通知渠道")
    notification_template: str | None = Field(None, description="通知模板")


class AlertRuleUpdateRequest(BaseModel):
    """更新告警规则请求"""
    name: str | None = Field(None, description="规则名称")
    description: str | None = Field(None, description="规则描述")
    rule_type: str | None = Field(None, description="规则类型")
    metric_name: str | None = Field(None, description="指标名称")
    metric_type: str | None = Field(None, description="指标类型")
    threshold_value: Decimal | None = Field(None, description="阈值")
    threshold_operator: str | None = Field(None, description="阈值操作符")
    threshold_duration: int | None = Field(None, description="阈值持续时间")
    rate_threshold: Decimal | None = Field(None, description="变化率阈值")
    rate_window: int | None = Field(None, description="变化率窗口")
    absence_duration: int | None = Field(None, description="缺失持续时间")
    anomaly_sensitivity: Decimal | None = Field(None, description="异常敏感度")
    anomaly_window: int | None = Field(None, description="异常检测窗口")
    severity: str | None = Field(None, description="严重程度")
    enabled: bool | None = Field(None, description="是否启用")
    notification_channels: list[str] | None = Field(None, description="通知渠道")
    notification_template: str | None = Field(None, description="通知模板")


class SystemAlertResponse(BaseModel):
    """系统告警响应"""
    id: int = Field(..., description="告警ID")
    rule_id: int = Field(..., description="规则ID")
    metric_name: str = Field(..., description="指标名称")
    metric_value: Decimal = Field(..., description="指标值")
    severity: str = Field(..., description="严重程度")
    message: str = Field(..., description="告警消息")
    triggered_at: datetime = Field(..., description="触发时间")
    acknowledged_at: datetime | None = Field(None, description="确认时间")
    resolved_at: datetime | None = Field(None, description="解决时间")
    status: str = Field(..., description="状态")
    duration_seconds: int = Field(..., description="持续时间（秒）")
    is_active: bool = Field(..., description="是否活跃")


class SystemAlertListResponse(BaseModel):
    """系统告警列表响应"""
    alerts: list[SystemAlertResponse] = Field(..., description="告警列表")
    total: int = Field(..., description="总数量")
    active_count: int = Field(..., description="活跃告警数量")
    critical_count: int = Field(..., description="严重告警数量")
    warning_count: int = Field(..., description="警告告警数量")


class SystemAlertActionRequest(BaseModel):
    """系统告警操作请求"""
    alert_id: int = Field(..., description="告警ID")


class SystemAlertActionResponse(BaseModel):
    """系统告警操作响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")


class SystemStatusResponse(BaseModel):
    """系统状态响应"""
    status: str = Field(..., description="系统状态")
    uptime: int = Field(..., description="运行时间（秒）")
    version: str = Field(..., description="版本")
    environment: str = Field(..., description="环境")
    last_restart: datetime = Field(..., description="最后重启时间")
    health_score: float = Field(..., description="健康分数")


class SystemSummaryResponse(BaseModel):
    """系统摘要响应"""
    system_status: SystemStatusResponse = Field(..., description="系统状态")
    health: SystemHealthResponse = Field(..., description="系统健康")
    alerts: dict[str, int] = Field(..., description="告警统计")
    performance: dict[str, Any] = Field(..., description="性能统计")
    timestamp: datetime = Field(..., description="时间戳")


class MetricUpdateRequest(BaseModel):
    """指标更新请求"""
    name: str = Field(..., description="指标名称")
    value: Decimal = Field(..., description="指标值")
    timestamp: datetime | None = Field(None, description="时间戳")


class MetricUpdateResponse(BaseModel):
    """指标更新响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    metric: SystemMetricResponse | None = Field(None, description="更新后的指标")


class PerformanceHistoryResponse(BaseModel):
    """性能历史响应"""
    metrics: list[PerformanceMetricsResponse] = Field(..., description="性能指标历史")
    total: int = Field(..., description="总数量")
    time_range: str = Field(..., description="时间范围")


class SystemDashboardResponse(BaseModel):
    """系统仪表板响应"""
    system_status: SystemStatusResponse = Field(..., description="系统状态")
    health: SystemHealthResponse = Field(..., description="系统健康")
    active_alerts: list[SystemAlertResponse] = Field(..., description="活跃告警")
    performance_trends: dict[str, list[float]] = Field(..., description="性能趋势")
    top_metrics: list[SystemMetricResponse] = Field(..., description="关键指标")
    alert_rules: list[AlertRuleResponse] = Field(..., description="告警规则")
    last_updated: datetime = Field(..., description="最后更新时间")
