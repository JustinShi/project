"""
哈希/签名工具
提供常用的哈希算法和签名功能
"""

import hashlib
import hmac
import secrets
from typing import Optional, Union

from loguru import logger


class HashUtil:
    """哈希工具类"""

    @staticmethod
    def md5(data: Union[str, bytes]) -> str:
        """计算 MD5 哈希值"""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def sha1(data: Union[str, bytes]) -> str:
        """计算 SHA1 哈希值"""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha1(data).hexdigest()

    @staticmethod
    def sha256(data: Union[str, bytes]) -> str:
        """计算 SHA256 哈希值"""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha512(data: Union[str, bytes]) -> str:
        """计算 SHA512 哈希值"""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def hmac_sha256(key: Union[str, bytes], data: Union[str, bytes]) -> str:
        """计算 HMAC-SHA256 签名"""
        if isinstance(key, str):
            key = key.encode("utf-8")
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hmac.new(key, data, hashlib.sha256).hexdigest()

    @staticmethod
    def hmac_sha512(key: Union[str, bytes], data: Union[str, bytes]) -> str:
        """计算 HMAC-SHA512 签名"""
        if isinstance(key, str):
            key = key.encode("utf-8")
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hmac.new(key, data, hashlib.sha512).hexdigest()

    @staticmethod
    def generate_salt(length: int = 32) -> str:
        """生成随机盐值"""
        return secrets.token_hex(length)

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """哈希密码"""
        if salt is None:
            salt = HashUtil.generate_salt()

        # 使用 PBKDF2 进行密码哈希
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000,  # 迭代次数
        )
        return password_hash.hex(), salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """验证密码"""
        try:
            computed_hash, _ = HashUtil.hash_password(password, salt)
            return computed_hash == password_hash
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False

    @staticmethod
    def file_hash(file_path: str, algorithm: str = "sha256") -> Optional[str]:
        """计算文件哈希值"""
        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"文件哈希计算失败: {e}")
            return None

    @staticmethod
    def compare_hashes(hash1: str, hash2: str) -> bool:
        """安全地比较两个哈希值"""
        return secrets.compare_digest(hash1, hash2)

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """生成随机令牌"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_api_key(prefix: str = "api") -> str:
        """生成 API 密钥"""
        token = HashUtil.generate_token(32)
        return f"{prefix}_{token}"

    @staticmethod
    def verify_signature(data: str, signature: str, secret_key: str) -> bool:
        """验证签名"""
        try:
            expected_signature = HashUtil.hmac_sha256(secret_key, data)
            return HashUtil.compare_hashes(signature, expected_signature)
        except Exception as e:
            logger.error(f"签名验证失败: {e}")
            return False

    @staticmethod
    def create_signature(data: str, secret_key: str) -> str:
        """创建签名"""
        return HashUtil.hmac_sha256(secret_key, data)

    @classmethod
    def get_available_algorithms(cls) -> list[str]:
        """获取可用的哈希算法"""
        return [
            "md5",
            "sha1",
            "sha224",
            "sha256",
            "sha384",
            "sha512",
            "blake2b",
            "blake2s",
            "sha3_224",
            "sha3_256",
            "sha3_384",
            "sha3_512",
        ]

    @staticmethod
    def is_valid_hash(hash_value: str, algorithm: str = "sha256") -> bool:
        """验证哈希值格式是否正确"""
        try:
            # 检查长度
            expected_lengths = {
                "md5": 32,
                "sha1": 40,
                "sha224": 56,
                "sha256": 64,
                "sha384": 96,
                "sha512": 128,
            }

            if algorithm in expected_lengths:
                if len(hash_value) != expected_lengths[algorithm]:
                    return False

            # 检查是否为十六进制
            int(hash_value, 16)
            return True
        except (ValueError, KeyError):
            return False
