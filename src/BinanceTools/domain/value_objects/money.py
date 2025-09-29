"""
金额值对象

表示货币金额，包含数值和货币类型。
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Union


@dataclass(frozen=True)
class Money:
    """金额值对象"""
    
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        """初始化后处理"""
        if self.amount < 0:
            raise ValueError("金额不能为负数")
        if not self.currency:
            raise ValueError("货币类型不能为空")
    
    def __add__(self, other: "Money") -> "Money":
        """加法运算"""
        if not isinstance(other, Money):
            raise TypeError("只能与Money对象相加")
        if self.currency != other.currency:
            raise ValueError("不同货币类型不能相加")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: "Money") -> "Money":
        """减法运算"""
        if not isinstance(other, Money):
            raise TypeError("只能与Money对象相减")
        if self.currency != other.currency:
            raise ValueError("不同货币类型不能相减")
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("减法结果不能为负数")
        return Money(result_amount, self.currency)
    
    def __mul__(self, multiplier: Union[Decimal, int, float]) -> "Money":
        """乘法运算"""
        if not isinstance(multiplier, (Decimal, int, float)):
            raise TypeError("乘数必须是数字类型")
        return Money(self.amount * Decimal(str(multiplier)), self.currency)
    
    def __truediv__(self, divisor: Union[Decimal, int, float]) -> "Money":
        """除法运算"""
        if not isinstance(divisor, (Decimal, int, float)):
            raise TypeError("除数必须是数字类型")
        if divisor == 0:
            raise ValueError("除数不能为零")
        return Money(self.amount / Decimal(str(divisor)), self.currency)
    
    def __eq__(self, other: "Money") -> bool:
        """相等比较"""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other: "Money") -> bool:
        """小于比较"""
        if not isinstance(other, Money):
            raise TypeError("只能与Money对象比较")
        if self.currency != other.currency:
            raise ValueError("不同货币类型不能比较")
        return self.amount < other.amount
    
    def __le__(self, other: "Money") -> bool:
        """小于等于比较"""
        return self < other or self == other
    
    def __gt__(self, other: "Money") -> bool:
        """大于比较"""
        return not self <= other
    
    def __ge__(self, other: "Money") -> bool:
        """大于等于比较"""
        return not self < other
    
    def is_zero(self) -> bool:
        """是否为零"""
        return self.amount == 0
    
    def is_positive(self) -> bool:
        """是否为正数"""
        return self.amount > 0
    
    def to_decimal(self) -> Decimal:
        """转换为Decimal"""
        return self.amount
    
    def to_float(self) -> float:
        """转换为float"""
        return float(self.amount)
    
    def to_string(self, precision: int = 8) -> str:
        """转换为字符串"""
        return f"{self.amount:.{precision}f} {self.currency}"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "amount": str(self.amount),
            "currency": self.currency
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Money":
        """从字典创建Money对象"""
        return cls(
            amount=Decimal(data["amount"]),
            currency=data["currency"]
        )
    
    @classmethod
    def zero(cls, currency: str) -> "Money":
        """创建零金额"""
        return cls(Decimal('0'), currency)
    
    @classmethod
    def usdt(cls, amount: Union[Decimal, int, float, str]) -> "Money":
        """创建USDT金额"""
        return cls(Decimal(str(amount)), "USDT")
    
    @classmethod
    def bnb(cls, amount: Union[Decimal, int, float, str]) -> "Money":
        """创建BNB金额"""
        return cls(Decimal(str(amount)), "BNB")
