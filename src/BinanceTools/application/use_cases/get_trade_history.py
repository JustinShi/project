"""
获取交易历史用例

获取用户的交易历史记录。
"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.trade import Trade
from ...domain.repositories.trade_repository import TradeRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.symbol import Symbol
from ..dto.trade_dto import TradeDTO


class GetTradeHistoryUseCase:
    """获取交易历史用例"""
    
    def __init__(
        self,
        trade_repository: TradeRepository,
        user_repository: UserRepository
    ):
        """初始化用例"""
        self.trade_repository = trade_repository
        self.user_repository = user_repository
    
    async def execute(
        self,
        user_id: str,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[TradeDTO]:
        """执行用例"""
        # 检查用户是否存在
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"用户不存在: {user_id}")
        
        if not user.is_active():
            raise ValueError(f"用户未激活: {user_id}")
        
        # 获取交易记录
        if start_date and end_date:
            trades = await self.trade_repository.get_trades_by_date_range(
                user_id, start_date, end_date
            )
        else:
            trades = await self.trade_repository.get_by_user_id(user_id)
        
        # 按交易对过滤
        if symbol:
            symbol_obj = Symbol.from_string(symbol)
            trades = [trade for trade in trades if trade.symbol == symbol_obj]
        
        # 限制数量
        trades = trades[:limit]
        
        # 转换为DTO
        return [TradeDTO.from_entity(trade) for trade in trades]
