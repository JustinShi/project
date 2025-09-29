"""
投资组合应用服务

协调投资组合相关的用例和领域服务。
"""

from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime

from ...domain.aggregates.portfolio import Portfolio, Position
from ...domain.repositories.trade_repository import TradeRepository
from ...domain.repositories.wallet_repository import WalletRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.symbol import Symbol


class PortfolioApplicationService:
    """投资组合应用服务"""
    
    def __init__(
        self,
        trade_repository: TradeRepository,
        wallet_repository: WalletRepository,
        user_repository: UserRepository
    ):
        """初始化应用服务"""
        self.trade_repository = trade_repository
        self.wallet_repository = wallet_repository
        self.user_repository = user_repository
    
    async def get_portfolio(self, user_id: str) -> Portfolio:
        """获取投资组合"""
        # 检查用户是否存在
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"用户不存在: {user_id}")
        
        if not user.is_active():
            raise ValueError(f"用户未激活: {user_id}")
        
        # 获取钱包信息
        wallet = await self.wallet_repository.get_by_user_id(user_id)
        if not wallet:
            raise ValueError(f"钱包不存在: {user_id}")
        
        # 获取交易记录
        trades = await self.trade_repository.get_by_user_id(user_id)
        
        # 创建投资组合
        portfolio = Portfolio(
            user_id=user_id,
            wallet=wallet,
            trades=trades
        )
        
        return portfolio
    
    async def get_positions(self, user_id: str) -> List[Position]:
        """获取持仓信息"""
        portfolio = await self.get_portfolio(user_id)
        return portfolio.positions
    
    async def get_position_by_symbol(self, user_id: str, symbol: str) -> Optional[Position]:
        """根据交易对获取持仓"""
        portfolio = await self.get_portfolio(user_id)
        symbol_obj = Symbol.from_string(symbol)
        return portfolio.get_position_by_symbol(symbol_obj)
    
    async def get_performance_summary(self, user_id: str) -> Dict[str, any]:
        """获取业绩摘要"""
        portfolio = await self.get_portfolio(user_id)
        return portfolio.get_performance_summary()
    
    async def get_asset_allocation(self, user_id: str) -> Dict[str, Decimal]:
        """获取资产配置"""
        portfolio = await self.get_portfolio(user_id)
        return portfolio.get_asset_allocation()
    
    async def get_top_positions(self, user_id: str, limit: int = 10) -> List[Position]:
        """获取持仓最大的前N个"""
        portfolio = await self.get_portfolio(user_id)
        return portfolio.get_top_positions(limit)
    
    async def get_top_gainers(self, user_id: str, limit: int = 10) -> List[Position]:
        """获取涨幅最大的前N个"""
        portfolio = await self.get_portfolio(user_id)
        return portfolio.get_top_gainers(limit)
    
    async def get_top_losers(self, user_id: str, limit: int = 10) -> List[Position]:
        """获取跌幅最大的前N个"""
        portfolio = await self.get_portfolio(user_id)
        return portfolio.get_top_losers(limit)
    
    async def get_pnl_analysis(self, user_id: str) -> Dict[str, any]:
        """获取盈亏分析"""
        portfolio = await self.get_portfolio(user_id)
        
        return {
            "total_market_value": str(portfolio.get_total_market_value()),
            "total_unrealized_pnl": str(portfolio.get_total_unrealized_pnl()),
            "total_realized_pnl": str(portfolio.get_total_realized_pnl()),
            "total_pnl": str(portfolio.get_total_pnl()),
            "pnl_percentage": str(portfolio.get_pnl_percentage()),
            "position_count": len(portfolio.positions),
            "winning_positions": len([p for p in portfolio.positions if p.total_pnl > 0]),
            "losing_positions": len([p for p in portfolio.positions if p.total_pnl < 0]),
            "break_even_positions": len([p for p in portfolio.positions if p.total_pnl == 0])
        }
    
    async def get_risk_metrics(self, user_id: str) -> Dict[str, any]:
        """获取风险指标"""
        portfolio = await self.get_portfolio(user_id)
        
        # 计算集中度风险
        asset_allocation = portfolio.get_asset_allocation()
        max_concentration = max(asset_allocation.values()) if asset_allocation else 0
        
        # 计算持仓数量
        position_count = len(portfolio.positions)
        
        # 计算平均持仓大小
        if position_count > 0:
            avg_position_size = portfolio.get_total_market_value() / position_count
        else:
            avg_position_size = 0
        
        return {
            "max_concentration": str(max_concentration),
            "position_count": position_count,
            "avg_position_size": str(avg_position_size),
            "diversification_score": min(100, position_count * 10),  # 简化的多样化评分
            "risk_level": self._calculate_risk_level(max_concentration, position_count)
        }
    
    def _calculate_risk_level(self, max_concentration: Decimal, position_count: int) -> str:
        """计算风险等级"""
        if max_concentration > 50 or position_count < 3:
            return "HIGH"
        elif max_concentration > 30 or position_count < 5:
            return "MEDIUM"
        else:
            return "LOW"
