"""
获取订单历史用例

获取用户的订单历史记录。
"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.order import Order
from ...domain.repositories.order_repository import OrderRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.symbol import Symbol
from ..dto.order_dto import OrderDTO


class GetOrderHistoryUseCase:
    """获取订单历史用例"""
    
    def __init__(
        self,
        order_repository: OrderRepository,
        user_repository: UserRepository
    ):
        """初始化用例"""
        self.order_repository = order_repository
        self.user_repository = user_repository
    
    async def execute(
        self,
        user_id: str,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[OrderDTO]:
        """执行用例"""
        # 检查用户是否存在
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"用户不存在: {user_id}")
        
        if not user.is_active():
            raise ValueError(f"用户未激活: {user_id}")
        
        # 获取订单
        if start_date and end_date:
            orders = await self.order_repository.get_orders_by_date_range(
                user_id, start_date, end_date
            )
        else:
            orders = await self.order_repository.get_by_user_id(user_id)
        
        # 按交易对过滤
        if symbol:
            symbol_obj = Symbol.from_string(symbol)
            orders = [order for order in orders if order.symbol == symbol_obj]
        
        # 限制数量
        orders = orders[:limit]
        
        # 转换为DTO
        return [OrderDTO.from_entity(order) for order in orders]
