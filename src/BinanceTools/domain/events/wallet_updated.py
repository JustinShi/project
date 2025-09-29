"""
钱包更新事件

当钱包余额发生变化时触发。
"""

from dataclasses import dataclass
from datetime import datetime

from ..entities.wallet import Wallet


@dataclass
class WalletUpdated:
    """钱包更新事件"""
    
    wallet: Wallet
    timestamp: datetime
    event_id: str
    change_type: str  # "DEPOSIT", "WITHDRAWAL", "TRADE", "FEE"
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.wallet:
            raise ValueError("钱包不能为空")
        if not self.timestamp:
            raise ValueError("时间戳不能为空")
        if not self.event_id:
            raise ValueError("事件ID不能为空")
        if not self.change_type:
            raise ValueError("变更类型不能为空")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "event_type": "WalletUpdated",
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "wallet": self.wallet.to_dict(),
            "change_type": self.change_type
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "WalletUpdated":
        """从字典创建事件"""
        return cls(
            wallet=Wallet.from_dict(data["wallet"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            event_id=data["event_id"],
            change_type=data["change_type"]
        )
