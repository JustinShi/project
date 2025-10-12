"""订单相关API路由"""

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from binance.api.dependencies import get_db_session, get_user_repository
from binance.api.schemas.order_schema import (
    OrderCancelRequest,
    OrderCancelResponse,
    OrderExecuteRequest,
    OrderExecuteResponse,
    OrderMonitorResponse,
    OrderStatisticsResponse,
    OrderStatusResponse,
    WebSocketStatusResponse,
)
from binance.application.services.notification_service import NotificationService
from binance.application.services.order_execution_service import OrderExecutionService
from binance.domain.entities.price_data import PriceData
from binance.domain.repositories.user_repository import UserRepository
from binance.domain.value_objects.price import Price
from binance.infrastructure.config import TradingTarget, YAMLConfigManager
from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])

# 全局服务实例
_order_execution_service: OrderExecutionService | None = None
_notification_service: NotificationService | None = None


def get_notification_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> NotificationService:
    """获取通知服务"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService(user_repo)
    return _notification_service


def get_order_execution_service(
    notification_service: NotificationService = Depends(get_notification_service),
) -> OrderExecutionService:
    """获取订单执行服务"""
    global _order_execution_service
    if _order_execution_service is None:
        _order_execution_service = OrderExecutionService(notification_service)
    return _order_execution_service


@router.post("/execute", response_model=OrderExecuteResponse)
async def execute_order(
    request: OrderExecuteRequest,
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db_session),
    user_repo: UserRepository = Depends(get_user_repository),
    order_service: OrderExecutionService = Depends(get_order_execution_service),
):
    """执行OTO订单"""
    try:
        # 获取用户信息
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        if not user.has_credentials():
            raise HTTPException(status_code=400, detail="用户认证信息不完整")

        # 获取用户交易配置
        config_manager = YAMLConfigManager()
        token_symbol_short = request.symbol.replace("usdt", "").upper()
        config = config_manager.get_trading_target(user_id, token_symbol_short)

        if not config:
            # 使用默认配置
            global_settings = config_manager.get_global_settings()
            config = TradingTarget(
                token_symbol_short=token_symbol_short,
                target_volume=Decimal("10000.0"),
                current_volume=Decimal("0.0"),
                volume_multiplier=Decimal("4.0"),
                price_offset_mode=global_settings.default_price_offset_mode,
                buy_offset_value=request.buy_offset_percentage,
                sell_offset_value=request.sell_offset_percentage,
                order_quantity=request.quantity,
                timeout_seconds=global_settings.default_timeout_seconds,
                price_volatility_threshold=global_settings.default_price_volatility_threshold,
                is_trading_active=True,
            )

        # 获取当前价格（这里需要从价格服务获取）
        # 暂时使用模拟价格
        current_price = PriceData(
            symbol=request.symbol,
            price=Price(Decimal("48.0"), precision=4),  # 模拟KOGE价格
            volume=Decimal("1000.0"),
            timestamp=datetime.now(),
        )

        # 解析用户认证信息
        headers = {}
        cookies = user.cookies

        # 执行订单
        success, message, order_pair = await order_service.execute_oto_order(
            user_id=user_id,
            symbol=request.symbol,
            current_price=current_price,
            config=config,
            headers=headers,
            cookies=cookies,
        )

        if success and order_pair:
            return OrderExecuteResponse(
                success=True,
                message=message,
                order_pair_id=order_pair.id,
                buy_order_id=order_pair.buy_order_id,
                sell_order_id=order_pair.sell_order_id,
                buy_price=order_pair.buy_price.value if order_pair.buy_price else None,
                sell_price=order_pair.sell_price.value
                if order_pair.sell_price
                else None,
                quantity=order_pair.quantity,
                status=order_pair.status.value,
            )
        else:
            return OrderExecuteResponse(
                success=False,
                message=message,
                order_pair_id=None,
                buy_order_id=None,
                sell_order_id=None,
                buy_price=None,
                sell_price=None,
                quantity=None,
                status=None,
            )

    except Exception as e:
        logger.error(f"执行订单异常: {e}")
        raise HTTPException(status_code=500, detail=f"执行订单失败: {e!s}")


@router.get("/status/{order_pair_id}", response_model=OrderStatusResponse)
async def get_order_status(
    order_pair_id: int,
    user_id: int = Query(..., description="用户ID"),
    order_service: OrderExecutionService = Depends(get_order_execution_service),
):
    """获取订单状态"""
    try:
        # 获取用户活跃订单
        order_pair = await order_service.get_user_active_order(user_id)

        if not order_pair or order_pair.id != order_pair_id:
            raise HTTPException(status_code=404, detail="订单不存在")

        return OrderStatusResponse(
            order_pair_id=order_pair.id,
            user_id=order_pair.user_id,
            symbol=order_pair.symbol,
            status=order_pair.status.value,
            buy_order_id=order_pair.buy_order_id,
            sell_order_id=order_pair.sell_order_id,
            buy_price=order_pair.buy_price.value if order_pair.buy_price else None,
            sell_price=order_pair.sell_price.value if order_pair.sell_price else None,
            quantity=order_pair.quantity,
            created_at=order_pair.created_at,
            updated_at=order_pair.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取订单状态异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取订单状态失败: {e!s}")


@router.post("/cancel", response_model=OrderCancelResponse)
async def cancel_order(
    request: OrderCancelRequest,
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db_session),
    user_repo: UserRepository = Depends(get_user_repository),
    order_service: OrderExecutionService = Depends(get_order_execution_service),
):
    """取消订单"""
    try:
        # 获取用户信息
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        if not user.has_credentials():
            raise HTTPException(status_code=400, detail="用户认证信息不完整")

        # 解析用户认证信息
        headers = {}
        cookies = user.cookies

        # 取消订单
        success, message = await order_service.cancel_user_order(
            user_id=user_id,
            symbol="kogeusdt",  # 这里应该从订单信息中获取
            headers=headers,
            cookies=cookies,
        )

        return OrderCancelResponse(success=success, message=message)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消订单异常: {e}")
        raise HTTPException(status_code=500, detail=f"取消订单失败: {e!s}")


@router.get("/statistics", response_model=OrderStatisticsResponse)
async def get_order_statistics(
    order_service: OrderExecutionService = Depends(get_order_execution_service),
):
    """获取订单统计"""
    try:
        stats = await order_service.get_order_statistics()

        return OrderStatisticsResponse(
            total_orders=stats.get("total", 0),
            pending_orders=stats.get("pending", 0),
            buy_filled_orders=stats.get("buy_filled", 0),
            completed_orders=stats.get("completed", 0),
            cancelled_orders=stats.get("cancelled", 0),
        )

    except Exception as e:
        logger.error(f"获取订单统计异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取订单统计失败: {e!s}")


@router.get("/monitor/{user_id}", response_model=OrderMonitorResponse)
async def get_order_monitor(
    user_id: int,
    order_service: OrderExecutionService = Depends(get_order_execution_service),
):
    """获取订单监控信息"""
    try:
        # 获取用户活跃订单
        active_order = await order_service.get_user_active_order(user_id)

        # 构建活跃订单列表
        active_orders = []
        if active_order:
            active_orders.append(
                OrderStatusResponse(
                    order_pair_id=active_order.id,
                    user_id=active_order.user_id,
                    symbol=active_order.symbol,
                    status=active_order.status.value,
                    buy_order_id=active_order.buy_order_id,
                    sell_order_id=active_order.sell_order_id,
                    buy_price=active_order.buy_price.value
                    if active_order.buy_price
                    else None,
                    sell_price=active_order.sell_price.value
                    if active_order.sell_price
                    else None,
                    quantity=active_order.quantity,
                    created_at=active_order.created_at,
                    updated_at=active_order.updated_at,
                )
            )

        # 获取订单统计
        stats = await order_service.get_order_statistics()

        # 构建WebSocket状态（这里需要从订单服务获取实际状态）
        websocket_status = WebSocketStatusResponse(
            user_id=user_id,
            connected=False,  # 这里需要从订单服务获取实际连接状态
            listen_key=None,
            reconnect_attempts=0,
            last_activity=None,
        )

        return OrderMonitorResponse(
            user_id=user_id,
            active_orders=active_orders,
            websocket_status=websocket_status,
            statistics=OrderStatisticsResponse(
                total_orders=stats.get("total", 0),
                pending_orders=stats.get("pending", 0),
                buy_filled_orders=stats.get("buy_filled", 0),
                completed_orders=stats.get("completed", 0),
                cancelled_orders=stats.get("cancelled", 0),
            ),
        )

    except Exception as e:
        logger.error(f"获取订单监控信息异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取订单监控信息失败: {e!s}")


@router.post("/cleanup")
async def cleanup_timeout_orders(
    order_service: OrderExecutionService = Depends(get_order_execution_service),
):
    """清理超时订单"""
    try:
        timeout_count = await order_service.cleanup_timeout_orders()

        return {
            "success": True,
            "message": f"清理了 {timeout_count} 个超时订单",
            "timeout_count": timeout_count,
        }

    except Exception as e:
        logger.error(f"清理超时订单异常: {e}")
        raise HTTPException(status_code=500, detail=f"清理超时订单失败: {e!s}")
