"""
API路由

REST API路由定义。
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from ...application.services.trading_application_service import TradingApplicationService
from ...application.services.portfolio_application_service import PortfolioApplicationService
from ...application.dto.wallet_dto import WalletDTO
from ...application.dto.order_dto import OrderDTO, PlaceOrderRequestDTO
from ...application.dto.trade_dto import TradeDTO, TradingVolumeDTO


class Routes:
    """API路由"""
    
    def __init__(
        self,
        trading_service: TradingApplicationService,
        portfolio_service: PortfolioApplicationService
    ):
        """初始化路由"""
        self.trading_service = trading_service
        self.portfolio_service = portfolio_service
        self.router = APIRouter()
        
        # 注册路由
        self._register_routes()
    
    def _register_routes(self):
        """注册路由"""
        
        # 钱包相关路由
        @self.router.get("/wallet/{user_id}/balance", response_model=WalletDTO)
        async def get_wallet_balance(user_id: str):
            """获取钱包余额"""
            try:
                wallet = await self.trading_service.get_wallet_balance(user_id)
                if not wallet:
                    raise HTTPException(status_code=404, detail="钱包不存在")
                return wallet
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # 订单相关路由
        @self.router.post("/orders", response_model=OrderDTO)
        async def place_order(request: PlaceOrderRequestDTO):
            """下单"""
            try:
                order = await self.trading_service.place_order(request)
                return order
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/orders/{order_id}/cancel", response_model=OrderDTO)
        async def cancel_order(order_id: int, user_id: str = Query(...)):
            """取消订单"""
            try:
                order = await self.trading_service.cancel_order(user_id, order_id)
                if not order:
                    raise HTTPException(status_code=404, detail="订单不存在")
                return order
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/orders", response_model=List[OrderDTO])
        async def get_orders(
            user_id: str = Query(...),
            symbol: Optional[str] = Query(None),
            start_date: Optional[datetime] = Query(None),
            end_date: Optional[datetime] = Query(None),
            limit: int = Query(100, ge=1, le=1000)
        ):
            """获取订单列表"""
            try:
                orders = await self.trading_service.get_order_history(
                    user_id, symbol, start_date, end_date, limit
                )
                return orders
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/orders/active", response_model=List[OrderDTO])
        async def get_active_orders(user_id: str = Query(...)):
            """获取活跃订单"""
            try:
                orders = await self.trading_service.get_active_orders(user_id)
                return orders
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # 交易相关路由
        @self.router.get("/trades", response_model=List[TradeDTO])
        async def get_trades(
            user_id: str = Query(...),
            symbol: Optional[str] = Query(None),
            start_date: Optional[datetime] = Query(None),
            end_date: Optional[datetime] = Query(None),
            limit: int = Query(100, ge=1, le=1000)
        ):
            """获取交易历史"""
            try:
                trades = await self.trading_service.get_trade_history(
                    user_id, symbol, start_date, end_date, limit
                )
                return trades
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/trades/volume", response_model=TradingVolumeDTO)
        async def get_trading_volume(user_id: str = Query(...)):
            """获取交易量"""
            try:
                volume = await self.trading_service.get_trading_volume(user_id)
                return volume
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # 投资组合相关路由
        @self.router.get("/portfolio/{user_id}/summary")
        async def get_portfolio_summary(user_id: str):
            """获取投资组合摘要"""
            try:
                summary = await self.portfolio_service.get_performance_summary(user_id)
                return summary
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/portfolio/{user_id}/positions")
        async def get_positions(
            user_id: str,
            limit: int = Query(10, ge=1, le=100)
        ):
            """获取持仓列表"""
            try:
                positions = await self.portfolio_service.get_top_positions(user_id, limit)
                return positions
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/portfolio/{user_id}/allocation")
        async def get_asset_allocation(user_id: str):
            """获取资产配置"""
            try:
                allocation = await self.portfolio_service.get_asset_allocation(user_id)
                return allocation
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/portfolio/{user_id}/pnl")
        async def get_pnl_analysis(user_id: str):
            """获取盈亏分析"""
            try:
                pnl = await self.portfolio_service.get_pnl_analysis(user_id)
                return pnl
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/portfolio/{user_id}/risk")
        async def get_risk_metrics(user_id: str):
            """获取风险指标"""
            try:
                risk = await self.portfolio_service.get_risk_metrics(user_id)
                return risk
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # 健康检查路由
        @self.router.get("/health")
        async def health_check():
            """健康检查"""
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
        
        # 信息路由
        @self.router.get("/info")
        async def get_info():
            """获取API信息"""
            return {
                "name": "币安Alpha代币自动交易工具",
                "version": "1.0.0",
                "description": "基于DDD架构的币安Alpha代币自动交易工具API",
                "author": "BinanceTools Team"
            }
