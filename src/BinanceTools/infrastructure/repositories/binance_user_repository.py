"""
币安用户仓储实现

实现用户仓储接口，从币安API获取用户信息。
"""

import json
from typing import List, Optional
from datetime import datetime

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ..config.user_config import UserConfig


class BinanceUserRepository(UserRepository):
    """币安用户仓储实现"""
    
    def __init__(self, user_config: UserConfig):
        """初始化仓储"""
        self.user_config = user_config
        self._users_cache = {}
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        if user_id in self._users_cache:
            return self._users_cache[user_id]
        
        # 从配置文件加载用户信息
        users_data = self.user_config.load_users()
        
        for user_data in users_data.get("users", []):
            if user_data["id"] == user_id:
                user = self._create_user_from_data(user_data)
                self._users_cache[user_id] = user
                return user
        
        return None
    
    async def get_all(self) -> List[User]:
        """获取所有用户"""
        users_data = self.user_config.load_users()
        users = []
        
        for user_data in users_data.get("users", []):
            user = self._create_user_from_data(user_data)
            users.append(user)
            self._users_cache[user.id] = user
        
        return users
    
    async def get_active_users(self) -> List[User]:
        """获取活跃用户"""
        all_users = await self.get_all()
        return [user for user in all_users if user.is_active()]
    
    async def save(self, user: User) -> User:
        """保存用户"""
        # 这里应该实现保存到配置文件的逻辑
        # 暂时只更新缓存
        self._users_cache[user.id] = user
        return user
    
    async def update(self, user: User) -> User:
        """更新用户"""
        # 这里应该实现更新配置文件的逻辑
        # 暂时只更新缓存
        self._users_cache[user.id] = user
        return user
    
    async def delete(self, user_id: str) -> bool:
        """删除用户"""
        if user_id in self._users_cache:
            del self._users_cache[user_id]
            return True
        return False
    
    async def exists(self, user_id: str) -> bool:
        """检查用户是否存在"""
        return await self.get_by_id(user_id) is not None
    
    def _create_user_from_data(self, user_data: dict) -> User:
        """从数据创建用户实体"""
        return User(
            id=user_data["id"],
            name=user_data["name"],
            enabled=user_data["enabled"],
            headers=user_data["headers"],
            cookies=user_data["cookies"],
            created_at=datetime.utcnow(),  # 配置文件没有创建时间，使用当前时间
            updated_at=datetime.utcnow()
        )
