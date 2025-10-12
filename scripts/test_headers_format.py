"""测试 user_id=2 的 headers 格式"""

import json
import sqlite3
from pathlib import Path


def test_headers():
    db_path = Path(__file__).parent.parent / "data" / "binance.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT headers FROM users WHERE id=2")
    result = cursor.fetchone()
    headers_str = result[0]

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("原始数据库字符串 (前 200 字符):")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(repr(headers_str[:200]))
    print()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("尝试 JSON 解析:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    try:
        headers_dict = json.loads(headers_str)
        print("✅ JSON 解析成功")
        print(f"   Type: {type(headers_dict)}")
        print(f"   Keys count: {len(headers_dict)}")
        print(f"   First 5 keys: {list(headers_dict.keys())[:5]}")
        print()
        print("   示例值:")
        for i, (key, value) in enumerate(list(headers_dict.items())[:3]):
            print(f"     {key}: {value[:50] if len(str(value)) > 50 else value}")
        print()

        # 测试是否可以传递给 httpx
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("测试 httpx.AsyncClient:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        import httpx

        try:
            # 测试是否可以用这个字典创建客户端
            client = httpx.AsyncClient(headers=headers_dict)
            print("✅ httpx.AsyncClient 创建成功")
            print(f"   Client headers type: {type(client.headers)}")
            client._transport.close()  # 立即关闭
        except Exception as e:
            print(f"❌ httpx.AsyncClient 创建失败: {e}")

    except Exception as e:
        print(f"❌ JSON 解析失败: {e}")

    conn.close()


if __name__ == "__main__":
    test_headers()
