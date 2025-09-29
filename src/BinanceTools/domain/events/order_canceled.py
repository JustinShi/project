"""
订单取消事件

当订单被取消时触发。
"""

from dataclasses import dataclass
from datetime import datetime

from ..entities.order import Order


@dataclass
class OrderCanceled:
    """订单取消事件"""
    
    order: Order
    timestamp: datetime
    event_id: str
    reason: str = "用户取消"
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.order:
            raise ValueError("订单不能为空")
        if not self.timestamp:
            raise ValueError("时间戳不能为空")
        if not self.event_id:
            raise ValueError("事件ID不能为空")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "event_type": "OrderCanceled",
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "order": self.order.to_dict(),
            "reason": self.reason
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "OrderCanceled":
        """从字典创建事件"""
        return cls(
            order=Order.from_dict(data["order"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            event_id=data["event_id"],
            reason=data.get("reason", "用户取消")
        )
