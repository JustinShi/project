"""
SDK客户端

Python SDK客户端。
"""

import asyncio
from typing import Optional, List
from datetime import datetime

from ...application.services.trading_application_service import TradingApplicationService
from ...application.services.portfolio_application_service import PortfolioApplicationService
from ...application.dto.wallet_dto import WalletDTO
from ...application.dto.order_dto import OrderDTO, PlaceOrderRequestDTO
from ...application.dto.trade_dto import TradeDTO, TradingVolumeDTO
from .sdk_config import SdkConfig


class SdkClient:
    """SDK客户端"""
    
    def __init__(self, config: SdkConfig):
        """初始化SDK客户端"""
        self.config = config
        self.trading_service = None
        self.portfolio_service = None
        self._initialized = False
    
    async def initialize(self):
        """初始化客户端"""
        if self._initialized:
            return
        
        try:
            # 初始化配置
            user_config = self.config.get_user_config()
            api_config = self.config.get_api_config()
            proxy_config = self.config.get_proxy_config()
            
            # 初始化HTTP适配器
            from ...infrastructure.adapters.http_adapter import HttpAdapter
            http_adapter = HttpAdapter(proxy_config, user_config)
            
            # 初始化API客户端
            from ...infrastructure.external_services.binance_api_client import BinanceApiClient
            api_client = BinanceApiClient(api_config, http_adapter)
            
            # 初始化仓储
            from ...infrastructure.repositories.binance_user_repository import BinanceUserRepository
            from ...infrastructure.repositories.binance_wallet_repository import BinanceWalletRepository
            from ...infrastructure.repositories.binance_order_repository import BinanceOrderRepository
            from ...infrastructure.repositories.binance_trade_repository import BinanceTradeRepository
            
            user_repository = BinanceUserRepository(user_config)
            wallet_repository = BinanceWalletRepository(api_client)
            order_repository = BinanceOrderRepository(api_client)
            trade_repository = BinanceTradeRepository(api_client)
            
            # 初始化领域服务
            from ...domain.services.trading_service import TradingService
            from ...domain.services.risk_service import RiskService
            
            trading_service = TradingService()
            risk_service = RiskService()
            
            # 初始化应用服务
            self.trading_service = TradingApplicationService(
                user_repository=user_repository,
                wallet_repository=wallet_repository,
                order_repository=order_repository,
                trade_repository=trade_repository,
                trading_service=trading_service,
                risk_service=risk_service
            )
            
            self.portfolio_service = PortfolioApplicationService(
                trade_repository=trade_repository,
                wallet_repository=wallet_repository,
                user_repository=user_repository
            )
            
            self._initialized = True
            
        except Exception as e:
            raise Exception(f"SDK初始化失败: {e}")
    
    async def get_wallet_balance(self, user_id: str) -> Optional[WalletDTO]:
        """获取钱包余额"""
        await self.initialize()
        return await self.trading_service.get_wallet_balance(user_id)
    
    async def place_buy_order(
        self,
        user_id: str,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> OrderDTO:
        """下买单"""
        await self.initialize()
        return await self.trading_service.place_buy_order(user_id, symbol, quantity, price, time_in_force)
    
    async def place_sell_order(
        self,
        user_id: str,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> OrderDTO:
        """下卖单"""
        await self.initialize()
        return await self.trading_service.place_sell_order(user_id, symbol, quantity, price, time_in_force)
    
    async def cancel_order(self, user_id: str, order_id: int) -> Optional[OrderDTO]:
        """取消订单"""
        await self.initialize()
        return await self.trading_service.cancel_order(user_id, order_id)
    
    async def get_order_history(
        self,
        user_id: str,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[OrderDTO]:
        """获取订单历史"""
        await self.initialize()
        return await self.trading_service.get_order_history(user_id, symbol, start_date, end_date, limit)
    
    async def get_active_orders(self, user_id: str) -> List[OrderDTO]:
        """获取活跃订单"""
        await self.initialize()
        return await self.trading_service.get_active_orders(user_id)
    
    async def get_trade_history(
        self,
        user_id: str,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[TradeDTO]:
        """获取交易历史"""
        await self.initialize()
        return await self.trading_service.get_trade_history(user_id, symbol, start_date, end_date, limit)
    
    async def get_trading_volume(self, user_id: str) -> TradingVolumeDTO:
        """获取交易量"""
        await self.initialize()
        return await self.trading_service.get_trading_volume(user_id)
    
    async def get_portfolio_summary(self, user_id: str) -> dict:
        """获取投资组合摘要"""
        await self.initialize()
        return await self.portfolio_service.get_performance_summary(user_id)
    
    async def get_positions(self, user_id: str, limit: int = 10) -> List:
        """获取持仓列表"""
        await self.initialize()
        return await self.portfolio_service.get_top_positions(user_id, limit)
    
    async def get_asset_allocation(self, user_id: str) -> dict:
        """获取资产配置"""
        await self.initialize()
        return await self.portfolio_service.get_asset_allocation(user_id)
    
    async def get_pnl_analysis(self, user_id: str) -> dict:
        """获取盈亏分析"""
        await self.initialize()
        return await self.portfolio_service.get_pnl_analysis(user_id)
    
    async def get_risk_metrics(self, user_id: str) -> dict:
        """获取风险指标"""
        await self.initialize()
        return await self.portfolio_service.get_risk_metrics(user_id)
    
    async def close(self):
        """关闭客户端"""
        if self.trading_service:
            # 清理资源
            pass
        self._initialized = False
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
