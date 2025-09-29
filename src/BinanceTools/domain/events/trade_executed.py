"""
交易执行事件

当交易被执行时触发。
"""

from dataclasses import dataclass
from datetime import datetime

from ..entities.trade import Trade


@dataclass
class TradeExecuted:
    """交易执行事件"""
    
    trade: Trade
    timestamp: datetime
    event_id: str
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.trade:
            raise ValueError("交易不能为空")
        if not self.timestamp:
            raise ValueError("时间戳不能为空")
        if not self.event_id:
            raise ValueError("事件ID不能为空")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "event_type": "TradeExecuted",
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "trade": self.trade.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TradeExecuted":
        """从字典创建事件"""
        return cls(
            trade=Trade.from_dict(data["trade"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            event_id=data["event_id"]
        )
