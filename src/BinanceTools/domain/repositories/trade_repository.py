"""
交易仓储接口

定义交易数据访问的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities.trade import Trade
from ..value_objects.symbol import Symbol


class TradeRepository(ABC):
    """交易仓储接口"""
    
    @abstractmethod
    async def get_by_id(self, trade_id: int) -> Optional[Trade]:
        """根据ID获取交易"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[Trade]:
        """根据用户ID获取交易"""
        pass
    
    @abstractmethod
    async def get_by_order_id(self, order_id: int) -> List[Trade]:
        """根据订单ID获取交易"""
        pass
    
    @abstractmethod
    async def get_by_symbol(self, symbol: Symbol) -> List[Trade]:
        """根据交易对获取交易"""
        pass
    
    @abstractmethod
    async def get_trades_by_date_range(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Trade]:
        """根据日期范围获取交易"""
        pass
    
    @abstractmethod
    async def get_24h_volume(self, user_id: str) -> dict:
        """获取24小时交易量"""
        pass
    
    @abstractmethod
    async def save(self, trade: Trade) -> Trade:
        """保存交易"""
        pass
    
    @abstractmethod
    async def update(self, trade: Trade) -> Trade:
        """更新交易"""
        pass
    
    @abstractmethod
    async def delete(self, trade_id: int) -> bool:
        """删除交易"""
        pass
    
    @abstractmethod
    async def exists(self, trade_id: int) -> bool:
        """检查交易是否存在"""
        pass
