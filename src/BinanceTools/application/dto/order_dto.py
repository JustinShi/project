"""
订单DTO

订单相关的数据传输对象。
"""

from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from ...domain.entities.order import Order, OrderSide, OrderType, OrderStatus, OrderTimeInForce, PaymentDetail


@dataclass
class PaymentDetailDTO:
    """支付详情DTO"""
    
    amount: Decimal
    payment_wallet_type: str
    
    @classmethod
    def from_entity(cls, payment_detail: PaymentDetail) -> "PaymentDetailDTO":
        """从实体创建DTO"""
        return cls(
            amount=payment_detail.amount,
            payment_wallet_type=payment_detail.payment_wallet_type
        )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "amount": str(self.amount),
            "payment_wallet_type": self.payment_wallet_type
        }


@dataclass
class OrderDTO:
    """订单DTO"""
    
    order_id: int
    user_id: str
    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Decimal
    status: str
    time_in_force: str
    working_order_id: Optional[int] = None
    pending_order_id: Optional[int] = None
    working_price: Optional[Decimal] = None
    pending_price: Optional[Decimal] = None
    payment_details: Optional[List[PaymentDetailDTO]] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    @property
    def is_buy_order(self) -> bool:
        """是否为买单"""
        return self.side == "BUY"
    
    @property
    def is_sell_order(self) -> bool:
        """是否为卖单"""
        return self.side == "SELL"
    
    @property
    def is_active(self) -> bool:
        """订单是否活跃"""
        return self.status in ["NEW", "PENDING", "PARTIALLY_FILLED"]
    
    @property
    def is_filled(self) -> bool:
        """订单是否已成交"""
        return self.status == "FILLED"
    
    @property
    def is_canceled(self) -> bool:
        """订单是否已取消"""
        return self.status == "CANCELED"
    
    def calculate_total_value(self) -> Decimal:
        """计算订单总价值"""
        return self.quantity * self.price
    
    @classmethod
    def from_entity(cls, order: Order) -> "OrderDTO":
        """从实体创建DTO"""
        payment_details = None
        if order.payment_details:
            payment_details = [
                PaymentDetailDTO.from_entity(pd) for pd in order.payment_details
            ]
        
        return cls(
            order_id=order.order_id,
            user_id=order.user_id,
            symbol=str(order.symbol),
            side=order.side.value,
            order_type=order.order_type.value,
            quantity=order.quantity,
            price=order.price,
            status=order.status.value,
            time_in_force=order.time_in_force.value,
            working_order_id=order.working_order_id,
            pending_order_id=order.pending_order_id,
            working_price=order.working_price,
            pending_price=order.pending_price,
            payment_details=payment_details,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "quantity": str(self.quantity),
            "price": str(self.price),
            "status": self.status,
            "time_in_force": self.time_in_force,
            "working_order_id": self.working_order_id,
            "pending_order_id": self.pending_order_id,
            "working_price": str(self.working_price) if self.working_price else None,
            "pending_price": str(self.pending_price) if self.pending_price else None,
            "payment_details": [
                pd.to_dict() for pd in (self.payment_details or [])
            ],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class PlaceOrderRequestDTO:
    """下单请求DTO"""
    
    user_id: str
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    time_in_force: str = "GTC"
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.user_id:
            raise ValueError("用户ID不能为空")
        if not self.symbol:
            raise ValueError("交易对不能为空")
        if self.side not in ["BUY", "SELL"]:
            raise ValueError("订单方向必须是BUY或SELL")
        if self.quantity <= 0:
            raise ValueError("订单数量必须大于0")
        if self.price <= 0:
            raise ValueError("订单价格必须大于0")
        if self.time_in_force not in ["GTC", "IOC", "FOK"]:
            raise ValueError("订单有效期无效")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": str(self.quantity),
            "price": str(self.price),
            "time_in_force": self.time_in_force
        }
