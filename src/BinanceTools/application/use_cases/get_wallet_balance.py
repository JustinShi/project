"""
获取钱包余额用例

获取用户的钱包余额信息。
"""

from typing import Optional
from decimal import Decimal

from ...domain.entities.wallet import Wallet
from ...domain.repositories.wallet_repository import WalletRepository
from ...domain.repositories.user_repository import UserRepository
from ..dto.wallet_dto import WalletDTO


class GetWalletBalanceUseCase:
    """获取钱包余额用例"""
    
    def __init__(
        self,
        wallet_repository: WalletRepository,
        user_repository: UserRepository
    ):
        """初始化用例"""
        self.wallet_repository = wallet_repository
        self.user_repository = user_repository
    
    async def execute(self, user_id: str) -> Optional[WalletDTO]:
        """执行用例"""
        # 检查用户是否存在
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"用户不存在: {user_id}")
        
        if not user.is_active():
            raise ValueError(f"用户未激活: {user_id}")
        
        # 获取钱包信息
        wallet = await self.wallet_repository.get_by_user_id(user_id)
        if not wallet:
            return None
        
        # 转换为DTO
        return WalletDTO.from_entity(wallet)
