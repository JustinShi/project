"""用户仓储实现"""


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from binance.domain.entities import User
from binance.domain.repositories import UserRepository
from binance.infrastructure.database import models


class UserRepositoryImpl(UserRepository):
    """用户仓储实现（SQLAlchemy）"""

    def __init__(self, session: AsyncSession):
        """初始化仓储

        Args:
            session: 数据库会话
        """
        self._session = session

    @staticmethod
    def _to_entity(model: models.User) -> User:
        """ORM模型转换为领域实体

        Args:
            model: User ORM模型

        Returns:
            User领域实体
        """
        # 确保 headers 和 cookies 是字符串类型（处理可能的 bytes）
        headers = model.headers
        if isinstance(headers, bytes):
            headers = headers.decode('utf-8')
        
        cookies = model.cookies
        if isinstance(cookies, bytes):
            cookies = cookies.decode('utf-8')
        
        return User(
            id=model.id,
            name=model.name,
            email=model.email,
            headers=headers,
            cookies=cookies,
            is_valid=model.is_valid,
        )

    async def get_by_id(self, user_id: int) -> User | None:
        """根据ID获取用户"""
        result = await self._session.execute(
            select(models.User).where(models.User.id == user_id)
        )
        user_model = result.scalar_one_or_none()
        return self._to_entity(user_model) if user_model else None

    async def get_by_name(self, name: str) -> User | None:
        """根据用户名获取用户"""
        result = await self._session.execute(
            select(models.User).where(models.User.name == name)
        )
        user_model = result.scalar_one_or_none()
        return self._to_entity(user_model) if user_model else None

    async def create(self, user: User) -> User:
        """创建用户"""
        user_model = models.User(
            name=user.name,
            email=user.email,
            headers=user.headers,
            cookies=user.cookies,
        )
        self._session.add(user_model)
        await self._session.flush()  # 获取ID
        await self._session.commit()  # 提交事务
        return self._to_entity(user_model)

    async def update(self, user: User) -> User:
        """更新用户"""
        result = await self._session.execute(
            select(models.User).where(models.User.id == user.id)
        )
        user_model = result.scalar_one()

        user_model.name = user.name
        user_model.email = user.email
        user_model.headers = user.headers
        user_model.cookies = user.cookies
        user_model.is_valid = user.is_valid

        await self._session.flush()
        return self._to_entity(user_model)

