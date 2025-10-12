"""加密服务实现（使用Fernet对称加密）"""

from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from binance.config import get_settings


class CryptoService:
    """加密服务（用于认证信息的加密和解密）"""

    def __init__(self, encryption_key: str):
        """初始化加密服务

        Args:
            encryption_key: Fernet加密密钥（base64编码的32字节密钥）
        """
        if not encryption_key:
            raise ValueError("Encryption key cannot be empty")

        try:
            self._fernet = Fernet(encryption_key.encode())
        except Exception as e:
            raise ValueError(f"Invalid encryption key: {e}") from e

    def encrypt(self, plaintext: str) -> str:
        """加密明文

        Args:
            plaintext: 需要加密的明文字符串

        Returns:
            加密后的密文（base64编码）

        Raises:
            ValueError: 如果明文为空
        """
        if not plaintext:
            raise ValueError("Plaintext cannot be empty")

        encrypted_bytes = self._fernet.encrypt(plaintext.encode())
        return encrypted_bytes.decode()

    def decrypt(self, ciphertext: str) -> str:
        """解密密文

        Args:
            ciphertext: 加密后的密文（base64编码）

        Returns:
            解密后的明文字符串

        Raises:
            ValueError: 如果密文为空或解密失败
        """
        if not ciphertext:
            raise ValueError("Ciphertext cannot be empty")

        try:
            decrypted_bytes = self._fernet.decrypt(ciphertext.encode())
            return decrypted_bytes.decode()
        except InvalidToken as e:
            raise ValueError("Failed to decrypt: invalid or corrupted data") from e

    @staticmethod
    def generate_key() -> str:
        """生成新的Fernet加密密钥

        Returns:
            base64编码的32字节密钥字符串
        """
        return Fernet.generate_key().decode()


@lru_cache
def get_crypto_service() -> CryptoService:
    """获取加密服务单例

    Returns:
        CryptoService实例

    Example:
        crypto = get_crypto_service()
        encrypted = crypto.encrypt("my secret")
        decrypted = crypto.decrypt(encrypted)
    """
    settings = get_settings()
    return CryptoService(settings.encryption_key)
