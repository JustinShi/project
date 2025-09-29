"""验证码相关异常类型"""

from typing import Any, Dict, Optional


class CaptchaError(Exception):
    """验证码基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ConfigError(CaptchaError):
    """配置错误异常"""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, "config_error")
        self.config_key = config_key


class NetworkError(CaptchaError):
    """网络错误异常"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "network_error")
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(CaptchaError):
    """认证错误异常"""

    def __init__(self, message: str, service: Optional[str] = None):
        super().__init__(message, "auth_error")
        self.service = service


class RecognitionError(CaptchaError):
    """识别错误异常"""

    def __init__(
        self,
        message: str,
        codetype: Optional[str] = None,
        confidence: Optional[float] = None,
    ):
        super().__init__(message, "recognition_error")
        self.codetype = codetype
        self.confidence = confidence


class ValidationError(CaptchaError):
    """验证错误异常"""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Optional[Any] = None
    ):
        super().__init__(message, "validation_error")
        self.field = field
        self.value = value


class ServiceError(CaptchaError):
    """服务错误异常"""

    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(message, error_code or "service_error")
        self.service = service


class TimeoutError(CaptchaError):
    """超时错误异常"""

    def __init__(self, message: str, timeout: Optional[float] = None):
        super().__init__(message, "timeout_error")
        self.timeout = timeout


class RateLimitError(CaptchaError):
    """频率限制错误异常"""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, "rate_limit_error")
        self.retry_after = retry_after


class InsufficientBalanceError(CaptchaError):
    """余额不足错误异常"""

    def __init__(
        self,
        message: str,
        current_balance: Optional[float] = None,
        required_balance: Optional[float] = None,
    ):
        super().__init__(message, "insufficient_balance_error")
        self.current_balance = current_balance
        self.required_balance = required_balance


class UnsupportedTypeError(CaptchaError):
    """不支持的类型错误异常"""

    def __init__(
        self,
        message: str,
        codetype: Optional[str] = None,
        supported_types: Optional[list] = None,
    ):
        super().__init__(message, "unsupported_type_error")
        self.codetype = codetype
        self.supported_types = supported_types or []
