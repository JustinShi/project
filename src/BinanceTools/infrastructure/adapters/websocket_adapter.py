"""
WebSocket适配器

封装WebSocket连接的适配器。
"""

import asyncio
import json
import websockets
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

from ..config.proxy_config import ProxyConfig


class WebSocketAdapter:
    """WebSocket适配器"""
    
    def __init__(self, proxy_config: ProxyConfig):
        """初始化适配器"""
        self.proxy_config = proxy_config
        self.connections = {}
        self.message_handlers = {}
    
    async def connect(
        self,
        url: str,
        stream_name: str,
        message_handler: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> bool:
        """连接WebSocket"""
        try:
            # 配置代理
            proxy = None
            if self.proxy_config.is_enabled():
                proxy = self.proxy_config.get_proxy_url()
            
            # 连接WebSocket
            websocket = await websockets.connect(url, proxy=proxy)
            self.connections[stream_name] = websocket
            
            # 设置消息处理器
            if message_handler:
                self.message_handlers[stream_name] = message_handler
            
            # 启动消息处理任务
            asyncio.create_task(self._handle_messages(stream_name, websocket))
            
            return True
            
        except Exception as e:
            print(f"WebSocket连接失败: {e}")
            return False
    
    async def send_message(
        self,
        stream_name: str,
        message: Dict[str, Any]
    ) -> bool:
        """发送消息"""
        if stream_name not in self.connections:
            return False
        
        try:
            websocket = self.connections[stream_name]
            await websocket.send(json.dumps(message))
            return True
            
        except Exception as e:
            print(f"发送WebSocket消息失败: {e}")
            return False
    
    async def subscribe(
        self,
        stream_name: str,
        params: List[str],
        message_id: int = 1
    ) -> bool:
        """订阅流"""
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": params,
            "id": message_id
        }
        
        return await self.send_message(stream_name, subscribe_message)
    
    async def unsubscribe(
        self,
        stream_name: str,
        params: List[str],
        message_id: int = 1
    ) -> bool:
        """取消订阅流"""
        unsubscribe_message = {
            "method": "UNSUBSCRIBE",
            "params": params,
            "id": message_id
        }
        
        return await self.send_message(stream_name, unsubscribe_message)
    
    async def _handle_messages(self, stream_name: str, websocket):
        """处理WebSocket消息"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    # 调用消息处理器
                    if stream_name in self.message_handlers:
                        handler = self.message_handlers[stream_name]
                        if asyncio.iscoroutinefunction(handler):
                            await handler(data)
                        else:
                            handler(data)
                    
                except json.JSONDecodeError as e:
                    print(f"解析WebSocket消息失败: {e}")
                except Exception as e:
                    print(f"处理WebSocket消息失败: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"WebSocket连接已关闭: {stream_name}")
        except Exception as e:
            print(f"WebSocket消息处理异常: {e}")
        finally:
            # 清理连接
            if stream_name in self.connections:
                del self.connections[stream_name]
            if stream_name in self.message_handlers:
                del self.message_handlers[stream_name]
    
    async def disconnect(self, stream_name: str) -> bool:
        """断开连接"""
        if stream_name in self.connections:
            try:
                websocket = self.connections[stream_name]
                await websocket.close()
                del self.connections[stream_name]
                return True
            except Exception as e:
                print(f"断开WebSocket连接失败: {e}")
                return False
        return True
    
    async def disconnect_all(self):
        """断开所有连接"""
        for stream_name in list(self.connections.keys()):
            await self.disconnect(stream_name)
    
    def get_connection_status(self) -> Dict[str, bool]:
        """获取连接状态"""
        return {
            stream_name: websocket.open
            for stream_name, websocket in self.connections.items()
        }
    
    def is_connected(self, stream_name: str) -> bool:
        """检查是否已连接"""
        return stream_name in self.connections and self.connections[stream_name].open
    
    async def ping(self, stream_name: str) -> bool:
        """发送ping"""
        if stream_name not in self.connections:
            return False
        
        try:
            websocket = self.connections[stream_name]
            await websocket.ping()
            return True
        except Exception as e:
            print(f"WebSocket ping失败: {e}")
            return False
    
    async def close(self):
        """关闭所有连接"""
        await self.disconnect_all()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
