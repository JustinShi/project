"""
API应用

REST API应用主程序。
"""

import asyncio
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn

from ...application.services.trading_application_service import TradingApplicationService
from ...application.services.portfolio_application_service import PortfolioApplicationService
from ...infrastructure.config.user_config import UserConfig
from ...infrastructure.config.api_config import ApiConfig
from ...infrastructure.config.proxy_config import ProxyConfig
from ...infrastructure.adapters.http_adapter import HttpAdapter
from ...infrastructure.external_services.binance_api_client import BinanceApiClient
from ...infrastructure.repositories.binance_user_repository import BinanceUserRepository
from ...infrastructure.repositories.binance_wallet_repository import BinanceWalletRepository
from ...infrastructure.repositories.binance_order_repository import BinanceOrderRepository
from ...infrastructure.repositories.binance_trade_repository import BinanceTradeRepository
from ...domain.services.trading_service import TradingService
from ...domain.services.risk_service import RiskService
from .routes import Routes


class ApiApp:
    """API应用"""
    
    def __init__(self):
        """初始化API应用"""
        self.app = FastAPI(
            title="币安Alpha代币自动交易工具",
            description="基于DDD架构的币安Alpha代币自动交易工具API",
            version="1.0.0"
        )
        
        self.trading_service = None
        self.portfolio_service = None
        self.routes = None
        
        # 配置CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 添加异常处理器
        self.app.add_exception_handler(Exception, self.exception_handler)
    
    async def initialize(self):
        """初始化应用"""
        try:
            # 初始化配置
            user_config = UserConfig()
            api_config = ApiConfig()
            proxy_config = ProxyConfig()
            
            # 初始化HTTP适配器
            http_adapter = HttpAdapter(proxy_config, user_config)
            
            # 初始化API客户端
            api_client = BinanceApiClient(api_config, http_adapter)
            
            # 初始化仓储
            user_repository = BinanceUserRepository(user_config)
            wallet_repository = BinanceWalletRepository(api_client)
            order_repository = BinanceOrderRepository(api_client)
            trade_repository = BinanceTradeRepository(api_client)
            
            # 初始化领域服务
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
            
            # 初始化路由
            self.routes = Routes(self.trading_service, self.portfolio_service)
            
            # 注册路由
            self.app.include_router(self.routes.router, prefix="/api/v1")
            
        except Exception as e:
            print(f"初始化失败: {e}")
            raise
    
    async def exception_handler(self, request, exc):
        """异常处理器"""
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "details": {}
            }
        )
    
    async def run(self, host: str = "0.0.0.0", port: int = 8000):
        """运行应用"""
        await self.initialize()
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    async def cleanup(self):
        """清理资源"""
        if self.trading_service:
            # 清理HTTP会话
            pass
