"""用户实体"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """用户领域实体（包含认证信息）"""

    id: int
    name: str
    email: Optional[str] = None
    
    # 认证信息（明文存储）
    headers: Optional[str] = None
    cookies: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    is_valid: bool = True  # 同时表示：认证有效 + 用户激活
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def deactivate(self) -> None:
        """停用用户（标记为无效）"""
        self.is_valid = False

    def activate(self) -> None:
        """激活用户（标记为有效）"""
        self.is_valid = True

    def mark_credentials_invalid(self) -> None:
        """标记认证凭证为无效（认证失败时调用）"""
        self.is_valid = False

    def mark_credentials_verified(self) -> None:
        """标记认证凭证已验证（成功调用API后）"""
        self.is_valid = True
        self.last_verified_at = datetime.now()

    def has_credentials(self) -> bool:
        """检查是否有认证凭证"""
        return bool(self.headers)

    def __str__(self) -> str:
        return f"User(id={self.id}, name={self.name}, valid={self.is_valid}, has_creds={self.has_credentials()})"

