"""
风险异常

风险控制相关的异常类。
"""

from .base_exception import BaseException


class RiskException(BaseException):
    """风险异常"""
    
    def __init__(self, message: str, error_code: str = "RISK_ERROR", details: dict = None):
        """初始化异常"""
        super().__init__(message, error_code, details)


class RiskLimitExceededException(RiskException):
    """风险限制超出异常"""
    
    def __init__(self, limit_type: str, limit_value: str, actual_value: str, details: dict = None):
        """初始化异常"""
        message = f"风险限制超出: {limit_type} 限制 {limit_value}, 实际 {actual_value}"
        super().__init__(message, "RISK_LIMIT_EXCEEDED", details)


class PositionSizeExceededException(RiskException):
    """仓位大小超出异常"""
    
    def __init__(self, symbol: str, max_size: str, actual_size: str, details: dict = None):
        """初始化异常"""
        message = f"仓位大小超出: {symbol} 最大 {max_size}, 实际 {actual_size}"
        super().__init__(message, "POSITION_SIZE_EXCEEDED", details)


class DailyLossLimitExceededException(RiskException):
    """日亏损限制超出异常"""
    
    def __init__(self, max_loss: str, actual_loss: str, details: dict = None):
        """初始化异常"""
        message = f"日亏损限制超出: 最大 {max_loss}, 实际 {actual_loss}"
        super().__init__(message, "DAILY_LOSS_LIMIT_EXCEEDED", details)


class DailyVolumeLimitExceededException(RiskException):
    """日交易量限制超出异常"""
    
    def __init__(self, max_volume: str, actual_volume: str, details: dict = None):
        """初始化异常"""
        message = f"日交易量限制超出: 最大 {max_volume}, 实际 {actual_volume}"
        super().__init__(message, "DAILY_VOLUME_LIMIT_EXCEEDED", details)


class LiquidityRiskException(RiskException):
    """流动性风险异常"""
    
    def __init__(self, symbol: str, required_liquidity: str, available_liquidity: str, details: dict = None):
        """初始化异常"""
        message = f"流动性风险: {symbol} 需要 {required_liquidity}, 可用 {available_liquidity}"
        super().__init__(message, "LIQUIDITY_RISK", details)


class ConcentrationRiskException(RiskException):
    """集中度风险异常"""
    
    def __init__(self, symbol: str, concentration: str, max_concentration: str, details: dict = None):
        """初始化异常"""
        message = f"集中度风险: {symbol} 集中度 {concentration}, 最大 {max_concentration}"
        super().__init__(message, "CONCENTRATION_RISK", details)
