"""
币安钱包仓储实现

实现钱包仓储接口，从币安API获取钱包信息。
"""

from typing import Optional
from datetime import datetime

from ...domain.entities.wallet import Wallet, Asset
from ...domain.repositories.wallet_repository import WalletRepository
from ..external_services.binance_api_client import BinanceApiClient


class BinanceWalletRepository(WalletRepository):
    """币安钱包仓储实现"""
    
    def __init__(self, api_client: BinanceApiClient):
        """初始化仓储"""
        self.api_client = api_client
        self._wallet_cache = {}
    
    async def get_by_user_id(self, user_id: str) -> Optional[Wallet]:
        """根据用户ID获取钱包"""
        if user_id in self._wallet_cache:
            return self._wallet_cache[user_id]
        
        try:
            # 从币安API获取钱包信息
            wallet_data = await self.api_client.get_alpha_wallet_balance(user_id)
            
            if not wallet_data:
                return None
            
            wallet = self._create_wallet_from_data(user_id, wallet_data)
            self._wallet_cache[user_id] = wallet
            return wallet
            
        except Exception as e:
            # 记录错误日志
            print(f"获取钱包信息失败: {e}")
            return None
    
    async def save(self, wallet: Wallet) -> Wallet:
        """保存钱包"""
        # 钱包信息通常不需要保存，因为它是从API实时获取的
        self._wallet_cache[wallet.user_id] = wallet
        return wallet
    
    async def update(self, wallet: Wallet) -> Wallet:
        """更新钱包"""
        # 钱包信息通常不需要更新，因为它是从API实时获取的
        self._wallet_cache[wallet.user_id] = wallet
        return wallet
    
    async def delete(self, user_id: str) -> bool:
        """删除钱包"""
        if user_id in self._wallet_cache:
            del self._wallet_cache[user_id]
            return True
        return False
    
    async def exists(self, user_id: str) -> bool:
        """检查钱包是否存在"""
        return await self.get_by_user_id(user_id) is not None
    
    def _create_wallet_from_data(self, user_id: str, wallet_data: dict) -> Wallet:
        """从数据创建钱包实体"""
        assets = []
        
        for asset_data in wallet_data.get("list", []):
            asset = Asset(
                chain_id=asset_data["chainId"],
                contract_address=asset_data["contractAddress"],
                name=asset_data["name"],
                symbol=asset_data["symbol"],
                token_id=asset_data["tokenId"],
                free=asset_data["free"],
                freeze=asset_data["freeze"],
                locked=asset_data["locked"],
                withdrawing=asset_data["withdrawing"],
                amount=asset_data["amount"],
                valuation=asset_data["valuation"],
                cex_asset=asset_data.get("cexAsset", False)
            )
            assets.append(asset)
        
        return Wallet(
            user_id=user_id,
            total_valuation=wallet_data["totalValuation"],
            assets=assets,
            updated_at=datetime.utcnow()
        )
