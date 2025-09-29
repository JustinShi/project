"""验证码类型定义模块"""

from .enums import (
    CaptchaType,
    ErrorCode,
    ImageFormat,
    ProcessingMode,
    ResultStatus,
    ServiceType,
)
from .exceptions import (
    AuthenticationError,
    CaptchaError,
    ConfigError,
    InsufficientBalanceError,
    NetworkError,
    RateLimitError,
    RecognitionError,
    ServiceError,
    TimeoutError,
    UnsupportedTypeError,
    ValidationError,
)


__all__ = [
    # 枚举类型
    "CaptchaType",
    "ErrorCode",
    "ImageFormat",
    "ProcessingMode",
    "ResultStatus",
    "ServiceType",
    # 异常类型
    "AuthenticationError",
    "CaptchaError",
    "ConfigError",
    "InsufficientBalanceError",
    "NetworkError",
    "RateLimitError",
    "RecognitionError",
    "ServiceError",
    "TimeoutError",
    "UnsupportedTypeError",
    "ValidationError",
]
