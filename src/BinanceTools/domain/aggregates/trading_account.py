"""
交易账户聚合

管理用户的所有交易相关操作，包括订单、交易记录等。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from decimal import Decimal
from datetime import datetime

from ..entities.user import User
from ..entities.wallet import Wallet
from ..entities.order import Order, OrderStatus, OrderSide
from ..entities.trade import Trade
from ..value_objects.symbol import Symbol
from ..value_objects.money import Money


@dataclass
class TradingAccount:
    """交易账户聚合根"""
    
    user: User
    wallet: Wallet
    orders: List[Order] = field(default_factory=list)
    trades: List[Trade] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.user:
            raise ValueError("用户不能为空")
        if not self.wallet:
            raise ValueError("钱包不能为空")
        if self.wallet.user_id != self.user.id:
            raise ValueError("钱包用户ID与用户ID不匹配")
    
    def get_active_orders(self) -> List[Order]:
        """获取活跃订单"""
        return [order for order in self.orders if order.is_active()]
    
    def get_orders_by_symbol(self, symbol: Symbol) -> List[Order]:
        """根据交易对获取订单"""
        return [order for order in self.orders if order.symbol == symbol]
    
    def get_active_orders_by_symbol(self, symbol: Symbol) -> List[Order]:
        """根据交易对获取活跃订单"""
        return [order for order in self.get_active_orders() if order.symbol == symbol]
    
    def get_trades_by_symbol(self, symbol: Symbol) -> List[Trade]:
        """根据交易对获取交易记录"""
        return [trade for trade in self.trades if trade.symbol == symbol]
    
    def get_trades_by_order(self, order_id: int) -> List[Trade]:
        """根据订单ID获取交易记录"""
        return [trade for trade in self.trades if trade.order_id == order_id]
    
    def place_order(self, order: Order) -> None:
        """下单"""
        if order.user_id != self.user.id:
            raise ValueError("订单用户ID与账户用户ID不匹配")
        
        # 检查余额是否足够
        if order.is_buy_order():
            # 买单需要检查报价资产余额
            required_amount = order.calculate_total_value()
            if not self.wallet.has_sufficient_balance(order.symbol.quote_asset, required_amount):
                raise ValueError(f"余额不足，需要 {required_amount} {order.symbol.quote_asset}")
        else:
            # 卖单需要检查基础资产余额
            if not self.wallet.has_sufficient_balance(order.symbol.base_asset, order.quantity):
                raise ValueError(f"余额不足，需要 {order.quantity} {order.symbol.base_asset}")
        
        # 添加订单
        self.orders.append(order)
        self.updated_at = datetime.utcnow()
    
    def cancel_order(self, order_id: int) -> bool:
        """取消订单"""
        for order in self.orders:
            if order.order_id == order_id and order.is_active():
                order.update_status(OrderStatus.CANCELED)
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    def execute_trade(self, trade: Trade) -> None:
        """执行交易"""
        if trade.user_id != self.user.id:
            raise ValueError("交易用户ID与账户用户ID不匹配")
        
        # 查找对应的订单
        order = self.get_order_by_id(trade.order_id)
        if not order:
            raise ValueError(f"未找到订单: {trade.order_id}")
        
        # 更新订单状态
        if order.is_buy_order():
            # 买单成交，增加基础资产，减少报价资产
            self._update_asset_balance(
                trade.symbol.base_asset,
                trade.quantity
            )
            self._update_asset_balance(
                trade.symbol.quote_asset,
                -trade.calculate_total_value()
            )
        else:
            # 卖单成交，减少基础资产，增加报价资产
            self._update_asset_balance(
                trade.symbol.base_asset,
                -trade.quantity
            )
            self._update_asset_balance(
                trade.symbol.quote_asset,
                trade.calculate_total_value()
            )
        
        # 添加交易记录
        self.trades.append(trade)
        
        # 更新订单状态
        if trade.quantity >= order.quantity:
            order.update_status(OrderStatus.FILLED)
        else:
            order.update_status(OrderStatus.PARTIALLY_FILLED)
        
        self.updated_at = datetime.utcnow()
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """根据ID获取订单"""
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None
    
    def get_trade_by_id(self, trade_id: int) -> Optional[Trade]:
        """根据ID获取交易"""
        for trade in self.trades:
            if trade.trade_id == trade_id:
                return trade
        return None
    
    def get_total_volume_24h(self) -> Dict[str, Decimal]:
        """获取24小时交易量"""
        now = datetime.utcnow()
        yesterday = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        volume_by_symbol = {}
        for trade in self.trades:
            if trade.executed_at >= yesterday:
                symbol_str = str(trade.symbol)
                if symbol_str not in volume_by_symbol:
                    volume_by_symbol[symbol_str] = Decimal('0')
                volume_by_symbol[symbol_str] += trade.calculate_total_value()
        
        return volume_by_symbol
    
    def get_pnl_summary(self) -> Dict[str, Dict[str, Decimal]]:
        """获取盈亏摘要"""
        pnl_by_symbol = {}
        
        for trade in self.trades:
            symbol_str = str(trade.symbol)
            if symbol_str not in pnl_by_symbol:
                pnl_by_symbol[symbol_str] = {
                    "total_buy_quantity": Decimal('0'),
                    "total_buy_value": Decimal('0'),
                    "total_sell_quantity": Decimal('0'),
                    "total_sell_value": Decimal('0'),
                    "realized_pnl": Decimal('0')
                }
            
            if trade.is_buy_trade():
                pnl_by_symbol[symbol_str]["total_buy_quantity"] += trade.quantity
                pnl_by_symbol[symbol_str]["total_buy_value"] += trade.calculate_total_value()
            else:
                pnl_by_symbol[symbol_str]["total_sell_quantity"] += trade.quantity
                pnl_by_symbol[symbol_str]["total_sell_value"] += trade.calculate_total_value()
        
        # 计算已实现盈亏
        for symbol_data in pnl_by_symbol.values():
            if symbol_data["total_sell_quantity"] > 0:
                avg_buy_price = symbol_data["total_buy_value"] / symbol_data["total_buy_quantity"]
                symbol_data["realized_pnl"] = symbol_data["total_sell_value"] - (
                    symbol_data["total_sell_quantity"] * avg_buy_price
                )
        
        return pnl_by_symbol
    
    def _update_asset_balance(self, symbol: str, amount: Decimal) -> None:
        """更新资产余额"""
        asset = self.wallet.get_asset_by_symbol(symbol)
        if asset:
            # 更新现有资产
            new_asset = asset
            new_asset.free += amount
            new_asset.amount = new_asset.free + new_asset.freeze + new_asset.locked
            self.wallet.update_asset(new_asset)
        else:
            # 创建新资产（仅当金额为正时）
            if amount > 0:
                from ..entities.wallet import Asset
                new_asset = Asset(
                    chain_id="56",  # BSC
                    contract_address="",
                    name=symbol,
                    symbol=symbol,
                    token_id=symbol,
                    free=amount,
                    freeze=Decimal('0'),
                    locked=Decimal('0'),
                    withdrawing=Decimal('0'),
                    amount=amount,
                    valuation=Decimal('0'),
                    cex_asset=False
                )
                self.wallet.update_asset(new_asset)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "user": self.user.to_dict(),
            "wallet": self.wallet.to_dict(),
            "orders": [order.to_dict() for order in self.orders],
            "trades": [trade.to_dict() for trade in self.trades],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TradingAccount":
        """从字典创建交易账户"""
        from ..entities.user import User
        from ..entities.wallet import Wallet
        from ..entities.order import Order
        from ..entities.trade import Trade
        
        user = User.from_dict(data["user"])
        wallet = Wallet.from_dict(data["wallet"])
        
        orders = [Order.from_dict(order_data) for order_data in data["orders"]]
        trades = [Trade.from_dict(trade_data) for trade_data in data["trades"]]
        
        return cls(
            user=user,
            wallet=wallet,
            orders=orders,
            trades=trades,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
