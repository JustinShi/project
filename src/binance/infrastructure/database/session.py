"""数据库会话管理"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from binance.config import get_settings


# 全局引擎和会话工厂
_engine = None
_async_session_factory = None


def init_db() -> None:
    """初始化数据库连接"""
    global _engine, _async_session_factory

    settings = get_settings()

    # 创建异步引擎
    _engine = create_async_engine(
        str(settings.database_url),
        echo=settings.debug,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,  # 连接池预检测
        pool_recycle=3600,  # 连接回收时间（秒）
    )

    # 创建会话工厂
    _async_session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（依赖注入使用）

    Yields:
        AsyncSession: 数据库会话

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    if _async_session_factory is None:
        init_db()

    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """关闭数据库连接"""
    global _engine
    if _engine:
        await _engine.dispose()

