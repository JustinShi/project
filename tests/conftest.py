"""
测试配置文件
提供测试用的fixtures和工具函数
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from src.BinanceTools.config.user_config import UserConfig, ApiConfig, WebSocketConfig


@pytest.fixture
def temp_config_dir():
    """创建临时配置目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "configs" / "binance"
        config_dir.mkdir(parents=True, exist_ok=True)
        yield config_dir


@pytest.fixture
def sample_users_config():
    """示例用户配置数据"""
    return {
        "users": [
            {
                "id": "test_user_001",
                "name": "测试用户1",
                "enabled": True,
                "headers": {
                    "User-Agent": "Test-Agent/1.0",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                "cookies": {
                    "session_id": "test_session_001",
                    "auth_token": "test_auth_token_001"
                }
            },
            {
                "id": "test_user_002",
                "name": "测试用户2",
                "enabled": False,
                "headers": {
                    "User-Agent": "Test-Agent/2.0",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                "cookies": {
                    "session_id": "test_session_002",
                    "auth_token": "test_auth_token_002"
                }
            }
        ],
        "default_user": "test_user_001"
    }


@pytest.fixture
def sample_api_config():
    """示例API配置数据"""
    return {
        "api_config": {
            "base_url": "https://test.example.com",
            "timeout": 30,
            "retry_times": 3,
            "endpoints": {
                "user_volume": "/api/v1/user/volume",
                "wallet_balance": "/api/v1/wallet/balance",
                "place_oto_order": "/api/v1/order/place",
                "get_listen_key": "/api/v1/stream/listen-key"
            }
        },
        "websocket_config": {
            "stream_url": "wss://test.example.com/stream",
            "order_stream_url": "wss://test.example.com/order-stream",
            "ping_interval": 30,
            "reconnect_interval": 5,
            "max_reconnect_attempts": 10
        }
    }


@pytest.fixture
def users_config_file(temp_config_dir, sample_users_config):
    """创建用户配置文件"""
    users_file = temp_config_dir / "users.json"
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(sample_users_config, f, ensure_ascii=False, indent=2)
    return users_file


@pytest.fixture
def api_config_file(temp_config_dir, sample_api_config):
    """创建API配置文件"""
    api_file = temp_config_dir / "api_config.json"
    with open(api_file, 'w', encoding='utf-8') as f:
        json.dump(sample_api_config, f, ensure_ascii=False, indent=2)
    return api_file


@pytest.fixture
def sample_user_config():
    """示例用户配置对象"""
    return UserConfig(
        id="test_user_001",
        name="测试用户1",
        enabled=True,
        headers={
            "User-Agent": "Test-Agent/1.0",
            "Accept": "application/json"
        },
        cookies={
            "session_id": "test_session_001",
            "auth_token": "test_auth_token_001"
        }
    )


@pytest.fixture
def sample_api_config_obj():
    """示例API配置对象"""
    return ApiConfig(
        base_url="https://test.example.com",
        timeout=30,
        retry_times=3,
        endpoints={
            "user_volume": "/api/v1/user/volume",
            "wallet_balance": "/api/v1/wallet/balance"
        }
    )


@pytest.fixture
def sample_websocket_config():
    """示例WebSocket配置对象"""
    return WebSocketConfig(
        stream_url="wss://test.example.com/stream",
        order_stream_url="wss://test.example.com/order-stream",
        ping_interval=30,
        reconnect_interval=5,
        max_reconnect_attempts=10
    )


@pytest.fixture
def mock_api_response():
    """模拟API响应"""
    return {
        "code": "000000",
        "message": None,
        "messageDetail": None,
        "data": {
            "totalVolume": 1000.0,
            "tradeVolumeInfoList": [
                {
                    "icon": "/test/icon.png",
                    "tokenName": "TEST",
                    "volume": 1000.0
                }
            ]
        },
        "success": True
    }


@pytest.fixture
def mock_wallet_response():
    """模拟钱包响应"""
    return {
        "code": "000000",
        "message": None,
        "messageDetail": None,
        "data": {
            "totalValuation": "100.50",
            "list": [
                {
                    "chainId": "56",
                    "contractAddress": "0x123456789",
                    "cexAsset": False,
                    "name": "Test Token",
                    "symbol": "TEST",
                    "tokenId": "TEST_001",
                    "free": "100.0",
                    "freeze": "0",
                    "locked": "0",
                    "withdrawing": "0",
                    "amount": "100.0",
                    "valuation": "100.50"
                }
            ]
        },
        "success": True
    }


@pytest.fixture
def mock_order_response():
    """模拟订单响应"""
    return {
        "code": "000000",
        "message": None,
        "messageDetail": None,
        "data": {
            "workingOrderId": 12345,
            "pendingOrderId": 12346
        },
        "success": True
    }


@pytest.fixture
def mock_listen_key_response():
    """模拟ListenKey响应"""
    return {
        "listenKey": "test_listen_key_123456789"
    }


@pytest.fixture
def mock_aiohttp_session():
    """模拟aiohttp会话"""
    session = AsyncMock()
    session.close = AsyncMock()
    session.request = AsyncMock()
    session.cookie_jar = Mock()
    session.cookie_jar.update_cookies = Mock()
    return session


@pytest.fixture
def mock_websocket():
    """模拟WebSocket连接"""
    ws = AsyncMock()
    ws.send = AsyncMock()
    ws.close = AsyncMock()
    ws.ping = AsyncMock()
    ws.closed = False
    return ws


class MockResponse:
    """模拟HTTP响应"""
    def __init__(self, status: int, data: Dict[str, Any]):
        self.status = status
        self.data = data
        self.headers = {"Content-Type": "application/json"}
    
    async def json(self):
        return self.data
    
    async def text(self):
        return json.dumps(self.data)


@pytest.fixture
def mock_http_response(mock_api_response):
    """模拟HTTP响应对象"""
    def create_response(status=200, data=None):
        if data is None:
            data = mock_api_response
        return MockResponse(status, data)
    return create_response


@pytest.fixture
def event_loop():
    """提供事件循环"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
