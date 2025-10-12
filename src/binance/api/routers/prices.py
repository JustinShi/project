"""价格API路由"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from binance.api.dependencies import get_user_repository
from binance.api.schemas.price_schema import (
    MonitoringStatusResponse,
    PriceDataResponse,
    PriceHistoryResponse,
    PriceStatisticsResponse,
    WebSocketStatusResponse,
)
from binance.application.services.notification_service import NotificationService
from binance.application.services.price_monitor_service import PriceMonitorService
from binance.domain.repositories import UserRepository
from binance.infrastructure.cache.cache_manager import CacheManager
from binance.infrastructure.cache.redis_client import get_redis_client


router = APIRouter(prefix="/prices", tags=["价格监控"])


async def get_cache_manager() -> CacheManager:
    """获取缓存管理器依赖"""
    redis = await get_redis_client()
    return CacheManager(redis)


async def get_price_monitor_service(
    cache_manager: CacheManager = Depends(get_cache_manager),
    user_repo: UserRepository = Depends(get_user_repository),
) -> PriceMonitorService:
    """获取价格监控服务依赖"""
    notification_service = NotificationService(user_repo)

    return PriceMonitorService(
        cache_manager=cache_manager,
        on_volatility_alert=notification_service.notify_volatility_alert,
    )


@router.get("/{symbol}/latest", response_model=PriceDataResponse)
async def get_latest_price(
    symbol: str,
    price_service: PriceMonitorService = Depends(get_price_monitor_service),
):
    """获取最新价格"""
    try:
        latest_price = await price_service.get_latest_price(symbol)
        if not latest_price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"代币 {symbol} 没有价格数据",
            )

        return PriceDataResponse(
            symbol=symbol,
            price=latest_price["price"],
            volume=latest_price.get("volume", 0),
            timestamp=datetime.fromisoformat(latest_price["timestamp"]),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取价格失败: {e!s}",
        )


@router.get("/{symbol}/history", response_model=PriceHistoryResponse)
async def get_price_history(
    symbol: str,
    minutes: int = Query(1, description="时间范围（分钟）", ge=1, le=60),
    price_service: PriceMonitorService = Depends(get_price_monitor_service),
):
    """获取价格历史"""
    try:
        history = await price_service.get_price_statistics(symbol, minutes)

        price_data = []
        for item in history:
            price_data.append(
                PriceDataResponse(
                    symbol=symbol,
                    price=item["price"],
                    volume=item.get("volume", 0),
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                )
            )

        return PriceHistoryResponse(
            symbol=symbol,
            prices=price_data,
            count=len(price_data),
            time_range_minutes=minutes,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取价格历史失败: {e!s}",
        )


@router.get("/{symbol}/statistics", response_model=PriceStatisticsResponse)
async def get_price_statistics(
    symbol: str,
    minutes: int = Query(1, description="统计时间范围（分钟）", ge=1, le=60),
    cache_manager: CacheManager = Depends(get_cache_manager),
):
    """获取价格统计信息"""
    try:
        # 获取价格历史
        history = await cache_manager.get_price_history(symbol, minutes * 60)

        if not history:
            return PriceStatisticsResponse(
                symbol=symbol,
                count=0,
                time_range_minutes=minutes,
            )

        # 计算统计信息
        prices = [float(item["price"]) for item in history if item.get("price")]

        if not prices:
            return PriceStatisticsResponse(
                symbol=symbol,
                count=0,
                time_range_minutes=minutes,
            )

        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)

        # 计算波动率
        volatility = None
        if min_price > 0:
            volatility = ((max_price - min_price) / min_price) * 100

        return PriceStatisticsResponse(
            symbol=symbol,
            count=len(prices),
            min_price=min_price,
            max_price=max_price,
            avg_price=avg_price,
            volatility=volatility,
            time_range_minutes=minutes,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取价格统计失败: {e!s}",
        )


@router.post("/monitoring/start")
async def start_price_monitoring(
    symbols: list[str],
    volatility_threshold: float = 2.0,
    price_service: PriceMonitorService = Depends(get_price_monitor_service),
):
    """启动价格监控"""
    try:
        from decimal import Decimal

        await price_service.start_monitoring(
            symbols=symbols, volatility_threshold=Decimal(str(volatility_threshold))
        )

        return {
            "message": "价格监控已启动",
            "symbols": symbols,
            "volatility_threshold": volatility_threshold,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动价格监控失败: {e!s}",
        )


@router.post("/monitoring/stop")
async def stop_price_monitoring(
    price_service: PriceMonitorService = Depends(get_price_monitor_service),
):
    """停止价格监控"""
    try:
        await price_service.stop_monitoring()

        return {
            "message": "价格监控已停止",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停止价格监控失败: {e!s}",
        )


@router.get("/monitoring/status", response_model=MonitoringStatusResponse)
async def get_monitoring_status(
    price_service: PriceMonitorService = Depends(get_price_monitor_service),
):
    """获取监控状态"""
    try:
        monitored_symbols = await price_service.get_monitored_symbols()

        return MonitoringStatusResponse(
            is_running=price_service.is_running,
            monitored_symbols=monitored_symbols,
            total_connections=len(monitored_symbols),
            active_connections=len(monitored_symbols)
            if price_service.is_running
            else 0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取监控状态失败: {e!s}",
        )


@router.get("/{symbol}/websocket-status", response_model=WebSocketStatusResponse)
async def get_websocket_status(
    symbol: str,
    price_service: PriceMonitorService = Depends(get_price_monitor_service),
):
    """获取WebSocket连接状态"""
    try:
        is_monitored = await price_service.is_symbol_monitored(symbol)

        return WebSocketStatusResponse(
            symbol=symbol,
            is_connected=is_monitored and price_service.is_running,
            is_running=is_monitored,
            reconnect_attempts=0,  # TODO: 从连接器获取实际重连次数
            last_activity=None,  # TODO: 从连接器获取最后活动时间
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取WebSocket状态失败: {e!s}",
        )
