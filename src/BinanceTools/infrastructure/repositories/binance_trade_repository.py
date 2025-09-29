"""
币安交易仓储实现

实现交易仓储接口，从币安API获取交易信息。
"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.trade import Trade
from ...domain.repositories.trade_repository import TradeRepository
from ...domain.value_objects.symbol import Symbol
from ..external_services.binance_api_client import BinanceApiClient


class BinanceTradeRepository(TradeRepository):
    """币安交易仓储实现"""
    
    def __init__(self, api_client: BinanceApiClient):
        """初始化仓储"""
        self.api_client = api_client
        self._trades_cache = {}
    
    async def get_by_id(self, trade_id: int) -> Optional[Trade]:
        """根据ID获取交易"""
        if trade_id in self._trades_cache:
            return self._trades_cache[trade_id]
        
        # 这里应该从API获取交易详情
        # 暂时返回None
        return None
    
    async def get_by_user_id(self, user_id: str) -> List[Trade]:
        """根据用户ID获取交易"""
        # 这里应该从API获取用户的所有交易
        # 暂时返回空列表
        return []
    
    async def get_by_order_id(self, order_id: int) -> List[Trade]:
        """根据订单ID获取交易"""
        # 这里应该从API获取指定订单的交易
        # 暂时返回空列表
        return []
    
    async def get_by_symbol(self, symbol: Symbol) -> List[Trade]:
        """根据交易对获取交易"""
        # 这里应该从API获取指定交易对的交易
        # 暂时返回空列表
        return []
    
    async def get_trades_by_date_range(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Trade]:
        """根据日期范围获取交易"""
        # 这里应该从API获取指定日期范围的交易
        # 暂时返回空列表
        return []
    
    async def get_24h_volume(self, user_id: str) -> dict:
        """获取24小时交易量"""
        try:
            # 从币安API获取24小时交易量
            volume_data = await self.api_client.get_user_volume(user_id)
            
            if not volume_data:
                return {"total_volume": 0, "volume_by_symbol": {}}
            
            return {
                "total_volume": volume_data.get("totalVolume", 0),
                "volume_by_symbol": {
                    item["tokenName"]: item["volume"]
                    for item in volume_data.get("tradeVolumeInfoList", [])
                }
            }
            
        except Exception as e:
            # 记录错误日志
            print(f"获取交易量失败: {e}")
            return {"total_volume": 0, "volume_by_symbol": {}}
    
    async def save(self, trade: Trade) -> Trade:
        """保存交易"""
        # 缓存交易
        self._trades_cache[trade.trade_id] = trade
        return trade
    
    async def update(self, trade: Trade) -> Trade:
        """更新交易"""
        # 缓存交易
        self._trades_cache[trade.trade_id] = trade
        return trade
    
    async def delete(self, trade_id: int) -> bool:
        """删除交易"""
        if trade_id in self._trades_cache:
            del self._trades_cache[trade_id]
            return True
        return False
    
    async def exists(self, trade_id: int) -> bool:
        """检查交易是否存在"""
        return trade_id in self._trades_cache
