"""
Binance API接口测试
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.BinanceTools.application.binance_api import (
    BinanceApi, TradeVolumeInfo, UserVolume, WalletAsset, WalletBalance,
    PaymentDetail, OTOOrderRequest, OTOOrderResponse
)
from src.BinanceTools.config.user_config import UserConfig, ApiConfig
from src.BinanceTools.infrastructure.http_client import ApiResponse


class TestDataClasses:
    """数据类测试"""
    
    def test_trade_volume_info(self):
        """测试交易量信息数据类"""
        info = TradeVolumeInfo(
            icon="/test/icon.png",
            token_name="TEST",
            volume=1000.0
        )
        
        assert info.icon == "/test/icon.png"
        assert info.token_name == "TEST"
        assert info.volume == 1000.0
    
    def test_user_volume(self):
        """测试用户交易量数据类"""
        trade_info = TradeVolumeInfo(
            icon="/test/icon.png",
            token_name="TEST",
            volume=1000.0
        )
        
        user_volume = UserVolume(
            total_volume=1000.0,
            trade_volume_info_list=[trade_info]
        )
        
        assert user_volume.total_volume == 1000.0
        assert len(user_volume.trade_volume_info_list) == 1
        assert user_volume.trade_volume_info_list[0].token_name == "TEST"
    
    def test_wallet_asset(self):
        """测试钱包资产数据类"""
        asset = WalletAsset(
            chain_id="56",
            contract_address="0x123456789",
            cex_asset=False,
            name="Test Token",
            symbol="TEST",
            token_id="TEST_001",
            free="100.0",
            freeze="0",
            locked="0",
            withdrawing="0",
            amount="100.0",
            valuation="100.50"
        )
        
        assert asset.chain_id == "56"
        assert asset.symbol == "TEST"
        assert asset.free == "100.0"
        assert asset.valuation == "100.50"
    
    def test_payment_detail(self):
        """测试支付详情数据类"""
        payment = PaymentDetail(
            amount="100.0",
            payment_wallet_type="CARD"
        )
        
        assert payment.amount == "100.0"
        assert payment.payment_wallet_type == "CARD"
    
    def test_oto_order_request(self):
        """测试反向订单请求数据类"""
        payment = PaymentDetail(
            amount="100.0",
            payment_wallet_type="CARD"
        )
        
        order_request = OTOOrderRequest(
            working_price="0.22983662",
            payment_details=[payment],
            pending_price="0.0001",
            working_side="BUY",
            working_quantity="435.09",
            base_asset="ALPHA_373",
            quote_asset="USDT"
        )
        
        assert order_request.working_price == "0.22983662"
        assert order_request.working_side == "BUY"
        assert len(order_request.payment_details) == 1
        assert order_request.payment_details[0].amount == "100.0"
    
    def test_oto_order_response(self):
        """测试反向订单响应数据类"""
        order_response = OTOOrderResponse(
            working_order_id=12345,
            pending_order_id=12346
        )
        
        assert order_response.working_order_id == 12345
        assert order_response.pending_order_id == 12346


class TestBinanceApi:
    """Binance API接口测试"""
    
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
            endpoints={
                "user_volume": "/api/v1/user/volume",
                "wallet_balance": "/api/v1/wallet/balance",
                "place_oto_order": "/api/v1/order/place",
                "get_listen_key": "/api/v1/stream/listen-key"
            }
        )
    
    @pytest.fixture
    def mock_http_client(self):
        """模拟HTTP客户端"""
        client = AsyncMock()
        return client
    
    @pytest.mark.asyncio
    async def test_init(self, user_config, api_config):
        """测试API初始化"""
        api = BinanceApi(user_config, api_config)
        
        assert api.user_config == user_config
        assert api.api_config == api_config
        assert api._client is None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, user_config, api_config, mock_http_client):
        """测试异步上下文管理器"""
        with patch('src.BinanceTools.application.binance_api.BinanceHttpClient', return_value=mock_http_client):
            async with BinanceApi(user_config, api_config) as api:
                assert api._client == mock_http_client
            
            mock_http_client.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_today_user_volume_success(self, user_config, api_config, mock_http_client):
        """测试成功获取今日交易量"""
        mock_response = ApiResponse(
            success=True,
            data={
                "code": "000000",
                "data": {
                    "totalVolume": 1000.0,
                    "tradeVolumeInfoList": [
                        {
                            "icon": "/test/icon.png",
                            "tokenName": "TEST",
                            "volume": 1000.0
                        }
                    ]
                }
            }
        )
        
        mock_http_client.get.return_value = mock_response
        
        api = BinanceApi(user_config, api_config)
        api._client = mock_http_client
        
        response = await api.get_today_user_volume()
        
        assert response.success is True
        assert "parsed_data" in response.data
        assert response.data["parsed_data"].total_volume == 1000.0
        assert len(response.data["parsed_data"].trade_volume_info_list) == 1
        mock_http_client.get.assert_called_once_with("/api/v1/user/volume")
    
    @pytest.mark.asyncio
    async def test_get_today_user_volume_failure(self, user_config, api_config, mock_http_client):
        """测试获取今日交易量失败"""
        mock_response = ApiResponse(
            success=False,
            error="API error",
            status_code=400
        )
        
        mock_http_client.get.return_value = mock_response
        
        api = BinanceApi(user_config, api_config)
        api._client = mock_http_client
        
        response = await api.get_today_user_volume()
        
        assert response.success is False
        assert response.error == "API error"
    
    @pytest.mark.asyncio
    async def test_get_today_user_volume_parse_error(self, user_config, api_config, mock_http_client):
        """测试获取今日交易量解析错误"""
        mock_response = ApiResponse(
            success=True,
            data={
                "code": "000000",
                "data": "invalid_data"  # 无效的数据格式
            }
        )
        
        mock_http_client.get.return_value = mock_response
        
        api = BinanceApi(user_config, api_config)
        api._client = mock_http_client
        
        response = await api.get_today_user_volume()
        
        assert response.success is False
        assert "数据解析失败" in response.error
    
    @pytest.mark.asyncio
    async def test_get_alpha_wallet_balance_success(self, user_config, api_config, mock_http_client):
        """测试成功获取Alpha钱包余额"""
        mock_response = ApiResponse(
            success=True,
            data={
                "code": "000000",
                "data": {
                    "totalValuation": "100.50",
                    "list": [
                        {
                            "chainId": "56",
                            "contractAddress": "0x123456789",
                            "cexAsset": False,
                            "name": "Test Token",
                            "symbol": "TEST",
                            "tokenId": "TEST_001",
                            "free": "100.0",
                            "freeze": "0",
                            "locked": "0",
                            "withdrawing": "0",
                            "amount": "100.0",
                            "valuation": "100.50"
                        }
                    ]
                }
            }
        )
        
        mock_http_client.get.return_value = mock_response
        
        api = BinanceApi(user_config, api_config)
        api._client = mock_http_client
        
        response = await api.get_alpha_wallet_balance()
        
        assert response.success is True
        assert "parsed_data" in response.data
        assert response.data["parsed_data"].total_valuation == "100.50"
        assert len(response.data["parsed_data"].list) == 1
        assert response.data["parsed_data"].list[0].symbol == "TEST"
        
        # 验证调用参数
        mock_http_client.get.assert_called_once_with(
            "/api/v1/wallet/balance",
            params={"includeCex": 1}
        )
    
    @pytest.mark.asyncio
    async def test_get_alpha_wallet_balance_without_cex(self, user_config, api_config, mock_http_client):
        """测试获取Alpha钱包余额（不包含CEX）"""
        mock_response = ApiResponse(success=True, data={"code": "000000", "data": {}})
        mock_http_client.get.return_value = mock_response
        
        api = BinanceApi(user_config, api_config)
        api._client = mock_http_client
        
        await api.get_alpha_wallet_balance(include_cex=False)
        
        mock_http_client.get.assert_called_once_with(
            "/api/v1/wallet/balance",
            params={"includeCex": 0}
        )
    
    @pytest.mark.asyncio
    async def test_place_oto_order_success(self, user_config, api_config, mock_http_client):
        """测试成功创建反向订单"""
        mock_response = ApiResponse(
            success=True,
            data={
                "code": "000000",
                "data": {
                    "workingOrderId": 12345,
                    "pendingOrderId": 12346
                }
            }
        )
        
        mock_http_client.post.return_value = mock_response
        
        payment_detail = PaymentDetail(
            amount="100.0",
            payment_wallet_type="CARD"
        )
        
        order_request = OTOOrderRequest(
            working_price="0.22983662",
            payment_details=[payment_detail],
            pending_price="0.0001",
            working_side="BUY",
            working_quantity="435.09",
            base_asset="ALPHA_373",
            quote_asset="USDT"
        )
        
        api = BinanceApi(user_config, api_config)
        api._client = mock_http_client
        
        response = await api.place_oto_order(order_request)
        
        assert response.success is True
        assert "parsed_data" in response.data
        assert response.data["parsed_data"].working_order_id == 12345
        assert response.data["parsed_data"].pending_order_id == 12346
        
        # 验证请求数据
        call_args = mock_http_client.post.call_args
        assert call_args[0][0] == "/api/v1/order/place"
        data = call_args[1]["data"]
        assert data["workingPrice"] == "0.22983662"
        assert data["workingSide"] == "BUY"
        assert data["baseAsset"] == "ALPHA_373"
        assert len(data["paymentDetails"]) == 1
    
    @pytest.mark.asyncio
    async def test_get_listen_key_success(self, user_config, api_config, mock_http_client):
        """测试成功获取ListenKey"""
        mock_response = ApiResponse(
            success=True,
            data={
                "listenKey": "test_listen_key_123456789"
            }
        )
        
        mock_http_client.post.return_value = mock_response
        
        api = BinanceApi(user_config, api_config)
        api._client = mock_http_client
        
        response = await api.get_listen_key()
        
        assert response.success is True
        assert "parsed_data" in response.data
        assert response.data["parsed_data"]["listen_key"] == "test_listen_key_123456789"
        
        mock_http_client.post.assert_called_once_with("/api/v1/stream/listen-key")
    
    @pytest.mark.asyncio
    async def test_renew_listen_key(self, user_config, api_config, mock_http_client):
        """测试续期ListenKey"""
        mock_response = ApiResponse(success=True, data={})
        mock_http_client.put.return_value = mock_response
        
        api = BinanceApi(user_config, api_config)
        api._client = mock_http_client
        
        response = await api.renew_listen_key("test_listen_key")
        
        assert response.success is True
        mock_http_client.put.assert_called_once_with(
            "/bapi/defi/v1/private/alpha-trade/stream/get-listen-key",
            data={"listenKey": "test_listen_key"}
        )
    
    @pytest.mark.asyncio
    async def test_delete_listen_key(self, user_config, api_config, mock_http_client):
        """测试删除ListenKey"""
        mock_response = ApiResponse(success=True, data={})
        mock_http_client.delete.return_value = mock_response
        
        api = BinanceApi(user_config, api_config)
        api._client = mock_http_client
        
        response = await api.delete_listen_key("test_listen_key")
        
        assert response.success is True
        mock_http_client.delete.assert_called_once_with("/bapi/defi/v1/private/alpha-trade/stream/get-listen-key")
    
    @pytest.mark.asyncio
    async def test_client_not_initialized(self, user_config, api_config, mock_http_client):
        """测试客户端未初始化的情况"""
        with patch('src.BinanceTools.application.binance_api.BinanceHttpClient', return_value=mock_http_client):
            api = BinanceApi(user_config, api_config)
            
            response = await api.get_today_user_volume()
            
            # 应该自动创建客户端
            assert api._client is not None
