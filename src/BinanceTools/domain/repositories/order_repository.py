"""
订单仓储接口

定义订单数据访问的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities.order import Order
from ..value_objects.symbol import Symbol


class OrderRepository(ABC):
    """订单仓储接口"""
    
    @abstractmethod
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """根据ID获取订单"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[Order]:
        """根据用户ID获取订单"""
        pass
    
    @abstractmethod
    async def get_by_symbol(self, symbol: Symbol) -> List[Order]:
        """根据交易对获取订单"""
        pass
    
    @abstractmethod
    async def get_active_orders(self, user_id: str) -> List[Order]:
        """获取活跃订单"""
        pass
    
    @abstractmethod
    async def get_orders_by_date_range(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Order]:
        """根据日期范围获取订单"""
        pass
    
    @abstractmethod
    async def save(self, order: Order) -> Order:
        """保存订单"""
        pass
    
    @abstractmethod
    async def update(self, order: Order) -> Order:
        """更新订单"""
        pass
    
    @abstractmethod
    async def delete(self, order_id: int) -> bool:
        """删除订单"""
        pass
    
    @abstractmethod
    async def exists(self, order_id: int) -> bool:
        """检查订单是否存在"""
        pass
