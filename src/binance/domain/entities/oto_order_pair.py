"""OTO订单对实体"""

from datetime import datetime
from decimal import Decimal

from binance.config.constants import OTOOrderPairStatus
from binance.domain.value_objects.price import Price


class OTOOrderPair:
    """OTO订单对实体"""

    def __init__(
        self,
        id: int,
        user_id: int,
        symbol: str,
        buy_order_id: str | None = None,
        sell_order_id: str | None = None,
        buy_price: Price | None = None,
        sell_price: Price | None = None,
        quantity: Decimal | None = None,
        status: OTOOrderPairStatus = OTOOrderPairStatus.PENDING,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id = id
        self.user_id = user_id
        self.symbol = symbol
        self.buy_order_id = buy_order_id
        self.sell_order_id = sell_order_id
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.quantity = quantity
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def set_buy_order(self, order_id: str, price: Price, quantity: Decimal) -> None:
        """设置买单信息"""
        self.buy_order_id = order_id
        self.buy_price = price
        self.quantity = quantity
        self.updated_at = datetime.now()

    def set_sell_order(self, order_id: str, price: Price) -> None:
        """设置卖单信息"""
        self.sell_order_id = order_id
        self.sell_price = price
        self.updated_at = datetime.now()

    def mark_buy_filled(self) -> None:
        """标记买单已成交"""
        if self.status == OTOOrderPairStatus.PENDING:
            self.status = OTOOrderPairStatus.BUY_FILLED
        self.updated_at = datetime.now()

    def mark_sell_filled(self) -> None:
        """标记卖单已成交"""
        if self.status == OTOOrderPairStatus.BUY_FILLED:
            self.status = OTOOrderPairStatus.COMPLETED
        self.updated_at = datetime.now()

    def mark_cancelled(self) -> None:
        """标记订单已取消"""
        self.status = OTOOrderPairStatus.CANCELLED
        self.updated_at = datetime.now()

    def is_pending(self) -> bool:
        """是否等待中"""
        return self.status == OTOOrderPairStatus.PENDING

    def is_buy_filled(self) -> bool:
        """买单是否已成交"""
        return self.status == OTOOrderPairStatus.BUY_FILLED

    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == OTOOrderPairStatus.COMPLETED

    def is_cancelled(self) -> bool:
        """是否已取消"""
        return self.status == OTOOrderPairStatus.CANCELLED

    def can_place_sell_order(self) -> bool:
        """是否可以下卖单"""
        return self.is_buy_filled() and self.sell_order_id is None

    def has_both_orders(self) -> bool:
        """是否同时有买卖单"""
        return self.buy_order_id is not None and self.sell_order_id is not None


    def __str__(self) -> str:
        return (
            f"OTOOrderPair(id={self.id}, user_id={self.user_id}, "
            f"symbol={self.symbol}, status={self.status.value}, "
            f"buy_order_id={self.buy_order_id}, sell_order_id={self.sell_order_id})"
        )

    def __repr__(self) -> str:
        return self.__str__()
