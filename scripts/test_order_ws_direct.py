#!/usr/bin/env python3
"""直接测试订单 WebSocket 推送（使用环境变量中的凭证）"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any

# 添加项目路径到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from binance.infrastructure.binance_client.listen_key_manager import ListenKeyManager
from binance.infrastructure.binance_client.order_websocket import OrderWebSocketConnector


async def test_listen_key_and_websocket():
    """测试 ListenKey 获取和 WebSocket 连接"""
    print("\n" + "=" * 70)
    print("🧪 订单 WebSocket 推送测试")
    print("=" * 70)
    
    # 从环境变量获取凭证
    print("\n📋 步骤 1: 读取环境变量中的凭证")
    
    headers_str = os.getenv("TEST_HEADERS")
    cookies_str = os.getenv("TEST_COOKIES")
    
    if not headers_str or not cookies_str:
        print("❌ 环境变量中未配置 TEST_HEADERS 或 TEST_COOKIES")
        print("\n💡 请在 .env 文件中配置:")
        print('   TEST_HEADERS=\'{"xxx":"yyy"}\'')
        print('   TEST_COOKIES="cookie1=value1; cookie2=value2"')
        return
    
    try:
        headers = json.loads(headers_str)
        print(f"✅ Headers 解析成功 ({len(headers)} 个字段)")
    except json.JSONDecodeError as e:
        print(f"❌ Headers 解析失败: {e}")
        return
    
    print(f"✅ Cookies 读取成功 (长度: {len(cookies_str)})")
    
    # 获取 ListenKey
    print("\n📋 步骤 2: 获取 ListenKey")
    try:
        listen_key_manager = ListenKeyManager(headers, cookies_str)
        success, message, listen_key = await listen_key_manager.get_listen_key()
        
        if not success or not listen_key:
            print(f"❌ ListenKey 获取失败: {message}")
            await listen_key_manager.close()
            return
        
        print(f"✅ ListenKey 获取成功")
        print(f"   ListenKey: {listen_key[:30]}...")
        print(f"   完整长度: {len(listen_key)} 字符")
        
    except Exception as e:
        print(f"❌ 获取 ListenKey 异常: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 创建并测试 WebSocket 连接
    print("\n📋 步骤 3: 建立 WebSocket 连接")
    
    order_updates_count = [0]  # 使用列表以便在闭包中修改
    
    async def handle_order_update(order_data: Dict[str, Any]):
        """处理订单更新"""
        order_updates_count[0] += 1
        print("\n" + "=" * 70)
        print(f"📦 订单更新 #{order_updates_count[0]}")
        print("-" * 70)
        print(json.dumps(order_data, indent=2, ensure_ascii=False))
        print("=" * 70)
    
    async def handle_connection_event(event_type: str, data: Dict[str, Any]):
        """处理连接事件"""
        print(f"\n🔌 连接事件: {event_type}")
        if data:
            print(f"   {json.dumps(data, ensure_ascii=False)}")
    
    try:
        # 创建订单 WebSocket 连接器
        order_connector = OrderWebSocketConnector(
            user_id=1,
            listen_key=listen_key,
            on_order_update=handle_order_update,
            on_connection_event=handle_connection_event,
            reconnect_interval=3,
            max_reconnect_attempts=10
        )
        
        print("✅ WebSocket 连接器创建成功")
        
        # 启动连接（在后台任务中运行）
        print("⏳ 正在连接 WebSocket...")
        connection_task = asyncio.create_task(order_connector.start())
        
        # 等待连接建立
        await asyncio.sleep(3)
        
        if order_connector.is_connected():
            print("✅ WebSocket 连接已建立")
        else:
            print("⚠️  WebSocket 连接未建立（可能正在连接中）")
        
        # 打印连接信息
        conn_info = order_connector.get_connection_info()
        print("\n📊 连接信息:")
        print(f"   用户ID: {conn_info['user_id']}")
        print(f"   ListenKey: {conn_info['listen_key'][:20]}...")
        print(f"   已连接: {conn_info['connected']}")
        print(f"   重连尝试: {conn_info['reconnect_attempts']}/{conn_info['max_reconnect_attempts']}")
        
        print("\n💡 提示:")
        print("   - WebSocket 已连接，等待订单推送...")
        print("   - 请在币安 Alpha 平台下单，或使用 quick_start_strategy.py 脚本")
        print("   - 按 Ctrl+C 停止测试")
        print()
        
        # 等待接收订单更新（60秒）
        test_duration = 60
        print(f"⏳ 将等待 {test_duration} 秒接收订单更新...\n")
        
        for i in range(test_duration):
            await asyncio.sleep(1)
            
            # 每10秒打印一次状态
            if (i + 1) % 10 == 0:
                if order_connector.is_connected():
                    print(f"⏱️  已运行 {i + 1}/{test_duration} 秒，接收到 {order_updates_count[0]} 个订单更新")
                else:
                    print(f"⚠️  WebSocket 连接已断开 (运行了 {i + 1} 秒)")
                    break
        
        print("\n📊 测试结果:")
        print(f"   总运行时间: {min(i + 1, test_duration)} 秒")
        print(f"   接收订单更新: {order_updates_count[0]} 次")
        print(f"   连接状态: {'正常' if order_connector.is_connected() else '已断开'}")
        
        # 停止 WebSocket
        print("\n⏹️  停止 WebSocket 连接...")
        await order_connector.stop()
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭 ListenKey 管理器
        await listen_key_manager.close()
        print("\n✅ 测试完成")


if __name__ == "__main__":
    try:
        asyncio.run(test_listen_key_and_websocket())
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()

