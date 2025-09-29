"""
Domain Repositories

仓储接口，定义数据访问的抽象。
"""

from .user_repository import UserRepository
from .wallet_repository import WalletRepository
from .order_repository import OrderRepository
from .trade_repository import TradeRepository

__all__ = [
    "UserRepository",
    "WalletRepository", 
    "OrderRepository",
    "TradeRepository"
]
