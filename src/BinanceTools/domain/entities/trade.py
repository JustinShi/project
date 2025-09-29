"""
交易实体

表示已执行的交易记录。
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional

from ..value_objects.symbol import Symbol


@dataclass
class Trade:
    """交易实体"""
    
    trade_id: int
    order_id: int
    user_id: str
    symbol: Symbol
    side: str  # BUY or SELL
    quantity: Decimal
    price: Decimal
    commission: Decimal
    commission_asset: str
    executed_at: datetime
    is_maker: bool = False
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.trade_id:
            raise ValueError("交易ID不能为空")
        if not self.order_id:
            raise ValueError("订单ID不能为空")
        if not self.user_id:
            raise ValueError("用户ID不能为空")
        if self.quantity <= 0:
            raise ValueError("交易数量必须大于0")
        if self.price <= 0:
            raise ValueError("交易价格必须大于0")
    
    def is_buy_trade(self) -> bool:
        """是否为买入交易"""
        return self.side == "BUY"
    
    def is_sell_trade(self) -> bool:
        """是否为卖出交易"""
        return self.side == "SELL"
    
    def calculate_total_value(self) -> Decimal:
        """计算交易总价值"""
        return self.quantity * self.price
    
    def calculate_net_value(self) -> Decimal:
        """计算净价值（扣除手续费）"""
        total_value = self.calculate_total_value()
        if self.is_buy_trade():
            # 买入时，手续费通常以基础资产计算
            return total_value
        else:
            # 卖出时，手续费通常以报价资产计算
            return total_value - self.commission
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "trade_id": self.trade_id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "symbol": self.symbol.to_dict(),
            "side": self.side,
            "quantity": str(self.quantity),
            "price": str(self.price),
            "commission": str(self.commission),
            "commission_asset": self.commission_asset,
            "executed_at": self.executed_at.isoformat(),
            "is_maker": self.is_maker
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Trade":
        """从字典创建交易实体"""
        return cls(
            trade_id=data["trade_id"],
            order_id=data["order_id"],
            user_id=data["user_id"],
            symbol=Symbol.from_dict(data["symbol"]),
            side=data["side"],
            quantity=Decimal(data["quantity"]),
            price=Decimal(data["price"]),
            commission=Decimal(data["commission"]),
            commission_asset=data["commission_asset"],
            executed_at=datetime.fromisoformat(data["executed_at"]),
            is_maker=data.get("is_maker", False)
        )
