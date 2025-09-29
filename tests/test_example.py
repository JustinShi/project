"""
测试示例 - 验证测试框架是否正常工作
"""
import pytest
from src.BinanceTools.utils.helpers import format_price, safe_float


class TestExample:
    """测试示例类"""
    
    def test_basic_functionality(self):
        """测试基本功能"""
        assert True
        assert 1 + 1 == 2
        assert "hello" == "hello"
    
    def test_format_price(self):
        """测试价格格式化函数"""
        assert format_price(123.456, 2) == "123.46"
        assert format_price(123.456, 4) == "123.456"  # rstrip会移除尾随零
        assert format_price("123.456", 2) == "123.46"
    
    def test_safe_float(self):
        """测试安全浮点数转换"""
        assert safe_float("123.45") == 123.45
        assert safe_float("") == 0.0
        assert safe_float(None) == 0.0
        assert safe_float("invalid", 999.0) == 999.0
    
    @pytest.mark.asyncio
    async def test_async_function(self):
        """测试异步函数"""
        import asyncio
        
        async def async_add(a, b):
            await asyncio.sleep(0.01)  # 模拟异步操作
            return a + b
        
        result = await async_add(2, 3)
        assert result == 5
    
    def test_parametrized(self, pytestconfig):
        """参数化测试"""
        test_data = [
            (123.456, 2, "123.46"),
            (123.456, 4, "123.456"),  # rstrip会移除尾随零
            (0, 2, "0"),
        ]
        
        for price, precision, expected in test_data:
            result = format_price(price, precision)
            assert result == expected
    
    def test_fixture_usage(self, sample_user_config):
        """测试使用fixture"""
        assert sample_user_config.id == "test_user_001"
        assert sample_user_config.name == "测试用户1"
        assert sample_user_config.enabled is True
