"""
获取交易量用例

获取用户的交易量信息。
"""

from typing import Dict
from decimal import Decimal

from ...domain.repositories.trade_repository import TradeRepository
from ...domain.repositories.user_repository import UserRepository
from ..dto.trade_dto import TradingVolumeDTO


class GetTradingVolumeUseCase:
    """获取交易量用例"""
    
    def __init__(
        self,
        trade_repository: TradeRepository,
        user_repository: UserRepository
    ):
        """初始化用例"""
        self.trade_repository = trade_repository
        self.user_repository = user_repository
    
    async def execute(self, user_id: str) -> TradingVolumeDTO:
        """执行用例"""
        # 检查用户是否存在
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"用户不存在: {user_id}")
        
        if not user.is_active():
            raise ValueError(f"用户未激活: {user_id}")
        
        # 获取24小时交易量
        volume_data = await self.trade_repository.get_24h_volume(user_id)
        
        # 转换为DTO
        return TradingVolumeDTO(
            user_id=user_id,
            total_volume=Decimal(str(volume_data.get("total_volume", 0))),
            volume_by_symbol=volume_data.get("volume_by_symbol", {})
        )
