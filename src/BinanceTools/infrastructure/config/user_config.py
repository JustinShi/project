"""
用户配置

管理用户配置信息。
"""

import json
import os
from typing import Dict, Any, List
from pathlib import Path


class UserConfig:
    """用户配置"""
    
    def __init__(self, config_path: str = "configs/binance/users.json"):
        """初始化配置"""
        self.config_path = Path(config_path)
        self._config_cache = None
    
    def load_users(self) -> Dict[str, Any]:
        """加载用户配置"""
        if self._config_cache is not None:
            return self._config_cache
        
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self._config_cache = config
            return config
            
        except Exception as e:
            print(f"加载用户配置失败: {e}")
            return {"users": [], "default_user": None}
    
    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """根据ID获取用户配置"""
        config = self.load_users()
        
        for user in config.get("users", []):
            if user["id"] == user_id:
                return user
        
        return {}
    
    def get_default_user(self) -> Dict[str, Any]:
        """获取默认用户配置"""
        config = self.load_users()
        default_user_id = config.get("default_user")
        
        if default_user_id:
            return self.get_user_by_id(default_user_id)
        
        return {}
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        """获取活跃用户配置"""
        config = self.load_users()
        
        return [
            user for user in config.get("users", [])
            if user.get("enabled", False)
        ]
    
    def save_users(self, config: Dict[str, Any]) -> bool:
        """保存用户配置"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 更新缓存
            self._config_cache = config
            return True
            
        except Exception as e:
            print(f"保存用户配置失败: {e}")
            return False
    
    def add_user(self, user_data: Dict[str, Any]) -> bool:
        """添加用户"""
        config = self.load_users()
        
        # 检查用户ID是否已存在
        for user in config.get("users", []):
            if user["id"] == user_data["id"]:
                return False
        
        # 添加用户
        if "users" not in config:
            config["users"] = []
        
        config["users"].append(user_data)
        
        return self.save_users(config)
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """更新用户"""
        config = self.load_users()
        
        for i, user in enumerate(config.get("users", [])):
            if user["id"] == user_id:
                config["users"][i] = user_data
                return self.save_users(config)
        
        return False
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        config = self.load_users()
        
        for i, user in enumerate(config.get("users", [])):
            if user["id"] == user_id:
                del config["users"][i]
                return self.save_users(config)
        
        return False
    
    def set_default_user(self, user_id: str) -> bool:
        """设置默认用户"""
        config = self.load_users()
        
        # 检查用户是否存在
        user_exists = any(user["id"] == user_id for user in config.get("users", []))
        if not user_exists:
            return False
        
        config["default_user"] = user_id
        return self.save_users(config)
    
    def clear_cache(self):
        """清除缓存"""
        self._config_cache = None
