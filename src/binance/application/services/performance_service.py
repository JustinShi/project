"""性能优化服务"""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标"""
    operation: str
    duration_ms: float
    timestamp: datetime
    success: bool
    error: str | None = None
    metadata: dict[str, Any] | None = None


class PerformanceService:
    """性能优化服务"""

    def __init__(self):
        self.metrics: list[PerformanceMetrics] = []
        self._cache: dict[str, Any] = {}
        self._cache_ttl: dict[str, datetime] = {}

    async def measure_operation(
        self,
        operation: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """测量操作性能"""
        start_time = time.time()
        success = True
        error = None
        result = None

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000

            # 记录性能指标
            metric = PerformanceMetrics(
                operation=operation,
                duration_ms=duration_ms,
                timestamp=datetime.now(),
                success=success,
                error=error
            )

            self.metrics.append(metric)

            # 限制指标数量
            if len(self.metrics) > 10000:
                self.metrics = self.metrics[-5000:]

            # 记录慢操作
            if duration_ms > 1000:  # 超过1秒的操作
                logger.warning(f"慢操作检测: {operation} 耗时 {duration_ms:.2f}ms")

        return result

    def get_performance_summary(self, hours: int = 1) -> dict[str, Any]:
        """获取性能摘要"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]

        if not recent_metrics:
            return {
                "total_operations": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "max_duration_ms": 0.0,
                "slow_operations": 0,
                "error_rate": 0.0
            }

        total_operations = len(recent_metrics)
        successful_operations = len([m for m in recent_metrics if m.success])
        error_operations = len([m for m in recent_metrics if not m.success])
        slow_operations = len([m for m in recent_metrics if m.duration_ms > 1000])

        durations = [m.duration_ms for m in recent_metrics]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0

        return {
            "total_operations": total_operations,
            "success_rate": (successful_operations / total_operations) * 100,
            "avg_duration_ms": avg_duration,
            "max_duration_ms": max_duration,
            "slow_operations": slow_operations,
            "error_rate": (error_operations / total_operations) * 100,
            "time_range_hours": hours
        }

    def get_operation_metrics(self, operation: str, hours: int = 1) -> dict[str, Any]:
        """获取特定操作的性能指标"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        operation_metrics = [
            m for m in self.metrics
            if m.operation == operation and m.timestamp >= cutoff_time
        ]

        if not operation_metrics:
            return {
                "operation": operation,
                "total_calls": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "max_duration_ms": 0.0,
                "min_duration_ms": 0.0
            }

        total_calls = len(operation_metrics)
        successful_calls = len([m for m in operation_metrics if m.success])
        durations = [m.duration_ms for m in operation_metrics]

        return {
            "operation": operation,
            "total_calls": total_calls,
            "success_rate": (successful_calls / total_calls) * 100,
            "avg_duration_ms": sum(durations) / len(durations),
            "max_duration_ms": max(durations),
            "min_duration_ms": min(durations),
            "time_range_hours": hours
        }

    def get_slow_operations(self, threshold_ms: float = 1000, hours: int = 1) -> list[dict[str, Any]]:
        """获取慢操作列表"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        slow_metrics = [
            m for m in self.metrics
            if m.duration_ms > threshold_ms and m.timestamp >= cutoff_time
        ]

        return [
            {
                "operation": m.operation,
                "duration_ms": m.duration_ms,
                "timestamp": m.timestamp.isoformat(),
                "success": m.success,
                "error": m.error
            }
            for m in sorted(slow_metrics, key=lambda x: x.duration_ms, reverse=True)
        ]

    def get_error_operations(self, hours: int = 1) -> list[dict[str, Any]]:
        """获取错误操作列表"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        error_metrics = [
            m for m in self.metrics
            if not m.success and m.timestamp >= cutoff_time
        ]

        return [
            {
                "operation": m.operation,
                "duration_ms": m.duration_ms,
                "timestamp": m.timestamp.isoformat(),
                "error": m.error
            }
            for m in sorted(error_metrics, key=lambda x: x.timestamp, reverse=True)
        ]

    def cache_get(self, key: str) -> Any | None:
        """从缓存获取数据"""
        if key in self._cache:
            # 检查TTL
            if key in self._cache_ttl:
                if datetime.now() > self._cache_ttl[key]:
                    # 缓存过期，删除
                    del self._cache[key]
                    del self._cache_ttl[key]
                    return None

            return self._cache[key]
        return None

    def cache_set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """设置缓存数据"""
        self._cache[key] = value
        self._cache_ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)

    def cache_clear(self, pattern: str | None = None) -> int:
        """清理缓存"""
        if pattern is None:
            # 清理所有缓存
            count = len(self._cache)
            self._cache.clear()
            self._cache_ttl.clear()
            return count
        else:
            # 按模式清理缓存
            keys_to_remove = [k for k in self._cache if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
                if key in self._cache_ttl:
                    del self._cache_ttl[key]
            return len(keys_to_remove)

    def get_cache_stats(self) -> dict[str, Any]:
        """获取缓存统计"""
        return {
            "total_keys": len(self._cache),
            "expired_keys": len([
                k for k, ttl in self._cache_ttl.items()
                if datetime.now() > ttl
            ]),
            "memory_usage_estimate": len(str(self._cache))  # 粗略估算
        }

    def optimize_database_queries(self, queries: list[str]) -> list[str]:
        """优化数据库查询"""
        optimized_queries = []

        for query in queries:
            # 简单的查询优化规则
            optimized_query = query

            # 添加索引提示
            if "SELECT" in query.upper() and "WHERE" in query.upper():
                # 这里可以添加索引优化逻辑
                pass

            # 限制结果集大小
            if "SELECT" in query.upper() and "LIMIT" not in query.upper():
                optimized_query += " LIMIT 1000"

            optimized_queries.append(optimized_query)

        return optimized_queries

    def get_performance_recommendations(self) -> list[str]:
        """获取性能优化建议"""
        recommendations = []

        # 分析慢操作
        slow_operations = self.get_slow_operations(threshold_ms=500, hours=24)
        if slow_operations:
            recommendations.append(f"发现 {len(slow_operations)} 个慢操作，建议优化")

        # 分析错误率
        summary = self.get_performance_summary(hours=24)
        if summary["error_rate"] > 5:
            recommendations.append(f"错误率过高 ({summary['error_rate']:.1f}%)，建议检查系统稳定性")

        # 分析平均响应时间
        if summary["avg_duration_ms"] > 1000:
            recommendations.append(f"平均响应时间过长 ({summary['avg_duration_ms']:.1f}ms)，建议优化")

        # 分析缓存命中率
        cache_stats = self.get_cache_stats()
        if cache_stats["expired_keys"] > cache_stats["total_keys"] * 0.5:
            recommendations.append("缓存过期率过高，建议调整TTL设置")

        return recommendations

    def get_performance_report(self, hours: int = 24) -> dict[str, Any]:
        """获取性能报告"""
        summary = self.get_performance_summary(hours)
        slow_operations = self.get_slow_operations(hours=hours)
        error_operations = self.get_error_operations(hours=hours)
        recommendations = self.get_performance_recommendations()
        cache_stats = self.get_cache_stats()

        return {
            "summary": summary,
            "slow_operations": slow_operations,
            "error_operations": error_operations,
            "recommendations": recommendations,
            "cache_stats": cache_stats,
            "report_time": datetime.now().isoformat(),
            "time_range_hours": hours
        }
