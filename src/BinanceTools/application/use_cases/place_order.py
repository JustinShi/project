"""
下单用例

创建新的交易订单。
"""

from typing import Optional
from decimal import Decimal

from ...domain.entities.order import Order, OrderSide, OrderType, OrderTimeInForce
from ...domain.entities.wallet import Wallet
from ...domain.value_objects.symbol import Symbol
from ...domain.repositories.order_repository import OrderRepository
from ...domain.repositories.wallet_repository import WalletRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.trading_service import TradingService
from ...domain.services.risk_service import RiskService
from ..dto.order_dto import OrderDTO, PlaceOrderRequestDTO


class PlaceOrderUseCase:
    """下单用例"""
    
    def __init__(
        self,
        order_repository: OrderRepository,
        wallet_repository: WalletRepository,
        user_repository: UserRepository,
        trading_service: TradingService,
        risk_service: RiskService
    ):
        """初始化用例"""
        self.order_repository = order_repository
        self.wallet_repository = wallet_repository
        self.user_repository = user_repository
        self.trading_service = trading_service
        self.risk_service = risk_service
    
    async def execute(self, request: PlaceOrderRequestDTO) -> OrderDTO:
        """执行用例"""
        # 检查用户是否存在
        user = await self.user_repository.get_by_id(request.user_id)
        if not user:
            raise ValueError(f"用户不存在: {request.user_id}")
        
        if not user.is_active():
            raise ValueError(f"用户未激活: {request.user_id}")
        
        # 获取钱包信息
        wallet = await self.wallet_repository.get_by_user_id(request.user_id)
        if not wallet:
            raise ValueError(f"钱包不存在: {request.user_id}")
        
        # 创建交易对
        symbol = Symbol.from_string(request.symbol)
        
        # 验证订单参数
        if not self.trading_service.validate_order_parameters(
            symbol, request.quantity, request.price
        ):
            raise ValueError("订单参数无效")
        
        # 风险检查
        if self.risk_service.should_reject_order(
            wallet, symbol, request.quantity, request.price, []
        ):
            raise ValueError("订单被风险控制系统拒绝")
        
        # 创建订单
        if request.side == "BUY":
            order = self.trading_service.create_buy_order(
                request.user_id,
                symbol,
                request.quantity,
                request.price,
                OrderTimeInForce(request.time_in_force)
            )
        else:
            order = self.trading_service.create_sell_order(
                request.user_id,
                symbol,
                request.quantity,
                request.price,
                OrderTimeInForce(request.time_in_force)
            )
        
        # 保存订单
        saved_order = await self.order_repository.save(order)
        
        # 转换为DTO
        return OrderDTO.from_entity(saved_order)
