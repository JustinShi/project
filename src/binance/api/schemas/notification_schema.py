"""通知相关API模式"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """通知响应"""
    id: str = Field(..., description="通知ID")
    user_id: int = Field(..., description="用户ID")
    type: str = Field(..., description="通知类型")
    title: str = Field(..., description="通知标题")
    message: str = Field(..., description="通知内容")
    data: dict[str, Any] | None = Field(None, description="附加数据")
    is_read: bool = Field(..., description="是否已读")
    created_at: datetime = Field(..., description="创建时间")
    read_at: datetime | None = Field(None, description="已读时间")


class NotificationListResponse(BaseModel):
    """通知列表响应"""
    notifications: list[NotificationResponse] = Field(..., description="通知列表")
    total: int = Field(..., description="总数量")
    unread_count: int = Field(..., description="未读数量")


class NotificationMarkReadRequest(BaseModel):
    """标记通知已读请求"""
    notification_id: str = Field(..., description="通知ID")


class NotificationMarkReadResponse(BaseModel):
    """标记通知已读响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")


class NotificationStatisticsResponse(BaseModel):
    """通知统计响应"""
    total_notifications: int = Field(..., description="总通知数")
    unread_notifications: int = Field(..., description="未读通知数")
    notifications_by_type: dict[str, int] = Field(..., description="按类型统计")
    recent_notifications: list[NotificationResponse] = Field(..., description="最近通知")


class NotificationSettingsResponse(BaseModel):
    """通知设置响应"""
    user_id: int = Field(..., description="用户ID")
    email_notifications: bool = Field(..., description="邮件通知")
    sms_notifications: bool = Field(..., description="短信通知")
    push_notifications: bool = Field(..., description="推送通知")
    volatility_alerts: bool = Field(..., description="价格波动警报")
    order_updates: bool = Field(..., description="订单更新通知")
    balance_alerts: bool = Field(..., description="余额警报")


class NotificationSettingsUpdateRequest(BaseModel):
    """更新通知设置请求"""
    email_notifications: bool | None = Field(None, description="邮件通知")
    sms_notifications: bool | None = Field(None, description="短信通知")
    push_notifications: bool | None = Field(None, description="推送通知")
    volatility_alerts: bool | None = Field(None, description="价格波动警报")
    order_updates: bool | None = Field(None, description="订单更新通知")
    balance_alerts: bool | None = Field(None, description="余额警报")


class NotificationTestRequest(BaseModel):
    """测试通知请求"""
    type: str = Field(..., description="通知类型", example="test")
    title: str = Field(..., description="测试标题", example="测试通知")
    message: str = Field(..., description="测试内容", example="这是一条测试通知")


class NotificationTestResponse(BaseModel):
    """测试通知响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    notification_id: str | None = Field(None, description="通知ID")
