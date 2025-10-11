"""订单状态机服务"""

from datetime import datetime, timedelta

from binance.config.constants import OTOOrderPairStatus
from binance.domain.entities.oto_order_pair import OTOOrderPair


class OrderStateMachine:
    """订单状态机服务"""

    def __init__(self, timeout_minutes: int = 30):
        self.timeout_minutes = timeout_minutes
        self._active_orders: dict[int, OTOOrderPair] = {}

    def add_order_pair(self, order_pair: OTOOrderPair) -> None:
        """添加订单对"""
        self._active_orders[order_pair.id] = order_pair

    def remove_order_pair(self, order_pair_id: int) -> None:
        """移除订单对"""
        if order_pair_id in self._active_orders:
            del self._active_orders[order_pair_id]

    def get_order_pair(self, order_pair_id: int) -> OTOOrderPair | None:
        """获取订单对"""
        return self._active_orders.get(order_pair_id)

    def get_active_orders(self) -> dict[int, OTOOrderPair]:
        """获取所有活跃订单"""
        return self._active_orders.copy()

    def has_active_order_for_user(self, user_id: int) -> bool:
        """用户是否有活跃订单"""
        for order_pair in self._active_orders.values():
            if order_pair.user_id == user_id and not order_pair.is_completed():
                return True
        return False

    def get_user_active_order(self, user_id: int) -> OTOOrderPair | None:
        """获取用户的活跃订单"""
        for order_pair in self._active_orders.values():
            if order_pair.user_id == user_id and not order_pair.is_completed():
                return order_pair
        return None

    def can_place_new_order(self, user_id: int) -> bool:
        """是否可以下新订单"""
        return not self.has_active_order_for_user(user_id)

    def update_order_status(self, order_pair_id: int, status: OTOOrderPairStatus) -> bool:
        """更新订单状态"""
        order_pair = self.get_order_pair(order_pair_id)
        if not order_pair:
            return False

        order_pair.status = status
        order_pair.updated_at = datetime.now()
        return True

    def mark_buy_filled(self, order_pair_id: int) -> bool:
        """标记买单已成交"""
        order_pair = self.get_order_pair(order_pair_id)
        if not order_pair:
            return False

        order_pair.mark_buy_filled()
        return True

    def mark_sell_filled(self, order_pair_id: int) -> bool:
        """标记卖单已成交"""
        order_pair = self.get_order_pair(order_pair_id)
        if not order_pair:
            return False

        order_pair.mark_sell_filled()
        # 完成后移除订单
        self.remove_order_pair(order_pair_id)
        return True

    def mark_cancelled(self, order_pair_id: int) -> bool:
        """标记订单已取消"""
        order_pair = self.get_order_pair(order_pair_id)
        if not order_pair:
            return False

        order_pair.mark_cancelled()
        # 取消后移除订单
        self.remove_order_pair(order_pair_id)
        return True

    def check_timeout_orders(self) -> list[int]:
        """检查超时订单"""
        timeout_orders = []
        timeout_threshold = datetime.now() - timedelta(minutes=self.timeout_minutes)

        for order_id, order_pair in self._active_orders.items():
            if order_pair.created_at < timeout_threshold:
                timeout_orders.append(order_id)

        return timeout_orders

    def cleanup_timeout_orders(self) -> int:
        """清理超时订单"""
        timeout_orders = self.check_timeout_orders()
        for order_id in timeout_orders:
            self.mark_cancelled(order_id)

        return len(timeout_orders)

    def get_order_statistics(self) -> dict[str, int]:
        """获取订单统计"""
        stats = {
            "total": len(self._active_orders),
            "pending": 0,
            "buy_filled": 0,
            "completed": 0,
            "cancelled": 0,
        }

        for order_pair in self._active_orders.values():
            if order_pair.is_pending():
                stats["pending"] += 1
            elif order_pair.is_buy_filled():
                stats["buy_filled"] += 1
            elif order_pair.is_completed():
                stats["completed"] += 1
            elif order_pair.is_cancelled():
                stats["cancelled"] += 1

        return stats


    def __str__(self) -> str:
        stats = self.get_order_statistics()
        return (
            f"OrderStateMachine(active_orders={stats['total']}, "
            f"pending={stats['pending']}, buy_filled={stats['buy_filled']}, "
            f"completed={stats['completed']}, cancelled={stats['cancelled']})"
        )

    def __repr__(self) -> str:
        return self.__str__()
