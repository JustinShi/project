"""
代理配置

管理代理相关的配置信息。
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ProxyConfig:
    """代理配置"""
    
    def __init__(self, config_path: str = "configs/proxy.json"):
        """初始化配置"""
        self.config_path = Path(config_path)
        self._config_cache = None
    
    def load_config(self) -> Dict[str, Any]:
        """加载代理配置"""
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
            print(f"加载代理配置失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "enabled": False,
            "type": "http",
            "host": "",
            "port": 0,
            "username": "",
            "password": "",
            "timeout": 30,
            "retry_count": 3,
            "retry_delay": 1
        }
    
    def is_enabled(self) -> bool:
        """是否启用代理"""
        config = self.load_config()
        return config.get("enabled", False)
    
    def get_proxy_url(self) -> Optional[str]:
        """获取代理URL"""
        config = self.load_config()
        
        if not config.get("enabled", False):
            return None
        
        proxy_type = config.get("type", "http")
        host = config.get("host", "")
        port = config.get("port", 0)
        username = config.get("username", "")
        password = config.get("password", "")
        
        if not host or not port:
            return None
        
        if username and password:
            return f"{proxy_type}://{username}:{password}@{host}:{port}"
        else:
            return f"{proxy_type}://{host}:{port}"
    
    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """获取代理字典"""
        config = self.load_config()
        
        if not config.get("enabled", False):
            return None
        
        proxy_type = config.get("type", "http")
        host = config.get("host", "")
        port = config.get("port", 0)
        username = config.get("username", "")
        password = config.get("password", "")
        
        if not host or not port:
            return None
        
        if username and password:
            proxy_url = f"{proxy_type}://{username}:{password}@{host}:{port}"
        else:
            proxy_url = f"{proxy_type}://{host}:{port}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    
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
            print(f"保存代理配置失败: {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """更新配置"""
        config = self.load_config()
        config.update(updates)
        return self.save_config(config)
    
    def clear_cache(self):
        """清除缓存"""
        self._config_cache = None
