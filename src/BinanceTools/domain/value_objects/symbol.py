"""
交易对值对象

表示交易对，包含基础资产和报价资产。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Symbol:
    """交易对值对象"""
    
    base_asset: str
    quote_asset: str
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.base_asset:
            raise ValueError("基础资产不能为空")
        if not self.quote_asset:
            raise ValueError("报价资产不能为空")
        if self.base_asset == self.quote_asset:
            raise ValueError("基础资产和报价资产不能相同")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.base_asset}{self.quote_asset}"
    
    def __eq__(self, other: "Symbol") -> bool:
        """相等比较"""
        if not isinstance(other, Symbol):
            return False
        return self.base_asset == other.base_asset and self.quote_asset == other.quote_asset
    
    def __hash__(self) -> int:
        """哈希值"""
        return hash((self.base_asset, self.quote_asset))
    
    def is_alpha_token(self) -> bool:
        """是否为Alpha代币"""
        return self.base_asset.startswith("ALPHA_")
    
    def get_alpha_id(self) -> Optional[str]:
        """获取Alpha ID"""
        if self.is_alpha_token():
            return self.base_asset
        return None
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        if self.is_alpha_token():
            return f"{self.base_asset}/{self.quote_asset}"
        return f"{self.base_asset}{self.quote_asset}"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "base_asset": self.base_asset,
            "quote_asset": self.quote_asset
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Symbol":
        """从字典创建Symbol对象"""
        return cls(
            base_asset=data["base_asset"],
            quote_asset=data["quote_asset"]
        )
    
    @classmethod
    def from_string(cls, symbol_str: str) -> "Symbol":
        """从字符串创建Symbol对象"""
        if not symbol_str:
            raise ValueError("交易对字符串不能为空")
        
        # 处理不同的交易对格式
        if "/" in symbol_str:
            # 格式: BTC/USDT
            parts = symbol_str.split("/")
            if len(parts) != 2:
                raise ValueError("无效的交易对格式")
            return cls(parts[0], parts[1])
        else:
            # 格式: BTCUSDT
            # 尝试分离基础资产和报价资产
            common_quote_assets = ["USDT", "USDC", "BUSD", "BNB", "BTC", "ETH"]
            
            for quote_asset in common_quote_assets:
                if symbol_str.endswith(quote_asset):
                    base_asset = symbol_str[:-len(quote_asset)]
                    if base_asset:
                        return cls(base_asset, quote_asset)
            
            # 如果无法分离，假设最后3个字符是报价资产
            if len(symbol_str) > 3:
                return cls(symbol_str[:-3], symbol_str[-3:])
            
            raise ValueError(f"无法解析交易对: {symbol_str}")
    
    @classmethod
    def alpha_token(cls, alpha_id: str, quote_asset: str = "USDT") -> "Symbol":
        """创建Alpha代币交易对"""
        if not alpha_id.startswith("ALPHA_"):
            raise ValueError("Alpha ID必须以ALPHA_开头")
        return cls(alpha_id, quote_asset)
