"""价格计算领域服务"""

from decimal import Decimal

from binance.config.constants import PriceOffsetMode
from binance.domain.value_objects.price import Price


class PriceCalculator:
    """价格计算领域服务
    
    负责计算买卖价格，支持百分比和固定金额偏移
    """

    @staticmethod
    def calculate_buy_price(
        current_price: Price,
        offset_value: Decimal,
        offset_mode: PriceOffsetMode
    ) -> Price:
        """计算买入价格（高于当前价，尽快成交）
        
        Args:
            current_price: 当前市场价格
            offset_value: 偏移值
            offset_mode: 偏移模式（仅支持百分比）
            
        Returns:
            计算后的买入价格
            
        Raises:
            ValueError: 参数无效时抛出
        """
        if offset_value < 0:
            raise ValueError(f"偏移值不能为负数: {offset_value}")
        
        if offset_mode == PriceOffsetMode.PERCENTAGE:
            # 百分比模式：买入价 = 当前价 * (1 + offset%) - 高价买，尽快成交
            return current_price.apply_percentage_offset(offset_value, is_increase=True)
        
        else:
            raise ValueError(f"仅支持百分比偏移模式: {offset_mode}")

    @staticmethod
    def calculate_sell_price(
        current_price: Price,
        offset_value: Decimal,
        offset_mode: PriceOffsetMode
    ) -> Price:
        """计算卖出价格（低于当前价，尽快成交）
        
        Args:
            current_price: 当前市场价格
            offset_value: 偏移值
            offset_mode: 偏移模式（仅支持百分比）
            
        Returns:
            计算后的卖出价格
            
        Raises:
            ValueError: 参数无效时抛出
        """
        if offset_value < 0:
            raise ValueError(f"偏移值不能为负数: {offset_value}")
        
        if offset_mode == PriceOffsetMode.PERCENTAGE:
            # 百分比模式：卖出价 = 当前价 * (1 - offset%) - 低价卖，尽快成交
            return current_price.apply_percentage_offset(offset_value, is_increase=False)
        
        else:
            raise ValueError(f"仅支持百分比偏移模式: {offset_mode}")

    @staticmethod
    def calculate_oto_prices(
        current_price: Price,
        buy_offset: Decimal,
        sell_offset: Decimal,
        offset_mode: PriceOffsetMode
    ) -> tuple[Price, Price]:
        """计算OTO订单的买卖价格（高价买，低价卖，尽快成交）
        
        Args:
            current_price: 当前市场价格
            buy_offset: 买入偏移值（百分比）
            sell_offset: 卖出偏移值（百分比）
            offset_mode: 偏移模式（仅支持百分比）
            
        Returns:
            (买入价格, 卖出价格)
        """
        buy_price = PriceCalculator.calculate_buy_price(
            current_price, buy_offset, offset_mode
        )
        sell_price = PriceCalculator.calculate_sell_price(
            current_price, sell_offset, offset_mode
        )
        
        return buy_price, sell_price

    @staticmethod
    def calculate_price_change_percentage(
        old_price: Price,
        new_price: Price
    ) -> Decimal:
        """计算价格变化百分比
        
        Args:
            old_price: 旧价格
            new_price: 新价格
            
        Returns:
            变化百分比（如2.5表示上涨2.5%，-2.5表示下跌2.5%）
        """
        if old_price.value == 0:
            raise ValueError("旧价格不能为0")
        
        change = new_price.value - old_price.value
        percentage = (change / old_price.value) * Decimal("100")
        
        return percentage

