"""应用配置管理"""

from functools import lru_cache

from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 数据库配置
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/binance.db",
        description="数据库连接URL（SQLite）",
    )
    database_pool_size: int = Field(default=20, description="数据库连接池大小")
    database_max_overflow: int = Field(default=10, description="数据库连接池最大溢出")

    # Redis配置
    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0", description="Redis连接URL"
    )
    redis_password: str = Field(default="", description="Redis密码")
    redis_db: int = Field(default=0, description="Redis数据库索引")

    # 加密密钥（使用 cryptography.fernet.Fernet.generate_key() 生成）
    encryption_key: str = Field(
        default="",
        description="Fernet加密密钥（用于加密用户认证信息）",
    )

    # API服务配置
    api_host: str = Field(default="0.0.0.0", description="API服务监听地址")
    api_port: int = Field(default=8000, description="API服务端口")
    api_reload: bool = Field(default=False, description="开发模式自动重载")
    api_workers: int = Field(default=4, description="API工作进程数")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="console", description="日志格式（json/console）")
    log_file: str = Field(default="logs/trading.log", description="日志文件路径")

    # WebSocket配置
    ws_reconnect_delay: int = Field(default=5, description="WebSocket重连延迟（秒）")
    ws_ping_interval: int = Field(default=30, description="WebSocket心跳间隔（秒）")
    ws_ping_timeout: int = Field(default=10, description="WebSocket心跳超时（秒）")

    # 价格波动监控配置
    price_volatility_window: int = Field(
        default=60, description="价格波动监控时间窗口（秒）"
    )
    price_volatility_threshold: float = Field(
        default=2.0, description="价格波动阈值（百分比）"
    )

    # 订单超时配置（秒）
    order_timeout: int = Field(default=300, description="订单超时时间（秒）")

    # 开发模式
    debug: bool = Field(default=False, description="调试模式")
    testing: bool = Field(default=False, description="测试模式")

    # CORS配置
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"], description="允许的CORS来源"
    )
    cors_allow_credentials: bool = Field(default=True, description="允许携带凭证")

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.debug or self.testing


@lru_cache
def get_settings() -> Settings:
    """获取配置单例（缓存）"""
    return Settings()
