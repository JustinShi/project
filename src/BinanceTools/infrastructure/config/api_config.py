"""
API配置

管理API相关的配置信息。
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ApiConfig:
    """API配置"""
    
    def __init__(self, config_path: str = "configs/binance/api_config.json"):
        """初始化配置"""
        self.config_path = Path(config_path)
        self._config_cache = None
    
    def load_config(self) -> Dict[str, Any]:
        """加载API配置"""
        if self._config_cache is not None:
            return self._config_cache
        
        try:
            if not self.config_path.exists():
                # 创建默认配置
                default_config = self._get_default_config()
                self.save_config(default_config)
                return default_config
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self._config_cache = config
            return config
            
        except Exception as e:
            print(f"加载API配置失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "base_url": "https://www.binance.com",
            "api_version": "v1",
            "timeout": 30,
            "retry_count": 3,
            "retry_delay": 1,
            "rate_limit": {
                "requests_per_minute": 1200,
                "requests_per_second": 20
            },
            "endpoints": {
                "alpha_token_list": "/bapi/defi/v1/public/wallet-direct/buw/wallet/cex/alpha/all/token/list",
                "exchange_info": "/bapi/defi/v1/public/alpha-trade/get-exchange-info",
                "wallet_balance": "/bapi/defi/v1/private/wallet-direct/cloud-wallet/alpha",
                "user_volume": "/bapi/defi/v1/private/wallet-direct/buw/wallet/today/user-volume",
                "place_order": "/bapi/defi/v1/private/alpha-trade/order/place",
                "place_oto_order": "/bapi/defi/v1/private/alpha-trade/oto-order/place",
                "cancel_order": "/bapi/defi/v1/private/alpha-trade/order/cancel",
                "get_listen_key": "/bapi/defi/v1/private/alpha-trade/stream/get-listen-key",
                "order_status": "/bapi/defi/v1/private/alpha-trade/order/status",
                "trade_history": "/bapi/defi/v1/private/alpha-trade/trade/history"
            },
            "websocket": {
                "public_url": "wss://nbstream.binance.com/w3w/wsa/stream",
                "private_url": "wss://nbstream.binance.com/w3w/stream",
                "ping_interval": 20,
                "ping_timeout": 10
            }
        }
    
    def get_base_url(self) -> str:
        """获取基础URL"""
        config = self.load_config()
        return config.get("base_url", "https://www.binance.com")
    
    def get_timeout(self) -> int:
        """获取超时时间"""
        config = self.load_config()
        return config.get("timeout", 30)
    
    def get_retry_count(self) -> int:
        """获取重试次数"""
        config = self.load_config()
        return config.get("retry_count", 3)
    
    def get_retry_delay(self) -> int:
        """获取重试延迟"""
        config = self.load_config()
        return config.get("retry_delay", 1)
    
    def get_rate_limit(self) -> Dict[str, int]:
        """获取速率限制"""
        config = self.load_config()
        return config.get("rate_limit", {"requests_per_minute": 1200, "requests_per_second": 20})
    
    def get_endpoint(self, endpoint_name: str) -> str:
        """获取端点URL"""
        config = self.load_config()
        endpoints = config.get("endpoints", {})
        return endpoints.get(endpoint_name, "")
    
    def get_websocket_config(self) -> Dict[str, Any]:
        """获取WebSocket配置"""
        config = self.load_config()
        return config.get("websocket", {})
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 更新缓存
            self._config_cache = config
            return True
            
        except Exception as e:
            print(f"保存API配置失败: {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """更新配置"""
        config = self.load_config()
        config.update(updates)
        return self.save_config(config)
    
    def clear_cache(self):
        """清除缓存"""
        self._config_cache = None
