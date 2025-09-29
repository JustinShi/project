"""超级鹰验证码识别客户端"""

import asyncio
import json
from hashlib import md5
from pathlib import Path
from typing import Any, Dict, Optional, Union

from aiohttp import ClientSession, ClientTimeout

from ..base import BaseCaptchaClient, CaptchaResult
from ..config import CaptchaConfig


class ChaojiyingClient(BaseCaptchaClient):
    """超级鹰验证码识别客户端"""

    def __init__(self, config_file: Optional[str] = None, env: str = "default"):
        super().__init__(config_file, env)
        self.config = CaptchaConfig("chaojiying", config_file, env)
        self._init_client()

    def _init_client(self):
        """初始化客户端"""
        # 获取认证凭据
        credentials = self.config.get_credentials()

        if not credentials:
            raise ValueError(
                "未找到超级鹰认证凭据, 请设置环境变量 CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID"
            )

        self.username = credentials.get("username")
        self.password = credentials.get("password")
        self.soft_id = credentials.get("soft_id")

        if not all([self.username, self.password, self.soft_id]):
            raise ValueError("超级鹰认证凭据不完整, 请检查环境变量")

        # HTTP 基本配置(aiohttp)
        self.base_url = "http://upload.chaojiying.net/Upload/"
        self.timeout_seconds = self.config.get_timeout()
        self.max_retries = self.config.get_max_retries()
        self.retry_delay = 1.0
        self.default_headers = {"User-Agent": self.config.get_user_agent()}
        self._session: Optional[ClientSession] = None

    async def _ensure_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = ClientSession(
                timeout=ClientTimeout(total=self.timeout_seconds),
                headers=self.default_headers,
            )
        return self._session

    async def _post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """使用 aiohttp 发送 POST 请求并处理重试与解析。"""
        session = await self._ensure_session()
        url = self.base_url + path

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                async with session.post(url, data=data) as resp:
                    status_code = resp.status
                    text = await resp.text()
                    parsed: Any
                    try:
                        parsed = json.loads(text)
                    except Exception:
                        parsed = text
                    return {"status_code": status_code, "data": parsed}
            except Exception as e:
                last_error = e
                if attempt == self.max_retries:
                    break
                await asyncio.sleep(self.retry_delay * (2**attempt))

        # 只有在完全失败时才会到达这里
        return {
            "status_code": 0,
            "data": {"error": f"request failed: {last_error!s}"},
        }

    async def recognize(
        self,
        image: Union[str, Path, bytes],
        codetype: str = "1902",
        **kwargs,  # noqa: ARG002
    ) -> CaptchaResult:
        """
        识别验证码

        Args:
            image: 验证码图片路径、字节数据或文件对象
            codetype: 验证码类型, 默认为1902(4位数字字母)
            **kwargs: 其他参数

        Returns:
            CaptchaResult: 识别结果
        """
        try:
            # 验证图片
            image_data = self._validate_image(image)

            # 构建请求数据
            data = {
                "user": self.username,
                "pass": self._md5_password(),
                "softid": self.soft_id,
                "codetype": codetype,
                "file_base64": self._encode_image(image_data),
            }

            # 发送请求
            response = await self._post("", data=data)

            if response["status_code"] == 200:
                result_data = response["data"]

                if isinstance(result_data, dict):
                    err_no = result_data.get("err_no", -1)

                    if err_no == 0:
                        # 识别成功
                        return CaptchaResult(
                            success=True,
                            result=result_data.get("pic_str", ""),
                            confidence=float(result_data.get("pic_id", 0)) / 100,
                            processing_time=0.0,
                            raw_response=result_data,
                        )
                    else:
                        # 识别失败
                        return CaptchaResult(
                            success=False,
                            error_code=str(err_no),
                            error_message=result_data.get("err_str", "识别失败"),
                            raw_response=result_data,
                        )
                else:
                    return CaptchaResult(
                        success=False,
                        error_message="响应格式错误",
                        raw_response=result_data,
                    )
            else:
                return CaptchaResult(
                    success=False,
                    error_message=f"HTTP 错误: {response['status_code']}",
                    raw_response=response,
                )

        except Exception as e:
            return CaptchaResult(
                success=False, error_message=f"识别过程出错: {e!s}", raw_response={}
            )

    async def report_error(self, result_id: str) -> bool:
        """
        报告识别错误

        Args:
            result_id: 识别结果ID

        Returns:
            bool: 是否成功报告
        """
        try:
            data = {
                "user": self.username,
                "pass": self._md5_password(),
                "softid": self.soft_id,
                "id": result_id,
            }

            response = await self._post("ReportErr.php", data=data)

            if response["status_code"] == 200:
                result_data = response["data"]
                if isinstance(result_data, dict):
                    return result_data.get("err_no", -1) == 0

            return False

        except Exception:
            return False

    def get_supported_types(self) -> Dict[str, str]:
        """
        获取支持的验证码类型

        Returns:
            Dict[str, str]: 验证码类型字典
        """
        return self.config.get_supported_codetypes()

    def _md5_password(self) -> str:
        """生成MD5密码"""
        return md5(self.password.encode()).hexdigest()

    def _encode_image(self, image_data: bytes) -> str:
        """编码图片为base64"""
        import base64

        return base64.b64encode(image_data).decode()

    async def get_balance(self) -> Optional[float]:
        """
        获取账户余额

        Returns:
            Optional[float]: 账户余额, 获取失败返回 None
        """
        try:
            data = {
                "user": self.username,
                "pass": self._md5_password(),
            }

            response = await self._post("GetScore.php", data=data)

            if response["status_code"] == 200:
                result_data = response["data"]
                if isinstance(result_data, dict) and result_data.get("err_no") == 0:
                    return float(result_data.get("score", 0))

            return None

        except Exception:
            return None

    async def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        获取用户信息

        Returns:
            Optional[Dict[str, Any]]: 用户信息, 获取失败返回 None
        """
        try:
            data = {
                "user": self.username,
                "pass": self._md5_password(),
            }

            response = await self._post("GetUserInfo.php", data=data)

            if response["status_code"] == 200:
                result_data = response["data"]
                if isinstance(result_data, dict) and result_data.get("err_no") == 0:
                    return result_data

            return None

        except Exception:
            return None

    def validate_codetype(self, codetype: str) -> bool:
        """
        验证验证码类型是否支持

        Args:
            codetype: 验证码类型

        Returns:
            bool: 是否支持
        """
        supported_types = self.get_supported_types()
        return codetype in supported_types

    def get_codetype_description(self, codetype: str) -> str:
        """
        获取验证码类型描述

        Args:
            codetype: 验证码类型

        Returns:
            str: 类型描述
        """
        supported_types = self.get_supported_types()
        return supported_types.get(codetype, "未知类型")

    async def close(self):
        """关闭客户端"""
        if self._session is not None and not self._session.closed:
            await self._session.close()

    def __str__(self) -> str:
        """字符串表示"""
        return f"ChaojiyingClient(username={self.username}, soft_id={self.soft_id})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()
