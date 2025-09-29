"""
交易领域服务

处理交易相关的业务逻辑。
"""

from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from ..entities.order import Order, OrderSide, OrderType, OrderTimeInForce
from ..entities.trade import Trade
from ..value_objects.symbol import Symbol
from ..value_objects.money import Money


class TradingService:
    """交易领域服务"""
    
    def __init__(self):
        """初始化交易服务"""
        pass
    
    def create_buy_order(
        self,
        user_id: str,
        symbol: Symbol,
        quantity: Decimal,
        price: Decimal,
        time_in_force: OrderTimeInForce = OrderTimeInForce.GTC
    ) -> Order:
        """创建买单"""
        if quantity <= 0:
            raise ValueError("订单数量必须大于0")
        if price <= 0:
            raise ValueError("订单价格必须大于0")
        
        order = Order(
            order_id=0,  # 将由仓储分配
            user_id=user_id,
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
            status=OrderStatus.NEW,
            time_in_force=time_in_force
        )
        
        return order
    
    def create_sell_order(
        self,
        user_id: str,
        symbol: Symbol,
        quantity: Decimal,
        price: Decimal,
        time_in_force: OrderTimeInForce = OrderTimeInForce.GTC
    ) -> Order:
        """创建卖单"""
        if quantity <= 0:
            raise ValueError("订单数量必须大于0")
        if price <= 0:
            raise ValueError("订单价格必须大于0")
        
        order = Order(
            order_id=0,  # 将由仓储分配
            user_id=user_id,
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
            status=OrderStatus.NEW,
            time_in_force=time_in_force
        )
        
        return order
    
    def create_oto_order(
        self,
        user_id: str,
        symbol: Symbol,
        working_quantity: Decimal,
        working_price: Decimal,
        pending_price: Decimal,
        payment_details: List[dict]
    ) -> Order:
        """创建OTO订单（反向订单）"""
        if working_quantity <= 0:
            raise ValueError("工作订单数量必须大于0")
        if working_price <= 0:
            raise ValueError("工作订单价格必须大于0")
        if pending_price <= 0:
            raise ValueError("挂单价格必须大于0")
        
        order = Order(
            order_id=0,  # 将由仓储分配
            user_id=user_id,
            symbol=symbol,
            side=OrderSide.BUY,  # OTO订单通常是买单
            order_type=OrderType.LIMIT,
            quantity=working_quantity,
            price=working_price,
            status=OrderStatus.NEW,
            time_in_force=OrderTimeInForce.GTC,
            working_price=working_price,
            pending_price=pending_price,
            payment_details=[
                PaymentDetail(
                    amount=Decimal(pd["amount"]),
                    payment_wallet_type=pd["payment_wallet_type"]
                )
                for pd in payment_details
            ]
        )
        
        return order
    
    def calculate_order_value(self, order: Order) -> Money:
        """计算订单价值"""
        total_value = order.quantity * order.price
        return Money(total_value, order.symbol.quote_asset)
    
    def calculate_trade_commission(
        self,
        trade: Trade,
        commission_rate: Decimal = Decimal('0.001')  # 0.1%
    ) -> Money:
        """计算交易手续费"""
        trade_value = trade.calculate_total_value()
        commission = trade_value * commission_rate
        
        # 手续费通常以基础资产计算
        return Money(commission, trade.symbol.base_asset)
    
    def calculate_slippage(
        self,
        expected_price: Decimal,
        actual_price: Decimal
    ) -> Decimal:
        """计算滑点"""
        if expected_price == 0:
            return Decimal('0')
        return (actual_price - expected_price) / expected_price * 100
    
    def is_profitable_trade(
        self,
        buy_trade: Trade,
        sell_trade: Trade
    ) -> bool:
        """判断交易是否盈利"""
        if not buy_trade.is_buy_trade() or not sell_trade.is_sell_trade():
            raise ValueError("买入和卖出交易方向错误")
        
        if buy_trade.symbol != sell_trade.symbol:
            raise ValueError("交易对不匹配")
        
        buy_price = buy_trade.price
        sell_price = sell_trade.price
        
        return sell_price > buy_price
    
    def calculate_trade_pnl(
        self,
        buy_trade: Trade,
        sell_trade: Trade
    ) -> Money:
        """计算交易盈亏"""
        if not self.is_profitable_trade(buy_trade, sell_trade):
            return Money.zero(buy_trade.symbol.quote_asset)
        
        quantity = min(buy_trade.quantity, sell_trade.quantity)
        pnl = (sell_trade.price - buy_trade.price) * quantity
        
        return Money(pnl, buy_trade.symbol.quote_asset)
    
    def validate_order_parameters(
        self,
        symbol: Symbol,
        quantity: Decimal,
        price: Decimal,
        min_quantity: Decimal = Decimal('0.001'),
        max_quantity: Decimal = Decimal('1000000'),
        min_price: Decimal = Decimal('0.000001'),
        max_price: Decimal = Decimal('1000000')
    ) -> bool:
        """验证订单参数"""
        if quantity < min_quantity or quantity > max_quantity:
            return False
        
        if price < min_price or price > max_price:
            return False
        
        return True
    
    def get_order_summary(self, orders: List[Order]) -> dict:
        """获取订单摘要"""
        total_orders = len(orders)
        active_orders = len([o for o in orders if o.is_active()])
        filled_orders = len([o for o in orders if o.is_filled()])
        canceled_orders = len([o for o in orders if o.is_canceled()])
        
        buy_orders = len([o for o in orders if o.is_buy_order()])
        sell_orders = len([o for o in orders if o.is_sell_order()])
        
        total_value = sum(o.calculate_total_value() for o in orders)
        
        return {
            "total_orders": total_orders,
            "active_orders": active_orders,
            "filled_orders": filled_orders,
            "canceled_orders": canceled_orders,
            "buy_orders": buy_orders,
            "sell_orders": sell_orders,
            "total_value": str(total_value)
        }
