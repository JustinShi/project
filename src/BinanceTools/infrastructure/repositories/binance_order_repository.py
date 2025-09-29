"""
币安订单仓储实现

实现订单仓储接口，从币安API获取订单信息。
"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.order import Order, OrderSide, OrderType, OrderStatus, OrderTimeInForce, PaymentDetail
from ...domain.repositories.order_repository import OrderRepository
from ...domain.value_objects.symbol import Symbol
from ..external_services.binance_api_client import BinanceApiClient


class BinanceOrderRepository(OrderRepository):
    """币安订单仓储实现"""
    
    def __init__(self, api_client: BinanceApiClient):
        """初始化仓储"""
        self.api_client = api_client
        self._orders_cache = {}
    
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """根据ID获取订单"""
        if order_id in self._orders_cache:
            return self._orders_cache[order_id]
        
        # 这里应该从API获取订单详情
        # 暂时返回None
        return None
    
    async def get_by_user_id(self, user_id: str) -> List[Order]:
        """根据用户ID获取订单"""
        # 这里应该从API获取用户的所有订单
        # 暂时返回空列表
        return []
    
    async def get_by_symbol(self, symbol: Symbol) -> List[Order]:
        """根据交易对获取订单"""
        # 这里应该从API获取指定交易对的订单
        # 暂时返回空列表
        return []
    
    async def get_active_orders(self, user_id: str) -> List[Order]:
        """获取活跃订单"""
        all_orders = await self.get_by_user_id(user_id)
        return [order for order in all_orders if order.is_active()]
    
    async def get_orders_by_date_range(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Order]:
        """根据日期范围获取订单"""
        # 这里应该从API获取指定日期范围的订单
        # 暂时返回空列表
        return []
    
    async def save(self, order: Order) -> Order:
        """保存订单"""
        try:
            # 调用币安API下单
            if order.payment_details:
                # OTO订单
                order_data = await self.api_client.place_oto_order(
                    user_id=order.user_id,
                    symbol=str(order.symbol),
                    working_quantity=order.quantity,
                    working_price=order.price,
                    pending_price=order.pending_price,
                    payment_details=[
                        {
                            "amount": str(pd.amount),
                            "paymentWalletType": pd.payment_wallet_type
                        }
                        for pd in order.payment_details
                    ]
                )
            else:
                # 普通订单
                order_data = await self.api_client.place_order(
                    user_id=order.user_id,
                    symbol=str(order.symbol),
                    side=order.side.value,
                    quantity=order.quantity,
                    price=order.price,
                    time_in_force=order.time_in_force.value
                )
            
            # 更新订单ID
            if order_data:
                order.order_id = order_data.get("orderId", 0)
                order.working_order_id = order_data.get("workingOrderId")
                order.pending_order_id = order_data.get("pendingOrderId")
            
            # 缓存订单
            self._orders_cache[order.order_id] = order
            return order
            
        except Exception as e:
            # 记录错误日志
            print(f"下单失败: {e}")
            raise
    
    async def update(self, order: Order) -> Order:
        """更新订单"""
        # 缓存订单
        self._orders_cache[order.order_id] = order
        return order
    
    async def delete(self, order_id: int) -> bool:
        """删除订单"""
        if order_id in self._orders_cache:
            del self._orders_cache[order_id]
            return True
        return False
    
    async def exists(self, order_id: int) -> bool:
        """检查订单是否存在"""
        return order_id in self._orders_cache
