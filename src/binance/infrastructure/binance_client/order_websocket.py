"""Binance订单WebSocket客户端"""

import asyncio
import contextlib
import json
from collections.abc import Callable
from typing import Any

import websockets

from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)


class OrderWebSocketConnector:
    """订单WebSocket连接器"""

    def __init__(
        self,
        user_id: int,
        listen_key: str,
        on_order_update: Callable[[dict[str, Any]], None],
        on_connection_event: Callable[[str, dict], None] | None = None,
        reconnect_interval: int = 30,
        max_reconnect_attempts: int = 10,
    ):
        self.user_id = user_id
        self.listen_key = listen_key
        self.on_order_update = on_order_update
        self.on_connection_event = on_connection_event
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts

        self._websocket: websockets.WebSocketClientProtocol | None = None
        self._running = False
        self._reconnect_attempts = 0
        self._listen_task: asyncio.Task | None = None

    async def start(self) -> None:
        """启动WebSocket连接"""
        self._running = True
        self._reconnect_attempts = 0

        while self._running and self._reconnect_attempts < self.max_reconnect_attempts:
            try:
                await self._connect()
                # 连接成功后，等待监听任务完成（或被中断）
                if self._listen_task:
                    await self._listen_task
                # 如果监听任务正常结束，退出循环
                break
            except Exception as e:
                try:
                    logger.error(f"订单WebSocket连接异常: {e}")
                except (OSError, BrokenPipeError):
                    pass  # 控制台已关闭，静默处理
                if self._running:
                    await self._handle_reconnect()

    async def stop(self) -> None:
        """停止WebSocket连接"""
        self._running = False

        # 停止监听任务
        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await asyncio.wait_for(self._listen_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass  # 正常取消或超时

        # 关闭WebSocket连接
        if self._websocket:
            try:
                # 使用超时关闭连接
                await asyncio.wait_for(self._websocket.close(), timeout=5.0)
            except (asyncio.TimeoutError, ConnectionResetError, AttributeError) as e:
                logger.warning(f"关闭WebSocket连接异常: {e}")
            except Exception as e:
                logger.warning(f"关闭WebSocket连接异常: {e}")
            finally:
                self._websocket = None

    async def _connect(self) -> None:
        """建立WebSocket连接"""
        # 构建WebSocket URL - 币安 Alpha 的订单推送使用不同的地址
        ws_url = "wss://nbstream.binance.com/w3w/stream"

        logger.info(f"连接订单WebSocket: {ws_url}")

        try:
            # 建立WebSocket连接，添加超时和错误处理
            self._websocket = await asyncio.wait_for(
                websockets.connect(
                    ws_url,
                    ping_interval=20,  # 20秒ping间隔
                    ping_timeout=10,   # 10秒ping超时
                    close_timeout=10,  # 10秒关闭超时
                ),
                timeout=30  # 30秒连接超时
            )

            # 发送订阅消息
            subscribe_msg = {
                "method": "SUBSCRIBE",
                "params": [f"alpha@{self.listen_key}"],
                "id": 1,
            }
            await self._websocket.send(json.dumps(subscribe_msg))
            logger.info(f"已发送订阅消息: {subscribe_msg}")

            # 触发连接成功事件
            if self.on_connection_event:
                await self.on_connection_event("connected", {"url": ws_url})

            # 开始监听消息
            self._listen_task = asyncio.create_task(self._listen_messages())

            logger.info("订单WebSocket连接成功")

        except asyncio.TimeoutError:
            logger.error("WebSocket连接超时")
            if self.on_connection_event:
                await self.on_connection_event("error", {"error": "连接超时"})
            raise
        except (ConnectionResetError, AttributeError) as e:
            logger.error(f"WebSocket连接重置错误: {e}")
            if self.on_connection_event:
                await self.on_connection_event("error", {"error": f"连接重置: {e}"})
            raise
        except Exception as e:
            logger.error(f"订单WebSocket连接异常: {e}")
            if self.on_connection_event:
                await self.on_connection_event("error", {"error": str(e)})
            raise

    async def _listen_messages(self) -> None:
        """监听WebSocket消息"""
        try:
            async for message in self._websocket:
                if not self._running:
                    break
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed as e:
            try:
                logger.warning(f"WebSocket连接关闭: {e}")
            except (OSError, BrokenPipeError):
                pass  # 控制台已关闭，静默处理
            if self._running:
                await self._handle_reconnect()
        except (ConnectionResetError, AttributeError) as e:
            # 处理websockets库内部的连接错误
            try:
                logger.warning(f"WebSocket连接重置: {e}")
            except (OSError, BrokenPipeError):
                pass  # 控制台已关闭，静默处理
            if self._running:
                await self._handle_reconnect()
        except Exception as e:
            try:
                logger.error(f"监听消息异常: {e}")
            except (OSError, BrokenPipeError):
                pass  # 控制台已关闭，静默处理
            if self._running:
                await self._handle_reconnect()

    async def _handle_message(self, message: str) -> None:
        """处理WebSocket消息"""
        try:
            data = json.loads(message)

            # 打印所有收到的消息（用于调试）
            logger.info(f"收到WebSocket消息: {data}")

            # 检查是否是订阅响应
            if "result" in data or "id" in data:
                logger.info(f"订阅响应: {data}")
                return

            # 检查是否是流数据（币安Alpha格式）
            if "stream" in data and "data" in data:
                # 币安Alpha的消息格式: {"stream": "alpha@xxx", "data": {...}}
                stream = data.get("stream")
                inner_data = data.get("data")
                logger.info(f"流消息 - stream: {stream}, data: {inner_data}")

                # 处理内部数据
                if isinstance(inner_data, dict) and "e" in inner_data:
                    event_type = inner_data["e"]
                    if event_type == "executionReport":
                        await self._handle_order_execution(inner_data)
                    elif event_type == "outboundAccountPosition":
                        await self._handle_account_update(inner_data)
                    else:
                        logger.info(f"未处理的事件类型: {event_type}")
                return

            # 检查直接消息类型（标准格式）
            if "e" in data:  # 事件类型
                event_type = data["e"]

                if event_type == "executionReport":
                    # 订单执行报告
                    await self._handle_order_execution(data)
                elif event_type == "outboundAccountPosition":
                    # 账户余额更新
                    await self._handle_account_update(data)
                else:
                    logger.info(f"未处理的事件类型: {event_type}")
            else:
                logger.info(f"未识别的消息格式: {data}")

        except json.JSONDecodeError as e:
            try:
                logger.error(f"解析WebSocket消息失败: {e}")
            except (OSError, BrokenPipeError):
                pass  # 控制台已关闭，静默处理
        except Exception as e:
            try:
                logger.error(f"处理WebSocket消息异常: {e}")
            except (OSError, BrokenPipeError):
                pass  # 控制台已关闭，静默处理

    async def _handle_order_execution(self, data: dict[str, Any]) -> None:
        """处理订单执行报告"""
        try:
            order_info = {
                "user_id": self.user_id,
                "order_id": data.get("i"),  # 订单ID
                "symbol": data.get("s"),  # 交易对
                "side": data.get("S"),  # 买卖方向
                "type": data.get("o"),  # 订单类型
                "status": data.get("X"),  # 订单状态
                "price": data.get("p"),  # 价格
                "quantity": data.get("q"),  # 数量
                "executed_quantity": data.get("z"),  # 已执行数量
                "time": data.get("T"),  # 时间戳
                "client_order_id": data.get("c"),  # 客户端订单ID
                "execution_type": data.get("x"),  # 执行类型
                "order_reject_reason": data.get("r"),  # 拒绝原因
                "commission": data.get("n"),  # 手续费
                "commission_asset": data.get("N"),  # 手续费资产
            }

            logger.info(f"订单执行报告: {order_info}")

            # 调用回调函数
            if self.on_order_update:
                await self.on_order_update(order_info)

        except Exception as e:
            logger.error(f"处理订单执行报告异常: {e}")

    async def _handle_account_update(self, data: dict[str, Any]) -> None:
        """处理账户余额更新"""
        try:
            account_info = {
                "user_id": self.user_id,
                "event_type": "account_update",
                "balances": data.get("B", []),
                "time": data.get("E"),
            }

            logger.info(f"账户余额更新: {account_info}")

            # 调用回调函数
            if self.on_order_update:
                await self.on_order_update(account_info)

        except Exception as e:
            logger.error(f"处理账户更新异常: {e}")

    async def _handle_connection_event(self, event_type: str, data: dict) -> None:
        """处理连接事件"""
        logger.info(f"订单WebSocket连接事件: {event_type}")

        if event_type == "connected":
            self._reconnect_attempts = 0
            logger.info("订单WebSocket连接成功")
        elif event_type == "disconnected":
            logger.warning("订单WebSocket连接断开")
            if self._running:
                await self._handle_reconnect()
        elif event_type == "error":
            logger.error(f"订单WebSocket连接错误: {data}")
            if self._running:
                await self._handle_reconnect()

        # 调用外部回调
        if self.on_connection_event:
            await self.on_connection_event(event_type, data)

    async def _handle_reconnect(self) -> None:
        """处理重连"""
        if not self._running:
            return

        self._reconnect_attempts += 1
        wait_time = min(
            self.reconnect_interval * self._reconnect_attempts, 300
        )  # 最大5分钟

        logger.info(
            f"订单WebSocket重连尝试 {self._reconnect_attempts}/{self.max_reconnect_attempts}, 等待 {wait_time} 秒"
        )

        await asyncio.sleep(wait_time)

    def is_connected(self) -> bool:
        """检查是否已连接"""
        if self._websocket is None:
            return False
        # 检查监听任务是否在运行
        if self._listen_task and not self._listen_task.done():
            return True
        # websockets 库：检查连接状态
        try:
            # ClientConnection 对象有 state 属性，State.OPEN 表示连接中
            from websockets.protocol import State

            return self._websocket.state == State.OPEN
        except Exception:
            # 如果检查失败，看监听任务是否还在运行
            return self._listen_task is not None and not self._listen_task.done()

    def get_connection_info(self) -> dict[str, Any]:
        """获取连接信息"""
        return {
            "user_id": self.user_id,
            "listen_key": self.listen_key,
            "connected": self.is_connected(),
            "reconnect_attempts": self._reconnect_attempts,
            "max_reconnect_attempts": self.max_reconnect_attempts,
        }
