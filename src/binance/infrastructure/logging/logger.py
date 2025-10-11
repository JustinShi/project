"""结构化日志配置（使用structlog）"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

import structlog

from binance.config import get_settings

_LOGGER_CONFIGURED = False


def _format_console_output(logger: Any, name: str, event_dict: Dict) -> str:
    """自定义控制台日志格式化器
    
    格式: [时间] [级别] [模块] 消息 | 字段1=值1 字段2=值2
    """
    # 提取关键字段
    timestamp = event_dict.pop("timestamp", datetime.utcnow().isoformat())
    level = event_dict.pop("level", "info").upper()
    module = event_dict.pop("module", "unknown")
    event = event_dict.pop("event", "")
    
    # 简化模块名（只保留最后两级）
    module_parts = module.split(".")
    if len(module_parts) > 2:
        short_module = ".".join(module_parts[-2:])
    else:
        short_module = module
    
    # 格式化时间（只保留时分秒）
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        time_str = dt.strftime("%H:%M:%S")
    except:
        time_str = timestamp[:8] if len(timestamp) >= 8 else timestamp
    
    # 级别颜色
    level_colors = {
        "DEBUG": "\033[36m",    # 青色
        "INFO": "\033[32m",     # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",    # 红色
        "CRITICAL": "\033[35m", # 紫色
    }
    reset = "\033[0m"
    level_color = level_colors.get(level, "")
    
    # 构建基础消息
    base_msg = f"[{time_str}] {level_color}[{level:7}]{reset} [{short_module:30}] {event}"
    
    # 添加额外字段
    if event_dict:
        extra_fields = " | ".join(f"{k}={v}" for k, v in event_dict.items())
        return f"{base_msg} | {extra_fields}"
    
    return base_msg


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
    
    # 禁用 httpx 和 httpcore 的详细日志
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

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
        # JSON 格式：文件日志使用，保留完整信息
        # ensure_ascii=False 让中文正常显示，不进行 Unicode 转义
        processors.append(structlog.processors.JSONRenderer(ensure_ascii=False))
    else:
        # 控制台格式：使用自定义格式化器，更易读
        processors.append(_format_console_output)

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
        structlog绑定日志记录器，自动包含模块名称

    Example:
        logger = get_logger(__name__)
        logger.info("user_created", user_id=123, username="alice")
        # 输出会包含: {"module": "my.module.name", "event": "user_created", ...}
    """
    if not _LOGGER_CONFIGURED:
        setup_logging()

    # 绑定模块名称到 logger 的 context 中
    return structlog.get_logger().bind(module=name)

