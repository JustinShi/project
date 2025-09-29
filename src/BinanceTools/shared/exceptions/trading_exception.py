"""
交易异常

交易相关的异常类。
"""

from .base_exception import BaseException


class TradingException(BaseException):
    """交易异常"""
    
    def __init__(self, message: str, error_code: str = "TRADING_ERROR", details: dict = None):
        """初始化异常"""
        super().__init__(message, error_code, details)


class InsufficientBalanceException(TradingException):
    """余额不足异常"""
    
    def __init__(self, symbol: str, required: str, available: str, details: dict = None):
        """初始化异常"""
        message = f"余额不足: 需要 {required} {symbol}, 可用 {available} {symbol}"
        super().__init__(message, "INSUFFICIENT_BALANCE", details)


class InvalidOrderException(TradingException):
    """无效订单异常"""
    
    def __init__(self, message: str, details: dict = None):
        """初始化异常"""
        super().__init__(message, "INVALID_ORDER", details)


class OrderNotFoundException(TradingException):
    """订单未找到异常"""
    
    def __init__(self, order_id: int, details: dict = None):
        """初始化异常"""
        message = f"订单未找到: {order_id}"
        super().__init__(message, "ORDER_NOT_FOUND", details)


class OrderAlreadyExistsException(TradingException):
    """订单已存在异常"""
    
    def __init__(self, order_id: int, details: dict = None):
        """初始化异常"""
        message = f"订单已存在: {order_id}"
        super().__init__(message, "ORDER_ALREADY_EXISTS", details)


class OrderCannotBeCanceledException(TradingException):
    """订单无法取消异常"""
    
    def __init__(self, order_id: int, status: str, details: dict = None):
        """初始化异常"""
        message = f"订单无法取消: {order_id}, 状态: {status}"
        super().__init__(message, "ORDER_CANNOT_BE_CANCELED", details)
