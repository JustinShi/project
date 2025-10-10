"""风险管理API路由"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from decimal import Decimal

from binance.api.dependencies import get_db_session, get_user_repository
from binance.api.schemas.risk_schema import (
    RiskProfileResponse,
    RiskProfileCreateRequest,
    RiskProfileUpdateRequest,
    RiskAlertResponse,
    RiskAlertListResponse,
    RiskAlertActionRequest,
    RiskAlertActionResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    RiskMetricsResponse,
    RiskSummaryResponse,
    RiskReportResponse
)
from binance.domain.services.risk_manager import RiskManager, RiskMetrics
from binance.domain.entities.risk_profile import RiskProfile, RiskLevel
from binance.domain.entities.risk_alert import AlertSeverity, AlertStatus
from binance.domain.entities.price_data import PriceData
from binance.domain.value_objects.price import Price
from binance.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/risk", tags=["risk"])

# 全局风险管理服务实例
_risk_manager: Optional[RiskManager] = None


def get_risk_manager() -> RiskManager:
    """获取风险管理服务"""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = RiskManager()
    return _risk_manager


@router.get("/profile/{user_id}", response_model=RiskProfileResponse)
async def get_risk_profile(
    user_id: int,
    risk_manager: RiskManager = Depends(get_risk_manager)
):
    """获取用户风险配置"""
    try:
        profile = risk_manager.get_risk_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="风险配置不存在")
        
        return RiskProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            risk_level=profile.risk_level.value,
            max_price_volatility=profile.max_price_volatility,
            volatility_window_minutes=profile.volatility_window_minutes,
            min_balance_ratio=profile.min_balance_ratio,
            max_position_ratio=profile.max_position_ratio,
            max_orders_per_hour=profile.max_orders_per_hour,
            max_orders_per_day=profile.max_orders_per_day,
            max_single_order_amount=profile.max_single_order_amount,
            max_daily_volume=profile.max_daily_volume,
            trading_hours_start=profile.trading_hours_start,
            trading_hours_end=profile.trading_hours_end,
            weekend_trading=profile.weekend_trading,
            max_consecutive_losses=profile.max_consecutive_losses,
            max_daily_loss=profile.max_daily_loss,
            is_active=profile.is_active,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取风险配置异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取风险配置失败: {str(e)}")


@router.post("/profile/{user_id}", response_model=RiskProfileResponse)
async def create_risk_profile(
    user_id: int,
    request: RiskProfileCreateRequest,
    risk_manager: RiskManager = Depends(get_risk_manager)
):
    """创建用户风险配置"""
    try:
        # 创建风险配置
        risk_level = RiskLevel(request.risk_level)
        profile = risk_manager.create_risk_profile(user_id, risk_level)
        
        # 应用自定义设置
        if request.max_price_volatility is not None:
            profile.max_price_volatility = request.max_price_volatility
        if request.volatility_window_minutes is not None:
            profile.volatility_window_minutes = request.volatility_window_minutes
        if request.min_balance_ratio is not None:
            profile.min_balance_ratio = request.min_balance_ratio
        if request.max_position_ratio is not None:
            profile.max_position_ratio = request.max_position_ratio
        if request.max_orders_per_hour is not None:
            profile.max_orders_per_hour = request.max_orders_per_hour
        if request.max_orders_per_day is not None:
            profile.max_orders_per_day = request.max_orders_per_day
        if request.max_single_order_amount is not None:
            profile.max_single_order_amount = request.max_single_order_amount
        if request.max_daily_volume is not None:
            profile.max_daily_volume = request.max_daily_volume
        if request.trading_hours_start is not None:
            profile.trading_hours_start = request.trading_hours_start
        if request.trading_hours_end is not None:
            profile.trading_hours_end = request.trading_hours_end
        if request.weekend_trading is not None:
            profile.weekend_trading = request.weekend_trading
        if request.max_consecutive_losses is not None:
            profile.max_consecutive_losses = request.max_consecutive_losses
        if request.max_daily_loss is not None:
            profile.max_daily_loss = request.max_daily_loss
        
        # 验证配置
        is_valid, validation_message = profile.validate()
        if not is_valid:
            raise HTTPException(status_code=400, detail=validation_message)
        
        # 设置配置
        risk_manager.set_risk_profile(profile)
        
        return RiskProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            risk_level=profile.risk_level.value,
            max_price_volatility=profile.max_price_volatility,
            volatility_window_minutes=profile.volatility_window_minutes,
            min_balance_ratio=profile.min_balance_ratio,
            max_position_ratio=profile.max_position_ratio,
            max_orders_per_hour=profile.max_orders_per_hour,
            max_orders_per_day=profile.max_orders_per_day,
            max_single_order_amount=profile.max_single_order_amount,
            max_daily_volume=profile.max_daily_volume,
            trading_hours_start=profile.trading_hours_start,
            trading_hours_end=profile.trading_hours_end,
            weekend_trading=profile.weekend_trading,
            max_consecutive_losses=profile.max_consecutive_losses,
            max_daily_loss=profile.max_daily_loss,
            is_active=profile.is_active,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建风险配置异常: {e}")
        raise HTTPException(status_code=500, detail=f"创建风险配置失败: {str(e)}")


@router.put("/profile/{user_id}", response_model=RiskProfileResponse)
async def update_risk_profile(
    user_id: int,
    request: RiskProfileUpdateRequest,
    risk_manager: RiskManager = Depends(get_risk_manager)
):
    """更新用户风险配置"""
    try:
        profile = risk_manager.get_risk_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="风险配置不存在")
        
        # 更新配置
        if request.risk_level is not None:
            profile.risk_level = RiskLevel(request.risk_level)
        if request.max_price_volatility is not None:
            profile.max_price_volatility = request.max_price_volatility
        if request.volatility_window_minutes is not None:
            profile.volatility_window_minutes = request.volatility_window_minutes
        if request.min_balance_ratio is not None:
            profile.min_balance_ratio = request.min_balance_ratio
        if request.max_position_ratio is not None:
            profile.max_position_ratio = request.max_position_ratio
        if request.max_orders_per_hour is not None:
            profile.max_orders_per_hour = request.max_orders_per_hour
        if request.max_orders_per_day is not None:
            profile.max_orders_per_day = request.max_orders_per_day
        if request.max_single_order_amount is not None:
            profile.max_single_order_amount = request.max_single_order_amount
        if request.max_daily_volume is not None:
            profile.max_daily_volume = request.max_daily_volume
        if request.trading_hours_start is not None:
            profile.trading_hours_start = request.trading_hours_start
        if request.trading_hours_end is not None:
            profile.trading_hours_end = request.trading_hours_end
        if request.weekend_trading is not None:
            profile.weekend_trading = request.weekend_trading
        if request.max_consecutive_losses is not None:
            profile.max_consecutive_losses = request.max_consecutive_losses
        if request.max_daily_loss is not None:
            profile.max_daily_loss = request.max_daily_loss
        if request.is_active is not None:
            profile.is_active = request.is_active
        
        # 验证配置
        is_valid, validation_message = profile.validate()
        if not is_valid:
            raise HTTPException(status_code=400, detail=validation_message)
        
        # 更新配置
        risk_manager.set_risk_profile(profile)
        
        return RiskProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            risk_level=profile.risk_level.value,
            max_price_volatility=profile.max_price_volatility,
            volatility_window_minutes=profile.volatility_window_minutes,
            min_balance_ratio=profile.min_balance_ratio,
            max_position_ratio=profile.max_position_ratio,
            max_orders_per_hour=profile.max_orders_per_hour,
            max_orders_per_day=profile.max_orders_per_day,
            max_single_order_amount=profile.max_single_order_amount,
            max_daily_volume=profile.max_daily_volume,
            trading_hours_start=profile.trading_hours_start,
            trading_hours_end=profile.trading_hours_end,
            weekend_trading=profile.weekend_trading,
            max_consecutive_losses=profile.max_consecutive_losses,
            max_daily_loss=profile.max_daily_loss,
            is_active=profile.is_active,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新风险配置异常: {e}")
        raise HTTPException(status_code=500, detail=f"更新风险配置失败: {str(e)}")


@router.get("/alerts/{user_id}", response_model=RiskAlertListResponse)
async def get_risk_alerts(
    user_id: int,
    risk_manager: RiskManager = Depends(get_risk_manager)
):
    """获取用户风险警报"""
    try:
        alerts = risk_manager.get_active_alerts(user_id)
        
        alert_responses = []
        for alert in alerts:
            alert_responses.append(RiskAlertResponse(
                id=alert.id,
                user_id=alert.user_id,
                title=alert.title,
                message=alert.message,
                severity=alert.severity.value,
                status=alert.status.value,
                risk_factor=alert.risk_factor.value,
                risk_level=alert.risk_level.value,
                current_value=alert.current_value,
                threshold_value=alert.threshold_value,
                data=alert.data,
                triggered_at=alert.triggered_at,
                acknowledged_at=alert.acknowledged_at,
                resolved_at=alert.resolved_at,
                duration_seconds=alert.get_duration()
            ))
        
        active_count = len([a for a in alerts if a.is_active()])
        critical_count = len([a for a in alerts if a.is_critical()])
        
        return RiskAlertListResponse(
            alerts=alert_responses,
            total=len(alerts),
            active_count=active_count,
            critical_count=critical_count
        )
        
    except Exception as e:
        logger.error(f"获取风险警报异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取风险警报失败: {str(e)}")


@router.post("/alerts/{user_id}/acknowledge", response_model=RiskAlertActionResponse)
async def acknowledge_risk_alert(
    user_id: int,
    request: RiskAlertActionRequest,
    risk_manager: RiskManager = Depends(get_risk_manager)
):
    """确认风险警报"""
    try:
        success = risk_manager.acknowledge_alert(user_id, request.alert_id)
        
        if success:
            return RiskAlertActionResponse(
                success=True,
                message="警报已确认"
            )
        else:
            return RiskAlertActionResponse(
                success=False,
                message="警报不存在或已处理"
            )
            
    except Exception as e:
        logger.error(f"确认风险警报异常: {e}")
        raise HTTPException(status_code=500, detail=f"确认风险警报失败: {str(e)}")


@router.post("/alerts/{user_id}/resolve", response_model=RiskAlertActionResponse)
async def resolve_risk_alert(
    user_id: int,
    request: RiskAlertActionRequest,
    risk_manager: RiskManager = Depends(get_risk_manager)
):
    """解决风险警报"""
    try:
        success = risk_manager.resolve_alert(user_id, request.alert_id)
        
        if success:
            return RiskAlertActionResponse(
                success=True,
                message="警报已解决"
            )
        else:
            return RiskAlertActionResponse(
                success=False,
                message="警报不存在或已处理"
            )
            
    except Exception as e:
        logger.error(f"解决风险警报异常: {e}")
        raise HTTPException(status_code=500, detail=f"解决风险警报失败: {str(e)}")


@router.post("/assess/{user_id}", response_model=RiskAssessmentResponse)
async def assess_risk(
    user_id: int,
    request: RiskAssessmentRequest,
    risk_manager: RiskManager = Depends(get_risk_manager)
):
    """风险评估"""
    try:
        # 创建价格数据
        current_price = PriceData(
            symbol=request.symbol,
            price=Price(request.current_price, precision=4),
            volume=Decimal("1000.0"),
            timestamp=datetime.now()
        )
        
        # 执行风险评估
        approved, message, alerts = risk_manager.assess_order_risk(
            user_id=user_id,
            symbol=request.symbol,
            order_amount=request.order_amount,
            current_price=current_price
        )
        
        # 构建警报响应
        alert_responses = []
        for alert in alerts:
            alert_responses.append(RiskAlertResponse(
                id=alert.id,
                user_id=alert.user_id,
                title=alert.title,
                message=alert.message,
                severity=alert.severity.value,
                status=alert.status.value,
                risk_factor=alert.risk_factor.value,
                risk_level=alert.risk_level.value,
                current_value=alert.current_value,
                threshold_value=alert.threshold_value,
                data=alert.data,
                triggered_at=alert.triggered_at,
                acknowledged_at=alert.acknowledged_at,
                resolved_at=alert.resolved_at,
                duration_seconds=alert.get_duration()
            ))
        
        # 获取风险等级
        profile = risk_manager.get_risk_profile(user_id)
        risk_level = profile.risk_level.value if profile else "UNKNOWN"
        
        # 生成建议
        recommendations = []
        if not approved:
            recommendations.append("请检查风险警报并调整交易参数")
        if len(alerts) > 0:
            recommendations.append("建议降低订单金额或等待市场条件改善")
        if risk_level == "HIGH":
            recommendations.append("建议降低风险等级或减少交易频率")
        
        return RiskAssessmentResponse(
            approved=approved,
            message=message,
            risk_level=risk_level,
            alerts=alert_responses,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"风险评估异常: {e}")
        raise HTTPException(status_code=500, detail=f"风险评估失败: {str(e)}")


@router.get("/metrics/{user_id}", response_model=RiskMetricsResponse)
async def get_risk_metrics(
    user_id: int,
    risk_manager: RiskManager = Depends(get_risk_manager)
):
    """获取风险指标"""
    try:
        metrics = risk_manager.get_risk_metrics(user_id)
        if not metrics:
            raise HTTPException(status_code=404, detail="风险指标不存在")
        
        return RiskMetricsResponse(
            user_id=metrics.user_id,
            current_balance=metrics.current_balance,
            daily_volume=metrics.daily_volume,
            daily_pnl=metrics.daily_pnl,
            consecutive_losses=metrics.consecutive_losses,
            orders_count_today=metrics.orders_count_today,
            orders_count_hour=metrics.orders_count_hour,
            price_volatility=metrics.price_volatility,
            position_ratio=metrics.position_ratio,
            last_order_time=metrics.last_order_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取风险指标异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取风险指标失败: {str(e)}")


@router.get("/summary/{user_id}", response_model=RiskSummaryResponse)
async def get_risk_summary(
    user_id: int,
    risk_manager: RiskManager = Depends(get_risk_manager)
):
    """获取风险摘要"""
    try:
        summary = risk_manager.get_risk_summary(user_id)
        
        return RiskSummaryResponse(
            user_id=summary["user_id"],
            risk_level=summary["risk_level"],
            active_alerts_count=summary["active_alerts_count"],
            critical_alerts_count=summary["critical_alerts_count"],
            current_balance=Decimal(str(summary["current_balance"])),
            daily_pnl=Decimal(str(summary["daily_pnl"])),
            consecutive_losses=summary["consecutive_losses"],
            orders_today=summary["orders_today"],
            orders_this_hour=summary["orders_this_hour"],
            trading_allowed=summary["trading_allowed"]
        )
        
    except Exception as e:
        logger.error(f"获取风险摘要异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取风险摘要失败: {str(e)}")


@router.get("/report/{user_id}", response_model=RiskReportResponse)
async def get_risk_report(
    user_id: int,
    risk_manager: RiskManager = Depends(get_risk_manager)
):
    """获取风险报告"""
    try:
        # 获取风险配置
        profile = risk_manager.get_risk_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="风险配置不存在")
        
        # 获取风险指标
        metrics = risk_manager.get_risk_metrics(user_id)
        if not metrics:
            raise HTTPException(status_code=404, detail="风险指标不存在")
        
        # 获取活跃警报
        alerts = risk_manager.get_active_alerts(user_id)
        
        # 获取风险摘要
        summary = risk_manager.get_risk_summary(user_id)
        
        # 构建报告
        return RiskReportResponse(
            user_id=user_id,
            report_date=datetime.now(),
            risk_profile=RiskProfileResponse(
                id=profile.id,
                user_id=profile.user_id,
                risk_level=profile.risk_level.value,
                max_price_volatility=profile.max_price_volatility,
                volatility_window_minutes=profile.volatility_window_minutes,
                min_balance_ratio=profile.min_balance_ratio,
                max_position_ratio=profile.max_position_ratio,
                max_orders_per_hour=profile.max_orders_per_hour,
                max_orders_per_day=profile.max_orders_per_day,
                max_single_order_amount=profile.max_single_order_amount,
                max_daily_volume=profile.max_daily_volume,
                trading_hours_start=profile.trading_hours_start,
                trading_hours_end=profile.trading_hours_end,
                weekend_trading=profile.weekend_trading,
                max_consecutive_losses=profile.max_consecutive_losses,
                max_daily_loss=profile.max_daily_loss,
                is_active=profile.is_active,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            ),
            risk_metrics=RiskMetricsResponse(
                user_id=metrics.user_id,
                current_balance=metrics.current_balance,
                daily_volume=metrics.daily_volume,
                daily_pnl=metrics.daily_pnl,
                consecutive_losses=metrics.consecutive_losses,
                orders_count_today=metrics.orders_count_today,
                orders_count_hour=metrics.orders_count_hour,
                price_volatility=metrics.price_volatility,
                position_ratio=metrics.position_ratio,
                last_order_time=metrics.last_order_time
            ),
            active_alerts=[RiskAlertResponse(
                id=alert.id,
                user_id=alert.user_id,
                title=alert.title,
                message=alert.message,
                severity=alert.severity.value,
                status=alert.status.value,
                risk_factor=alert.risk_factor.value,
                risk_level=alert.risk_level.value,
                current_value=alert.current_value,
                threshold_value=alert.threshold_value,
                data=alert.data,
                triggered_at=alert.triggered_at,
                acknowledged_at=alert.acknowledged_at,
                resolved_at=alert.resolved_at,
                duration_seconds=alert.get_duration()
            ) for alert in alerts],
            risk_summary=RiskSummaryResponse(
                user_id=summary["user_id"],
                risk_level=summary["risk_level"],
                active_alerts_count=summary["active_alerts_count"],
                critical_alerts_count=summary["critical_alerts_count"],
                current_balance=Decimal(str(summary["current_balance"])),
                daily_pnl=Decimal(str(summary["daily_pnl"])),
                consecutive_losses=summary["consecutive_losses"],
                orders_today=summary["orders_today"],
                orders_this_hour=summary["orders_this_hour"],
                trading_allowed=summary["trading_allowed"]
            ),
            recommendations=[
                "定期检查风险配置",
                "监控价格波动",
                "控制订单频率",
                "设置合理的止损点"
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取风险报告异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取风险报告失败: {str(e)}")
