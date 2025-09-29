"""
币安WebSocket客户端

与币安WebSocket API交互的客户端。
"""

import asyncio
import json
import websockets
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime

from ..config.api_config import ApiConfig


class BinanceWebSocketClient:
    """币安WebSocket客户端"""
    
    def __init__(self, api_config: ApiConfig):
        """初始化WebSocket客户端"""
        self.api_config = api_config
        self.ws_url = "wss://nbstream.binance.com/w3w/wsa/stream"
        self.private_ws_url = "wss://nbstream.binance.com/w3w/stream"
        self.connections = {}
        self.subscriptions = {}
        self.message_handlers = {}
    
    async def connect_public_stream(self, stream_name: str) -> bool:
        """连接公共流"""
        try:
            websocket = await websockets.connect(self.ws_url)
            self.connections[stream_name] = websocket
            
            # 启动消息处理任务
            asyncio.create_task(self._handle_messages(stream_name, websocket))
            
            return True
        except Exception as e:
            print(f"连接公共流失败: {e}")
            return False
    
    async def connect_private_stream(self, stream_name: str, listen_key: str) -> bool:
        """连接私有流"""
        try:
            websocket = await websockets.connect(self.private_ws_url)
            self.connections[stream_name] = websocket
            
            # 启动消息处理任务
            asyncio.create_task(self._handle_messages(stream_name, websocket))
            
            return True
        except Exception as e:
            print(f"连接私有流失败: {e}")
            return False
    
    async def subscribe_to_ticker(self, symbol: str) -> bool:
        """订阅价格行情"""
        stream_name = f"ticker_{symbol}"
        
        if stream_name in self.connections:
            return True
        
        if not await self.connect_public_stream(stream_name):
            return False
        
        # 发送订阅消息
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@ticker"],
            "id": 1
        }
        
        try:
            await self.connections[stream_name].send(json.dumps(subscribe_message))
            self.subscriptions[stream_name] = subscribe_message
            return True
        except Exception as e:
            print(f"订阅价格行情失败: {e}")
            return False
    
    async def subscribe_to_trades(self, symbol: str) -> bool:
        """订阅交易数据"""
        stream_name = f"trades_{symbol}"
        
        if stream_name in self.connections:
            return True
        
        if not await self.connect_public_stream(stream_name):
            return False
        
        # 发送订阅消息
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@aggTrade"],
            "id": 1
        }
        
        try:
            await self.connections[stream_name].send(json.dumps(subscribe_message))
            self.subscriptions[stream_name] = subscribe_message
            return True
        except Exception as e:
            print(f"订阅交易数据失败: {e}")
            return False
    
    async def subscribe_to_user_data(self, listen_key: str) -> bool:
        """订阅用户数据"""
        stream_name = f"user_data_{listen_key}"
        
        if stream_name in self.connections:
            return True
        
        if not await self.connect_private_stream(stream_name, listen_key):
            return False
        
        # 发送订阅消息
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [f"alpha@{listen_key}"],
            "id": 1
        }
        
        try:
            await self.connections[stream_name].send(json.dumps(subscribe_message))
            self.subscriptions[stream_name] = subscribe_message
            return True
        except Exception as e:
            print(f"订阅用户数据失败: {e}")
            return False
    
    def set_message_handler(self, stream_name: str, handler: Callable[[Dict[str, Any]], None]):
        """设置消息处理器"""
        self.message_handlers[stream_name] = handler
    
    async def _handle_messages(self, stream_name: str, websocket):
        """处理WebSocket消息"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    # 调用消息处理器
                    if stream_name in self.message_handlers:
                        await self.message_handlers[stream_name](data)
                    
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
            if stream_name in self.subscriptions:
                del self.subscriptions[stream_name]
            if stream_name in self.message_handlers:
                del self.message_handlers[stream_name]
    
    async def disconnect(self, stream_name: str) -> bool:
        """断开连接"""
        if stream_name in self.connections:
            try:
                await self.connections[stream_name].close()
                del self.connections[stream_name]
                return True
            except Exception as e:
                print(f"断开连接失败: {e}")
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
