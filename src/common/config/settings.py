"""
配置管理模块
支持从环境变量和Redis读取配置
"""

from typing import Any, Dict, Optional

import redis
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """应用配置类"""

    # 数据库配置
    db_type: str = Field(default="mysql", env="DB_TYPE")
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=3306, env="DB_PORT")
    db_name: str = Field(default="my_platform", env="DB_NAME")
    db_user: str = Field(default="root", env="DB_USER")
    db_password: str = Field(default="", env="DB_PASSWORD")

    # Redis配置
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")

    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")

    # 应用配置
    app_name: str = Field(default="Multi-Project Platform", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    # 超级鹰验证码配置
    chaojiying_username: Optional[str] = Field(default=None, env="CHAOJIYING_USERNAME")
    chaojiying_password: Optional[str] = Field(default=None, env="CHAOJIYING_PASSWORD")
    chaojiying_soft_id: Optional[str] = Field(default=None, env="CHAOJIYING_SOFT_ID")
    chaojiying_config_file: Optional[str] = Field(
        default=None, env="CHAOJIYING_CONFIG_FILE"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # 允许额外字段

    def get_db_url(self) -> str:
        """获取数据库连接URL"""
        if self.db_type == "mysql":
            return f"mysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        elif self.db_type == "postgresql":
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        elif self.db_type == "sqlite":
            return f"sqlite:///{self.db_name}.db"
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")

    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def get_redis_client(self) -> redis.Redis:
        """获取Redis客户端"""
        return redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            db=self.redis_db,
            decode_responses=True,
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """从字典创建配置"""
        return cls(**data)

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """从字典更新配置"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def validate_config(self) -> bool:
        """验证配置是否有效"""
        try:
            # 验证数据库配置
            if not all([self.db_host, self.db_name, self.db_user]):
                return False

            # 验证Redis配置
            return all([self.redis_host])
        except Exception:
            return False

    def __str__(self) -> str:
        """字符串表示"""
        return f"Config(app_name={self.app_name}, version={self.app_version}, debug={self.debug})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()


# 全局配置实例
config = Config()
