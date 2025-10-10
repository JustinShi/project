#!/usr/bin/env python3
"""快速测试 ListenKey 获取"""

import asyncio
import json
import sys
import os
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from binance.infrastructure.binance_client.listen_key_manager import ListenKeyManager


async def quick_test():
    """快速测试"""
    print("=" * 60)
    print("🧪 快速测试 ListenKey 获取")
    print("=" * 60)
    
    # 从环境变量获取凭证
    headers_str = os.getenv("TEST_HEADERS")
    cookies_str = os.getenv("TEST_COOKIES")
    
    if not headers_str or not cookies_str:
        print("\n❌ 未配置 TEST_HEADERS 或 TEST_COOKIES")
        return
    
    headers = json.loads(headers_str)
    print(f"\n✅ 凭证已加载")
    
    # 测试 ListenKey 获取
    try:
        manager = ListenKeyManager(headers, cookies_str)
        success, message, listen_key = await manager.get_listen_key()
        
        if success and listen_key:
            print(f"\n✅ ListenKey 获取成功!")
            print(f"   ListenKey: {listen_key[:40]}...")
            print(f"   长度: {len(listen_key)}")
            
            # WebSocket 连接信息
            ws_url = "wss://nbstream.binance.com/w3w/stream"
            subscribe_msg = {
                "method": "SUBSCRIBE",
                "params": [f"alpha@{listen_key}"],
                "id": 1
            }
            
            print(f"\n📡 WebSocket 连接信息:")
            print(f"   URL: {ws_url}")
            print(f"   订阅: {subscribe_msg}")
            
            print(f"\n✅ 订单 WebSocket 推送准备就绪！")
            print(f"   您可以使用上述信息连接 WebSocket")
        else:
            print(f"\n❌ ListenKey 获取失败: {message}")
        
        await manager.close()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(quick_test())

