"""
数据库连接管理模块
支持MySQL和PostgreSQL数据库连接
"""

from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from ..config import config
from ..logging import get_logger


logger = get_logger(__name__)


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.metadata = None
        # 延迟初始化，不在构造函数中连接

    def _init_database(self):
        """初始化数据库连接"""
        if self.engine is not None:
            return

        try:
            # 获取数据库连接URL
            db_url = config.get_db_url()
            logger.info(f"连接数据库: {config.db_type}")

            # 创建数据库引擎
            self.engine = create_engine(
                db_url,
                echo=config.debug,
                pool_pre_ping=True,
                pool_recycle=3600,
            )

            # 创建会话工厂
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            # 创建元数据
            self.metadata = MetaData()

            logger.info("数据库连接初始化成功")

        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise

    def get_session(self) -> Session:
        """获取数据库会话"""
        self._init_database()
        return self.SessionLocal()

    @contextmanager
    def get_session_context(self):
        """获取数据库会话上下文管理器"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    async def execute_query(
        self, query: str, params: Optional[Dict] = None
    ) -> List[Dict]:
        """
        执行查询语句

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            查询结果列表
        """
        try:
            with self.get_session_context() as session:
                result = session.execute(text(query), params or {})
                columns = result.keys()
                rows = result.fetchall()

                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            raise

    async def execute_update(self, query: str, params: Optional[Dict] = None) -> int:
        """
        执行更新语句

        Args:
            query: SQL更新语句
            params: 更新参数

        Returns:
            影响的行数
        """
        try:
            with self.get_session_context() as session:
                result = session.execute(text(query), params or {})
                return result.rowcount

        except Exception as e:
            logger.error(f"执行更新失败: {e}")
            raise

    async def execute_insert(self, query: str, params: Optional[Dict] = None) -> int:
        """
        执行插入语句

        Args:
            query: SQL插入语句
            params: 插入参数

        Returns:
            插入的行数
        """
        try:
            with self.get_session_context() as session:
                result = session.execute(text(query), params or {})
                return result.rowcount

        except Exception as e:
            logger.error(f"执行插入失败: {e}")
            raise

    async def execute_delete(self, query: str, params: Optional[Dict] = None) -> int:
        """
        执行删除语句

        Args:
            query: SQL删除语句
            params: 删除参数

        Returns:
            删除的行数
        """
        try:
            with self.get_session_context() as session:
                result = session.execute(text(query), params or {})
                return result.rowcount

        except Exception as e:
            logger.error(f"执行删除失败: {e}")
            raise

    async def test_connection(self) -> bool:
        """
        测试数据库连接

        Returns:
            连接是否成功
        """
        try:
            with self.get_session_context() as session:
                session.execute(text("SELECT 1"))
                logger.info("数据库连接测试成功")
                return True

        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False

    async def get_table_info(self, table_name: str) -> List[Dict]:
        """
        获取表信息

        Args:
            table_name: 表名

        Returns:
            表信息列表
        """
        try:
            if config.db_type == "mysql":
                query = """
                SELECT
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = :table_name
                """
            elif config.db_type == "postgresql":
                query = """
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    '' as column_comment
                FROM information_schema.columns
                WHERE table_name = :table_name
                """
            else:
                raise ValueError(f"不支持的数据库类型: {config.db_type}")

            return await self.execute_query(query, {"table_name": table_name})

        except Exception as e:
            logger.error(f"获取表信息失败: {e}")
            raise

    async def get_database_info(self) -> Dict[str, Any]:
        """
        获取数据库信息

        Returns:
            数据库信息字典
        """
        try:
            info = {
                "db_type": config.db_type,
                "db_host": config.db_host,
                "db_port": config.db_port,
                "db_name": config.db_name,
                "connected": False,
            }

            # 测试连接
            info["connected"] = await self.test_connection()

            return info

        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            return {
                "db_type": config.db_type,
                "db_host": config.db_host,
                "db_port": config.db_port,
                "db_name": config.db_name,
                "connected": False,
                "error": str(e),
            }

    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")

    def __del__(self):
        """析构函数"""
        self.close()


# 全局数据库管理器实例
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    return db_manager


def get_db_session() -> Session:
    """获取数据库会话"""
    return db_manager.get_session()


@contextmanager
def get_db_session_context():
    """获取数据库会话上下文管理器"""
    with db_manager.get_session_context() as session:
        yield session
