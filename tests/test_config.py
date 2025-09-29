"""
配置管理模块测试
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from src.BinanceTools.config.user_config import (
    UserConfig, ApiConfig, WebSocketConfig, UserConfigManager
)


class TestUserConfig:
    """用户配置数据类测试"""
    
    def test_user_config_creation(self):
        """测试用户配置创建"""
        user = UserConfig(
            id="test_user",
            name="测试用户",
            enabled=True,
            headers={"User-Agent": "Test"},
            cookies={"session_id": "test123"}
        )
        
        assert user.id == "test_user"
        assert user.name == "测试用户"
        assert user.enabled is True
        assert user.headers["User-Agent"] == "Test"
        assert user.cookies["session_id"] == "test123"
    
    def test_user_config_equality(self):
        """测试用户配置相等性"""
        user1 = UserConfig(
            id="test_user",
            name="测试用户",
            enabled=True,
            headers={"User-Agent": "Test"},
            cookies={"session_id": "test123"}
        )
        
        user2 = UserConfig(
            id="test_user",
            name="测试用户",
            enabled=True,
            headers={"User-Agent": "Test"},
            cookies={"session_id": "test123"}
        )
        
        assert user1 == user2


class TestApiConfig:
    """API配置数据类测试"""
    
    def test_api_config_creation(self):
        """测试API配置创建"""
        api = ApiConfig(
            base_url="https://test.com",
            timeout=30,
            retry_times=3,
            endpoints={"test": "/api/test"}
        )
        
        assert api.base_url == "https://test.com"
        assert api.timeout == 30
        assert api.retry_times == 3
        assert api.endpoints["test"] == "/api/test"
    
    def test_api_config_defaults(self):
        """测试API配置默认值"""
        api = ApiConfig(base_url="https://test.com")
        
        assert api.base_url == "https://test.com"
        assert api.timeout == 30
        assert api.retry_times == 3
        assert api.endpoints is None


class TestWebSocketConfig:
    """WebSocket配置数据类测试"""
    
    def test_websocket_config_creation(self):
        """测试WebSocket配置创建"""
        ws = WebSocketConfig(
            stream_url="wss://test.com/stream",
            order_stream_url="wss://test.com/orders",
            ping_interval=30,
            reconnect_interval=5,
            max_reconnect_attempts=10
        )
        
        assert ws.stream_url == "wss://test.com/stream"
        assert ws.order_stream_url == "wss://test.com/orders"
        assert ws.ping_interval == 30
        assert ws.reconnect_interval == 5
        assert ws.max_reconnect_attempts == 10
    
    def test_websocket_config_defaults(self):
        """测试WebSocket配置默认值"""
        ws = WebSocketConfig(
            stream_url="wss://test.com/stream",
            order_stream_url="wss://test.com/orders"
        )
        
        assert ws.stream_url == "wss://test.com/stream"
        assert ws.order_stream_url == "wss://test.com/orders"
        assert ws.ping_interval == 30
        assert ws.reconnect_interval == 5
        assert ws.max_reconnect_attempts == 10


class TestUserConfigManager:
    """用户配置管理器测试"""
    
    def test_init_with_default_paths(self):
        """测试使用默认路径初始化"""
        manager = UserConfigManager()
        
        assert manager.users_config_path.name == "users.json"
        assert manager.api_config_path.name == "api_config.json"
    
    def test_init_with_custom_paths(self, temp_config_dir):
        """测试使用自定义路径初始化"""
        users_path = temp_config_dir / "custom_users.json"
        api_path = temp_config_dir / "custom_api.json"
        
        manager = UserConfigManager(str(users_path), str(api_path))
        
        assert manager.users_config_path == users_path
        assert manager.api_config_path == api_path
    
    def test_load_config_success(self, users_config_file, api_config_file, sample_users_config, sample_api_config):
        """测试成功加载配置"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        
        result = manager.load_config()
        
        assert result is True
        assert len(manager._users) == 2
        assert manager._users[0].id == "test_user_001"
        assert manager._users[0].enabled is True
        assert manager._users[1].id == "test_user_002"
        assert manager._users[1].enabled is False
        assert manager._api_config.base_url == "https://test.example.com"
        assert manager._websocket_config.stream_url == "wss://test.example.com/stream"
    
    def test_load_config_file_not_found(self, temp_config_dir):
        """测试配置文件不存在的情况"""
        manager = UserConfigManager(
            str(temp_config_dir / "nonexistent_users.json"),
            str(temp_config_dir / "nonexistent_api.json")
        )
        
        result = manager.load_config()
        
        assert result is False
    
    def test_load_config_invalid_json(self, temp_config_dir):
        """测试无效JSON文件"""
        # 创建无效的JSON文件
        invalid_file = temp_config_dir / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("invalid json content")
        
        manager = UserConfigManager(str(invalid_file), str(invalid_file))
        
        result = manager.load_config()
        
        assert result is False
    
    def test_get_user_default(self, users_config_file, api_config_file):
        """测试获取默认用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        user = manager.get_user()
        
        assert user is not None
        assert user.id == "test_user_001"  # 默认用户
    
    def test_get_user_by_id(self, users_config_file, api_config_file):
        """测试根据ID获取用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        user = manager.get_user_by_id("test_user_001")
        
        assert user is not None
        assert user.id == "test_user_001"
        assert user.enabled is True
    
    def test_get_user_by_id_disabled(self, users_config_file, api_config_file):
        """测试获取禁用的用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        user = manager.get_user_by_id("test_user_002")
        
        assert user is None  # 禁用的用户不应该被返回
    
    def test_get_user_by_id_not_found(self, users_config_file, api_config_file):
        """测试获取不存在的用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        user = manager.get_user_by_id("nonexistent_user")
        
        assert user is None
    
    def test_get_all_users(self, users_config_file, api_config_file):
        """测试获取所有用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        users = manager.get_all_users()
        
        assert len(users) == 2
        assert users[0].id == "test_user_001"
        assert users[1].id == "test_user_002"
    
    def test_get_enabled_users(self, users_config_file, api_config_file):
        """测试获取启用的用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        enabled_users = manager.get_enabled_users()
        
        assert len(enabled_users) == 1
        assert enabled_users[0].id == "test_user_001"
        assert enabled_users[0].enabled is True
    
    def test_get_users_by_ids(self, users_config_file, api_config_file):
        """测试根据ID列表获取用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        users = manager.get_users_by_ids(["test_user_001", "test_user_002"])
        
        # 只有启用的用户会被返回
        assert len(users) == 1
        assert users[0].id == "test_user_001"
    
    def test_get_api_config(self, users_config_file, api_config_file):
        """测试获取API配置"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        api_config = manager.get_api_config()
        
        assert api_config is not None
        assert api_config.base_url == "https://test.example.com"
        assert api_config.timeout == 30
        assert api_config.retry_times == 3
    
    def test_get_websocket_config(self, users_config_file, api_config_file):
        """测试获取WebSocket配置"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        ws_config = manager.get_websocket_config()
        
        assert ws_config is not None
        assert ws_config.stream_url == "wss://test.example.com/stream"
        assert ws_config.ping_interval == 30
    
    def test_add_user_success(self, users_config_file, api_config_file):
        """测试成功添加用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        new_user = UserConfig(
            id="new_user",
            name="新用户",
            enabled=True,
            headers={"User-Agent": "New-Agent"},
            cookies={"session_id": "new_session"}
        )
        
        result = manager.add_user(new_user)
        
        assert result is True
        assert len(manager._users_config_data["users"]) == 3
    
    def test_add_user_duplicate_id(self, users_config_file, api_config_file):
        """测试添加重复ID的用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        duplicate_user = UserConfig(
            id="test_user_001",  # 已存在的ID
            name="重复用户",
            enabled=True,
            headers={"User-Agent": "Duplicate-Agent"},
            cookies={"session_id": "duplicate_session"}
        )
        
        result = manager.add_user(duplicate_user)
        
        assert result is False
    
    def test_update_user_success(self, users_config_file, api_config_file):
        """测试成功更新用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        result = manager.update_user("test_user_001", name="更新后的名称")
        
        assert result is True
        # 验证更新是否生效
        updated_user = manager.get_user_by_id("test_user_001")
        assert updated_user.name == "更新后的名称"
    
    def test_update_user_not_found(self, users_config_file, api_config_file):
        """测试更新不存在的用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        result = manager.update_user("nonexistent_user", name="新名称")
        
        assert result is False
    
    def test_remove_user_success(self, users_config_file, api_config_file):
        """测试成功删除用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        initial_count = len(manager._users_config_data["users"])
        result = manager.remove_user("test_user_002")
        
        assert result is True
        assert len(manager._users_config_data["users"]) == initial_count - 1
    
    def test_remove_user_not_found(self, users_config_file, api_config_file):
        """测试删除不存在的用户"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        result = manager.remove_user("nonexistent_user")
        
        assert result is False
    
    def test_save_users_config(self, temp_config_dir, sample_users_config):
        """测试保存用户配置"""
        users_file = temp_config_dir / "test_users.json"
        api_file = temp_config_dir / "test_api.json"
        
        # 创建API配置文件
        with open(api_file, 'w') as f:
            json.dump({"api_config": {}, "websocket_config": {}}, f)
        
        manager = UserConfigManager(str(users_file), str(api_file))
        manager._users_config_data = sample_users_config
        
        result = manager.save_users_config()
        
        assert result is True
        assert users_file.exists()
        
        # 验证保存的内容
        with open(users_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data == sample_users_config
    
    def test_reload_config(self, users_config_file, api_config_file):
        """测试重新加载配置"""
        manager = UserConfigManager(str(users_config_file), str(api_config_file))
        manager.load_config()
        
        # 修改内存中的数据
        manager._users[0].name = "修改后的名称"
        
        # 重新加载配置
        result = manager.reload_config()
        
        assert result is True
        # 验证数据已重置
        assert manager._users[0].name == "测试用户1"  # 原始名称
