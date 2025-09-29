"""
订单实体

表示交易订单，包含订单状态和详情。
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from ..value_objects.money import Money
from ..value_objects.symbol import Symbol


class OrderSide(Enum):
    """订单方向"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """订单类型"""
    LIMIT = "LIMIT"
    MARKET = "MARKET"


class OrderStatus(Enum):
    """订单状态"""
    NEW = "NEW"
    PENDING = "PENDING"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


class OrderTimeInForce(Enum):
    """订单有效期"""
    GTC = "GTC"  # Good Till Cancel
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill


@dataclass
class PaymentDetail:
    """支付详情"""
    
    amount: Decimal
    payment_wallet_type: str  # CARD, WALLET, etc.


@dataclass
class Order:
    """订单实体"""
    
    order_id: int
    user_id: str
    symbol: Symbol
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Decimal
    status: OrderStatus
    time_in_force: OrderTimeInForce
    working_order_id: Optional[int] = None
    pending_order_id: Optional[int] = None
    working_price: Optional[Decimal] = None
    pending_price: Optional[Decimal] = None
    payment_details: Optional[List[PaymentDetail]] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.order_id:
            raise ValueError("订单ID不能为空")
        if not self.user_id:
            raise ValueError("用户ID不能为空")
        if self.quantity <= 0:
            raise ValueError("订单数量必须大于0")
        if self.price <= 0:
            raise ValueError("订单价格必须大于0")
        
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def is_buy_order(self) -> bool:
        """是否为买单"""
        return self.side == OrderSide.BUY
    
    def is_sell_order(self) -> bool:
        """是否为卖单"""
        return self.side == OrderSide.SELL
    
    def is_active(self) -> bool:
        """订单是否活跃"""
        return self.status in [OrderStatus.NEW, OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]
    
    def is_filled(self) -> bool:
        """订单是否已成交"""
        return self.status == OrderStatus.FILLED
    
    def is_canceled(self) -> bool:
        """订单是否已取消"""
        return self.status == OrderStatus.CANCELED
    
    def update_status(self, status: OrderStatus) -> None:
        """更新订单状态"""
        self.status = status
        self.updated_at = datetime.utcnow()
    
    def calculate_total_value(self) -> Decimal:
        """计算订单总价值"""
        return self.quantity * self.price
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "symbol": self.symbol.to_dict(),
            "side": self.side.value,
            "order_type": self.order_type.value,
            "quantity": str(self.quantity),
            "price": str(self.price),
            "status": self.status.value,
            "time_in_force": self.time_in_force.value,
            "working_order_id": self.working_order_id,
            "pending_order_id": self.pending_order_id,
            "working_price": str(self.working_price) if self.working_price else None,
            "pending_price": str(self.pending_price) if self.pending_price else None,
            "payment_details": [
                {
                    "amount": str(pd.amount),
                    "payment_wallet_type": pd.payment_wallet_type
                }
                for pd in (self.payment_details or [])
            ],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """从字典创建订单实体"""
        payment_details = None
        if data.get("payment_details"):
            payment_details = [
                PaymentDetail(
                    amount=Decimal(pd["amount"]),
                    payment_wallet_type=pd["payment_wallet_type"]
                )
                for pd in data["payment_details"]
            ]
        
        return cls(
            order_id=data["order_id"],
            user_id=data["user_id"],
            symbol=Symbol.from_dict(data["symbol"]),
            side=OrderSide(data["side"]),
            order_type=OrderType(data["order_type"]),
            quantity=Decimal(data["quantity"]),
            price=Decimal(data["price"]),
            status=OrderStatus(data["status"]),
            time_in_force=OrderTimeInForce(data["time_in_force"]),
            working_order_id=data.get("working_order_id"),
            pending_order_id=data.get("pending_order_id"),
            working_price=Decimal(data["working_price"]) if data.get("working_price") else None,
            pending_price=Decimal(data["pending_price"]) if data.get("pending_price") else None,
            payment_details=payment_details,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
