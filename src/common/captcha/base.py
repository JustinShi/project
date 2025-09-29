"""验证码识别基础抽象类"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union


class CaptchaResult:
    """验证码识别结果"""

    def __init__(
        self,
        success: bool,
        result: str = "",
        error_code: str = "",
        error_message: str = "",
        confidence: float = 0.0,
        processing_time: float = 0.0,
        raw_response: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.result = result
        self.error_code = error_code
        self.error_message = error_message
        self.confidence = confidence
        self.processing_time = processing_time
        self.raw_response = raw_response or {}

    def __str__(self) -> str:
        if self.success:
            return f"CaptchaResult(success=True, result='{self.result}', confidence={self.confidence})"
        else:
            return f"CaptchaResult(success=False, error='{self.error_message}')"

    def __repr__(self) -> str:
        return self.__str__()


class BaseCaptchaClient(ABC):
    """验证码识别客户端基类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._session = None

    @abstractmethod
    async def recognize(
        self, image: Union[str, Path, bytes], codetype: str = "1902", **kwargs
    ) -> CaptchaResult:
        """
        识别验证码

        Args:
            image: 验证码图片路径、字节数据或文件对象
            codetype: 验证码类型
            **kwargs: 其他参数

        Returns:
            CaptchaResult: 识别结果
        """
        pass

    @abstractmethod
    async def report_error(self, result_id: str) -> bool:
        """
        报告识别错误

        Args:
            result_id: 识别结果ID

        Returns:
            bool: 是否成功报告
        """
        pass

    @abstractmethod
    def get_supported_types(self) -> Dict[str, str]:
        """
        获取支持的验证码类型

        Returns:
            Dict[str, str]: 验证码类型字典
        """
        pass

    def _validate_image(self, image: Union[str, Path, bytes]) -> bytes:
        """验证并转换图片为字节数据"""
        if isinstance(image, bytes):
            return image
        elif isinstance(image, (str, Path)):
            path = Path(image)
            if not path.exists():
                raise FileNotFoundError(f"图片文件不存在: {path}")
            return path.read_bytes()
        else:
            raise ValueError(f"不支持的图片类型: {type(image)}")

    def _build_headers(self, **kwargs) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        headers.update(kwargs.get("headers", {}))
        return headers
