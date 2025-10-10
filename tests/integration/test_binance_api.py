"""币安私有API集成测试

按照规范要求的测试顺序执行：
1. 第一阶段：代币信息测试（符号映射和精度）
2. 第二阶段：代币价格测试
3. 第三阶段：订单查询测试
4. 第四阶段：完整交易流程测试（后续实现）

注意：这些测试需要真实的用户认证信息（headers和cookies）
"""

import asyncio
import pytest
import pytest_asyncio
import json
from decimal import Decimal
from typing import Dict, Any

from binance.infrastructure.binance_client.http_client import BinanceClient
from binance.infrastructure.database.session import get_db
from binance.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl


class TestBinanceAPI:
    """币安私有API集成测试类"""

    @pytest_asyncio.fixture
    async def user_credentials(self):
        """从数据库获取测试用户的认证信息"""
        async for session in get_db():
            user_repo = UserRepositoryImpl(session)
            # 获取第一个有效用户
            user = await user_repo.get_by_id(1)
            
            if not user or not user.has_credentials():
                pytest.skip("测试用户不存在或没有认证信息")
            
            # 获取认证信息（明文）
            headers_str = user.headers
            cookies_str = user.cookies
            
            # 解析headers（JSON格式）
            headers_dict = json.loads(headers_str)
            
            # 解析cookies（可能是JSON或字符串格式）
            try:
                cookies_obj = json.loads(cookies_str)
                # 如果是JSON对象，转换为字符串格式
                cookies_str = "; ".join([f"{k}={v}" for k, v in cookies_obj.items()])
            except json.JSONDecodeError:
                # 已经是字符串格式，直接使用
                pass
            
            return {
                "headers": headers_dict,
                "cookies": cookies_str,
                "user": user,
            }

    @pytest_asyncio.fixture
    async def binance_client(self, user_credentials):
        """创建币安API客户端"""
        client = BinanceClient(
            headers=user_credentials["headers"],
            cookies=user_credentials["cookies"],
        )
        yield client
        await client.close()

    # ========================================================================
    # 第一阶段：代币信息测试（符号映射和精度）
    # ========================================================================

    @pytest.mark.asyncio
    async def test_1_get_token_info(self, binance_client):
        """测试获取代币信息（符号映射）
        
        验证点：
        - API调用成功
        - 返回代币列表
        - 每个代币包含必要的字段（symbol, price等）
        """
        print("\n" + "="*80)
        print("【第一阶段-1】测试代币信息查询（符号映射）")
        print("="*80)
        
        # 调用API
        token_list = await binance_client.get_token_info()
        
        # 验证返回数据
        assert isinstance(token_list, list), "应该返回列表"
        assert len(token_list) > 0, "代币列表不应为空"
        
        print(f"\n[OK] 成功获取 {len(token_list)} 个代币信息")
        
        # 检查第一个代币的字段
        first_token = token_list[0]
        print(f"\n示例代币信息:")
        print(f"  symbol: {first_token.get('symbol')}")
        print(f"  price: {first_token.get('price')}")
        print(f"  volume: {first_token.get('volume')}")
        
        # 验证必要字段
        assert "symbol" in first_token, "代币应包含symbol字段"
        assert "price" in first_token, "代币应包含price字段"
        
        # 保存一些代币符号供后续测试使用
        self.test_symbols = [t.get("symbol") for t in token_list[:3] if t.get("symbol")]
        print(f"\n保存测试符号: {self.test_symbols}")

    @pytest.mark.asyncio
    async def test_2_get_exchange_info(self, binance_client):
        """测试获取交易精度信息
        
        验证点：
        - API调用成功
        - 返回精度配置信息
        - 包含交易对精度（tradeDecimal, tokenDecimal）
        """
        print("\n" + "="*80)
        print("【第一阶段-2】测试交易精度信息查询")
        print("="*80)
        
        # 调用API
        exchange_info = await binance_client.get_exchange_info()
        
        # 验证返回数据
        assert isinstance(exchange_info, dict), "应该返回字典"
        assert "symbols" in exchange_info or len(exchange_info) > 0, "应包含交易对信息"
        
        print(f"\n[OK] 成功获取交易精度信息")
        print(f"数据结构: {list(exchange_info.keys())[:5]}")
        
        # 如果有symbols字段，检查第一个交易对
        if "symbols" in exchange_info and len(exchange_info["symbols"]) > 0:
            first_symbol = exchange_info["symbols"][0]
            print(f"\n示例交易对精度:")
            print(f"  symbol: {first_symbol.get('symbol')}")
            print(f"  tradeDecimal: {first_symbol.get('tradeDecimal')}")
            print(f"  tokenDecimal: {first_symbol.get('tokenDecimal')}")

    # ========================================================================
    # 第二阶段：用户数据查询测试
    # ========================================================================

    @pytest.mark.asyncio
    async def test_3_get_wallet_balance(self, binance_client):
        """测试获取钱包余额
        
        验证点：
        - API调用成功
        - 返回余额数据
        - 包含总估值和代币列表
        """
        print("\n" + "="*80)
        print("【第二阶段-1】测试钱包余额查询")
        print("="*80)
        
        # 调用API
        balance_data = await binance_client.get_wallet_balance()
        
        # 验证返回数据
        assert isinstance(balance_data, dict), "应该返回字典"
        assert "totalValuation" in balance_data, "应包含totalValuation字段"
        assert "list" in balance_data, "应包含list字段"
        
        total_value = balance_data.get("totalValuation", "0")
        balance_list = balance_data.get("list", [])
        
        print(f"\n[OK] 总估值: {total_value} USDT")
        print(f"[OK] 代币数量: {len(balance_list)}")
        
        # 显示前3个代币余额
        if balance_list:
            print(f"\n代币余额详情（前3个）:")
            for token in balance_list[:3]:
                print(f"  {token.get('symbol'):10} | "
                      f"可用: {token.get('free'):15} | "
                      f"估值: {token.get('valuation'):10} USDT")

    @pytest.mark.asyncio
    async def test_4_get_user_volume(self, binance_client):
        """测试获取用户今日交易量
        
        验证点：
        - API调用成功
        - 返回交易量数据
        - 包含总交易量和分代币交易量
        """
        print("\n" + "="*80)
        print("【第二阶段-2】测试用户交易量查询")
        print("="*80)
        
        # 调用API
        volume_data = await binance_client.get_user_volume()
        
        # 验证返回数据
        assert isinstance(volume_data, dict), "应该返回字典"
        
        total_volume = volume_data.get("totalVolume", 0)
        volume_list = volume_data.get("tradeVolumeInfoList", [])
        
        print(f"\n[OK] 今日总交易量: {total_volume} USDT")
        print(f"[OK] 交易代币数量: {len(volume_list)}")
        
        # 显示各代币交易量
        if volume_list:
            print(f"\n各代币交易量:")
            for token_vol in volume_list:
                print(f"  {token_vol.get('tokenName'):10} : {token_vol.get('volume'):15} USDT")

    # ========================================================================
    # 第三阶段：订单查询测试
    # ========================================================================

    @pytest.mark.asyncio
    async def test_5_get_open_orders(self, binance_client):
        """测试获取挂起订单
        
        验证点：
        - API调用成功
        - 返回订单列表（可能为空）
        """
        print("\n" + "="*80)
        print("【第三阶段】测试挂起订单查询")
        print("="*80)
        
        # 调用API
        open_orders = await binance_client.get_open_orders()
        
        # 验证返回数据
        assert isinstance(open_orders, list), "应该返回列表"
        
        print(f"\n[OK] 当前挂起订单数量: {len(open_orders)}")
        
        # 如果有挂起订单，显示详情
        if open_orders:
            print(f"\n挂起订单详情:")
            for order in open_orders[:3]:  # 显示前3个
                print(f"  订单ID: {order.get('orderId')}")
                print(f"    代币: {order.get('symbol')}")
                print(f"    方向: {order.get('side')}")
                print(f"    价格: {order.get('price')}")
                print(f"    数量: {order.get('quantity')}")
                print(f"    状态: {order.get('status')}")
                print()
        else:
            print("  (当前没有挂起订单)")

    # ========================================================================
    # 综合测试：验证数据一致性
    # ========================================================================

    @pytest.mark.asyncio
    async def test_6_data_consistency(self, binance_client):
        """综合测试：验证不同API返回数据的一致性
        
        验证点：
        - 代币信息中的符号与余额中的符号可以对应
        - 精度信息可以用于价格和数量格式化
        """
        print("\n" + "="*80)
        print("【综合测试】验证API数据一致性")
        print("="*80)
        
        # 获取各类数据
        token_info = await binance_client.get_token_info()
        exchange_info = await binance_client.get_exchange_info()
        balance_data = await binance_client.get_wallet_balance()
        
        # 提取符号集合
        token_symbols = {t.get("symbol") for t in token_info if t.get("symbol")}
        balance_symbols = {b.get("symbol") for b in balance_data.get("list", []) if b.get("symbol")}
        
        print(f"\n[OK] 代币信息中的符号数量: {len(token_symbols)}")
        print(f"[OK] 余额中的符号数量: {len(balance_symbols)}")
        
        # 检查余额中的代币是否都在代币信息中
        if balance_symbols:
            common_symbols = token_symbols.intersection(balance_symbols)
            print(f"[OK] 共同符号数量: {len(common_symbols)}")
            
            if common_symbols:
                print(f"\n示例共同符号: {list(common_symbols)[:5]}")


if __name__ == "__main__":
    """直接运行此脚本进行测试"""
    pytest.main([
        __file__,
        "-v",  # 详细输出
        "-s",  # 显示print输出
        "--tb=short",  # 简短的traceback
    ])

