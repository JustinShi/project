"""价格值对象"""

from decimal import Decimal, ROUND_DOWN
from typing import Union


class Price:
    """价格值对象
    
    不可变的价格表示，确保价格的有效性和精度控制
    """

    def __init__(self, value: Union[str, float, Decimal], precision: int = 8):
        """初始化价格
        
        Args:
            value: 价格值
            precision: 精度（小数位数）
            
        Raises:
            ValueError: 价格无效时抛出
        """
        self._value = Decimal(str(value))
        self._precision = precision
        
        if self._value < 0:
            raise ValueError(f"价格不能为负数: {self._value}")
        
        # 格式化到指定精度
        self._value = self._format(self._value, precision)

    @staticmethod
    def _format(value: Decimal, precision: int) -> Decimal:
        """格式化价格到指定精度
        
        Args:
            value: 原始价格
            precision: 精度
            
        Returns:
            格式化后的价格
        """
        if precision < 0:
            precision = 0
        
        quantize_value = Decimal('0.1') ** precision
        return value.quantize(quantize_value, rounding=ROUND_DOWN)

    @property
    def value(self) -> Decimal:
        """获取价格值"""
        return self._value

    @property
    def precision(self) -> int:
        """获取精度"""
        return self._precision

    def add(self, offset: Union['Price', Decimal, float]) -> 'Price':
        """加法运算
        
        Args:
            offset: 偏移量
            
        Returns:
            新的价格对象
        """
        if isinstance(offset, Price):
            offset_value = offset.value
        else:
            offset_value = Decimal(str(offset))
        
        return Price(self._value + offset_value, self._precision)

    def subtract(self, offset: Union['Price', Decimal, float]) -> 'Price':
        """减法运算
        
        Args:
            offset: 偏移量
            
        Returns:
            新的价格对象
        """
        if isinstance(offset, Price):
            offset_value = offset.value
        else:
            offset_value = Decimal(str(offset))
        
        result = self._value - offset_value
        if result < 0:
            raise ValueError(f"减法结果不能为负数: {self._value} - {offset_value}")
        
        return Price(result, self._precision)

    def multiply(self, factor: Union[Decimal, float]) -> 'Price':
        """乘法运算
        
        Args:
            factor: 乘数
            
        Returns:
            新的价格对象
        """
        factor_value = Decimal(str(factor))
        return Price(self._value * factor_value, self._precision)

    def apply_percentage_offset(self, percentage: Decimal, is_increase: bool = True) -> 'Price':
        """应用百分比偏移
        
        Args:
            percentage: 百分比（如2.0表示2%）
            is_increase: 是否增加（False为减少）
            
        Returns:
            新的价格对象
        """
        factor = Decimal("1") + (percentage / Decimal("100"))
        if not is_increase:
            factor = Decimal("1") - (percentage / Decimal("100"))
        
        if factor <= 0:
            raise ValueError(f"百分比偏移后的因子必须大于0: {factor}")
        
        return self.multiply(factor)

    def to_string(self) -> str:
        """转换为字符串格式（保留精度）"""
        return str(self._value)

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return f"Price(value={self._value}, precision={self._precision})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Price):
            return False
        return self._value == other._value

    def __lt__(self, other: 'Price') -> bool:
        return self._value < other._value

    def __le__(self, other: 'Price') -> bool:
        return self._value <= other._value

    def __gt__(self, other: 'Price') -> bool:
        return self._value > other._value

    def __ge__(self, other: 'Price') -> bool:
        return self._value >= other._value

