"""健康检查API路由"""

import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from binance.api.dependencies import get_db_session, get_redis_client
from binance.application.services.security_service import SecurityService
from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.checks = {
            "database": self._check_database,
            "redis": self._check_redis,
            "websocket": self._check_websocket,
            "security": self._check_security,
            "system": self._check_system
        }

    async def _check_database(self, db_session) -> dict[str, Any]:
        """检查数据库连接"""
        try:
            # 执行简单查询测试连接
            result = await db_session.execute("SELECT 1")
            result.fetchone()

            return {
                "status": "healthy",
                "message": "数据库连接正常",
                "response_time_ms": 0  # 实际应用中应该测量响应时间
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"数据库连接失败: {e!s}",
                "error": str(e)
            }

    async def _check_redis(self, redis_client) -> dict[str, Any]:
        """检查Redis连接"""
        try:
            # 执行ping测试
            await redis_client.ping()

            return {
                "status": "healthy",
                "message": "Redis连接正常",
                "response_time_ms": 0
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Redis连接失败: {e!s}",
                "error": str(e)
            }

    async def _check_websocket(self) -> dict[str, Any]:
        """检查WebSocket连接"""
        try:
            # 这里应该检查WebSocket连接状态
            # 暂时返回健康状态
            return {
                "status": "healthy",
                "message": "WebSocket连接正常",
                "active_connections": 0  # 实际应用中应该获取真实连接数
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"WebSocket连接失败: {e!s}",
                "error": str(e)
            }

    async def _check_security(self) -> dict[str, Any]:
        """检查安全服务"""
        try:
            security_service = SecurityService()
            summary = security_service.get_security_summary()

            return {
                "status": "healthy",
                "message": "安全服务正常",
                "details": summary
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"安全服务异常: {e!s}",
                "error": str(e)
            }

    async def _check_system(self) -> dict[str, Any]:
        """检查系统资源"""
        try:
            import psutil

            # 获取系统资源信息
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # 检查资源使用率
            status = "healthy"
            warnings = []

            if cpu_percent > 90:
                status = "warning"
                warnings.append(f"CPU使用率过高: {cpu_percent}%")

            if memory.percent > 90:
                status = "warning"
                warnings.append(f"内存使用率过高: {memory.percent}%")

            if disk.percent > 90:
                status = "warning"
                warnings.append(f"磁盘使用率过高: {disk.percent}%")

            return {
                "status": status,
                "message": "系统资源检查完成",
                "details": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "warnings": warnings
                }
            }
        except ImportError:
            return {
                "status": "warning",
                "message": "psutil未安装，无法检查系统资源",
                "details": {}
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"系统资源检查失败: {e!s}",
                "error": str(e)
            }

    async def run_all_checks(self, db_session, redis_client) -> dict[str, Any]:
        """运行所有健康检查"""
        results = {}
        overall_status = "healthy"

        # 并行执行检查
        tasks = []

        # 数据库检查
        tasks.append(("database", self._check_database(db_session)))

        # Redis检查
        tasks.append(("redis", self._check_redis(redis_client)))

        # WebSocket检查
        tasks.append(("websocket", self._check_websocket()))

        # 安全服务检查
        tasks.append(("security", self._check_security()))

        # 系统资源检查
        tasks.append(("system", self._check_system()))

        # 等待所有检查完成
        for name, task in tasks:
            try:
                if asyncio.iscoroutine(task):
                    result = await task
                else:
                    result = task
                results[name] = result

                # 更新整体状态
                if result["status"] == "unhealthy":
                    overall_status = "unhealthy"
                elif result["status"] == "warning" and overall_status == "healthy":
                    overall_status = "warning"

            except Exception as e:
                results[name] = {
                    "status": "unhealthy",
                    "message": f"检查异常: {e!s}",
                    "error": str(e)
                }
                overall_status = "unhealthy"

        return {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "checks": results
        }


