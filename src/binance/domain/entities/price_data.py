"""价格数据实体"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from binance.domain.value_objects.price import Price


@dataclass
class PriceData:
    """价格数据实体
    
    存储实时价格信息，支持波动计算
    """

    symbol: str  # 代币符号
    price: Price  # 价格
    volume: Decimal  # 成交量
    timestamp: datetime  # 时间戳
    
    # 波动计算相关
    price_change_24h: Optional[Decimal] = None  # 24小时价格变化
    price_change_percentage_24h: Optional[Decimal] = None  # 24小时价格变化百分比
    
    def __post_init__(self):
        """验证价格数据有效性"""
        if self.volume < 0:
            raise ValueError(f"成交量不能为负数: {self.volume}")
        
        if self.timestamp > datetime.now():
            raise ValueError(f"时间戳不能是未来时间: {self.timestamp}")

    def calculate_price_change(self, old_price: Price) -> Decimal:
        """计算价格变化
        
        Args:
            old_price: 旧价格
            
        Returns:
            价格变化（新价格 - 旧价格）
        """
        return self.price.value - old_price.value

    def calculate_price_change_percentage(self, old_price: Price) -> Decimal:
        """计算价格变化百分比
        
        Args:
            old_price: 旧价格
            
        Returns:
            价格变化百分比
        """
        if old_price.value == 0:
            raise ValueError("旧价格不能为0")
        
        change = self.price.value - old_price.value
        percentage = (change / old_price.value) * Decimal("100")
        
        return percentage

    def is_price_increase(self, old_price: Price) -> bool:
        """检查价格是否上涨
        
        Args:
            old_price: 旧价格
            
        Returns:
            是否上涨
        """
        return self.price > old_price

    def is_price_decrease(self, old_price: Price) -> bool:
        """检查价格是否下跌
        
        Args:
            old_price: 旧价格
            
        Returns:
            是否下跌
        """
        return self.price < old_price

    def get_price_change_info(self, old_price: Price) -> dict:
        """获取价格变化信息
        
        Args:
            old_price: 旧价格
            
        Returns:
            价格变化信息字典
        """
        change = self.calculate_price_change(old_price)
        percentage = self.calculate_price_change_percentage(old_price)
        
        return {
            "old_price": old_price.value,
            "new_price": self.price.value,
            "change": change,
            "percentage": percentage,
            "is_increase": self.is_price_increase(old_price),
            "is_decrease": self.is_price_decrease(old_price),
        }

    def __str__(self) -> str:
        return (
            f"PriceData(symbol={self.symbol}, "
            f"price={self.price}, "
            f"volume={self.volume}, "
            f"timestamp={self.timestamp})"
        )
