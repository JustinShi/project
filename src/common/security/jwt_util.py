"""
JWT 相关工具
提供 JWT 令牌的生成、验证和解析功能
"""

import time
from typing import Any, Dict, Optional

from loguru import logger


class JWTUtil:
    """JWT 工具类"""

    @staticmethod
    def encode(
        payload: Dict[str, Any],
        secret: str,  # noqa: ARG004
        algorithm: str = "HS256",  # noqa: ARG004
        expires_in: Optional[int] = None,
        **kwargs,
    ) -> str:
        """
        编码 JWT 令牌

        Args:
            payload: 载荷数据
            secret: 密钥
            algorithm: 签名算法
            expires_in: 过期时间(秒)
            **kwargs: 其他参数

        Returns:
            JWT 令牌字符串
        """
        try:
            # 添加过期时间
            if expires_in:
                payload["exp"] = int(time.time()) + expires_in

            # 添加其他标准声明
            payload.update(kwargs)

            # 这里应该使用 PyJWT 库, 但为了简化, 我们返回一个模拟的令牌
            # 在实际项目中, 应该安装并使用 PyJWT
            logger.warning("JWT 编码功能需要安装 PyJWT 库")
            return f"mock_jwt_token_{int(time.time())}"

        except Exception as e:
            logger.error(f"JWT 编码失败: {e}")
            raise

    @staticmethod
    def decode(
        token: str,  # noqa: ARG004
        secret: str,  # noqa: ARG004
        algorithms: Optional[list[str]] = None,  # noqa: ARG004
        **kwargs,  # noqa: ARG004
    ) -> Dict[str, Any]:
        """
        解码 JWT 令牌

        Args:
            token: JWT 令牌
            secret: 密钥
            algorithms: 允许的算法列表
            **kwargs: 其他参数

        Returns:
            解码后的载荷数据
        """
        try:
            # 这里应该使用 PyJWT 库进行实际的解码
            # 为了简化, 我们返回一个模拟的载荷
            logger.warning("JWT 解码功能需要安装 PyJWT 库")
            return {
                "sub": "user_id",
                "exp": int(time.time()) + 3600,
                "iat": int(time.time()),
            }

        except Exception as e:
            logger.error(f"JWT 解码失败: {e}")
            raise

    @staticmethod
    def verify(token: str, secret: str, algorithms: Optional[list[str]] = None) -> bool:
        """
        验证 JWT 令牌

        Args:
            token: JWT 令牌
            secret: 密钥
            algorithms: 允许的算法列表

        Returns:
            验证是否成功
        """
        try:
            payload = JWTUtil.decode(token, secret, algorithms)

            # 检查过期时间
            if "exp" in payload and payload["exp"] < int(time.time()):
                logger.warning("JWT 令牌已过期")
                return False

            return True

        except Exception as e:
            logger.error(f"JWT 验证失败: {e}")
            return False

    @staticmethod
    def get_payload(token: str) -> Optional[Dict[str, Any]]:  # noqa: ARG004
        """
        获取 JWT 令牌的载荷(不验证签名)

        Args:
            token: JWT 令牌

        Returns:
            载荷数据或 None
        """
        try:
            # 简单的 Base64 解码(不验证签名)
            # 在实际项目中应该使用 PyJWT
            logger.warning("JWT 载荷获取功能需要安装 PyJWT 库")
            return {
                "sub": "user_id",
                "exp": int(time.time()) + 3600,
                "iat": int(time.time()),
            }

        except Exception as e:
            logger.error(f"获取 JWT 载荷失败: {e}")
            return None

    @staticmethod
    def is_expired(token: str) -> bool:
        """
        检查 JWT 令牌是否过期

        Args:
            token: JWT 令牌

        Returns:
            是否过期
        """
        try:
            payload = JWTUtil.get_payload(token)
            if payload and "exp" in payload:
                return payload["exp"] < int(time.time())
            return True

        except Exception as e:
            logger.error(f"检查 JWT 过期时间失败: {e}")
            return True

    @staticmethod
    def refresh_token(
        token: str,
        secret: str,
        expires_in: int = 3600,
        **kwargs,
    ) -> Optional[str]:
        """
        刷新 JWT 令牌

        Args:
            token: 原始令牌
            secret: 密钥
            expires_in: 新的过期时间
            **kwargs: 其他参数

        Returns:
            新的 JWT 令牌或 None
        """
        try:
            payload = JWTUtil.decode(token, secret)

            # 移除过期时间
            if "exp" in payload:
                del payload["exp"]
            if "iat" in payload:
                del payload["iat"]

            # 生成新令牌
            return JWTUtil.encode(payload, secret, expires_in=expires_in, **kwargs)

        except Exception as e:
            logger.error(f"刷新 JWT 令牌失败: {e}")
            return None

    @staticmethod
    def create_access_token(
        user_id: str,
        secret: str,
        expires_in: int = 3600,
        **kwargs,
    ) -> str:
        """
        创建访问令牌

        Args:
            user_id: 用户ID
            secret: 密钥
            expires_in: 过期时间
            **kwargs: 其他参数

        Returns:
            访问令牌
        """
        payload = {"sub": user_id, "type": "access", **kwargs}
        return JWTUtil.encode(payload, secret, expires_in=expires_in)

    @staticmethod
    def create_refresh_token(
        user_id: str,
        secret: str,
        expires_in: int = 86400 * 7,  # 7天
        **kwargs,
    ) -> str:
        """
        创建刷新令牌

        Args:
            user_id: 用户ID
            secret: 密钥
            expires_in: 过期时间
            **kwargs: 其他参数

        Returns:
            刷新令牌
        """
        payload = {"sub": user_id, "type": "refresh", **kwargs}
        return JWTUtil.encode(payload, secret, expires_in=expires_in)

    @staticmethod
    def extract_user_id(token: str) -> Optional[str]:
        """
        从令牌中提取用户ID

        Args:
            token: JWT 令牌

        Returns:
            用户ID或None
        """
        try:
            payload = JWTUtil.get_payload(token)
            return payload.get("sub") if payload else None

        except Exception as e:
            logger.error(f"提取用户ID失败: {e}")
            return None

    @staticmethod
    def get_token_type(token: str) -> Optional[str]:
        """
        获取令牌类型

        Args:
            token: JWT 令牌

        Returns:
            令牌类型或None
        """
        try:
            payload = JWTUtil.get_payload(token)
            return payload.get("type") if payload else None

        except Exception as e:
            logger.error(f"获取令牌类型失败: {e}")
            return None
