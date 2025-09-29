"""
日志管理模块
基于loguru的统一日志管理
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from ..config import config


def setup_logger():
    """设置日志配置"""
    # 移除默认的日志处理器
    logger.remove()

    # 创建日志目录
    log_dir = Path(config.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # 控制台日志格�?
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # 文件日志格式
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )

    # 添加控制台处理器
    logger.add(sys.stdout, format=console_format, level=config.log_level, colorize=True)

    # 添加文件处理�?
    logger.add(
        config.log_file,
        format=file_format,
        level=config.log_level,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )

    # 添加错误日志文件
    error_log_file = str(log_dir / "error.log")
    logger.add(
        error_log_file,
        format=file_format,
        level="ERROR",
        rotation="50 MB",
        retention="60 days",
        compression="zip",
        encoding="utf-8",
    )


def get_logger(name: Optional[str] = None):
    """
    获取日志记录�?

    Args:
        name: 日志记录器名称，通常使用模块�?

    Returns:
        loguru.Logger: 配置好的日志记录�?
    """
    if name:
        return logger.bind(name=name)
    return logger


# 初始化日志配�?
setup_logger()

# 导出主日志记录器
__all__ = ["get_logger", "logger"]
