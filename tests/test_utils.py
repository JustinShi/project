"""
工具函数测试
"""
import pytest
import time
from datetime import datetime, timezone

from src.BinanceTools.utils.helpers import (
    format_timestamp, format_price, format_volume, format_percentage,
    safe_float, safe_int, safe_str, deep_merge_dict,
    extract_symbol_from_stream, parse_websocket_message,
    create_order_message, validate_order_params,
    get_current_timestamp_ms, format_order_status, format_side
)


class TestFormatFunctions:
    """格式化函数测试"""
    
    def test_format_timestamp_milliseconds(self):
        """测试格式化毫秒时间戳"""
        # 测试毫秒时间戳
        timestamp = 1640995200000  # 2022-01-01 00:00:00 UTC
        result = format_timestamp(timestamp)
        
        assert "2022-01-01 00:00:00 UTC" in result
    
    def test_format_timestamp_seconds(self):
        """测试格式化秒时间戳"""
        # 测试秒时间戳
        timestamp = 1640995200  # 2022-01-01 00:00:00 UTC
        result = format_timestamp(timestamp)
        
        assert "2022-01-01 00:00:00 UTC" in result
    
    def test_format_timestamp_string(self):
        """测试格式化字符串时间戳"""
        timestamp = "1640995200000"
        result = format_timestamp(timestamp)
        
        assert "2022-01-01 00:00:00 UTC" in result
    
    def test_format_timestamp_invalid(self):
        """测试格式化无效时间戳"""
        result = format_timestamp("invalid")
        assert result == "invalid"
    
    def test_format_price(self):
        """测试格式化价格"""
        assert format_price(123.456789, 4) == "123.4568"
        assert format_price(123.456789, 2) == "123.46"
        assert format_price("123.456789", 2) == "123.46"
        assert format_price(123.0, 2) == "123"
        assert format_price(123.50, 2) == "123.5"
    
    def test_format_price_invalid(self):
        """测试格式化无效价格"""
        result = format_price("invalid", 2)
        assert result == "invalid"
    
    def test_format_volume(self):
        """测试格式化交易量"""
        assert format_volume(1500000000) == "1.50B"
        assert format_volume(1500000) == "1.50M"
        assert format_volume(1500) == "1.50K"
        assert format_volume(500) == "500.00"
        assert format_volume("1500000") == "1.50M"
    
    def test_format_volume_invalid(self):
        """测试格式化无效交易量"""
        result = format_volume("invalid")
        assert result == "invalid"
    
    def test_format_percentage(self):
        """测试格式化百分比"""
        assert format_percentage(12.345, 2) == "12.35%"
        assert format_percentage("12.345", 1) == "12.3%"
        assert format_percentage(0, 2) == "0.00%"
    
    def test_format_percentage_invalid(self):
        """测试格式化无效百分比"""
        result = format_percentage("invalid", 2)
        assert result == "invalid"


class TestSafeConversionFunctions:
    """安全转换函数测试"""
    
    def test_safe_float(self):
        """测试安全转换为浮点数"""
        assert safe_float(123.45) == 123.45
        assert safe_float("123.45") == 123.45
        assert safe_float("") == 0.0
        assert safe_float(None) == 0.0
        assert safe_float("NULL") == 0.0
        assert safe_float("N/A") == 0.0
        assert safe_float("invalid", 999.0) == 999.0
        assert safe_float("invalid") == 0.0
    
    def test_safe_int(self):
        """测试安全转换为整数"""
        assert safe_int(123.45) == 123
        assert safe_int("123") == 123
        assert safe_int("123.0") == 123
        assert safe_int("") == 0
        assert safe_int(None) == 0
        assert safe_int("NULL") == 0
        assert safe_int("invalid", 999) == 999
        assert safe_int("invalid") == 0
    
    def test_safe_str(self):
        """测试安全转换为字符串"""
        assert safe_str(123) == "123"
        assert safe_str(123.45) == "123.45"
        assert safe_str(None) == ""
        assert safe_str(None, "default") == "default"
        assert safe_str({"key": "value"}) == "{'key': 'value'}"


