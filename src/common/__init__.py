"""
通用模块
提供多项目平台的基础功能和工具
"""

# 配置管理
from .config import Config

# 日志管理
from .logging import get_logger, setup_logger

# 网络相关
from .network import HTTPClient, HTTPClientError


__all__ = [
    # 配置
    "Config",
    # 网络
    "HTTPClient",
    "HTTPClientError",
    # 日志
    "get_logger",
    "setup_logger",
]

__version__ = "0.1.0"
