"""
多用户服务测试
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from src.BinanceTools.service.multi_user_service import (
    MultiUserBinanceService, MultiUserConfig, MultiUserResult
)
from src.BinanceTools.config.user_config import UserConfig, ApiConfig, WebSocketConfig
from src.BinanceTools.service.binance_service import BinanceService


class TestMultiUserResult:
    """多用户结果数据类测试"""
    
    def test_multi_user_result_success(self):
        """测试成功结果"""
        result = MultiUserResult(
            user_id="user_001",
            success=True,
            data={"test": "data"}
        )
        
        assert result.user_id == "user_001"
        assert result.success is True
        assert result.data == {"test": "data"}
        assert result.error is None
    
    def test_multi_user_result_error(self):
        """测试错误结果"""
        result = MultiUserResult(
            user_id="user_001",
            success=False,
            error="Test error"
        )
        
        assert result.user_id == "user_001"
        assert result.success is False
        assert result.error == "Test error"
        assert result.data is None


class TestMultiUserConfig:
    """多用户配置测试"""
    
    def test_multi_user_config_defaults(self):
        """测试默认配置"""
        config = MultiUserConfig()
        
        assert config.max_concurrent_users == 5
        assert config.auto_detect_enabled_users is True
        assert config.retry_failed_users is True
        assert config.max_retry_attempts == 2
    
    def test_multi_user_config_custom(self):
        """测试自定义配置"""
        config = MultiUserConfig(
            max_concurrent_users=10,
            auto_detect_enabled_users=False,
            retry_failed_users=False,
            max_retry_attempts=5
        )
        
        assert config.max_concurrent_users == 10
        assert config.auto_detect_enabled_users is False
        assert config.retry_failed_users is False
        assert config.max_retry_attempts == 5


class TestMultiUserBinanceService:
    """多用户Binance服务测试"""
    
    @pytest.fixture
    def mock_user_configs(self):
        """模拟用户配置"""
        return [
            UserConfig(
                id="user_001",
                name="用户1",
                enabled=True,
                headers={"User-Agent": "Agent1"},
                cookies={"session": "session1"}
            ),
            UserConfig(
                id="user_002",
                name="用户2",
                enabled=True,
                headers={"User-Agent": "Agent2"},
                cookies={"session": "session2"}
            ),
            UserConfig(
                id="user_003",
                name="用户3",
                enabled=False,
                headers={"User-Agent": "Agent3"},
                cookies={"session": "session3"}
            )
        ]
    
    @pytest.fixture
    def mock_api_config(self):
        """模拟API配置"""
        return ApiConfig(
            base_url="https://test.com",
            timeout=30,
            retry_times=3,
            endpoints={"test": "/api/test"}
        )
    
    @pytest.fixture
    def mock_websocket_config(self):
        """模拟WebSocket配置"""
        return WebSocketConfig(
            stream_url="wss://test.com/stream",
            order_stream_url="wss://test.com/orders",
            ping_interval=30,
            reconnect_interval=5,
            max_reconnect_attempts=10
        )
    
    @pytest.fixture
    def mock_config_manager(self, mock_user_configs, mock_api_config, mock_websocket_config):
        """模拟配置管理器"""
        manager = Mock()
        manager.get_enabled_users.return_value = [mock_user_configs[0], mock_user_configs[1]]
        manager.get_users_by_ids.return_value = [mock_user_configs[0]]
        manager.get_api_config.return_value = mock_api_config
        manager.get_websocket_config.return_value = mock_websocket_config
        return manager
    
    @pytest.fixture
    def mock_binance_service(self):
        """模拟Binance服务"""
        service = AsyncMock(spec=BinanceService)
        service.initialize = AsyncMock(return_value=True)
        service.disconnect = AsyncMock()
        service.get_wallet_balance = AsyncMock(return_value={"balance": "100.0"})
        service.get_today_volume = AsyncMock(return_value={"volume": "1000.0"})
        service.place_oto_order = AsyncMock(return_value={"order_id": "12345"})
        service.connect_websocket = AsyncMock(return_value=True)
        return service
    
    @pytest.mark.asyncio
    async def test_init(self):
        """测试初始化"""
        service = MultiUserBinanceService()
        
        assert service.multi_user_config.max_concurrent_users == 5
        assert service.multi_user_config.auto_detect_enabled_users is True
        assert len(service._user_services) == 0
        assert len(service._enabled_users) == 0
    
    @pytest.mark.asyncio
    async def test_init_with_config(self):
        """测试使用配置初始化"""
        config = MultiUserConfig(max_concurrent_users=10)
        service = MultiUserBinanceService(config)
        
        assert service.multi_user_config.max_concurrent_users == 10
    
    @pytest.mark.asyncio
    async def test_initialize_auto_detect_users(self, mock_config_manager, mock_binance_service):
        """测试自动检测用户初始化"""
        with patch('src.BinanceTools.service.multi_user_service.UserConfigManager', return_value=mock_config_manager), \
             patch('src.BinanceTools.service.multi_user_service.BinanceService', return_value=mock_binance_service):
            
            service = MultiUserBinanceService()
            result = await service.initialize()
            
            assert result is True
            assert len(service._enabled_users) == 2
            assert len(service._user_services) == 2
            mock_config_manager.get_enabled_users.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_specific_users(self, mock_config_manager, mock_binance_service):
        """测试指定用户初始化"""
        with patch('src.BinanceTools.service.multi_user_service.UserConfigManager', return_value=mock_config_manager), \
             patch('src.BinanceTools.service.multi_user_service.BinanceService', return_value=mock_binance_service):
            
            service = MultiUserBinanceService()
            result = await service.initialize(["user_001"])
            
            assert result is True
            assert len(service._enabled_users) == 1
            mock_config_manager.get_users_by_ids.assert_called_once_with(["user_001"])
    
    @pytest.mark.asyncio
    async def test_initialize_no_config(self, mock_config_manager):
        """测试初始化失败（无配置）"""
        mock_config_manager.get_api_config.return_value = None
        
        with patch('src.BinanceTools.service.multi_user_service.UserConfigManager', return_value=mock_config_manager):
            service = MultiUserBinanceService()
            result = await service.initialize()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_initialize_no_users(self, mock_config_manager):
        """测试初始化失败（无用户）"""
        mock_config_manager.get_enabled_users.return_value = []
        
        with patch('src.BinanceTools.service.multi_user_service.UserConfigManager', return_value=mock_config_manager):
            service = MultiUserBinanceService()
            result = await service.initialize()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_all_wallet_balances(self, mock_binance_service):
        """测试获取所有用户钱包余额"""
        service = MultiUserBinanceService()
        service._user_services = {
            "user_001": mock_binance_service,
            "user_002": mock_binance_service
        }
        
        results = await service.get_all_wallet_balances()
        
        assert len(results) == 2
        assert all(result.success for result in results)
        assert all("balance" in result.data for result in results)
        assert mock_binance_service.get_wallet_balance.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_all_trading_volumes(self, mock_binance_service):
        """测试获取所有用户交易量"""
        service = MultiUserBinanceService()
        service._user_services = {
            "user_001": mock_binance_service,
            "user_002": mock_binance_service
        }
        
        results = await service.get_all_trading_volumes()
        
        assert len(results) == 2
        assert all(result.success for result in results)
        assert all("volume" in result.data for result in results)
        assert mock_binance_service.get_today_volume.call_count == 2
    
    @pytest.mark.asyncio
    async def test_place_orders_all_users(self, mock_binance_service):
        """测试为所有用户创建订单"""
        service = MultiUserBinanceService()
        service._user_services = {
            "user_001": mock_binance_service,
            "user_002": mock_binance_service
        }
        
        results = await service.place_orders_all_users(
            working_price="0.1",
            working_quantity="100",
            pending_price="0.01",
            base_asset="TEST",
            quote_asset="USDT"
        )
        
        assert len(results) == 2
        assert all(result.success for result in results)
        assert all("order_id" in result.data for result in results)
        assert mock_binance_service.place_oto_order.call_count == 2
    
    @pytest.mark.asyncio
    async def test_connect_all_websockets(self, mock_binance_service):
        """测试连接所有用户WebSocket"""
        service = MultiUserBinanceService()
        service._user_services = {
            "user_001": mock_binance_service,
            "user_002": mock_binance_service
        }
        
        results = await service.connect_all_websockets()
        
        assert len(results) == 2
        assert all(result.success for result in results)
        assert all(result.data["connected"] for result in results)
        assert mock_binance_service.connect_websocket.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_user_service(self, mock_binance_service):
        """测试获取用户服务"""
        service = MultiUserBinanceService()
        service._user_services = {"user_001": mock_binance_service}
        
        result = service.get_user_service("user_001")
        assert result == mock_binance_service
        
        result = service.get_user_service("nonexistent")
        assert result is None
    
    def test_get_enabled_user_ids(self, mock_user_configs):
        """测试获取启用用户ID列表"""
        service = MultiUserBinanceService()
        service._enabled_users = [mock_user_configs[0], mock_user_configs[1]]
        
        user_ids = service.get_enabled_user_ids()
        
        assert user_ids == ["user_001", "user_002"]
    
    def test_get_user_count(self, mock_user_configs):
        """测试获取用户数量"""
        service = MultiUserBinanceService()
        service._enabled_users = [mock_user_configs[0], mock_user_configs[1]]
        
        count = service.get_user_count()
        
        assert count == 2
    
    @pytest.mark.asyncio
    async def test_disconnect_all(self, mock_binance_service):
        """测试断开所有连接"""
        service = MultiUserBinanceService()
        service._user_services = {
            "user_001": mock_binance_service,
            "user_002": mock_binance_service
        }
        service._enabled_users = [Mock(), Mock()]
        
        await service.disconnect_all()
        
        assert mock_binance_service.disconnect.call_count == 2
        assert len(service._user_services) == 0
        assert len(service._enabled_users) == 0
    
    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config_manager, mock_binance_service):
        """测试异步上下文管理器"""
        with patch('src.BinanceTools.service.multi_user_service.UserConfigManager', return_value=mock_config_manager), \
             patch('src.BinanceTools.service.multi_user_service.BinanceService', return_value=mock_binance_service):
            
            async with MultiUserBinanceService() as service:
                assert len(service._user_services) == 2
            
            mock_binance_service.disconnect.assert_called()
    
    @pytest.mark.asyncio
    async def test_service_initialization_failure(self, mock_config_manager):
        """测试服务初始化失败"""
        mock_service = AsyncMock(spec=BinanceService)
        mock_service.initialize = AsyncMock(return_value=False)
        
        with patch('src.BinanceTools.service.multi_user_service.UserConfigManager', return_value=mock_config_manager), \
             patch('src.BinanceTools.service.multi_user_service.BinanceService', return_value=mock_service):
            
            service = MultiUserBinanceService()
            result = await service.initialize()
            
            assert result is True  # 整体初始化成功，但某些用户服务可能失败
            assert len(service._user_services) == 0  # 没有成功的服务
    
    @pytest.mark.asyncio
    async def test_individual_service_failure(self, mock_binance_service):
        """测试单个服务失败"""
        # 创建一个会失败的服务
        failing_service = AsyncMock(spec=BinanceService)
        failing_service.get_wallet_balance = AsyncMock(side_effect=Exception("Service error"))
        
        service = MultiUserBinanceService()
        service._user_services = {
            "user_001": mock_binance_service,
            "user_002": failing_service
        }
        
        results = await service.get_all_wallet_balances()
        
        assert len(results) == 2
        assert results[0].success is True  # 第一个成功
        assert results[1].success is False  # 第二个失败
        assert "Service error" in results[1].error
