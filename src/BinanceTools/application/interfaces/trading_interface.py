"""
交易接口

定义交易相关的应用接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..dto.wallet_dto import WalletDTO
from ..dto.order_dto import OrderDTO
from ..dto.trade_dto import TradeDTO, TradingVolumeDTO


class TradingInterface(ABC):
    """交易接口"""
    
    @abstractmethod
    async def get_wallet_balance(self, user_id: str) -> Optional[WalletDTO]:
        """获取钱包余额"""
        pass
    
    @abstractmethod
    async def place_buy_order(
        self,
        user_id: str,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> OrderDTO:
        """下买单"""
        pass
    
    @abstractmethod
    async def place_sell_order(
        self,
        user_id: str,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> OrderDTO:
        """下卖单"""
        pass
    
    @abstractmethod
    async def cancel_order(self, user_id: str, order_id: int) -> Optional[OrderDTO]:
        """取消订单"""
        pass
    
    @abstractmethod
    async def get_trading_volume(self, user_id: str) -> TradingVolumeDTO:
        """获取交易量"""
        pass
    
    @abstractmethod
    async def get_order_history(
        self,
        user_id: str,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[OrderDTO]:
        """获取订单历史"""
        pass
    
    @abstractmethod
    async def get_trade_history(
        self,
        user_id: str,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[TradeDTO]:
        """获取交易历史"""
        pass
    
    @abstractmethod
    async def get_active_orders(self, user_id: str) -> List[OrderDTO]:
        """获取活跃订单"""
        pass
    
    @abstractmethod
    async def get_orders_by_symbol(self, user_id: str, symbol: str) -> List[OrderDTO]:
        """根据交易对获取订单"""
        pass
    
    @abstractmethod
    async def get_trades_by_symbol(self, user_id: str, symbol: str) -> List[TradeDTO]:
        """根据交易对获取交易记录"""
        pass
