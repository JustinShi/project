"""FastAPI应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from binance.config import get_settings
from binance.infrastructure.cache import init_redis
from binance.infrastructure.database import init_db
from binance.infrastructure.logging import get_logger, setup_logging

from .application.services.security_service import SecurityConfig, SecurityService

# 导入中间件
from .middleware.security_middleware import (
    AuditMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
)

# 导入路由
from .routers import health, monitoring, notifications, orders, prices, risk, users


# 设置日志
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("application_starting")

    # 初始化数据库
    init_db()
    logger.info("database_initialized")

    # 初始化Redis
    await init_redis()
    logger.info("redis_initialized")

    yield

    # 关闭时
    logger.info("application_shutting_down")


# 创建FastAPI应用
settings = get_settings()

app = FastAPI(
    title="币安Alpha代币OTO订单自动交易系统",
    description="多用户币安Alpha代币OTO订单自动化交易API",
    version="0.1.0",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加安全中间件
security_service = SecurityService(SecurityConfig())
app.add_middleware(SecurityMiddleware, security_service=security_service)
app.add_middleware(RateLimitMiddleware, security_service=security_service)
app.add_middleware(AuditMiddleware, security_service=security_service)

# 注册路由
app.include_router(users.router, prefix="/api/v1", tags=["用户"])
app.include_router(prices.router, prefix="/api/v1", tags=["价格监控"])
app.include_router(orders.router, prefix="/api/v1", tags=["订单管理"])
app.include_router(notifications.router, prefix="/api/v1", tags=["通知管理"])
app.include_router(risk.router, prefix="/api/v1", tags=["风险管理"])
app.include_router(monitoring.router, prefix="/api/v1", tags=["系统监控"])
app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "币安Alpha代币OTO订单自动交易系统",
        "version": "0.1.0",
        "docs_url": "/docs",
    }
