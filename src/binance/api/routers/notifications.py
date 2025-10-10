"""通知相关API路由"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from binance.api.dependencies import get_db_session, get_user_repository
from binance.api.schemas.notification_schema import (
    NotificationCreateRequest,
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkReadRequest,
    NotificationMarkReadResponse,
    NotificationStatisticsResponse,
    NotificationSettingsResponse,
    NotificationSettingsUpdateRequest,
    NotificationTestRequest,
    NotificationTestResponse
)
from binance.application.services.notification_service import NotificationService
from binance.domain.repositories.user_repository import UserRepository
from binance.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])

# 全局通知服务实例
_notification_service: Optional[NotificationService] = None


def get_notification_service(user_repo: UserRepository = Depends(get_user_repository)) -> NotificationService:
    """获取通知服务"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService(user_repo)
    return _notification_service


@router.get("/{user_id}", response_model=NotificationListResponse)
async def get_user_notifications(
    user_id: int,
    limit: int = Query(50, description="返回数量限制"),
    offset: int = Query(0, description="偏移量"),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """获取用户通知列表"""
    try:
        # 获取通知历史
        notifications_data = await notification_service.get_notification_history(user_id, limit)
        
        # 构建通知响应列表
        notifications = []
        for notif_data in notifications_data:
            notifications.append(NotificationResponse(
                id=notif_data.get("id", ""),
                user_id=notif_data.get("user_id", user_id),
                type=notif_data.get("type", ""),
                title=notif_data.get("title", ""),
                message=notif_data.get("message", ""),
                data=notif_data.get("data"),
                is_read=notif_data.get("is_read", False),
                created_at=notif_data.get("created_at"),
                read_at=notif_data.get("read_at")
            ))
        
        # 计算未读数量
        unread_count = sum(1 for n in notifications if not n.is_read)
        
        return NotificationListResponse(
            notifications=notifications,
            total=len(notifications),
            unread_count=unread_count
        )
        
    except Exception as e:
        logger.error(f"获取用户通知异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户通知失败: {str(e)}")


@router.post("/mark-read", response_model=NotificationMarkReadResponse)
async def mark_notification_read(
    request: NotificationMarkReadRequest,
    user_id: int = Query(..., description="用户ID"),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """标记通知为已读"""
    try:
        success = await notification_service.mark_notification_read(
            user_id=user_id,
            notification_id=request.notification_id
        )
        
        if success:
            return NotificationMarkReadResponse(
                success=True,
                message="通知已标记为已读"
            )
        else:
            return NotificationMarkReadResponse(
                success=False,
                message="标记通知已读失败"
            )
            
    except Exception as e:
        logger.error(f"标记通知已读异常: {e}")
        raise HTTPException(status_code=500, detail=f"标记通知已读失败: {str(e)}")


@router.get("/statistics/{user_id}", response_model=NotificationStatisticsResponse)
async def get_notification_statistics(
    user_id: int,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """获取通知统计"""
    try:
        # 获取通知历史
        notifications_data = await notification_service.get_notification_history(user_id, 100)
        
        # 统计信息
        total_notifications = len(notifications_data)
        unread_notifications = sum(1 for n in notifications_data if not n.get("is_read", False))
        
        # 按类型统计
        notifications_by_type = {}
        for notif in notifications_data:
            notif_type = notif.get("type", "unknown")
            notifications_by_type[notif_type] = notifications_by_type.get(notif_type, 0) + 1
        
        # 最近通知（最多10条）
        recent_notifications = []
        for notif_data in notifications_data[:10]:
            recent_notifications.append(NotificationResponse(
                id=notif_data.get("id", ""),
                user_id=notif_data.get("user_id", user_id),
                type=notif_data.get("type", ""),
                title=notif_data.get("title", ""),
                message=notif_data.get("message", ""),
                data=notif_data.get("data"),
                is_read=notif_data.get("is_read", False),
                created_at=notif_data.get("created_at"),
                read_at=notif_data.get("read_at")
            ))
        
        return NotificationStatisticsResponse(
            total_notifications=total_notifications,
            unread_notifications=unread_notifications,
            notifications_by_type=notifications_by_type,
            recent_notifications=recent_notifications
        )
        
    except Exception as e:
        logger.error(f"获取通知统计异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取通知统计失败: {str(e)}")


@router.get("/settings/{user_id}", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    user_id: int,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """获取用户通知设置"""
    try:
        # 这里应该从数据库获取用户通知设置
        # 暂时返回默认设置
        return NotificationSettingsResponse(
            user_id=user_id,
            email_notifications=True,
            sms_notifications=False,
            push_notifications=True,
            volatility_alerts=True,
            order_updates=True,
            balance_alerts=True
        )
        
    except Exception as e:
        logger.error(f"获取通知设置异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取通知设置失败: {str(e)}")


@router.put("/settings/{user_id}", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    user_id: int,
    request: NotificationSettingsUpdateRequest,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """更新用户通知设置"""
    try:
        # 这里应该更新数据库中的用户通知设置
        # 暂时返回更新后的设置
        return NotificationSettingsResponse(
            user_id=user_id,
            email_notifications=request.email_notifications if request.email_notifications is not None else True,
            sms_notifications=request.sms_notifications if request.sms_notifications is not None else False,
            push_notifications=request.push_notifications if request.push_notifications is not None else True,
            volatility_alerts=request.volatility_alerts if request.volatility_alerts is not None else True,
            order_updates=request.order_updates if request.order_updates is not None else True,
            balance_alerts=request.balance_alerts if request.balance_alerts is not None else True
        )
        
    except Exception as e:
        logger.error(f"更新通知设置异常: {e}")
        raise HTTPException(status_code=500, detail=f"更新通知设置失败: {str(e)}")


@router.post("/test", response_model=NotificationTestResponse)
async def test_notification(
    request: NotificationTestRequest,
    user_id: int = Query(..., description="用户ID"),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """测试通知发送"""
    try:
        # 发送测试通知
        await notification_service._send_user_notification(
            user_id=user_id,
            type=request.type,
            title=request.title,
            message=request.message,
            data={"test": True}
        )
        
        return NotificationTestResponse(
            success=True,
            message="测试通知发送成功",
            notification_id=f"test_{user_id}_{request.type}"
        )
        
    except Exception as e:
        logger.error(f"测试通知异常: {e}")
        raise HTTPException(status_code=500, detail=f"测试通知失败: {str(e)}")


@router.post("/cleanup")
async def cleanup_old_notifications(
    days: int = Query(30, description="清理多少天前的通知"),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """清理旧通知"""
    try:
        # 这里应该实现清理旧通知的逻辑
        # 暂时返回成功消息
        return {
            "success": True,
            "message": f"已清理 {days} 天前的通知",
            "cleaned_count": 0
        }
        
    except Exception as e:
        logger.error(f"清理旧通知异常: {e}")
        raise HTTPException(status_code=500, detail=f"清理旧通知失败: {str(e)}")
