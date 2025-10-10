"""订单执行服务"""

import asyncio
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal

from binance.domain.entities.oto_order_pair import OTOOrderPair
from binance.domain.entities.price_data import PriceData
from binance.domain.services.oto_order_executor import OTOOrderExecutor
from binance.domain.services.order_state_machine import OrderStateMachine
from binance.infrastructure.binance_client.oto_order_client import BinanceOTOOrderClient
from binance.infrastructure.binance_client.order_websocket import OrderWebSocketConnector
from binance.infrastructure.binance_client.listen_key_manager import ListenKeyManager
from binance.infrastructure.logging.logger import get_logger
from binance.application.services.notification_service import NotificationService
from binance.config.constants import OTOOrderPairStatus
from binance.infrastructure.config import TradingTarget

logger = get_logger(__name__)


class OrderExecutionService:
    """订单执行服务"""
    
    def __init__(self, notification_service: Optional[NotificationService] = None):
        self.order_state_machine = OrderStateMachine()
        self.order_executor = OTOOrderExecutor(self.order_state_machine)
        self._active_connections: Dict[int, OrderWebSocketConnector] = {}
        self._listen_key_managers: Dict[int, ListenKeyManager] = {}
        self._notification_service = notification_service
        self._blocked_users: set[int] = set()
    
    async def execute_oto_order(
        self,
        user_id: int,
        symbol: str,
        current_price: PriceData,
        config: TradingTarget,
        headers: Dict[str, str],
        cookies: str
    ) -> Tuple[bool, str, Optional[OTOOrderPair]]:
        """执行OTO订单"""
        try:
            if user_id in self._blocked_users:
                message = "用户尚未完成补充认证，已暂停交易。"
                logger.warning(message, user_id=user_id)
                return False, message, None

            # 检查是否可以执行订单
            can_execute, reason = self.order_executor.can_execute_order(
                user_id, symbol, current_price, config
            )
            
            if not can_execute:
                logger.warning(f"用户 {user_id} 无法执行订单: {reason}")
                return False, reason, None
            
            # 计算订单价格
            buy_price, sell_price = self.order_executor.calculate_order_prices(
                current_price, config
            )
            
            # 验证订单参数
            is_valid, validation_reason = self.order_executor.validate_order_parameters(
                symbol, config.order_quantity, buy_price, sell_price
            )
            
            if not is_valid:
                logger.warning(f"订单参数验证失败: {validation_reason}")
                return False, validation_reason, None
            
            # 创建订单对（使用临时ID，实际应该从数据库获取）
            temp_order_id = int(datetime.now().timestamp() * 1000) % 1000000  # 简单的临时ID生成
            order_pair = self.order_executor.create_order_pair(
                user_id=user_id,
                symbol=symbol,
                quantity=config.order_quantity,
                buy_price=buy_price,
                sell_price=sell_price,
                order_pair_id=temp_order_id
            )
            
            # 下OTO订单
            async with BinanceOTOOrderClient(headers, cookies) as oto_client:
                success, message, order_info = await oto_client.place_oto_order(
                    symbol=symbol,
                    quantity=config.order_quantity,
                    buy_price=buy_price,
                    sell_price=sell_price,
                    precision=None,
                    chain=config.chain
                )
                
                if success and order_info:
                    # 更新订单信息
                    buy_order_id = order_info.get("orderId")
                    if buy_order_id:
                        self.order_executor.update_buy_order(order_pair.id, str(buy_order_id))
                        logger.info(f"OTO订单下单成功: {order_pair.id}, 订单ID: {buy_order_id}")
                        
                        # 启动WebSocket监听
                        await self._start_order_monitoring(user_id, headers, cookies)
                        
                        return True, "订单执行成功", order_pair
                    else:
                        logger.error(f"订单信息中缺少订单ID: {order_info}")
                        return False, "订单信息不完整", None
                else:
                    logger.error(f"OTO订单下单失败: {message}")
                    if message and "补充认证失败" in message:
                        self._blocked_users.add(user_id)
                        block_msg = "用户因补充认证未完成被暂停交易，请完成认证后再尝试。"
                        logger.error(block_msg, user_id=user_id)
                        return False, block_msg, None
                    return False, message, None
                    
        except Exception as e:
            error_msg = f"执行OTO订单异常: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    async def _start_order_monitoring(self, user_id: int, headers: Dict[str, str], cookies: str):
        """启动订单监控"""
        try:
            # 检查是否已有连接
            if user_id in self._active_connections:
                logger.info(f"用户 {user_id} 已有订单监控连接")
                return
            
            # 获取ListenKey
            listen_key_manager = ListenKeyManager(headers, cookies)
            async with listen_key_manager:
                success, message, listen_key = await listen_key_manager.get_listen_key()
                
                if not success or not listen_key:
                    logger.error(f"获取ListenKey失败: {message}")
                    return
                
                # 创建订单WebSocket连接
                order_connector = OrderWebSocketConnector(
                    user_id=user_id,
                    listen_key=listen_key,
                    on_order_update=self._handle_order_update,
                    on_connection_event=self._handle_connection_event
                )
                
                # 启动连接
                self._active_connections[user_id] = order_connector
                self._listen_key_managers[user_id] = listen_key_manager
                
                # 异步启动WebSocket连接
                asyncio.create_task(order_connector.start())
                
                logger.info(f"用户 {user_id} 订单监控已启动")
                
        except Exception as e:
            logger.error(f"启动订单监控异常: {e}")
    
    async def _handle_order_update(self, order_data: Dict[str, Any]):
        """处理订单更新"""
        try:
            user_id = order_data.get("user_id")
            order_id = order_data.get("order_id")
            status = order_data.get("status")
            side = order_data.get("side")
            
            logger.info(f"收到订单更新: 用户={user_id}, 订单={order_id}, 状态={status}, 方向={side}")
            
            # 查找对应的订单对
            order_pair = self.order_state_machine.get_user_active_order(user_id)
            if not order_pair:
                logger.warning(f"未找到用户 {user_id} 的活跃订单")
                return
            
            # 根据订单状态更新订单对
            if status == "FILLED":
                if side == "BUY":
                    # 买单成交
                    self.order_executor.mark_buy_filled(order_pair.id)
                    logger.info(f"买单成交: {order_pair.id}")
                    # 可选通知：买单完成
                    if self._notification_service:
                        # 买单成交后通常不通知暂停/恢复，仅做信息通知
                        await self._notification_service._send_user_notification(
                            user_id=user_id,
                            type="buy_filled",
                            title="买单成交",
                            message=f"订单 {order_pair.id} 买单已成交",
                            data={"order_id": order_pair.id, "symbol": order_pair.symbol}
                        )
                elif side == "SELL":
                    # 卖单成交
                    self.order_executor.mark_sell_filled(order_pair.id)
                    logger.info(f"卖单成交: {order_pair.id}")
                    
                    logger.info(f"订单完成: {order_pair.id}")
                    # 通知交易完成
                    if self._notification_service:
                        await self._notification_service._send_user_notification(
                            user_id=user_id,
                            type="order_completed",
                            title="订单完成",
                            message=f"订单 {order_pair.id} 已完成",
                            data={
                                "order_id": order_pair.id,
                                "symbol": order_pair.symbol
                            }
                        )
            elif status == "CANCELLED":
                # 订单取消
                self.order_executor.mark_cancelled(order_pair.id)
                logger.info(f"订单取消: {order_pair.id}")
                if self._notification_service:
                    await self._notification_service._send_user_notification(
                        user_id=user_id,
                        type="order_cancelled",
                        title="订单已取消",
                        message=f"订单 {order_pair.id} 已被取消",
                        data={"order_id": order_pair.id, "symbol": order_pair.symbol}
                    )
            elif status == "REJECTED":
                # 订单被拒绝
                self.order_executor.mark_cancelled(order_pair.id)
                logger.warning(f"订单被拒绝: {order_pair.id}")
                if self._notification_service:
                    await self._notification_service._send_user_notification(
                        user_id=user_id,
                        type="order_rejected",
                        title="订单被拒绝",
                        message=f"订单 {order_pair.id} 被拒绝",
                        data={"order_id": order_pair.id, "symbol": order_pair.symbol}
                    )
                
        except Exception as e:
            logger.error(f"处理订单更新异常: {e}")
    
    async def _handle_connection_event(self, event_type: str, data: Dict):
        """处理连接事件"""
        logger.info(f"订单监控连接事件: {event_type}")
        
        if event_type == "disconnected":
            # 连接断开，需要重新连接
            logger.warning("订单监控连接断开，将尝试重连")
        elif event_type == "error":
            logger.error(f"订单监控连接错误: {data}")
    
    async def stop_order_monitoring(self, user_id: int):
        """停止订单监控"""
        try:
            if user_id in self._active_connections:
                await self._active_connections[user_id].stop()
                del self._active_connections[user_id]
                logger.info(f"用户 {user_id} 订单监控已停止")
            
            if user_id in self._listen_key_managers:
                await self._listen_key_managers[user_id].close()
                del self._listen_key_managers[user_id]
                logger.info(f"用户 {user_id} ListenKey管理器已关闭")
                
        except Exception as e:
            logger.error(f"停止订单监控异常: {e}")
    
    async def get_user_active_order(self, user_id: int) -> Optional[OTOOrderPair]:
        """获取用户活跃订单"""
        return self.order_executor.get_user_active_order(user_id)
    
    async def cancel_user_order(self, user_id: int, symbol: str, headers: Dict[str, str], cookies: str) -> Tuple[bool, str]:
        """取消用户订单"""
        try:
            # 获取用户活跃订单
            order_pair = await self.get_user_active_order(user_id)
            if not order_pair:
                return False, "用户没有活跃订单"
            
            # 取消订单
            async with BinanceOTOOrderClient(headers, cookies) as oto_client:
                if order_pair.buy_order_id:
                    success, message = await oto_client.cancel_order(symbol, order_pair.buy_order_id)
                    if not success:
                        return False, f"取消买单失败: {message}"
                
                if order_pair.sell_order_id:
                    success, message = await oto_client.cancel_order(symbol, order_pair.sell_order_id)
                    if not success:
                        return False, f"取消卖单失败: {message}"
            
            # 标记订单为已取消
            self.order_executor.mark_cancelled(order_pair.id)
            
            return True, "订单取消成功"
            
        except Exception as e:
            error_msg = f"取消订单异常: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    async def get_order_statistics(self) -> Dict[str, Any]:
        """获取订单统计"""
        return self.order_executor.get_order_statistics()
    
    async def cleanup_timeout_orders(self) -> int:
        """清理超时订单"""
        cleaned = self.order_executor.cleanup_timeout_orders()
        # 发送超时通知（无法逐个获取，这里仅记录数量；实际实现可返回被清理的ID列表）
        if cleaned > 0:
            logger.warning(f"清理了 {cleaned} 个超时订单")
        return cleaned
    
    async def close_all_connections(self):
        """关闭所有连接"""
        try:
            # 停止所有订单监控
            for user_id in list(self._active_connections.keys()):
                await self.stop_order_monitoring(user_id)
            
            logger.info("所有订单监控连接已关闭")
            
        except Exception as e:
            logger.error(f"关闭所有连接异常: {e}")
