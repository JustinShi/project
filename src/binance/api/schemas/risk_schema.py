"""风险管理相关API模式"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from binance.domain.entities.risk_profile import RiskLevel, RiskFactor
from binance.domain.entities.risk_alert import AlertSeverity, AlertStatus


class RiskProfileResponse(BaseModel):
    """风险配置响应"""
    id: int = Field(..., description="风险配置ID")
    user_id: int = Field(..., description="用户ID")
    risk_level: str = Field(..., description="风险等级")
    max_price_volatility: Decimal = Field(..., description="最大价格波动百分比")
    volatility_window_minutes: int = Field(..., description="波动计算窗口（分钟）")
    min_balance_ratio: Decimal = Field(..., description="最小余额比例")
    max_position_ratio: Decimal = Field(..., description="最大仓位比例")
    max_orders_per_hour: int = Field(..., description="每小时最大订单数")
    max_orders_per_day: int = Field(..., description="每天最大订单数")
    max_single_order_amount: Decimal = Field(..., description="单笔订单最大金额")
    max_daily_volume: Decimal = Field(..., description="每日最大交易量")
    trading_hours_start: int = Field(..., description="交易开始时间")
    trading_hours_end: int = Field(..., description="交易结束时间")
    weekend_trading: bool = Field(..., description="是否允许周末交易")
    max_consecutive_losses: int = Field(..., description="最大连续亏损次数")
    max_daily_loss: Decimal = Field(..., description="每日最大亏损")
    is_active: bool = Field(..., description="是否激活")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class RiskProfileCreateRequest(BaseModel):
    """创建风险配置请求"""
    risk_level: str = Field(..., description="风险等级", example="MEDIUM")
    max_price_volatility: Optional[Decimal] = Field(None, description="最大价格波动百分比")
    volatility_window_minutes: Optional[int] = Field(None, description="波动计算窗口（分钟）")
    min_balance_ratio: Optional[Decimal] = Field(None, description="最小余额比例")
    max_position_ratio: Optional[Decimal] = Field(None, description="最大仓位比例")
    max_orders_per_hour: Optional[int] = Field(None, description="每小时最大订单数")
    max_orders_per_day: Optional[int] = Field(None, description="每天最大订单数")
    max_single_order_amount: Optional[Decimal] = Field(None, description="单笔订单最大金额")
    max_daily_volume: Optional[Decimal] = Field(None, description="每日最大交易量")
    trading_hours_start: Optional[int] = Field(None, description="交易开始时间")
    trading_hours_end: Optional[int] = Field(None, description="交易结束时间")
    weekend_trading: Optional[bool] = Field(None, description="是否允许周末交易")
    max_consecutive_losses: Optional[int] = Field(None, description="最大连续亏损次数")
    max_daily_loss: Optional[Decimal] = Field(None, description="每日最大亏损")


class RiskProfileUpdateRequest(BaseModel):
    """更新风险配置请求"""
    risk_level: Optional[str] = Field(None, description="风险等级")
    max_price_volatility: Optional[Decimal] = Field(None, description="最大价格波动百分比")
    volatility_window_minutes: Optional[int] = Field(None, description="波动计算窗口（分钟）")
    min_balance_ratio: Optional[Decimal] = Field(None, description="最小余额比例")
    max_position_ratio: Optional[Decimal] = Field(None, description="最大仓位比例")
    max_orders_per_hour: Optional[int] = Field(None, description="每小时最大订单数")
    max_orders_per_day: Optional[int] = Field(None, description="每天最大订单数")
    max_single_order_amount: Optional[Decimal] = Field(None, description="单笔订单最大金额")
    max_daily_volume: Optional[Decimal] = Field(None, description="每日最大交易量")
    trading_hours_start: Optional[int] = Field(None, description="交易开始时间")
    trading_hours_end: Optional[int] = Field(None, description="交易结束时间")
    weekend_trading: Optional[bool] = Field(None, description="是否允许周末交易")
    max_consecutive_losses: Optional[int] = Field(None, description="最大连续亏损次数")
    max_daily_loss: Optional[Decimal] = Field(None, description="每日最大亏损")
    is_active: Optional[bool] = Field(None, description="是否激活")


class RiskAlertResponse(BaseModel):
    """风险警报响应"""
    id: int = Field(..., description="警报ID")
    user_id: int = Field(..., description="用户ID")
    title: str = Field(..., description="警报标题")
    message: str = Field(..., description="警报内容")
    severity: str = Field(..., description="严重程度")
    status: str = Field(..., description="警报状态")
    risk_factor: str = Field(..., description="风险因子")
    risk_level: str = Field(..., description="风险等级")
    current_value: Optional[Decimal] = Field(None, description="当前值")
    threshold_value: Optional[Decimal] = Field(None, description="阈值")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")
    triggered_at: datetime = Field(..., description="触发时间")
    acknowledged_at: Optional[datetime] = Field(None, description="确认时间")
    resolved_at: Optional[datetime] = Field(None, description="解决时间")
    duration_seconds: Optional[int] = Field(None, description="持续时间（秒）")


class RiskAlertListResponse(BaseModel):
    """风险警报列表响应"""
    alerts: List[RiskAlertResponse] = Field(..., description="警报列表")
    total: int = Field(..., description="总数量")
    active_count: int = Field(..., description="活跃警报数量")
    critical_count: int = Field(..., description="严重警报数量")


class RiskAlertActionRequest(BaseModel):
    """风险警报操作请求"""
    alert_id: int = Field(..., description="警报ID")


class RiskAlertActionResponse(BaseModel):
    """风险警报操作响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")


