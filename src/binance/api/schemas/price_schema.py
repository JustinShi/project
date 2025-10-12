"""价格API模式"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PriceDataResponse(BaseModel):
    """价格数据响应"""

    symbol: str = Field(..., description="代币符号")
    price: Decimal = Field(..., description="价格")
    volume: Decimal = Field(..., description="成交量")
    timestamp: datetime = Field(..., description="时间戳")
    price_change_24h: Decimal | None = Field(None, description="24小时价格变化")
    price_change_percentage_24h: Decimal | None = Field(
        None, description="24小时价格变化百分比"
    )

    class Config:
        from_attributes = True


class PriceHistoryResponse(BaseModel):
    """价格历史响应"""

    symbol: str = Field(..., description="代币符号")
    prices: list[PriceDataResponse] = Field(..., description="价格历史数据")
    count: int = Field(..., description="数据数量")
    time_range_minutes: int = Field(..., description="时间范围（分钟）")


class PriceStatisticsResponse(BaseModel):
    """价格统计响应"""

    symbol: str = Field(..., description="代币符号")
    count: int = Field(..., description="数据数量")
    min_price: Decimal | None = Field(None, description="最低价格")
    max_price: Decimal | None = Field(None, description="最高价格")
    avg_price: Decimal | None = Field(None, description="平均价格")
    volatility: Decimal | None = Field(None, description="波动率（百分比）")
    time_range_minutes: int = Field(..., description="时间范围（分钟）")


class VolatilityAlertResponse(BaseModel):
    """波动警报响应"""

    symbol: str = Field(..., description="代币符号")
    volatility_percentage: Decimal = Field(..., description="波动百分比")
    threshold: Decimal = Field(..., description="阈值")
    price_range: dict[str, Decimal] = Field(..., description="价格范围")
    window_size: int = Field(..., description="窗口大小")
    timestamp: datetime = Field(..., description="警报时间")


class WebSocketStatusResponse(BaseModel):
    """WebSocket状态响应"""

    symbol: str = Field(..., description="代币符号")
    is_connected: bool = Field(..., description="是否连接")
    is_running: bool = Field(..., description="是否运行")
    reconnect_attempts: int = Field(..., description="重连尝试次数")
    last_activity: datetime | None = Field(None, description="最后活动时间")


class MonitoringStatusResponse(BaseModel):
    """监控状态响应"""

    is_running: bool = Field(..., description="是否正在运行")
    monitored_symbols: list[str] = Field(..., description="监控的代币列表")
    total_connections: int = Field(..., description="总连接数")
    active_connections: int = Field(..., description="活跃连接数")
