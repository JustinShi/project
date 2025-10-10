"""余额查询服务"""

import json
from typing import Dict, List, Any

from binance.domain.repositories import UserRepository
from binance.infrastructure.binance_client import BinanceClient
from binance.infrastructure.encryption import get_crypto_service
from binance.infrastructure.logging import get_logger

logger = get_logger(__name__)


class BalanceService:
    """余额查询应用服务"""

    def __init__(self, user_repository: UserRepository):
        """初始化服务

        Args:
            user_repository: 用户仓储
        """
        self._user_repo = user_repository
        self._crypto = get_crypto_service()

    async def get_user_balance(self, user_id: int) -> Dict[str, Any]:
        """获取用户余额

        Args:
            user_id: 用户ID

        Returns:
            余额信息，格式：
            {
                "total_valuation": "47.52",
                "balances": [
                    {
                        "symbol": "BR",
                        "token_id": "ALPHA_118",
                        "free": "0.006657",
                        "locked": "0",
                        "amount": "0.006657",
                        "valuation": "0.00051714"
                    }
                ]
            }

        Raises:
            ValueError: 用户不存在或认证凭证无效
        """
        logger.info("get_user_balance", user_id=user_id)

        # 1. 获取用户
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"用户不存在: {user_id}")

        if not user.is_active:
            raise ValueError(f"用户未激活: {user_id}")

        # 2. 检查认证凭证
        if not user.has_credentials():
            raise ValueError(f"用户认证凭证不存在: {user_id}")

        if not user.is_valid:
            raise ValueError(f"用户认证凭证已失效: {user_id}")

        # 3. 解密认证信息
        try:
            headers_json = self._crypto.decrypt(user.headers_encrypted)
            headers = json.loads(headers_json)
            cookies = self._crypto.decrypt(user.cookies_encrypted)
        except Exception as e:
            logger.error("decrypt_credentials_failed", user_id=user_id, error=str(e))
            raise ValueError("解密认证凭证失败") from e

        # 4. 调用币安API
        async with BinanceClient(headers=headers, cookies=cookies) as client:
            try:
                balance_data = await client.get_wallet_balance()
                
                # 5. 标记凭证已验证
                user.mark_credentials_verified()
                await self._user_repo.update(user)
                
                logger.info(
                    "balance_retrieved",
                    user_id=user_id,
                    total_valuation=balance_data.get("totalValuation"),
                )
                
                return {
                    "total_valuation": balance_data.get("totalValuation", "0"),
                    "balances": balance_data.get("list", []),
                }
            except ValueError as e:
                # API返回错误（可能是认证失败）
                if "登录状态已经失效" in str(e):
                    user.mark_credentials_invalid()
                    await self._user_repo.update(user)
                    logger.warning(
                        "credentials_invalidated", user_id=user_id, error=str(e)
                    )
                raise

    async def get_user_volume(self, user_id: int) -> Dict[str, Any]:
        """获取用户今日交易量

        Args:
            user_id: 用户ID

        Returns:
            交易量信息，格式：
            {
                "total_volume": 604467.94,
                "volumes_by_token": [
                    {
                        "token_name": "ALEO",
                        "volume": 604467.94
                    }
                ]
            }

        Raises:
            ValueError: 用户不存在或认证凭证无效
        """
        logger.info("get_user_volume", user_id=user_id)

        # 1. 获取用户
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"用户不存在: {user_id}")

        # 2. 检查认证凭证
        if not user.has_credentials() or not user.is_valid:
            raise ValueError(f"用户认证凭证无效: {user_id}")

        # 3. 解密认证信息
        try:
            headers_json = self._crypto.decrypt(user.headers_encrypted)
            headers = json.loads(headers_json)
            cookies = self._crypto.decrypt(user.cookies_encrypted)
        except Exception as e:
            logger.error("decrypt_credentials_failed", user_id=user_id, error=str(e))
            raise ValueError("解密认证凭证失败") from e

        # 4. 调用币安API
        async with BinanceClient(headers=headers, cookies=cookies) as client:
            try:
                volume_data = await client.get_user_volume()
                
                logger.info(
                    "volume_retrieved",
                    user_id=user_id,
                    total_volume=volume_data.get("totalVolume"),
                )
                
                return {
                    "total_volume": volume_data.get("totalVolume", 0),
                    "volumes_by_token": volume_data.get("tradeVolumeInfoList", []),
                }
            except ValueError as e:
                if "登录状态已经失效" in str(e):
                    user.mark_credentials_invalid()
                    await self._user_repo.update(user)
                raise

