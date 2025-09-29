"""
钱包实体

表示用户的数字钱包，包含资产信息。
"""

from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from ..value_objects.money import Money


@dataclass
class Asset:
    """资产信息"""
    
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


@dataclass
class Wallet:
    """钱包实体"""
    
    user_id: str
    total_valuation: Decimal
    assets: List[Asset]
    updated_at: datetime
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.user_id:
            raise ValueError("用户ID不能为空")
        if self.total_valuation < 0:
            raise ValueError("总估值不能为负数")
    
    def get_asset_by_symbol(self, symbol: str) -> Optional[Asset]:
        """根据符号获取资产"""
        for asset in self.assets:
            if asset.symbol == symbol:
                return asset
        return None
    
    def get_asset_by_token_id(self, token_id: str) -> Optional[Asset]:
        """根据代币ID获取资产"""
        for asset in self.assets:
            if asset.token_id == token_id:
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
    
    def update_asset(self, asset: Asset) -> None:
        """更新资产信息"""
        for i, existing_asset in enumerate(self.assets):
            if existing_asset.symbol == asset.symbol:
                self.assets[i] = asset
                self.updated_at = datetime.utcnow()
                return
        
        # 如果资产不存在，添加新资产
        self.assets.append(asset)
        self.updated_at = datetime.utcnow()
    
    def calculate_total_valuation(self) -> Decimal:
        """计算总估值"""
        return sum(asset.valuation for asset in self.assets)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "total_valuation": str(self.total_valuation),
            "assets": [
                {
                    "chain_id": asset.chain_id,
                    "contract_address": asset.contract_address,
                    "name": asset.name,
                    "symbol": asset.symbol,
                    "token_id": asset.token_id,
                    "free": str(asset.free),
                    "freeze": str(asset.freeze),
                    "locked": str(asset.locked),
                    "withdrawing": str(asset.withdrawing),
                    "amount": str(asset.amount),
                    "valuation": str(asset.valuation),
                    "cex_asset": asset.cex_asset
                }
                for asset in self.assets
            ],
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Wallet":
        """从字典创建钱包实体"""
        assets = [
            Asset(
                chain_id=asset_data["chain_id"],
                contract_address=asset_data["contract_address"],
                name=asset_data["name"],
                symbol=asset_data["symbol"],
                token_id=asset_data["token_id"],
                free=Decimal(asset_data["free"]),
                freeze=Decimal(asset_data["freeze"]),
                locked=Decimal(asset_data["locked"]),
                withdrawing=Decimal(asset_data["withdrawing"]),
                amount=Decimal(asset_data["amount"]),
                valuation=Decimal(asset_data["valuation"]),
                cex_asset=asset_data.get("cex_asset", False)
            )
            for asset_data in data["assets"]
        ]
        
        return cls(
            user_id=data["user_id"],
            total_valuation=Decimal(data["total_valuation"]),
            assets=assets,
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
