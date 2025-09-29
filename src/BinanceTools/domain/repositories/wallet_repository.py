"""
钱包仓储接口

定义钱包数据访问的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.wallet import Wallet


class WalletRepository(ABC):
    """钱包仓储接口"""
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[Wallet]:
        """根据用户ID获取钱包"""
        pass
    
    @abstractmethod
    async def save(self, wallet: Wallet) -> Wallet:
        """保存钱包"""
        pass
    
    @abstractmethod
    async def update(self, wallet: Wallet) -> Wallet:
        """更新钱包"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """删除钱包"""
        pass
    
    @abstractmethod
    async def exists(self, user_id: str) -> bool:
        """检查钱包是否存在"""
        pass
