"""
简化的HTTP客户端测试
使用更简单的方法测试HTTP客户端功能
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.BinanceTools.infrastructure.http_client import BinanceHttpClient, ApiResponse
from src.BinanceTools.config.user_config import UserConfig, ApiConfig


class TestBinanceHttpClientSimple:
    """简化的Binance HTTP客户端测试"""
    
    @pytest.fixture
    def user_config(self):
        """用户配置fixture"""
        return UserConfig(
            id="test_user",
            name="测试用户",
            enabled=True,
            headers={"User-Agent": "Test-Agent"},
            cookies={"session_id": "test_session"}
        )
    
    @pytest.fixture
    def api_config(self):
        """API配置fixture"""
        return ApiConfig(
            base_url="https://test.example.com",
            timeout=30,
            retry_times=3,
            endpoints={"test": "/api/test"}
        )
    
    def test_init(self, user_config, api_config):
        """测试客户端初始化"""
        client = BinanceHttpClient(user_config, api_config)
        
        assert client.user_config == user_config
        assert client.api_config == api_config
        assert client.session is None
    
    def test_get_host_from_url(self, user_config, api_config):
        """测试从URL提取主机名"""
        client = BinanceHttpClient(user_config, api_config)
        
        host = client._get_host_from_url("https://test.example.com/api")
        
        assert host == "test.example.com"
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, user_config, api_config):
        """测试成功发送请求"""
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
    async def test_make_request_error(self, user_config, api_config):
        """测试请求错误"""
        client = BinanceHttpClient(user_config, api_config)
        
        # 模拟错误响应
        with patch.object(client, '_make_request') as mock_make_request:
            mock_response = ApiResponse(
                success=False,
                error="Bad Request",
                status_code=400
            )
            mock_make_request.return_value = mock_response
            
            response = await client._make_request("GET", "/test")
            
            assert response.success is False
            assert response.error == "Bad Request"
            assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_request(self, user_config, api_config):
        """测试GET请求"""
        client = BinanceHttpClient(user_config, api_config)
        
        with patch.object(client, '_make_request') as mock_make_request:
            mock_response = ApiResponse(success=True, data={"result": "success"})
            mock_make_request.return_value = mock_response
            
            response = await client.get("/test", params={"param": "value"})
            
            assert response.success is True
            mock_make_request.assert_called_once_with("GET", "/test", params={"param": "value"}, headers=None)
    
    @pytest.mark.asyncio
    async def test_post_request(self, user_config, api_config):
        """测试POST请求"""
        client = BinanceHttpClient(user_config, api_config)
        
        with patch.object(client, '_make_request') as mock_make_request:
            mock_response = ApiResponse(success=True, data={"result": "success"})
            mock_make_request.return_value = mock_response
            
            response = await client.post("/test", data={"key": "value"})
            
            assert response.success is True
            mock_make_request.assert_called_once_with("POST", "/test", data={"key": "value"}, headers=None)
    
    @pytest.mark.asyncio
    async def test_put_request(self, user_config, api_config):
        """测试PUT请求"""
        client = BinanceHttpClient(user_config, api_config)
        
        with patch.object(client, '_make_request') as mock_make_request:
            mock_response = ApiResponse(success=True, data={"result": "success"})
            mock_make_request.return_value = mock_response
            
            response = await client.put("/test", data={"key": "value"})
            
            assert response.success is True
            mock_make_request.assert_called_once_with("PUT", "/test", data={"key": "value"}, headers=None)
    
    @pytest.mark.asyncio
    async def test_delete_request(self, user_config, api_config):
        """测试DELETE请求"""
        client = BinanceHttpClient(user_config, api_config)
        
        with patch.object(client, '_make_request') as mock_make_request:
            mock_response = ApiResponse(success=True, data={"result": "success"})
            mock_make_request.return_value = mock_response
            
            response = await client.delete("/test")
            
            assert response.success is True
            mock_make_request.assert_called_once_with("DELETE", "/test", headers=None)
    
    @pytest.mark.asyncio
    async def test_close(self, user_config, api_config):
        """测试关闭连接"""
        client = BinanceHttpClient(user_config, api_config)
        mock_session = AsyncMock()
        client.session = mock_session
        
        await client.close()
        
        mock_session.close.assert_called_once()
        assert client.session is None
