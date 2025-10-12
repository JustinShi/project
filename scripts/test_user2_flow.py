"""测试 user_id=2 完整流程"""

import asyncio
import json
import sqlite3
from pathlib import Path


async def test_full_flow():
    """模拟从数据库获取 headers 并创建客户端的完整流程"""

    # 1. 从数据库获取 headers
    db_path = Path(__file__).parent.parent / "data" / "binance.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, headers, cookies FROM users WHERE id=2")
    result = cursor.fetchone()
    conn.close()

    if not result:
        print("❌ 未找到 user_id=2")
        return

    user_id, headers_str, cookies_str = result

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("步骤 1: 从数据库读取")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"User ID: {user_id}")
    print(f"Headers type: {type(headers_str)}")
    print(f"Headers length: {len(headers_str)}")
    print(f"Headers starts with: {headers_str[:30]!r}")
    print()

    # 2. 解析 JSON（模拟 _get_user_credentials）
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("步骤 2: JSON 解析（_get_user_credentials）")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    try:
        headers_dict = json.loads(headers_str)
        print("✅ JSON 解析成功")
        print(f"   Type: {type(headers_dict)}")
        print(f"   Is dict: {isinstance(headers_dict, dict)}")
        print(f"   Keys count: {len(headers_dict)}")
        print(f"   First 3 keys: {list(headers_dict.keys())[:3]}")
        print()
    except Exception as e:
        print(f"❌ JSON 解析失败: {e}")
        return

    # 3. 创建 BinanceClient（模拟实际调用）
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("步骤 3: 创建 BinanceClient")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    try:
        from binance.infrastructure.binance_client.http_client import BinanceClient

        print("传入参数:")
        print(f"  headers type: {type(headers_dict)}")
        print(f"  headers is dict: {isinstance(headers_dict, dict)}")
        print(f"  cookies type: {type(cookies_str)}")
        print()

        # 这里会触发 BinanceClient.__init__
        client = BinanceClient(headers=headers_dict, cookies=cookies_str)
        print("✅ BinanceClient 创建成功")
        print(f"   Client._headers type: {type(client._headers)}")
        print(f"   Client._headers keys count: {len(client._headers)}")
        await client.close()
        print()

    except Exception as e:
        print("❌ BinanceClient 创建失败")
        print(f"   Error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        print()
        return

    # 4. 创建 ListenKeyManager
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("步骤 4: 创建 ListenKeyManager")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    try:
        from binance.infrastructure.binance_client.listen_key_manager import (
            ListenKeyManager,
        )

        manager = ListenKeyManager(headers=headers_dict, cookies=cookies_str)
        print("✅ ListenKeyManager 创建成功")
        print(f"   Manager.headers type: {type(manager.headers)}")
        print()

    except Exception as e:
        print("❌ ListenKeyManager 创建失败")
        print(f"   Error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        print()
        return

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ 所有测试通过！")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()


if __name__ == "__main__":
    asyncio.run(test_full_flow())
