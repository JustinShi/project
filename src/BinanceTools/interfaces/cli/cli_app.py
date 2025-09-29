"""
CLI应用

命令行应用主程序。
"""

import asyncio
import click
from typing import Optional

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
from .commands import Commands


class CliApp:
    """CLI应用"""
    
    def __init__(self):
        """初始化CLI应用"""
        self.trading_service = None
        self.portfolio_service = None
        self.commands = None
    
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
            
            # 初始化命令
            self.commands = Commands(self.trading_service, self.portfolio_service)
            
        except Exception as e:
            click.echo(f"初始化失败: {e}")
            raise
    
    async def run(self):
        """运行应用"""
        await self.initialize()
        
        # 创建CLI命令组
        @click.group()
        def cli():
            """币安Alpha代币自动交易工具"""
            pass
        
        # 添加命令
        cli.add_command(self.commands.wallet)
        cli.add_command(self.commands.order)
        cli.add_command(self.commands.trade)
        cli.add_command(self.commands.portfolio)
        cli.add_command(self.commands.config)
        
        # 运行CLI
        cli()
    
    async def cleanup(self):
        """清理资源"""
        if self.trading_service:
            # 清理HTTP会话
            pass
