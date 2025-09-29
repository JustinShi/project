"""
币安API客户端

与币安API交互的客户端。
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime

from ..config.api_config import ApiConfig
from ..adapters.http_adapter import HttpAdapter


class BinanceApiClient:
    """币安API客户端"""
    
    def __init__(self, api_config: ApiConfig, http_adapter: HttpAdapter):
        """初始化API客户端"""
        self.api_config = api_config
        self.http_adapter = http_adapter
        self.base_url = api_config.get_base_url()
    
    async def get_alpha_token_list(self) -> List[Dict[str, Any]]:
        """获取Alpha代币列表"""
        url = f"{self.base_url}/bapi/defi/v1/public/wallet-direct/buw/wallet/cex/alpha/all/token/list"
        
        try:
            response = await self.http_adapter.get(url)
            if response.get("success"):
                return response.get("data", [])
            else:
                raise Exception(f"API请求失败: {response.get('message')}")
        except Exception as e:
            print(f"获取Alpha代币列表失败: {e}")
            return []
    
    async def get_exchange_info(self) -> Dict[str, Any]:
        """获取交易精度信息"""
        url = f"{self.base_url}/bapi/defi/v1/public/alpha-trade/get-exchange-info"
        
        try:
            response = await self.http_adapter.get(url)
            return response
        except Exception as e:
            print(f"获取交易精度信息失败: {e}")
            return {}
    
    async def get_alpha_wallet_balance(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取Alpha钱包余额"""
        url = f"{self.base_url}/bapi/defi/v1/private/wallet-direct/cloud-wallet/alpha"
        params = {"includeCex": "1"}
        
        try:
            response = await self.http_adapter.get(url, params=params, user_id=user_id)
            if response.get("success"):
                return response.get("data")
            else:
                raise Exception(f"API请求失败: {response.get('message')}")
        except Exception as e:
            print(f"获取Alpha钱包余额失败: {e}")
            return None
    
    async def get_user_volume(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户交易量"""
        url = f"{self.base_url}/bapi/defi/v1/private/wallet-direct/buw/wallet/today/user-volume"
        
        try:
            response = await self.http_adapter.get(url, user_id=user_id)
            if response.get("success"):
                return response.get("data")
            else:
                raise Exception(f"API请求失败: {response.get('message')}")
        except Exception as e:
            print(f"获取用户交易量失败: {e}")
            return None
    
    async def place_order(
        self,
        user_id: str,
        symbol: str,
        side: str,
        quantity: Decimal,
        price: Decimal,
        time_in_force: str = "GTC"
    ) -> Optional[Dict[str, Any]]:
        """下普通订单"""
        url = f"{self.base_url}/bapi/defi/v1/private/alpha-trade/order/place"
        
        data = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "quantity": str(quantity),
            "price": str(price),
            "timeInForce": time_in_force
        }
        
        try:
            response = await self.http_adapter.post(url, data=data, user_id=user_id)
            if response.get("success"):
                return response.get("data")
            else:
                raise Exception(f"API请求失败: {response.get('message')}")
        except Exception as e:
            print(f"下单失败: {e}")
            return None
    
    async def place_oto_order(
        self,
        user_id: str,
        symbol: str,
        working_quantity: Decimal,
        working_price: Decimal,
        pending_price: Decimal,
        payment_details: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """下OTO订单（反向订单）"""
        url = f"{self.base_url}/bapi/defi/v1/private/alpha-trade/oto-order/place"
        
        data = {
            "workingPrice": str(working_price),
            "paymentDetails": payment_details,
            "pendingPrice": str(pending_price),
            "workingSide": "BUY",
            "workingQuantity": str(working_quantity),
            "baseAsset": symbol,
            "quoteAsset": "USDT"
        }
        
        try:
            response = await self.http_adapter.post(url, data=data, user_id=user_id)
            if response.get("success"):
                return response.get("data")
            else:
                raise Exception(f"API请求失败: {response.get('message')}")
        except Exception as e:
            print(f"下OTO订单失败: {e}")
            return None
    
    async def cancel_order(self, user_id: str, order_id: int) -> bool:
        """取消订单"""
        url = f"{self.base_url}/bapi/defi/v1/private/alpha-trade/order/cancel"
        
        data = {
            "orderId": order_id
        }
        
        try:
            response = await self.http_adapter.post(url, data=data, user_id=user_id)
            return response.get("success", False)
        except Exception as e:
            print(f"取消订单失败: {e}")
            return False
    
    async def get_listen_key(self, user_id: str) -> Optional[str]:
        """获取ListenKey"""
        url = f"{self.base_url}/bapi/defi/v1/private/alpha-trade/stream/get-listen-key"
        
        try:
            response = await self.http_adapter.post(url, user_id=user_id)
            if response.get("success"):
                return response.get("data", {}).get("listenKey")
            else:
                raise Exception(f"API请求失败: {response.get('message')}")
        except Exception as e:
            print(f"获取ListenKey失败: {e}")
            return None
    
    async def get_order_status(self, user_id: str, order_id: int) -> Optional[Dict[str, Any]]:
        """获取订单状态"""
        url = f"{self.base_url}/bapi/defi/v1/private/alpha-trade/order/status"
        params = {"orderId": order_id}
        
        try:
            response = await self.http_adapter.get(url, params=params, user_id=user_id)
            if response.get("success"):
                return response.get("data")
            else:
                raise Exception(f"API请求失败: {response.get('message')}")
        except Exception as e:
            print(f"获取订单状态失败: {e}")
            return None
    
    async def get_trade_history(
        self,
        user_id: str,
        symbol: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取交易历史"""
        url = f"{self.base_url}/bapi/defi/v1/private/alpha-trade/trade/history"
        
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            params["endTime"] = int(end_time.timestamp() * 1000)
        
        try:
            response = await self.http_adapter.get(url, params=params, user_id=user_id)
            if response.get("success"):
                return response.get("data", [])
            else:
                raise Exception(f"API请求失败: {response.get('message')}")
        except Exception as e:
            print(f"获取交易历史失败: {e}")
            return []
