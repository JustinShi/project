"""精度值对象"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Precision:
    """精度值对象
    
    不可变的精度表示，用于价格和数量的格式化
    """

    trade_decimal: int  # 交易精度（价格小数位数）
    token_decimal: int  # 代币精度（数量小数位数）

    def __post_init__(self) -> None:
        """验证精度值的有效性"""
        if not 0 <= self.trade_decimal <= 18:
            raise ValueError(f"交易精度必须在0-18之间: {self.trade_decimal}")
        
        if not 0 <= self.token_decimal <= 18:
            raise ValueError(f"代币精度必须在0-18之间: {self.token_decimal}")

    def __str__(self) -> str:
        return f"Precision(trade={self.trade_decimal}, token={self.token_decimal})"

