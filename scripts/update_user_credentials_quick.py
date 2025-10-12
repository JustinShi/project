"""快速更新用户凭证"""

import asyncio
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

from binance.infrastructure.database import get_db, init_db
from binance.infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)


async def main():
    """更新用户凭证"""
    print("\n=== 更新用户凭证 ===\n")

    # 初始化数据库
    await init_db()

    user_id = 1

    print(f"用户ID: {user_id}")
    print("\n请提供新的凭证信息：")
    print("（提示：从移动端抓包获取）\n")

    # 获取 headers（单行字符串格式）
    print("请输入 headers (单行字符串格式):")
    print("例如: csrftoken: xxx\\r\\nclienttype: ios\\r\\n...")
    print('或者从浏览器复制，格式类似: "key1: value1, key2: value2"')
    headers_str = input("> ").strip()

    # 如果用户输入的是 JSON 格式，给出警告
    if headers_str.startswith("{"):
        print("\n⚠️  警告: 检测到 JSON 格式的 headers")
        print("   HTTP 客户端需要单行字符串格式")
        print("   建议重新输入正确格式，或按 Ctrl+C 取消")
        print("\n是否继续？(y/n): ", end="")
        if input().strip().lower() != "y":
            print("❌ 取消更新")
            return

    # 获取 cookies
    print("\n请输入 cookies:")
    print("例如: lang=zh-CN; theme=dark; ...")
    cookies_str = input("> ").strip()

    # 确认
    print(f"\n确认更新用户 {user_id} 的凭证？(y/n): ", end="")
    confirm = input().strip().lower()

    if confirm != "y":
        print("❌ 取消更新")
        return

    # 更新数据库
    try:
        async for session in get_db():
            repo = UserRepositoryImpl(session)
            user = await repo.get_by_id(user_id)

            if not user:
                print(f"❌ 用户 {user_id} 不存在")
                return

            # 更新凭证
            user.headers = headers_str
            user.cookies = cookies_str

            await session.commit()

            print(f"\n✅ 用户 {user_id} 凭证更新成功！")
            print(f"   Headers 长度: {len(headers_str)} 字符")
            print(f"   Cookies 长度: {len(cookies_str)} 字符")

    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
