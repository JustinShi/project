"""FastAPI依赖注入"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from binance.application.services import BalanceService
from binance.domain.repositories import UserRepository
from binance.infrastructure.database import get_db
from binance.infrastructure.database.repositories import (
    UserRepositoryImpl,
)


async def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[UserRepository, None]:
    """获取用户仓储依赖

    Args:
        db: 数据库会话

    Yields:
        用户仓储实例
    """
    yield UserRepositoryImpl(db)


async def get_balance_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> BalanceService:
    """获取余额服务依赖

    Args:
        user_repo: 用户仓储

    Returns:
        余额服务实例
    """
    return BalanceService(user_repo)

