"""通知应用服务"""

import logging
from decimal import Decimal
from typing import Any

from binance.domain.repositories import UserRepository


logger = logging.getLogger(__name__)


class NotificationService:
    """通知应用服务

    负责发送各种通知，如暂停交易、余额不足等
    """

    def __init__(self, user_repository: UserRepository):
        """初始化通知服务

        Args:
            user_repository: 用户仓储
        """
        self._user_repository = user_repository

    async def notify_volatility_alert(
        self,
        symbol: str,
        volatility_percentage: Decimal,
        threshold: Decimal,
        affected_users: list[int],
    ) -> None:
        """通知价格波动警报

        Args:
            symbol: 代币符号
            volatility_percentage: 实际波动百分比
            threshold: 阈值
            affected_users: 受影响的用户ID列表
        """
        message = (
            f"价格波动警报: {symbol} "
            f"波动率 {volatility_percentage:.2f}% 超过阈值 {threshold:.2f}%，"
            f"已暂停 {len(affected_users)} 个用户的交易"
        )

        logger.warning(
            message,
            extra={
                "symbol": symbol,
                "volatility_percentage": float(volatility_percentage),
                "threshold": float(threshold),
                "affected_users": affected_users,
            },
        )

        # TODO: 实现具体的通知逻辑（邮件、短信、推送等）
        for user_id in affected_users:
            await self._send_user_notification(
                user_id=user_id,
                type="volatility_alert",
                title="价格波动警报",
                message=f"代币 {symbol} 价格波动过大，交易已暂停",
                data={
                    "symbol": symbol,
                    "volatility_percentage": float(volatility_percentage),
                    "threshold": float(threshold),
                },
            )

    async def notify_insufficient_balance(
        self,
        user_id: int,
        symbol: str,
        required_amount: Decimal,
        available_amount: Decimal,
    ) -> None:
        """通知余额不足

        Args:
            user_id: 用户ID
            symbol: 代币符号
            required_amount: 所需金额
            available_amount: 可用金额
        """
        message = (
            f"用户 {user_id} 余额不足: "
            f"需要 {required_amount} USDT，可用 {available_amount} USDT"
        )

        logger.warning(
            message,
            extra={
                "user_id": user_id,
                "symbol": symbol,
                "required_amount": float(required_amount),
                "available_amount": float(available_amount),
            },
        )

        await self._send_user_notification(
            user_id=user_id,
            type="insufficient_balance",
            title="余额不足",
            message=f"代币 {symbol} 余额不足，请充值后继续交易",
            data={
                "symbol": symbol,
                "required_amount": float(required_amount),
                "available_amount": float(available_amount),
            },
        )

    async def notify_order_timeout(
        self,
        user_id: int,
        symbol: str,
        order_id: str,
        timeout_seconds: int,
    ) -> None:
        """通知订单超时

        Args:
            user_id: 用户ID
            symbol: 代币符号
            order_id: 订单ID
            timeout_seconds: 超时时间
        """
        message = (
            f"用户 {user_id} 订单超时: "
            f"代币 {symbol} 订单 {order_id} 在 {timeout_seconds} 秒后超时"
        )

        logger.warning(
            message,
            extra={
                "user_id": user_id,
                "symbol": symbol,
                "order_id": order_id,
                "timeout_seconds": timeout_seconds,
            },
        )

        await self._send_user_notification(
            user_id=user_id,
            type="order_timeout",
            title="订单超时",
            message=f"代币 {symbol} 订单超时，已自动取消",
            data={
                "symbol": symbol,
                "order_id": order_id,
                "timeout_seconds": timeout_seconds,
            },
        )

    async def notify_websocket_disconnected(
        self,
        symbol: str,
        affected_users: list[int],
    ) -> None:
        """通知WebSocket断开连接

        Args:
            symbol: 代币符号
            affected_users: 受影响的用户ID列表
        """
        message = (
            f"WebSocket连接断开: {symbol}，已暂停 {len(affected_users)} 个用户的交易"
        )

        logger.error(
            message,
            extra={
                "symbol": symbol,
                "affected_users": affected_users,
            },
        )

        for user_id in affected_users:
            await self._send_user_notification(
                user_id=user_id,
                type="websocket_disconnected",
                title="连接断开",
                message=f"代币 {symbol} 价格连接断开，交易已暂停",
                data={
                    "symbol": symbol,
                },
            )

    async def notify_trading_paused(
        self,
        user_id: int,
        reason: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """通知交易暂停

        Args:
            user_id: 用户ID
            reason: 暂停原因
            details: 详细信息
        """
        message = f"用户 {user_id} 交易暂停: {reason}"

        logger.info(
            message,
            extra={
                "user_id": user_id,
                "reason": reason,
                "details": details,
            },
        )

        await self._send_user_notification(
            user_id=user_id,
            type="trading_paused",
            title="交易暂停",
            message=f"交易已暂停: {reason}",
            data={
                "reason": reason,
                "details": details or {},
            },
        )

    async def notify_trading_resumed(
        self,
        user_id: int,
        symbol: str,
    ) -> None:
        """通知交易恢复

        Args:
            user_id: 用户ID
            symbol: 代币符号
        """
        message = f"用户 {user_id} 交易恢复: {symbol}"

        logger.info(
            message,
            extra={
                "user_id": user_id,
                "symbol": symbol,
            },
        )

        await self._send_user_notification(
            user_id=user_id,
            type="trading_resumed",
            title="交易恢复",
            message=f"代币 {symbol} 交易已恢复",
            data={
                "symbol": symbol,
            },
        )

    async def _send_user_notification(
        self,
        user_id: int,
        type: str,
        title: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """发送用户通知

        Args:
            user_id: 用户ID
            type: 通知类型
            title: 通知标题
            message: 通知内容
            data: 附加数据
        """
        try:
            # 获取用户信息
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                logger.error(f"用户不存在: {user_id}")
                return

            # TODO: 实现具体的通知发送逻辑
            # 这里可以集成邮件、短信、推送等服务

            logger.info(f"通知已发送: 用户 {user_id}, 类型 {type}, 标题 {title}")

        except Exception as e:
            logger.error(f"发送通知失败: {e}")

    async def get_notification_history(
        self,
        user_id: int,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """获取用户通知历史

        Args:
            user_id: 用户ID
            limit: 返回数量限制

        Returns:
            通知历史列表
        """
        # TODO: 实现通知历史查询
        # 这里需要添加通知存储和查询功能
        return []

    async def mark_notification_read(
        self,
        user_id: int,
        notification_id: str,
    ) -> bool:
        """标记通知为已读

        Args:
            user_id: 用户ID
            notification_id: 通知ID

        Returns:
            是否标记成功
        """
        # TODO: 实现通知已读标记
        return True
