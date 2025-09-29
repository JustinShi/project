"""
投资组合接口

定义投资组合相关的应用接口。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from decimal import Decimal

from ...domain.aggregates.portfolio import Position


class PortfolioInterface(ABC):
    """投资组合接口"""
    
    @abstractmethod
    async def get_positions(self, user_id: str) -> List[Position]:
        """获取持仓信息"""
        pass
    
    @abstractmethod
    async def get_position_by_symbol(self, user_id: str, symbol: str) -> Optional[Position]:
        """根据交易对获取持仓"""
        pass
    
    @abstractmethod
    async def get_performance_summary(self, user_id: str) -> Dict[str, any]:
        """获取业绩摘要"""
        pass
    
    @abstractmethod
    async def get_asset_allocation(self, user_id: str) -> Dict[str, Decimal]:
        """获取资产配置"""
        pass
    
    @abstractmethod
    async def get_top_positions(self, user_id: str, limit: int = 10) -> List[Position]:
        """获取持仓最大的前N个"""
        pass
    
    @abstractmethod
    async def get_top_gainers(self, user_id: str, limit: int = 10) -> List[Position]:
        """获取涨幅最大的前N个"""
        pass
    
    @abstractmethod
    async def get_top_losers(self, user_id: str, limit: int = 10) -> List[Position]:
        """获取跌幅最大的前N个"""
        pass
    
    @abstractmethod
    async def get_pnl_analysis(self, user_id: str) -> Dict[str, any]:
        """获取盈亏分析"""
        pass
    
    @abstractmethod
    async def get_risk_metrics(self, user_id: str) -> Dict[str, any]:
        """获取风险指标"""
        pass
