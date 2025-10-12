"""OTO订单执行服务"""

from decimal import Decimal

from binance.config.constants import OTOOrderPairStatus
from binance.domain.entities.oto_order_pair import OTOOrderPair
from binance.domain.entities.price_data import PriceData
from binance.domain.services.order_state_machine import OrderStateMachine
from binance.domain.services.price_calculator import PriceCalculator
from binance.domain.value_objects.price import Price
from binance.infrastructure.config import TradingTarget


class OTOOrderExecutor:
    """OTO订单执行服务"""

    def __init__(self, order_state_machine: OrderStateMachine):
        self.order_state_machine = order_state_machine
        self.price_calculator = PriceCalculator()

    def can_execute_order(
        self, user_id: int, symbol: str, current_price: PriceData, config: TradingTarget
    ) -> tuple[bool, str]:
        """检查是否可以执行订单"""
        # 检查用户是否有活跃订单
        if not self.order_state_machine.can_place_new_order(user_id):
            return False, "用户已有活跃订单，无法下新订单"

        # 检查价格波动
        if self._is_price_too_volatile(current_price, config):
            return False, "价格波动过大，暂停交易"

        # 检查余额（这里需要从外部服务获取）
        # 这个检查将在应用层实现

        return True, "可以执行订单"

    def calculate_order_prices(
        self, current_price: PriceData, config: TradingTarget
    ) -> tuple[Price, Price]:
        """计算订单价格"""
        # 计算买单价格（高价买入，快速成交）
        buy_price = self.price_calculator.calculate_buy_price(
            current_price.price, config.buy_offset_value, config.price_offset_mode
        )

        # 计算卖单价格（低价卖出，快速成交）
        sell_price = self.price_calculator.calculate_sell_price(
            current_price.price, config.sell_offset_value, config.price_offset_mode
        )

        return buy_price, sell_price

    def create_order_pair(
        self,
        user_id: int,
        symbol: str,
        quantity: Decimal,
        buy_price: Price,
        sell_price: Price,
        order_pair_id: int,
    ) -> OTOOrderPair:
        """创建OTO订单对"""
        order_pair = OTOOrderPair(
            id=order_pair_id,
            user_id=user_id,
            symbol=symbol,
            quantity=quantity,
            buy_price=buy_price,
            sell_price=sell_price,
            status=OTOOrderPairStatus.PENDING,
        )

        # 添加到状态机
        self.order_state_machine.add_order_pair(order_pair)

        return order_pair

    def update_buy_order(self, order_pair_id: int, binance_order_id: str) -> bool:
        """更新买单信息"""
        order_pair = self.order_state_machine.get_order_pair(order_pair_id)
        if not order_pair:
            return False

        order_pair.set_buy_order(
            binance_order_id, order_pair.buy_price, order_pair.quantity
        )
        return True

    def update_sell_order(self, order_pair_id: int, binance_order_id: str) -> bool:
        """更新卖单信息"""
        order_pair = self.order_state_machine.get_order_pair(order_pair_id)
        if not order_pair:
            return False

        order_pair.set_sell_order(binance_order_id, order_pair.sell_price)
        return True

    def mark_buy_filled(self, order_pair_id: int) -> bool:
        """标记买单已成交"""
        return self.order_state_machine.mark_buy_filled(order_pair_id)

    def mark_sell_filled(self, order_pair_id: int) -> bool:
        """标记卖单已成交"""
        return self.order_state_machine.mark_sell_filled(order_pair_id)

    def mark_cancelled(self, order_pair_id: int) -> bool:
        """标记订单已取消"""
        return self.order_state_machine.mark_cancelled(order_pair_id)

    def get_user_active_order(self, user_id: int) -> OTOOrderPair | None:
        """获取用户的活跃订单"""
        return self.order_state_machine.get_user_active_order(user_id)

    def get_order_statistics(self) -> dict:
        """获取订单统计"""
        return self.order_state_machine.get_order_statistics()

    def cleanup_timeout_orders(self) -> int:
        """清理超时订单"""
        return self.order_state_machine.cleanup_timeout_orders()

    def _is_price_too_volatile(
        self, current_price: PriceData, config: TradingTarget
    ) -> bool:
        """检查价格是否过于波动"""
        # 这里需要从价格波动监控服务获取波动信息
        # 暂时返回False，实际实现需要集成价格波动监控
        return False

    def validate_order_parameters(
        self, symbol: str, quantity: Decimal, buy_price: Price, sell_price: Price
    ) -> tuple[bool, str]:
        """验证订单参数"""
        # 检查数量
        if quantity <= 0:
            return False, "订单数量必须大于0"

        # 检查价格
        if buy_price.value <= 0:
            return False, "买单价格必须大于0"

        if sell_price.value <= 0:
            return False, "卖单价格必须大于0"

        # 检查价格关系（卖价应该低于买价，以便快速成交）
        if sell_price.value >= buy_price.value:
            return False, "卖单价格应该低于买单价格"

        # 检查价格差异是否合理
        price_diff = buy_price.value - sell_price.value
        price_diff_percentage = (price_diff / buy_price.value) * Decimal("100")

        if price_diff_percentage < Decimal("0.1"):  # 至少0.1%的价差
            return False, "买卖价差过小，可能无法快速成交"

        if price_diff_percentage > Decimal("10"):  # 最多10%的价差
            return False, "买卖价差过大，可能造成较大损失"

        return True, "参数验证通过"

    def __str__(self) -> str:
        return f"OTOOrderExecutor(state_machine={self.order_state_machine})"

    def __repr__(self) -> str:
        return self.__str__()