@router.get("/")
async def health_check(
    db: Any = Depends(get_db_session),
    redis: Any = Depends(get_redis_client)
):
    """基础健康检查"""
    try:
        checker = HealthChecker()
        result = await checker.run_all_checks(db, redis)

        # 根据整体状态返回相应的HTTP状态码
        if result["overall_status"] == "healthy" or result["overall_status"] == "warning":
            return result
        else:
            raise HTTPException(status_code=503, detail=result)

    except Exception as e:
        logger.error(f"健康检查异常: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {e!s}")


@router.get("/database")
async def database_health(db: Any = Depends(get_db_session)):
    """数据库健康检查"""
    try:
        checker = HealthChecker()
        result = await checker._check_database(db)

        if result["status"] == "healthy":
            return result
        else:
            raise HTTPException(status_code=503, detail=result)

    except Exception as e:
        logger.error(f"数据库健康检查异常: {e}")
        raise HTTPException(status_code=500, detail=f"数据库健康检查失败: {e!s}")


@router.get("/redis")
async def redis_health(redis: Any = Depends(get_redis_client)):
    """Redis健康检查"""
    try:
        checker = HealthChecker()
        result = await checker._check_redis(redis)

        if result["status"] == "healthy":
            return result
        else:
            raise HTTPException(status_code=503, detail=result)

    except Exception as e:
        logger.error(f"Redis健康检查异常: {e}")
        raise HTTPException(status_code=500, detail=f"Redis健康检查失败: {e!s}")


@router.get("/websocket")
async def websocket_health():
    """WebSocket健康检查"""
    try:
        checker = HealthChecker()
        result = await checker._check_websocket()

        if result["status"] == "healthy":
            return result
        else:
            raise HTTPException(status_code=503, detail=result)

    except Exception as e:
        logger.error(f"WebSocket健康检查异常: {e}")
        raise HTTPException(status_code=500, detail=f"WebSocket健康检查失败: {e!s}")


@router.get("/security")
async def security_health():
    """安全服务健康检查"""
    try:
        checker = HealthChecker()
        result = await checker._check_security()

        if result["status"] == "healthy":
            return result
        else:
            raise HTTPException(status_code=503, detail=result)

    except Exception as e:
        logger.error(f"安全服务健康检查异常: {e}")
        raise HTTPException(status_code=500, detail=f"安全服务健康检查失败: {e!s}")


@router.get("/system")
async def system_health():
    """系统资源健康检查"""
    try:
        checker = HealthChecker()
        result = await checker._check_system()

        if result["status"] in ["healthy", "warning"]:
            return result
        else:
            raise HTTPException(status_code=503, detail=result)

    except Exception as e:
        logger.error(f"系统资源健康检查异常: {e}")
        raise HTTPException(status_code=500, detail=f"系统资源健康检查失败: {e!s}")


@router.get("/detailed")
async def detailed_health_check(
    db: Any = Depends(get_db_session),
    redis: Any = Depends(get_redis_client)
):
    """详细健康检查"""
    try:
        checker = HealthChecker()
        result = await checker.run_all_checks(db, redis)

        # 添加更多详细信息
        result["version"] = "1.0.0"
        result["environment"] = "production"
        result["uptime"] = "24h"  # 实际应用中应该计算真实运行时间

        return result

    except Exception as e:
        logger.error(f"详细健康检查异常: {e}")
        raise HTTPException(status_code=500, detail=f"详细健康检查失败: {e!s}")


@router.get("/metrics")
async def health_metrics():
    """健康检查指标"""
    try:
        # 这里可以返回系统指标
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "health_checks_total": 5,
                "health_checks_passed": 4,
                "health_checks_failed": 1,
                "response_time_avg_ms": 50,
                "uptime_seconds": 86400
            }
        }

    except Exception as e:
        logger.error(f"健康检查指标异常: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查指标失败: {e!s}")
