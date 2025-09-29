"""
时间戳值对象

表示时间戳，包含时间信息。
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Union


@dataclass(frozen=True)
class Timestamp:
    """时间戳值对象"""
    
    value: datetime
    
    def __post_init__(self):
        """初始化后处理"""
        if not isinstance(self.value, datetime):
            raise TypeError("时间戳必须是datetime对象")
    
    def __str__(self) -> str:
        """字符串表示"""
        return self.value.isoformat()
    
    def __eq__(self, other: "Timestamp") -> bool:
        """相等比较"""
        if not isinstance(other, Timestamp):
            return False
        return self.value == other.value
    
    def __lt__(self, other: "Timestamp") -> bool:
        """小于比较"""
        if not isinstance(other, Timestamp):
            raise TypeError("只能与Timestamp对象比较")
        return self.value < other.value
    
    def __le__(self, other: "Timestamp") -> bool:
        """小于等于比较"""
        return self < other or self == other
    
    def __gt__(self, other: "Timestamp") -> bool:
        """大于比较"""
        return not self <= other
    
    def __ge__(self, other: "Timestamp") -> bool:
        """大于等于比较"""
        return not self < other
    
    def to_utc(self) -> "Timestamp":
        """转换为UTC时间"""
        if self.value.tzinfo is None:
            # 如果没有时区信息，假设为UTC
            utc_value = self.value.replace(tzinfo=timezone.utc)
        else:
            utc_value = self.value.astimezone(timezone.utc)
        return Timestamp(utc_value)
    
    def to_timestamp(self) -> float:
        """转换为Unix时间戳"""
        return self.value.timestamp()
    
    def to_milliseconds(self) -> int:
        """转换为毫秒时间戳"""
        return int(self.value.timestamp() * 1000)
    
    def to_iso_string(self) -> str:
        """转换为ISO字符串"""
        return self.value.isoformat()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "value": self.value.isoformat(),
            "timestamp": self.to_timestamp(),
            "milliseconds": self.to_milliseconds()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Timestamp":
        """从字典创建Timestamp对象"""
        if "value" in data:
            return cls(datetime.fromisoformat(data["value"]))
        elif "timestamp" in data:
            return cls(datetime.fromtimestamp(data["timestamp"]))
        elif "milliseconds" in data:
            return cls(datetime.fromtimestamp(data["milliseconds"] / 1000))
        else:
            raise ValueError("无效的时间戳数据")
    
    @classmethod
    def now(cls) -> "Timestamp":
        """创建当前时间戳"""
        return cls(datetime.utcnow())
    
    @classmethod
    def from_timestamp(cls, timestamp: Union[int, float]) -> "Timestamp":
        """从Unix时间戳创建"""
        if timestamp > 1e10:  # 毫秒时间戳
            timestamp = timestamp / 1000
        return cls(datetime.fromtimestamp(timestamp))
    
    @classmethod
    def from_iso_string(cls, iso_string: str) -> "Timestamp":
        """从ISO字符串创建"""
        return cls(datetime.fromisoformat(iso_string))
    
    @classmethod
    def from_datetime(cls, dt: datetime) -> "Timestamp":
        """从datetime对象创建"""
        return cls(dt)
