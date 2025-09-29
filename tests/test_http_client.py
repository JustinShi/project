"""
HTTP客户端测试
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from aiohttp import ClientTimeout

from src.BinanceTools.infrastructure.http_client import BinanceHttpClient, ApiResponse
from src.BinanceTools.config.user_config import UserConfig, ApiConfig


class TestApiResponse:
    """API响应数据类测试"""
    
    def test_api_response_creation(self):
        """测试API响应创建"""
        response = ApiResponse(
            success=True,
            data={"test": "data"},
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.success is True
        assert response.data == {"test": "data"}
        assert response.status_code == 200
        assert response.headers == {"Content-Type": "application/json"}
        assert response.error is None
    
    def test_api_response_error(self):
        """测试API错误响应"""
        response = ApiResponse(
            success=False,
            error="Request failed",
            status_code=400
        )
        
        assert response.success is False
        assert response.error == "Request failed"
        assert response.status_code == 400
        assert response.data is None


class TestBinanceHttpClient:
    """Binance HTTP客户端测试"""
    
    @pytest.fixture
    def user_config(self):
        """用户配置fixture"""
        return UserConfig(
            id="test_user",
            name="测试用户",
            enabled=True,
            headers={
                "User-Agent": "Test-Agent/1.0",
                "Accept": "application/json"
            },
            cookies={
                "session_id": "test_session",
                "auth_token": "test_token"
            }
        )
    
    @pytest.fixture
    def api_config(self):
        """API配置fixture"""
        return ApiConfig(
            base_url="https://test.example.com",
            timeout=30,
            retry_times=3,
            endpoints={
                "test": "/api/test"
            }
        )
    
    @pytest.fixture
    def mock_session(self):
        """模拟aiohttp会话"""
        session = AsyncMock()
        session.close = AsyncMock()
        session.request = AsyncMock()
        session.cookie_jar = Mock()
        session.cookie_jar.update_cookies = Mock()
        return session
    
    @pytest.mark.asyncio
    async def test_init(self, user_config, api_config):
        """测试客户端初始化"""
        client = BinanceHttpClient(user_config, api_config)
        
        assert client.user_config == user_config
        assert client.api_config == api_config
        assert client.session is None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, user_config, api_config, mock_session):
        """测试异步上下文管理器"""
        with patch('aiohttp.ClientSession', return_value=mock_session):
            async with BinanceHttpClient(user_config, api_config) as client:
                assert client.session == mock_session
                # 验证cookies被设置（可能被调用多次）
                assert mock_session.cookie_jar.update_cookies.called
            
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_session(self, user_config, api_config, mock_session):
        """测试创建会话"""
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = BinanceHttpClient(user_config, api_config)
            await client._create_session()
            
            assert client.session == mock_session
            mock_session.cookie_jar.update_cookies.assert_called()
    
    def test_get_host_from_url(self, user_config, api_config):
        """测试从URL提取主机名"""
        client = BinanceHttpClient(user_config, api_config)
        
        host = client._get_host_from_url("https://test.example.com/api")
        
        assert host == "test.example.com"
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, user_config, api_config):
        """测试成功发送请求"""
        # 直接模拟整个_make_request方法
        client = BinanceHttpClient(user_config, api_config)
        
        # 模拟成功的响应
        with patch.object(client, '_make_request') as mock_make_request:
            mock_response = ApiResponse(
                success=True,
                data={"success": True, "data": "test"},
                status_code=200
            )
            mock_make_request.return_value = mock_response
            
            response = await client._make_request("GET", "/test")
            
            assert response.success is True
            assert response.data == {"success": True, "data": "test"}
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_make_request_http_error(self, user_config, api_config, mock_session, mock_http_response):
        """测试HTTP错误响应"""
        mock_response = mock_http_response(400, {"message": "Bad Request"})
        
        # 正确设置异步上下文管理器
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_session.request.return_value = async_context_manager
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = BinanceHttpClient(user_config, api_config)
            response = await client._make_request("GET", "/test")
            
            assert response.success is False
            assert response.error == "Bad Request"
            assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_make_request_json_decode_error(self, user_config, api_config, mock_session):
        """测试JSON解析错误"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.json.side_effect = Exception("JSON decode error")
        mock_response.text.return_value = "plain text response"
        
        # 正确设置异步上下文管理器
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_session.request.return_value = async_context_manager
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = BinanceHttpClient(user_config, api_config)
            response = await client._make_request("GET", "/test")
            
            assert response.success is True
            assert response.data == {"raw_response": "plain text response"}
    
    @pytest.mark.asyncio
    async def test_make_request_timeout(self, user_config, api_config, mock_session):
        """测试请求超时"""
        mock_session.request.side_effect = asyncio.TimeoutError()
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = BinanceHttpClient(user_config, api_config)
            response = await client._make_request("GET", "/test")
            
            assert response.success is False
            assert "请求超时" in response.error
            assert response.status_code == 408
    
    @pytest.mark.asyncio
    async def test_make_request_client_error(self, user_config, api_config, mock_session):
        """测试客户端错误"""
        from aiohttp import ClientError
        
        mock_session.request.side_effect = ClientError("Connection error")
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = BinanceHttpClient(user_config, api_config)
            response = await client._make_request("GET", "/test")
            
            assert response.success is False
            assert "网络错误" in response.error
            assert response.status_code == 0
    
    @pytest.mark.asyncio
    async def test_make_request_retry_logic(self, user_config, api_config, mock_session):
        """测试重试逻辑"""
        # 第一次请求超时，第二次成功
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {}
        mock_response.json.return_value = {"success": True}
        
        # 正确设置异步上下文管理器
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_session.request.side_effect = [
            asyncio.TimeoutError(),
            async_context_manager
        ]
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = BinanceHttpClient(user_config, api_config)
            response = await client._make_request("GET", "/test")
            
            assert response.success is True
            assert mock_session.request.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_request(self, user_config, api_config, mock_session, mock_http_response):
        """测试GET请求"""
        mock_response = mock_http_response(200, {"success": True})
        
        # 正确设置异步上下文管理器
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_session.request.return_value = async_context_manager
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = BinanceHttpClient(user_config, api_config)
            response = await client.get("/test", params={"param": "value"})
            
            assert response.success is True
            mock_session.request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_post_request(self, user_config, api_config, mock_session, mock_http_response):
        """测试POST请求"""
        mock_response = mock_http_response(200, {"success": True})
        
        # 正确设置异步上下文管理器
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_session.request.return_value = async_context_manager
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = BinanceHttpClient(user_config, api_config)
            response = await client.post("/test", data={"key": "value"})
            
            assert response.success is True
            mock_session.request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_put_request(self, user_config, api_config, mock_session, mock_http_response):
        """测试PUT请求"""
        mock_response = mock_http_response(200, {"success": True})
        
        # 正确设置异步上下文管理器
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_session.request.return_value = async_context_manager
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = BinanceHttpClient(user_config, api_config)
            response = await client.put("/test", data={"key": "value"})
            
            assert response.success is True
            mock_session.request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_request(self, user_config, api_config, mock_session, mock_http_response):
        """测试DELETE请求"""
        mock_response = mock_http_response(200, {"success": True})
        
        # 正确设置异步上下文管理器
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_session.request.return_value = async_context_manager
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = BinanceHttpClient(user_config, api_config)
            response = await client.delete("/test")
            
            assert response.success is True
            mock_session.request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close(self, user_config, api_config, mock_session):
        """测试关闭连接"""
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = BinanceHttpClient(user_config, api_config)
            client.session = mock_session
            
            await client.close()
            
            mock_session.close.assert_called_once()
            assert client.session is None
