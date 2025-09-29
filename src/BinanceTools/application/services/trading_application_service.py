"""
交易应用服务

协调交易相关的用例和领域服务。
"""

from typing import List, Optional
from datetime import datetime

from ..use_cases.get_wallet_balance import GetWalletBalanceUseCase
from ..use_cases.place_order import PlaceOrderUseCase
from ..use_cases.cancel_order import CancelOrderUseCase
from ..use_cases.get_trading_volume import GetTradingVolumeUseCase
from ..use_cases.get_order_history import GetOrderHistoryUseCase
from ..use_cases.get_trade_history import GetTradeHistoryUseCase
from ..dto.wallet_dto import WalletDTO
from ..dto.order_dto import OrderDTO, PlaceOrderRequestDTO
from ..dto.trade_dto import TradeDTO, TradingVolumeDTO


class TradingApplicationService:
    """交易应用服务"""
    
    def __init__(
        self,
        get_wallet_balance_use_case: GetWalletBalanceUseCase,
        place_order_use_case: PlaceOrderUseCase,
        cancel_order_use_case: CancelOrderUseCase,
        get_trading_volume_use_case: GetTradingVolumeUseCase,
        get_order_history_use_case: GetOrderHistoryUseCase,
        get_trade_history_use_case: GetTradeHistoryUseCase
    ):
        """初始化应用服务"""
        self.get_wallet_balance_use_case = get_wallet_balance_use_case
        self.place_order_use_case = place_order_use_case
        self.cancel_order_use_case = cancel_order_use_case
        self.get_trading_volume_use_case = get_trading_volume_use_case
        self.get_order_history_use_case = get_order_history_use_case
        self.get_trade_history_use_case = get_trade_history_use_case
    
    async def get_wallet_balance(self, user_id: str) -> Optional[WalletDTO]:
        """获取钱包余额"""
        return await self.get_wallet_balance_use_case.execute(user_id)
    
    async def place_buy_order(
        self,
        user_id: str,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> OrderDTO:
        """下买单"""
        request = PlaceOrderRequestDTO(
            user_id=user_id,
            symbol=symbol,
            side="BUY",
            quantity=quantity,
            price=price,
            time_in_force=time_in_force
        )
        return await self.place_order_use_case.execute(request)
    
    async def place_sell_order(
        self,
        user_id: str,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> OrderDTO:
        """下卖单"""
        request = PlaceOrderRequestDTO(
            user_id=user_id,
            symbol=symbol,
            side="SELL",
            quantity=quantity,
            price=price,
            time_in_force=time_in_force
        )
        return await self.place_order_use_case.execute(request)
    
    async def cancel_order(self, user_id: str, order_id: int) -> Optional[OrderDTO]:
        """取消订单"""
        return await self.cancel_order_use_case.execute(user_id, order_id)
    
    async def get_trading_volume(self, user_id: str) -> TradingVolumeDTO:
        """获取交易量"""
        return await self.get_trading_volume_use_case.execute(user_id)
    
    async def get_order_history(
        self,
        user_id: str,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[OrderDTO]:
        """获取订单历史"""
        return await self.get_order_history_use_case.execute(
            user_id, symbol, start_date, end_date, limit
        )
    
    async def get_trade_history(
        self,
        user_id: str,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[TradeDTO]:
        """获取交易历史"""
        return await self.get_trade_history_use_case.execute(
            user_id, symbol, start_date, end_date, limit
        )
    
    async def get_active_orders(self, user_id: str) -> List[OrderDTO]:
        """获取活跃订单"""
        orders = await self.get_order_history_use_case.execute(user_id)
        return [order for order in orders if order.is_active]
    
    async def get_orders_by_symbol(self, user_id: str, symbol: str) -> List[OrderDTO]:
        """根据交易对获取订单"""
        return await self.get_order_history_use_case.execute(user_id, symbol)
    
    async def get_trades_by_symbol(self, user_id: str, symbol: str) -> List[TradeDTO]:
        """根据交易对获取交易记录"""
        return await self.get_trade_history_use_case.execute(user_id, symbol)
