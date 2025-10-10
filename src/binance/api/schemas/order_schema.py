"""订单相关API模式"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from binance.config.constants import OTOOrderPairStatus


class OrderExecuteRequest(BaseModel):
    """订单执行请求"""
    symbol: str = Field(..., description="交易对符号", example="kogeusdt")
    quantity: Decimal = Field(..., description="订单数量", example=100.0)
    buy_offset_percentage: Decimal = Field(..., description="买单价格偏移百分比", example=0.1)
    sell_offset_percentage: Decimal = Field(..., description="卖单价格偏移百分比", example=0.1)


class OrderExecuteResponse(BaseModel):
    """订单执行响应"""
    success: bool = Field(..., description="执行是否成功")
    message: str = Field(..., description="执行消息")
    order_pair_id: Optional[int] = Field(None, description="订单对ID")
    buy_order_id: Optional[str] = Field(None, description="买单ID")
    sell_order_id: Optional[str] = Field(None, description="卖单ID")
    buy_price: Optional[Decimal] = Field(None, description="买单价格")
    sell_price: Optional[Decimal] = Field(None, description="卖单价格")
    quantity: Optional[Decimal] = Field(None, description="订单数量")
    status: Optional[str] = Field(None, description="订单状态")


class OrderStatusResponse(BaseModel):
    """订单状态响应"""
    order_pair_id: int = Field(..., description="订单对ID")
    user_id: int = Field(..., description="用户ID")
    symbol: str = Field(..., description="交易对符号")
    status: str = Field(..., description="订单状态")
    buy_order_id: Optional[str] = Field(None, description="买单ID")
    sell_order_id: Optional[str] = Field(None, description="卖单ID")
    buy_price: Optional[Decimal] = Field(None, description="买单价格")
    sell_price: Optional[Decimal] = Field(None, description="卖单价格")
    quantity: Optional[Decimal] = Field(None, description="订单数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class OrderCancelRequest(BaseModel):
    """订单取消请求"""
    order_pair_id: int = Field(..., description="订单对ID")


class OrderCancelResponse(BaseModel):
    """订单取消响应"""
    success: bool = Field(..., description="取消是否成功")
    message: str = Field(..., description="取消消息")


class OrderStatisticsResponse(BaseModel):
    """订单统计响应"""
    total_orders: int = Field(..., description="总订单数")
    pending_orders: int = Field(..., description="等待中订单数")
    buy_filled_orders: int = Field(..., description="买单已成交订单数")
    completed_orders: int = Field(..., description="已完成订单数")
    cancelled_orders: int = Field(..., description="已取消订单数")


class OrderListResponse(BaseModel):
    """订单列表响应"""
    orders: list[OrderStatusResponse] = Field(..., description="订单列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class WebSocketStatusResponse(BaseModel):
    """WebSocket状态响应"""
    user_id: int = Field(..., description="用户ID")
    connected: bool = Field(..., description="是否已连接")
    listen_key: Optional[str] = Field(None, description="ListenKey")
    reconnect_attempts: int = Field(..., description="重连尝试次数")
    last_activity: Optional[datetime] = Field(None, description="最后活动时间")


class OrderMonitorResponse(BaseModel):
    """订单监控响应"""
    user_id: int = Field(..., description="用户ID")
    active_orders: list[OrderStatusResponse] = Field(..., description="活跃订单列表")
    websocket_status: WebSocketStatusResponse = Field(..., description="WebSocket状态")
    statistics: OrderStatisticsResponse = Field(..., description="订单统计")
