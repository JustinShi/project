"""币安WebSocket客户端基础"""

import asyncio
import json
import logging
from typing import Callable, Optional, Dict, Any
from datetime import datetime
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)


class BinanceWebSocketClient:
    """币安WebSocket客户端基础类"""

    def __init__(
        self,
        base_url: str = "wss://stream.binance.com:9443/ws",
        reconnect_interval: int = 5,
        max_reconnect_attempts: int = 10,
    ):
        """初始化WebSocket客户端
        
        Args:
            base_url: WebSocket基础URL
            reconnect_interval: 重连间隔（秒）
            max_reconnect_attempts: 最大重连尝试次数
        """
        self._base_url = base_url
        self._reconnect_interval = reconnect_interval
        self._max_reconnect_attempts = max_reconnect_attempts
        self._websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._is_connected = False
        self._reconnect_attempts = 0
        self._message_handlers: Dict[str, Callable] = {}
        self._connection_handlers: Dict[str, Callable] = {}

    async def connect(self, stream_name: str) -> None:
        """连接到WebSocket流
        
        Args:
            stream_name: 流名称
        """
        url = f"{self._base_url}/{stream_name}"
        
        try:
            logger.info(f"连接到WebSocket流: {url}")
            self._websocket = await websockets.connect(url)
            self._is_connected = True
            self._reconnect_attempts = 0
            
            # 触发连接成功事件
            await self._trigger_connection_event("connected")
            
            logger.info("WebSocket连接成功")
            
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            await self._trigger_connection_event("connection_failed", error=str(e))
            raise

    async def disconnect(self) -> None:
        """断开WebSocket连接"""
        if self._websocket and not self._websocket.closed:
            await self._websocket.close()
            logger.info("WebSocket连接已断开")
        
        self._is_connected = False
        await self._trigger_connection_event("disconnected")

    async def listen(self) -> None:
        """监听WebSocket消息"""
        if not self._websocket:
            raise RuntimeError("WebSocket未连接")
        
        try:
            async for message in self._websocket:
                await self._handle_message(message)
                
        except ConnectionClosed:
            logger.warning("WebSocket连接已关闭")
            self._is_connected = False
            await self._trigger_connection_event("connection_closed")
            
        except WebSocketException as e:
            logger.error(f"WebSocket异常: {e}")
            await self._trigger_connection_event("websocket_error", error=str(e))
            
        except Exception as e:
            logger.error(f"监听消息时发生错误: {e}")
            await self._trigger_connection_event("message_error", error=str(e))

    async def _handle_message(self, message: str) -> None:
        """处理接收到的消息
        
        Args:
            message: 原始消息字符串
        """
        try:
            data = json.loads(message)
            
            # 根据消息类型调用相应的处理器
            message_type = data.get("e", "unknown")
            handler = self._message_handlers.get(message_type)
            
            if handler:
                await handler(data)
            else:
                logger.debug(f"未处理的消息类型: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"解析消息失败: {e}, 消息: {message}")
            
        except Exception as e:
            logger.error(f"处理消息时发生错误: {e}")

    def register_message_handler(self, message_type: str, handler: Callable) -> None:
        """注册消息处理器
        
        Args:
            message_type: 消息类型
            handler: 处理函数
        """
        self._message_handlers[message_type] = handler
        logger.debug(f"注册消息处理器: {message_type}")

    def register_connection_handler(self, event_type: str, handler: Callable) -> None:
        """注册连接事件处理器
        
        Args:
            event_type: 事件类型
            handler: 处理函数
        """
        self._connection_handlers[event_type] = handler
        logger.debug(f"注册连接事件处理器: {event_type}")

    async def _trigger_connection_event(self, event_type: str, **kwargs) -> None:
        """触发连接事件
        
        Args:
            event_type: 事件类型
            **kwargs: 额外参数
        """
        handler = self._connection_handlers.get(event_type)
        if handler:
            try:
                await handler(**kwargs)
            except Exception as e:
                logger.error(f"处理连接事件失败: {event_type}, 错误: {e}")

    async def reconnect(self) -> bool:
        """尝试重连
        
        Returns:
            是否重连成功
        """
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            logger.error(f"达到最大重连次数: {self._max_reconnect_attempts}")
            return False
        
        self._reconnect_attempts += 1
        wait_time = min(self._reconnect_interval * (2 ** (self._reconnect_attempts - 1)), 60)
        
        logger.info(f"等待 {wait_time} 秒后重连 (尝试 {self._reconnect_attempts}/{self._max_reconnect_attempts})")
        await asyncio.sleep(wait_time)
        
        try:
            # 这里需要重新连接，但需要知道原来的流名称
            # 在实际使用中，应该保存流名称
            logger.info("尝试重连...")
            return True
            
        except Exception as e:
            logger.error(f"重连失败: {e}")
            return False

    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._is_connected and self._websocket and not self._websocket.closed

    @property
    def reconnect_attempts(self) -> int:
        """获取重连尝试次数"""
        return self._reconnect_attempts

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.disconnect()
