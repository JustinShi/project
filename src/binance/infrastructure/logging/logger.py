"""结构化日志配置（使用structlog）"""

import logging
import sys
from pathlib import Path
from typing import Any

import structlog

from binance.config import get_settings

_LOGGER_CONFIGURED = False


def setup_logging() -> None:
    """初始化structlog日志配置"""
    global _LOGGER_CONFIGURED
    if _LOGGER_CONFIGURED:
        return

    settings = get_settings()

    # 确保日志目录存在
    log_file_path = Path(settings.log_file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # 配置标准库logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )

    # 添加文件处理器
    file_handler = logging.FileHandler(settings.log_file)
    file_handler.setLevel(getattr(logging, settings.log_level.upper()))
    logging.root.addHandler(file_handler)

    # 配置structlog处理器链
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    # 根据配置选择渲染器
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    _LOGGER_CONFIGURED = True


def get_logger(name: str = __name__) -> Any:
    """获取结构化日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        structlog绑定日志记录器

    Example:
        logger = get_logger(__name__)
        logger.info("user_created", user_id=123, username="alice")
    """
    if not _LOGGER_CONFIGURED:
        setup_logging()

    return structlog.get_logger(name)

