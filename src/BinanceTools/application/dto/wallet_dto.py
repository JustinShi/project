"""
钱包DTO

钱包相关的数据传输对象。
"""

from dataclasses import dataclass
from typing import List
from decimal import Decimal
from datetime import datetime

from ...domain.entities.wallet import Wallet, Asset


@dataclass
class AssetDTO:
    """资产DTO"""
    
    chain_id: str
    contract_address: str
    name: str
    symbol: str
    token_id: str
    free: Decimal
    freeze: Decimal
    locked: Decimal
    withdrawing: Decimal
    amount: Decimal
    valuation: Decimal
    cex_asset: bool = False
    
    @property
    def total_balance(self) -> Decimal:
        """总余额"""
        return self.free + self.freeze + self.locked
    
    @property
    def available_balance(self) -> Decimal:
        """可用余额"""
        return self.free
    
    @classmethod
    def from_entity(cls, asset: Asset) -> "AssetDTO":
        """从实体创建DTO"""
        return cls(
            chain_id=asset.chain_id,
            contract_address=asset.contract_address,
            name=asset.name,
            symbol=asset.symbol,
            token_id=asset.token_id,
            free=asset.free,
            freeze=asset.freeze,
            locked=asset.locked,
            withdrawing=asset.withdrawing,
            amount=asset.amount,
            valuation=asset.valuation,
            cex_asset=asset.cex_asset
        )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "chain_id": self.chain_id,
            "contract_address": self.contract_address,
            "name": self.name,
            "symbol": self.symbol,
            "token_id": self.token_id,
            "free": str(self.free),
            "freeze": str(self.freeze),
            "locked": str(self.locked),
            "withdrawing": str(self.withdrawing),
            "amount": str(self.amount),
            "valuation": str(self.valuation),
            "cex_asset": self.cex_asset,
            "total_balance": str(self.total_balance),
            "available_balance": str(self.available_balance)
        }


@dataclass
class WalletDTO:
    """钱包DTO"""
    
    user_id: str
    total_valuation: Decimal
    assets: List[AssetDTO]
    updated_at: datetime
    
    def get_asset_by_symbol(self, symbol: str) -> AssetDTO:
        """根据符号获取资产"""
        for asset in self.assets:
            if asset.symbol == symbol:
                return asset
        return None
    
    def get_available_balance(self, symbol: str) -> Decimal:
        """获取指定代币的可用余额"""
        asset = self.get_asset_by_symbol(symbol)
        return asset.available_balance if asset else Decimal('0')
    
    def get_total_balance(self, symbol: str) -> Decimal:
        """获取指定代币的总余额"""
        asset = self.get_asset_by_symbol(symbol)
        return asset.total_balance if asset else Decimal('0')
    
    def has_sufficient_balance(self, symbol: str, amount: Decimal) -> bool:
        """检查是否有足够的余额"""
        return self.get_available_balance(symbol) >= amount
    
    @classmethod
    def from_entity(cls, wallet: Wallet) -> "WalletDTO":
        """从实体创建DTO"""
        return cls(
            user_id=wallet.user_id,
            total_valuation=wallet.total_valuation,
            assets=[AssetDTO.from_entity(asset) for asset in wallet.assets],
            updated_at=wallet.updated_at
        )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "total_valuation": str(self.total_valuation),
            "assets": [asset.to_dict() for asset in self.assets],
            "updated_at": self.updated_at.isoformat()
        }
