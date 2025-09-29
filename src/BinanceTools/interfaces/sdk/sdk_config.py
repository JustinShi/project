"""
SDK配置

SDK配置管理。
"""

from typing import Optional
from pathlib import Path

from ...infrastructure.config.user_config import UserConfig
from ...infrastructure.config.api_config import ApiConfig
from ...infrastructure.config.proxy_config import ProxyConfig


class SdkConfig:
    """SDK配置"""
    
    def __init__(
        self,
        user_config_path: Optional[str] = None,
        api_config_path: Optional[str] = None,
        proxy_config_path: Optional[str] = None
    ):
        """初始化SDK配置"""
        self.user_config_path = user_config_path or "configs/binance/users.json"
        self.api_config_path = api_config_path or "configs/binance/api_config.json"
        self.proxy_config_path = proxy_config_path or "configs/proxy.json"
        
        self._user_config = None
        self._api_config = None
        self._proxy_config = None
    
    def get_user_config(self) -> UserConfig:
        """获取用户配置"""
        if self._user_config is None:
            self._user_config = UserConfig(self.user_config_path)
        return self._user_config
    
    def get_api_config(self) -> ApiConfig:
        """获取API配置"""
        if self._api_config is None:
            self._api_config = ApiConfig(self.api_config_path)
        return self._api_config
    
    def get_proxy_config(self) -> ProxyConfig:
        """获取代理配置"""
        if self._proxy_config is None:
            self._proxy_config = ProxyConfig(self.proxy_config_path)
        return self._proxy_config
    
    def set_user_config_path(self, path: str):
        """设置用户配置文件路径"""
        self.user_config_path = path
        self._user_config = None
    
    def set_api_config_path(self, path: str):
        """设置API配置文件路径"""
        self.api_config_path = path
        self._api_config = None
    
    def set_proxy_config_path(self, path: str):
        """设置代理配置文件路径"""
        self.proxy_config_path = path
        self._proxy_config = None
    
    def validate_config(self) -> bool:
        """验证配置"""
        try:
            # 检查配置文件是否存在
            user_config_path = Path(self.user_config_path)
            if not user_config_path.exists():
                return False
            
            api_config_path = Path(self.api_config_path)
            if not api_config_path.exists():
                return False
            
            # 检查配置是否有效
            user_config = self.get_user_config()
            api_config = self.get_api_config()
            
            # 检查是否有活跃用户
            active_users = user_config.get_active_users()
            if not active_users:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_config_info(self) -> dict:
        """获取配置信息"""
        return {
            "user_config_path": self.user_config_path,
            "api_config_path": self.api_config_path,
            "proxy_config_path": self.proxy_config_path,
            "user_config_exists": Path(self.user_config_path).exists(),
            "api_config_exists": Path(self.api_config_path).exists(),
            "proxy_config_exists": Path(self.proxy_config_path).exists(),
            "config_valid": self.validate_config()
        }