class RiskAssessmentRequest(BaseModel):
    """风险评估请求"""
    symbol: str = Field(..., description="交易对符号", example="kogeusdt")
    order_amount: Decimal = Field(..., description="订单金额", example=1000.0)
    current_price: Decimal = Field(..., description="当前价格", example=48.0)


class RiskAssessmentResponse(BaseModel):
    """风险评估响应"""
    approved: bool = Field(..., description="是否批准")
    message: str = Field(..., description="评估消息")
    risk_level: str = Field(..., description="风险等级")
    alerts: List[RiskAlertResponse] = Field(..., description="风险警报")
    recommendations: List[str] = Field(..., description="建议")


class RiskMetricsResponse(BaseModel):
    """风险指标响应"""
    user_id: int = Field(..., description="用户ID")
    current_balance: Decimal = Field(..., description="当前余额")
    daily_volume: Decimal = Field(..., description="每日交易量")
    daily_pnl: Decimal = Field(..., description="每日盈亏")
    consecutive_losses: int = Field(..., description="连续亏损次数")
    orders_count_today: int = Field(..., description="今日订单数")
    orders_count_hour: int = Field(..., description="本小时订单数")
    price_volatility: Decimal = Field(..., description="价格波动率")
    position_ratio: Decimal = Field(..., description="仓位比例")
    last_order_time: Optional[datetime] = Field(None, description="最后订单时间")


class RiskSummaryResponse(BaseModel):
    """风险摘要响应"""
    user_id: int = Field(..., description="用户ID")
    risk_level: str = Field(..., description="风险等级")
    active_alerts_count: int = Field(..., description="活跃警报数量")
    critical_alerts_count: int = Field(..., description="严重警报数量")
    current_balance: Decimal = Field(..., description="当前余额")
    daily_pnl: Decimal = Field(..., description="每日盈亏")
    consecutive_losses: int = Field(..., description="连续亏损次数")
    orders_today: int = Field(..., description="今日订单数")
    orders_this_hour: int = Field(..., description="本小时订单数")
    trading_allowed: bool = Field(..., description="是否允许交易")


class RiskReportResponse(BaseModel):
    """风险报告响应"""
    user_id: int = Field(..., description="用户ID")
    report_date: datetime = Field(..., description="报告日期")
    risk_profile: RiskProfileResponse = Field(..., description="风险配置")
    risk_metrics: RiskMetricsResponse = Field(..., description="风险指标")
    active_alerts: List[RiskAlertResponse] = Field(..., description="活跃警报")
    risk_summary: RiskSummaryResponse = Field(..., description="风险摘要")
    recommendations: List[str] = Field(..., description="建议")
