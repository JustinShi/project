"""验证码相关枚举类型"""

from enum import Enum


class CaptchaType(Enum):
    """验证码类型枚举"""

    # 通用类型
    GENERAL = "1902"  # 通用数字英文验证码

    # 数字类型
    DIGIT_4 = "1004"  # 4位纯数字验证码
    DIGIT_5 = "1005"  # 5位纯数字验证码
    DIGIT_6 = "1006"  # 6位纯数字验证码

    # 英文类型
    LETTER_4 = "2004"  # 4位纯英文验证码

    # 混合类型
    MIXED_4 = "3004"  # 4位英文数字验证码
    MIXED_5 = "3005"  # 5位英文数字验证码
    MIXED_6 = "3006"  # 6位英文数字验证码

    # 中文类型
    CHINESE_4 = "4004"  # 4位纯中文验证码

    # 特殊类型
    NONE = "5000"  # 无类型验证码


class ServiceType(Enum):
    """验证码服务类型枚举"""

    CHAOJIYING = "chaojiying"  # 超级鹰
    RUOKUAI = "ruokuai"  # 若快
    TWOCAPTCHA = "2captcha"  # 2captcha
    LOCAL = "local"  # 本地识别


class ResultStatus(Enum):
    """识别结果状态枚举"""

    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失败
    ERROR = "error"  # 错误
    TIMEOUT = "timeout"  # 超时
    INVALID = "invalid"  # 无效


class ErrorCode(Enum):
    """错误代码枚举"""

    # 通用错误
    UNKNOWN_ERROR = "unknown_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    INVALID_IMAGE = "invalid_image"
    INVALID_CONFIG = "invalid_config"

    # 认证错误
    AUTH_FAILED = "auth_failed"
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_SUSPENDED = "account_suspended"

    # 服务错误
    SERVICE_UNAVAILABLE = "service_unavailable"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INSUFFICIENT_BALANCE = "insufficient_balance"

    # 识别错误
    RECOGNITION_FAILED = "recognition_failed"
    UNSUPPORTED_TYPE = "unsupported_type"
    IMAGE_TOO_SMALL = "image_too_small"
    IMAGE_TOO_LARGE = "image_too_large"


class ImageFormat(Enum):
    """图片格式枚举"""

    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    WEBP = "webp"


class ProcessingMode(Enum):
    """处理模式枚举"""

    SYNC = "sync"  # 同步处理
    ASYNC = "async"  # 异步处理
    BATCH = "batch"  # 批量处理
