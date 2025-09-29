"""
API异常

API相关的异常类。
"""

from .base_exception import BaseException


class ApiException(BaseException):
    """API异常"""
    
    def __init__(self, message: str, error_code: str = "API_ERROR", details: dict = None):
        """初始化异常"""
        super().__init__(message, error_code, details)


class ApiConnectionException(ApiException):
    """API连接异常"""
    
    def __init__(self, message: str, details: dict = None):
        """初始化异常"""
        super().__init__(message, "API_CONNECTION_ERROR", details)


class ApiTimeoutException(ApiException):
    """API超时异常"""
    
    def __init__(self, message: str, details: dict = None):
        """初始化异常"""
        super().__init__(message, "API_TIMEOUT", details)


class ApiRateLimitException(ApiException):
    """API速率限制异常"""
    
    def __init__(self, message: str, details: dict = None):
        """初始化异常"""
        super().__init__(message, "API_RATE_LIMIT", details)


class ApiAuthenticationException(ApiException):
    """API认证异常"""
    
    def __init__(self, message: str, details: dict = None):
        """初始化异常"""
        super().__init__(message, "API_AUTHENTICATION_ERROR", details)


class ApiResponseException(ApiException):
    """API响应异常"""
    
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        """初始化异常"""
        if status_code:
            message = f"HTTP {status_code}: {message}"
        super().__init__(message, "API_RESPONSE_ERROR", details)
