"""订单ID值对象"""

from typing import Optional


class OrderId:
    """订单ID值对象"""
    
    def __init__(self, value: str):
        if not value or not value.strip():
            raise ValueError("Order ID cannot be empty")
        
        self.value = value.strip()
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"OrderId('{self.value}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, OrderId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def is_empty(self) -> bool:
        """是否为空"""
        return not self.value
    
    @classmethod
    def from_string(cls, value: Optional[str]) -> Optional['OrderId']:
        """从字符串创建OrderId"""
        if not value or not value.strip():
            return None
        return cls(value.strip())
