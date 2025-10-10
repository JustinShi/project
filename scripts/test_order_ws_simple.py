#!/usr/bin/env python3
"""简单的订单 WebSocket 测试"""

import asyncio
import json
import sys
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from binance.infrastructure.binance_client.listen_key_manager import ListenKeyManager
from binance.infrastructure.database import get_db, init_db
from binance.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl


async def get_user_credentials(user_id: int = 1):
    """从数据库获取用户凭证"""
    try:
        # 初始化数据库
        init_db()
        
        # 获取数据库会话
        async for db_session in get_db():
            user_repo = UserRepositoryImpl(db_session)
            user = await user_repo.get_by_id(user_id)
            
            if not user:
                print(f"❌ 用户 {user_id} 不存在")
                return None, None
            
            if not user.headers or not user.cookies:
                print(f"❌ 用户 {user_id} 没有配置凭证")
                return None, None
            
            print(f"✅ 成功获取用户 {user_id} 的凭证")
            return user.headers, user.cookies
            
    except Exception as e:
        print(f"❌ 获取用户凭证失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None


async def test_listen_key():
    """测试 ListenKey 获取"""
    print("\n" + "=" * 60)
    print("🧪 测试订单 WebSocket 推送 - ListenKey")
    print("=" * 60)
    
    # 获取用户凭证
    print("\n📋 步骤 1: 获取用户凭证")
    headers, cookies = await get_user_credentials(user_id=1)
    
    if not headers or not cookies:
        print("❌ 无法获取用户凭证，测试终止")
        return
    
    # 获取 ListenKey
    print("\n📋 步骤 2: 获取 ListenKey")
    try:
        listen_key_manager = ListenKeyManager(headers, cookies)
        success, message, listen_key = await listen_key_manager.get_listen_key()
        
        if success and listen_key:
            print(f"✅ ListenKey 获取成功")
            print(f"   ListenKey: {listen_key[:30]}...")
            print(f"   完整长度: {len(listen_key)} 字符")
            
            # 构建 WebSocket URL
            ws_url = f"wss://nbstream.binance.com/w3w/stream"
            subscribe_msg = {
                "method": "SUBSCRIBE",
                "params": [f"alpha@{listen_key}"],
                "id": 1
            }
            
            print(f"\n📋 步骤 3: WebSocket 连接信息")
            print(f"   WebSocket URL: {ws_url}")
            print(f"   订阅消息: {json.dumps(subscribe_msg, indent=2)}")
            
            print(f"\n✅ ListenKey 测试通过！")
            print(f"   您可以使用以上信息手动测试 WebSocket 连接")
            
        else:
            print(f"❌ ListenKey 获取失败: {message}")
        
        # 关闭管理器
        await listen_key_manager.close()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_listen_key())
    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

