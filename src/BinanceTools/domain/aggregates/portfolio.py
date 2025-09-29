"""
投资组合聚合

管理用户的资产组合，包括持仓、盈亏分析等。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime

from ..entities.wallet import Wallet, Asset
from ..entities.trade import Trade
from ..value_objects.money import Money
from ..value_objects.symbol import Symbol


@dataclass
class Position:
    """持仓信息"""
    
    symbol: Symbol
    quantity: Decimal
    avg_price: Decimal
    current_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal = Decimal('0')
    
    @property
    def pnl_percentage(self) -> Decimal:
        """盈亏百分比"""
        if self.avg_price == 0:
            return Decimal('0')
        return (self.current_price - self.avg_price) / self.avg_price * 100
    
    @property
    def total_pnl(self) -> Decimal:
        """总盈亏"""
        return self.realized_pnl + self.unrealized_pnl


@dataclass
class Portfolio:
    """投资组合聚合根"""
    
    user_id: str
    wallet: Wallet
    positions: List[Position] = field(default_factory=list)
    trades: List[Trade] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.user_id:
            raise ValueError("用户ID不能为空")
        if not self.wallet:
            raise ValueError("钱包不能为空")
        if self.wallet.user_id != self.user_id:
            raise ValueError("钱包用户ID与投资组合用户ID不匹配")
    
    def add_trade(self, trade: Trade) -> None:
        """添加交易记录"""
        if trade.user_id != self.user_id:
            raise ValueError("交易用户ID与投资组合用户ID不匹配")
        
        self.trades.append(trade)
        self._update_positions()
        self.updated_at = datetime.utcnow()
    
    def _update_positions(self) -> None:
        """更新持仓信息"""
        # 按交易对分组计算持仓
        positions_by_symbol = {}
        
        for trade in self.trades:
            symbol_str = str(trade.symbol)
            if symbol_str not in positions_by_symbol:
                positions_by_symbol[symbol_str] = {
                    "symbol": trade.symbol,
                    "total_buy_quantity": Decimal('0'),
                    "total_buy_value": Decimal('0'),
                    "total_sell_quantity": Decimal('0'),
                    "total_sell_value": Decimal('0'),
                    "realized_pnl": Decimal('0')
                }
            
            if trade.is_buy_trade():
                positions_by_symbol[symbol_str]["total_buy_quantity"] += trade.quantity
                positions_by_symbol[symbol_str]["total_buy_value"] += trade.calculate_total_value()
            else:
                positions_by_symbol[symbol_str]["total_sell_quantity"] += trade.quantity
                positions_by_symbol[symbol_str]["total_sell_value"] += trade.calculate_total_value()
        
        # 计算持仓和已实现盈亏
        self.positions = []
        for symbol_data in positions_by_symbol.values():
            net_quantity = symbol_data["total_buy_quantity"] - symbol_data["total_sell_quantity"]
            
            if net_quantity > 0:  # 有持仓
                avg_price = symbol_data["total_buy_value"] / symbol_data["total_buy_quantity"]
                
                # 计算已实现盈亏
                if symbol_data["total_sell_quantity"] > 0:
                    realized_pnl = symbol_data["total_sell_value"] - (
                        symbol_data["total_sell_quantity"] * avg_price
                    )
                else:
                    realized_pnl = Decimal('0')
                
                # 获取当前价格（这里需要从外部获取）
                current_price = self._get_current_price(symbol_data["symbol"])
                market_value = net_quantity * current_price
                unrealized_pnl = market_value - (net_quantity * avg_price)
                
                position = Position(
                    symbol=symbol_data["symbol"],
                    quantity=net_quantity,
                    avg_price=avg_price,
                    current_price=current_price,
                    market_value=market_value,
                    unrealized_pnl=unrealized_pnl,
                    realized_pnl=realized_pnl
                )
                
                self.positions.append(position)
    
    def _get_current_price(self, symbol: Symbol) -> Decimal:
        """获取当前价格（这里需要从外部服务获取）"""
        # 这里应该调用价格服务，暂时返回1作为占位符
        return Decimal('1')
    
    def get_position_by_symbol(self, symbol: Symbol) -> Optional[Position]:
        """根据交易对获取持仓"""
        for position in self.positions:
            if position.symbol == symbol:
                return position
        return None
    
    def get_total_market_value(self) -> Decimal:
        """获取总市值"""
        return sum(position.market_value for position in self.positions)
    
    def get_total_unrealized_pnl(self) -> Decimal:
        """获取总未实现盈亏"""
        return sum(position.unrealized_pnl for position in self.positions)
    
    def get_total_realized_pnl(self) -> Decimal:
        """获取总已实现盈亏"""
        return sum(position.realized_pnl for position in self.positions)
    
    def get_total_pnl(self) -> Decimal:
        """获取总盈亏"""
        return self.get_total_unrealized_pnl() + self.get_total_realized_pnl()
    
    def get_pnl_percentage(self) -> Decimal:
        """获取总盈亏百分比"""
        total_cost = sum(position.quantity * position.avg_price for position in self.positions)
        if total_cost == 0:
            return Decimal('0')
        return self.get_total_pnl() / total_cost * 100
    
    def get_top_positions(self, limit: int = 10) -> List[Position]:
        """获取持仓最大的前N个"""
        return sorted(self.positions, key=lambda p: p.market_value, reverse=True)[:limit]
    
    def get_top_gainers(self, limit: int = 10) -> List[Position]:
        """获取涨幅最大的前N个"""
        return sorted(self.positions, key=lambda p: p.pnl_percentage, reverse=True)[:limit]
    
    def get_top_losers(self, limit: int = 10) -> List[Position]:
        """获取跌幅最大的前N个"""
        return sorted(self.positions, key=lambda p: p.pnl_percentage)[:limit]
    
    def get_asset_allocation(self) -> Dict[str, Decimal]:
        """获取资产配置"""
        total_value = self.get_total_market_value()
        if total_value == 0:
            return {}
        
        allocation = {}
        for position in self.positions:
            symbol_str = str(position.symbol)
            allocation[symbol_str] = position.market_value / total_value * 100
        
        return allocation
    
    def get_performance_summary(self) -> Dict[str, any]:
        """获取业绩摘要"""
        return {
            "total_market_value": str(self.get_total_market_value()),
            "total_unrealized_pnl": str(self.get_total_unrealized_pnl()),
            "total_realized_pnl": str(self.get_total_realized_pnl()),
            "total_pnl": str(self.get_total_pnl()),
            "pnl_percentage": str(self.get_pnl_percentage()),
            "position_count": len(self.positions),
            "asset_allocation": {k: str(v) for k, v in self.get_asset_allocation().items()}
        }
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "wallet": self.wallet.to_dict(),
            "positions": [
                {
                    "symbol": position.symbol.to_dict(),
                    "quantity": str(position.quantity),
                    "avg_price": str(position.avg_price),
                    "current_price": str(position.current_price),
                    "market_value": str(position.market_value),
                    "unrealized_pnl": str(position.unrealized_pnl),
                    "realized_pnl": str(position.realized_pnl),
                    "pnl_percentage": str(position.pnl_percentage),
                    "total_pnl": str(position.total_pnl)
                }
                for position in self.positions
            ],
            "trades": [trade.to_dict() for trade in self.trades],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Portfolio":
        """从字典创建投资组合"""
        from ..entities.wallet import Wallet
        from ..entities.trade import Trade
        
        wallet = Wallet.from_dict(data["wallet"])
        trades = [Trade.from_dict(trade_data) for trade_data in data["trades"]]
        
        portfolio = cls(
            user_id=data["user_id"],
            wallet=wallet,
            trades=trades,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
        
        # 重新计算持仓
        portfolio._update_positions()
        
        return portfolio
