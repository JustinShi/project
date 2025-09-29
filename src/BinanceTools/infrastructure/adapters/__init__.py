"""
Infrastructure Adapters

适配器，封装外部依赖的接口。
"""

from .http_adapter import HttpAdapter
from .websocket_adapter import WebSocketAdapter

__all__ = [
    "HttpAdapter",
    "WebSocketAdapter"
]
