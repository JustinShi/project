"""
交易DTO

交易相关的数据传输对象。
"""

from dataclasses import dataclass
from typing import Dict
from decimal import Decimal
from datetime import datetime

from ...domain.entities.trade import Trade


@dataclass
class TradeDTO:
    """交易DTO"""
    
    trade_id: int
    order_id: int
    user_id: str
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    commission: Decimal
    commission_asset: str
    executed_at: datetime
    is_maker: bool = False
    
    @property
    def is_buy_trade(self) -> bool:
        """是否为买入交易"""
        return self.side == "BUY"
    
    @property
    def is_sell_trade(self) -> bool:
        """是否为卖出交易"""
        return self.side == "SELL"
    
    def calculate_total_value(self) -> Decimal:
        """计算交易总价值"""
        return self.quantity * self.price
    
    def calculate_net_value(self) -> Decimal:
        """计算净价值（扣除手续费）"""
        total_value = self.calculate_total_value()
        if self.is_buy_trade:
            return total_value
        else:
            return total_value - self.commission
    
    @classmethod
    def from_entity(cls, trade: Trade) -> "TradeDTO":
        """从实体创建DTO"""
        return cls(
            trade_id=trade.trade_id,
            order_id=trade.order_id,
            user_id=trade.user_id,
            symbol=str(trade.symbol),
            side=trade.side,
            quantity=trade.quantity,
            price=trade.price,
            commission=trade.commission,
            commission_asset=trade.commission_asset,
            executed_at=trade.executed_at,
            is_maker=trade.is_maker
        )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "trade_id": self.trade_id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": str(self.quantity),
            "price": str(self.price),
            "commission": str(self.commission),
            "commission_asset": self.commission_asset,
            "executed_at": self.executed_at.isoformat(),
            "is_maker": self.is_maker,
            "total_value": str(self.calculate_total_value()),
            "net_value": str(self.calculate_net_value())
        }


@dataclass
class TradingVolumeDTO:
    """交易量DTO"""
    
    user_id: str
    total_volume: Decimal
    volume_by_symbol: Dict[str, Decimal]
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "total_volume": str(self.total_volume),
            "volume_by_symbol": {k: str(v) for k, v in self.volume_by_symbol.items()}
        }
