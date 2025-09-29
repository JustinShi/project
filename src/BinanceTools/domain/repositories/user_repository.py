"""
用户仓储接口

定义用户数据访问的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.user import User


class UserRepository(ABC):
    """用户仓储接口"""
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[User]:
        """获取所有用户"""
        pass
    
    @abstractmethod
    async def get_active_users(self) -> List[User]:
        """获取活跃用户"""
        pass
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """保存用户"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """更新用户"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """删除用户"""
        pass
    
    @abstractmethod
    async def exists(self, user_id: str) -> bool:
        """检查用户是否存在"""
        pass
