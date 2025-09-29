"""
用户实体

表示币安用户，包含用户身份信息和配置。
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class User:
    """用户实体"""
    
    id: str
    name: str
    enabled: bool
    headers: Dict[str, str]
    cookies: Dict[str, str]
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.id:
            raise ValueError("用户ID不能为空")
        if not self.name:
            raise ValueError("用户名不能为空")
    
    def is_active(self) -> bool:
        """检查用户是否激活"""
        return self.enabled
    
    def update_headers(self, headers: Dict[str, str]) -> None:
        """更新请求头"""
        self.headers.update(headers)
        self.updated_at = datetime.utcnow()
    
    def update_cookies(self, cookies: Dict[str, str]) -> None:
        """更新Cookie"""
        self.cookies.update(cookies)
        self.updated_at = datetime.utcnow()
    
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证相关的请求头"""
        auth_headers = {}
        for key, value in self.headers.items():
            if key.lower() in ['authorization', 'x-api-key', 'csrftoken']:
                auth_headers[key] = value
        return auth_headers
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "headers": self.headers,
            "cookies": self.cookies,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """从字典创建用户实体"""
        return cls(
            id=data["id"],
            name=data["name"],
            enabled=data["enabled"],
            headers=data["headers"],
            cookies=data["cookies"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
