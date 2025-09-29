"""验证码识别模块"""

from .base import BaseCaptchaClient, CaptchaResult
from .chaojiying.client import ChaojiyingClient
from .config import CaptchaConfig
from .types import CaptchaType, ResultStatus, ServiceType
from .types.exceptions import CaptchaError, ConfigError, NetworkError


# 导出主要类
__all__ = [
    # 核心类
    "BaseCaptchaClient",
    "CaptchaConfig",
    # 异常
    "CaptchaError",
    "CaptchaResult",
    # 类型和枚举
    "CaptchaType",
    # 客户端
    "ChaojiyingClient",
    "ConfigError",
    "NetworkError",
    "ResultStatus",
    "ServiceType",
    # 工具函数
    "create_client",
    "get_available_services",
    "get_supported_types",
]


# 便捷函数
def create_client(service: str = "chaojiying", **kwargs) -> BaseCaptchaClient:
    """
    创建验证码识别客户端

    Args:
        service: 服务名称 ("chaojiying", "ruokuai", "2captcha", "local")
        **kwargs: 其他参数

    Returns:
        BaseCaptchaClient: 验证码识别客户端
    """
    if service == "chaojiying":
        return ChaojiyingClient(**kwargs)
    elif service == "ruokuai":
        # 未来实现
        raise NotImplementedError("若快服务暂未实现")
    elif service == "2captcha":
        # 未来实现
        raise NotImplementedError("2captcha服务暂未实现")
    elif service == "local":
        # 未来实现
        raise NotImplementedError("本地识别服务暂未实现")
    else:
        raise ValueError(f"不支持的服务: {service}")


def get_available_services() -> list:
    """获取可用的验证码识别服务"""
    return ["chaojiying"]  # 目前只支持超级鹰


def get_supported_types(service: str = "chaojiying") -> dict:
    """
    获取指定服务支持的验证码类型

    Args:
        service: 服务名称

    Returns:
        dict: 支持的验证码类型字典
    """
    if service == "chaojiying":
        return {
            "1902": "通用数字英文验证码",
            "1004": "4位纯数字验证码",
            "1005": "5位纯数字验证码",
            "1006": "6位纯数字验证码",
            "2004": "4位纯英文验证码",
            "3004": "4位英文数字验证码",
            "3005": "5位英文数字验证码",
            "3006": "6位英文数字验证码",
            "4004": "4位纯中文验证码",
            "5000": "无类型验证码",
        }
    else:
        return {}
