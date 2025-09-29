"""
基础异常类

定义系统中所有异常的基础类。
"""


class BaseException(Exception):
    """基础异常类"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """初始化异常"""
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        """字符串表示"""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self):
        """转换为字典"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }
