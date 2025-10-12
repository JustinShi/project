"""用户相关的Pydantic schemas"""

from datetime import datetime

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """用户信息响应"""

    id: int
    name: str
    email: str | None = None
    is_valid: bool
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class TokenBalance(BaseModel):
    """代币余额"""

    symbol: str = Field(..., description="代币符号")
    token_id: str = Field(..., description="代币ID，如ALPHA_118")
    free: str = Field(..., description="可用余额")
    freeze: str = Field(default="0", description="冻结余额")
    locked: str = Field(default="0", description="锁定余额")
    amount: str = Field(..., description="总余额")
    valuation: str = Field(..., description="估值（USDT）")


class BalanceResponse(BaseModel):
    """余额查询响应"""

    total_valuation: str = Field(..., description="总估值（USDT）")
    balances: list[TokenBalance] = Field(default_factory=list, description="余额列表")


class TokenVolume(BaseModel):
    """代币交易量"""

    token_name: str = Field(..., description="代币名称")
    volume: float = Field(..., description="交易量（USDT）")


class VolumeResponse(BaseModel):
    """交易量查询响应"""

    total_volume: float = Field(..., description="总交易量（USDT）")
    volumes_by_token: list[TokenVolume] = Field(
        default_factory=list, description="各代币交易量"
    )
