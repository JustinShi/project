"""
验证异常

数据验证相关的异常类。
"""

from .base_exception import BaseException


class ValidationException(BaseException):
    """验证异常"""
    
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR", details: dict = None):
        """初始化异常"""
        super().__init__(message, error_code, details)


class InvalidParameterException(ValidationException):
    """无效参数异常"""
    
    def __init__(self, parameter: str, value: any, message: str = None, details: dict = None):
        """初始化异常"""
        if message is None:
            message = f"无效参数: {parameter} = {value}"
        super().__init__(message, "INVALID_PARAMETER", details)


class MissingParameterException(ValidationException):
    """缺少参数异常"""
    
    def __init__(self, parameter: str, details: dict = None):
        """初始化异常"""
        message = f"缺少必需参数: {parameter}"
        super().__init__(message, "MISSING_PARAMETER", details)


class InvalidSymbolException(ValidationException):
    """无效交易对异常"""
    
    def __init__(self, symbol: str, details: dict = None):
        """初始化异常"""
        message = f"无效交易对: {symbol}"
        super().__init__(message, "INVALID_SYMBOL", details)


class InvalidQuantityException(ValidationException):
    """无效数量异常"""
    
    def __init__(self, quantity: any, details: dict = None):
        """初始化异常"""
        message = f"无效数量: {quantity}"
        super().__init__(message, "INVALID_QUANTITY", details)


class InvalidPriceException(ValidationException):
    """无效价格异常"""
    
    def __init__(self, price: any, details: dict = None):
        """初始化异常"""
        message = f"无效价格: {price}"
        super().__init__(message, "INVALID_PRICE", details)
