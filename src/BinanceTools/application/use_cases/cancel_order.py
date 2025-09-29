"""
取消订单用例

取消指定的交易订单。
"""

from typing import Optional

from ...domain.entities.order import Order
from ...domain.repositories.order_repository import OrderRepository
from ...domain.repositories.user_repository import UserRepository
from ..dto.order_dto import OrderDTO


class CancelOrderUseCase:
    """取消订单用例"""
    
    def __init__(
        self,
        order_repository: OrderRepository,
        user_repository: UserRepository
    ):
        """初始化用例"""
        self.order_repository = order_repository
        self.user_repository = user_repository
    
    async def execute(self, user_id: str, order_id: int) -> Optional[OrderDTO]:
        """执行用例"""
        # 检查用户是否存在
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"用户不存在: {user_id}")
        
        if not user.is_active():
            raise ValueError(f"用户未激活: {user_id}")
        
        # 获取订单
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            return None
        
        # 检查订单是否属于该用户
        if order.user_id != user_id:
            raise ValueError("订单不属于该用户")
        
        # 检查订单是否可以取消
        if not order.is_active():
            raise ValueError("订单无法取消")
        
        # 取消订单
        order.update_status(OrderStatus.CANCELED)
        updated_order = await self.order_repository.update(order)
        
        # 转换为DTO
        return OrderDTO.from_entity(updated_order)