class TestUtilityFunctions:
    """工具函数测试"""
    
    def test_deep_merge_dict(self):
        """测试深度合并字典"""
        dict1 = {
            "a": 1,
            "b": {
                "c": 2,
                "d": 3
            }
        }
        dict2 = {
            "b": {
                "c": 4,
                "e": 5
            },
            "f": 6
        }
        
        result = deep_merge_dict(dict1, dict2)
        
        assert result["a"] == 1
        assert result["b"]["c"] == 4  # 被覆盖
        assert result["b"]["d"] == 3  # 保持不变
        assert result["b"]["e"] == 5  # 新增
        assert result["f"] == 6  # 新增
    
    def test_extract_symbol_from_stream(self):
        """测试从流名称提取交易对符号"""
        assert extract_symbol_from_stream("btcusdt@aggTrade") == "BTCUSDT"
        assert extract_symbol_from_stream("ethusdt@ticker") == "ETHUSDT"
        assert extract_symbol_from_stream("invalid_stream") is None
        assert extract_symbol_from_stream("") is None
    
    def test_parse_websocket_message(self):
        """测试解析WebSocket消息"""
        valid_message = '{"stream": "btcusdt@aggTrade", "data": {"s": "BTCUSDT"}}'
        result = parse_websocket_message(valid_message)
        
        assert result is not None
        assert result["stream"] == "btcusdt@aggTrade"
        assert result["data"]["s"] == "BTCUSDT"
        
        # 测试无效JSON
        invalid_message = "invalid json"
        result = parse_websocket_message(invalid_message)
        assert result is None
    
    def test_get_current_timestamp_ms(self):
        """测试获取当前时间戳（毫秒）"""
        timestamp = get_current_timestamp_ms()
        
        # 验证时间戳是毫秒级别的
        assert timestamp > 1600000000000  # 2020年之后
        assert isinstance(timestamp, int)
        
        # 验证时间戳在合理范围内
        current_time = int(time.time() * 1000)
        assert abs(timestamp - current_time) < 1000  # 误差小于1秒
    
    def test_format_order_status(self):
        """测试格式化订单状态"""
        assert format_order_status("NEW") == "新建"
        assert format_order_status("FILLED") == "完全成交"
        assert format_order_status("CANCELED") == "已取消"
        assert format_order_status("UNKNOWN_STATUS") == "UNKNOWN_STATUS"
    
    def test_format_side(self):
        """测试格式化交易方向"""
        assert format_side("BUY") == "买入"
        assert format_side("SELL") == "卖出"
        assert format_side("UNKNOWN_SIDE") == "UNKNOWN_SIDE"


class TestOrderFunctions:
    """订单相关函数测试"""
    
    def test_create_order_message(self):
        """测试创建订单消息"""
        message = create_order_message(
            working_price="0.22983662",
            working_quantity="435.09",
            pending_price="0.0001",
            base_asset="ALPHA_373",
            quote_asset="USDT",
            working_side="BUY",
            payment_amount="100.0",
            payment_wallet_type="CARD"
        )
        
        assert message["workingPrice"] == "0.22983662"
        assert message["workingQuantity"] == "435.09"
        assert message["pendingPrice"] == "0.0001"
        assert message["baseAsset"] == "ALPHA_373"
        assert message["quoteAsset"] == "USDT"
        assert message["workingSide"] == "BUY"
        assert len(message["paymentDetails"]) == 1
        assert message["paymentDetails"][0]["amount"] == "100.0"
        assert message["paymentDetails"][0]["paymentWalletType"] == "CARD"
    
    def test_create_order_message_no_payment(self):
        """测试创建订单消息（无支付）"""
        message = create_order_message(
            working_price="0.22983662",
            working_quantity="435.09",
            pending_price="0.0001",
            base_asset="ALPHA_373",
            quote_asset="USDT",
            payment_amount="0"
        )
        
        assert message["workingPrice"] == "0.22983662"
        assert len(message["paymentDetails"]) == 0
    
    def test_validate_order_params_valid(self):
        """测试验证订单参数（有效）"""
        is_valid, error = validate_order_params(
            working_price="0.22983662",
            working_quantity="435.09",
            pending_price="0.0001",
            base_asset="ALPHA_373",
            quote_asset="USDT"
        )
        
        assert is_valid is True
        assert error is None
    
    def test_validate_order_params_invalid_price(self):
        """测试验证订单参数（无效价格）"""
        # 测试负价格
        is_valid, error = validate_order_params(
            working_price="-0.1",
            working_quantity="435.09",
            pending_price="0.0001",
            base_asset="ALPHA_373",
            quote_asset="USDT"
        )
        
        assert is_valid is False
        assert "工作价格必须大于0" in error
        
        # 测试零价格
        is_valid, error = validate_order_params(
            working_price="0",
            working_quantity="435.09",
            pending_price="0.0001",
            base_asset="ALPHA_373",
            quote_asset="USDT"
        )
        
        assert is_valid is False
        assert "工作价格必须大于0" in error
    
    def test_validate_order_params_invalid_quantity(self):
        """测试验证订单参数（无效数量）"""
        is_valid, error = validate_order_params(
            working_price="0.22983662",
            working_quantity="0",
            pending_price="0.0001",
            base_asset="ALPHA_373",
            quote_asset="USDT"
        )
        
        assert is_valid is False
        assert "工作数量必须大于0" in error
    
    def test_validate_order_params_invalid_pending_price(self):
        """测试验证订单参数（无效待定价格）"""
        is_valid, error = validate_order_params(
            working_price="0.22983662",
            working_quantity="435.09",
            pending_price="-0.1",
            base_asset="ALPHA_373",
            quote_asset="USDT"
        )
        
        assert is_valid is False
        assert "待定价格必须大于0" in error
    
    def test_validate_order_params_empty_assets(self):
        """测试验证订单参数（空资产）"""
        is_valid, error = validate_order_params(
            working_price="0.22983662",
            working_quantity="435.09",
            pending_price="0.0001",
            base_asset="",
            quote_asset="USDT"
        )
        
        assert is_valid is False
        assert "基础资产和报价资产不能为空" in error
    
    def test_validate_order_params_invalid_type(self):
        """测试验证订单参数（无效类型）"""
        is_valid, error = validate_order_params(
            working_price="invalid",
            working_quantity="435.09",
            pending_price="0.0001",
            base_asset="ALPHA_373",
            quote_asset="USDT"
        )
        
        assert is_valid is False
        # safe_float会将"invalid"转换为0.0，所以错误信息是"工作价格必须大于0"
        assert "工作价格必须大于0" in error
