"""用户相关API路由"""

from fastapi import APIRouter, Depends, HTTPException

from binance.api.dependencies import get_balance_service, get_user_repository
from binance.api.schemas import BalanceResponse, UserResponse, VolumeResponse
from binance.application.services import BalanceService
from binance.domain.repositories import UserRepository
from binance.infrastructure.logging import get_logger


logger = get_logger(__name__)

router = APIRouter()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """获取用户信息

    Args:
        user_id: 用户ID
        user_repo: 用户仓储（依赖注入）

    Returns:
        用户信息

    Raises:
        HTTPException: 用户不存在时返回404
    """
    logger.info("api_get_user", user_id=user_id)

    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"用户不存在: {user_id}")

    return UserResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.get("/users/{user_id}/balance", response_model=BalanceResponse)
async def get_user_balance(
    user_id: int,
    balance_service: BalanceService = Depends(get_balance_service),
):
    """获取用户余额

    Args:
        user_id: 用户ID
        balance_service: 余额服务（依赖注入）

    Returns:
        用户余额信息

    Raises:
        HTTPException: 用户不存在或认证失败时返回400/404
    """
    logger.info("api_get_user_balance", user_id=user_id)

    try:
        balance_data = await balance_service.get_user_balance(user_id)
        return BalanceResponse(**balance_data)
    except ValueError as e:
        error_msg = str(e)
        if "不存在" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)


@router.get("/users/{user_id}/volume", response_model=VolumeResponse)
async def get_user_volume(
    user_id: int,
    balance_service: BalanceService = Depends(get_balance_service),
):
    """获取用户今日交易量

    Args:
        user_id: 用户ID
        balance_service: 余额服务（依赖注入）

    Returns:
        用户交易量信息

    Raises:
        HTTPException: 用户不存在或认证失败时返回400/404
    """
    logger.info("api_get_user_volume", user_id=user_id)

    try:
        volume_data = await balance_service.get_user_volume(user_id)
        return VolumeResponse(**volume_data)
    except ValueError as e:
        error_msg = str(e)
        if "不存在" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
