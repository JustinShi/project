"""数量值对象"""

from decimal import Decimal, ROUND_DOWN
from typing import Union


class Quantity:
    """数量值对象
    
    不可变的数量表示，确保数量的有效性和精度控制
    """

    def __init__(self, value: Union[str, float, Decimal], precision: int = 6):
        """初始化数量
        
        Args:
            value: 数量值
            precision: 精度（小数位数）
            
        Raises:
            ValueError: 数量无效时抛出
        """
        self._value = Decimal(str(value))
        self._precision = precision
        
        if self._value < 0:
            raise ValueError(f"数量不能为负数: {self._value}")
        
        # 格式化到指定精度
        self._value = self._format(self._value, precision)

    @staticmethod
    def _format(value: Decimal, precision: int) -> Decimal:
        """格式化数量到指定精度
        
        Args:
            value: 原始数量
            precision: 精度
            
        Returns:
            格式化后的数量
        """
        if precision < 0:
            precision = 0
        
        quantize_value = Decimal('0.1') ** precision
        return value.quantize(quantize_value, rounding=ROUND_DOWN)

    @property
    def value(self) -> Decimal:
        """获取数量值"""
        return self._value

    @property
    def precision(self) -> int:
        """获取精度"""
        return self._precision

    def add(self, amount: Union['Quantity', Decimal, float]) -> 'Quantity':
        """加法运算
        
        Args:
            amount: 增量
            
        Returns:
            新的数量对象
        """
        if isinstance(amount, Quantity):
            amount_value = amount.value
        else:
            amount_value = Decimal(str(amount))
        
        return Quantity(self._value + amount_value, self._precision)

    def subtract(self, amount: Union['Quantity', Decimal, float]) -> 'Quantity':
        """减法运算
        
        Args:
            amount: 减量
            
        Returns:
            新的数量对象
        """
        if isinstance(amount, Quantity):
            amount_value = amount.value
        else:
            amount_value = Decimal(str(amount))
        
        result = self._value - amount_value
        if result < 0:
            raise ValueError(f"减法结果不能为负数: {self._value} - {amount_value}")
        
        return Quantity(result, self._precision)

    def multiply(self, factor: Union[Decimal, float]) -> 'Quantity':
        """乘法运算
        
        Args:
            factor: 乘数
            
        Returns:
            新的数量对象
        """
        factor_value = Decimal(str(factor))
        if factor_value < 0:
            raise ValueError(f"乘数不能为负数: {factor_value}")
        
        return Quantity(self._value * factor_value, self._precision)

    def divide(self, divisor: Union[Decimal, float]) -> 'Quantity':
        """除法运算
        
        Args:
            divisor: 除数
            
        Returns:
            新的数量对象
        """
        divisor_value = Decimal(str(divisor))
        if divisor_value <= 0:
            raise ValueError(f"除数必须大于0: {divisor_value}")
        
        return Quantity(self._value / divisor_value, self._precision)

    def is_zero(self) -> bool:
        """检查是否为零"""
        return self._value == Decimal("0")

    def to_string(self) -> str:
        """转换为字符串格式（保留精度）"""
        return str(self._value)

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return f"Quantity(value={self._value}, precision={self._precision})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return False
        return self._value == other._value

    def __lt__(self, other: 'Quantity') -> bool:
        return self._value < other._value

    def __le__(self, other: 'Quantity') -> bool:
        return self._value <= other._value

    def __gt__(self, other: 'Quantity') -> bool:
        return self._value > other._value

    def __ge__(self, other: 'Quantity') -> bool:
        return self._value >= other._value

