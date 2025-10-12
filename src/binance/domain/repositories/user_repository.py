"""用户仓储接口"""

from abc import ABC, abstractmethod

from binance.domain.entities import User


class UserRepository(ABC):
    """用户仓储接口"""

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        """根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户实体，不存在则返回None
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> User | None:
        """根据用户名获取用户

        Args:
            name: 用户名

        Returns:
            用户实体，不存在则返回None
        """
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        """创建用户

        Args:
            user: 用户实体

        Returns:
            创建后的用户实体（包含ID）
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """更新用户

        Args:
            user: 用户实体

        Returns:
            更新后的用户实体
        """
        pass
