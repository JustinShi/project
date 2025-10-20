"""查询所有用户的实际交易量（显示所有代币）

用法:
    python scripts/check_all_users_volume.py [TOKEN]

示例:
    python scripts/check_all_users_volume.py        # 显示所有代币
    python scripts/check_all_users_volume.py AOP    # 只显示AOP代币
    python scripts/check_all_users_volume.py USDT   # 只显示USDT代币
"""

import argparse
import asyncio
import json
import sys
from decimal import Decimal
from pathlib import Path

import structlog


# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from binance.infrastructure.binance_client.http_client import BinanceClient
from binance.infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from binance.infrastructure.database.session import get_db


logger = structlog.get_logger(__name__)


# 全局缓存，避免重复获取代币信息
_token_info_cache = {}
_global_client = None


def get_token_info_from_local_cache(target_token: str) -> dict | None:
    """从本地缓存获取代币信息"""
    try:
        from binance.infrastructure.cache.local_cache import LocalCache

        cache = LocalCache()
        return cache.get_token_info(target_token)
    except Exception as e:
        print(f"⚠️ 从本地缓存获取代币信息失败: {e}")
        return None


async def get_token_info_cached(
    target_token: str, headers: dict, cookies: str
) -> dict | None:
    """获取代币信息（优先使用本地缓存）"""
    global _global_client
    cache_key = target_token.upper()

    # 1. 优先使用本地缓存
    if cache_key not in _token_info_cache:
        local_cached = get_token_info_from_local_cache(target_token)
        if local_cached:
            _token_info_cache[cache_key] = local_cached
            print(f"✅ 使用本地缓存获取代币信息: {target_token}")
            return local_cached

    # 2. 如果本地缓存没有，则从API获取
    if cache_key not in _token_info_cache:
        try:
            # 使用全局客户端，避免重复创建连接
            if _global_client is None:
                _global_client = BinanceClient(headers=headers, cookies=cookies)
                await _global_client.__aenter__()

            print(f"🔄 从API获取代币信息: {target_token}")
            token_list = await _global_client.get_token_info()
            for entry in token_list:
                if str(entry.get("symbol", "")).upper() == target_token.upper():
                    _token_info_cache[cache_key] = entry
                    break
            else:
                _token_info_cache[cache_key] = None
        except Exception as e:
            print(f"⚠️ 从API获取代币信息失败: {e}")
            _token_info_cache[cache_key] = None

    return _token_info_cache[cache_key]


async def get_user_volume_shared(headers: dict, cookies: str) -> dict:
    """获取用户交易量（每个用户使用自己的客户端）"""
    # 每个用户需要自己的认证信息，所以不能共享客户端
    # 但我们可以优化连接池设置
    async with BinanceClient(headers=headers, cookies=cookies) as client:
        return await client.get_user_volume()


async def cleanup_global_client():
    """清理全局客户端"""
    global _global_client
    if _global_client is not None:
        try:
            await _global_client.__aexit__(None, None, None)
        except Exception:
            pass
        _global_client = None


async def query_single_user(
    user,
    target_token: str | None = None,
) -> dict | None:
    """查询单个用户的完整信息（并行查询用）

    Args:
        user: 用户对象
        target_token: 目标代币符号，如果为None则显示所有代币

    Returns:
        用户结果字典，或 None（如果查询失败）
    """
    try:
        # 解析 headers（JSON格式）
        headers_str = user.headers
        if isinstance(headers_str, bytes):
            headers_str = headers_str.decode("utf-8")
        headers = json.loads(headers_str) if headers_str else {}
    except Exception:
        # 静默跳过无效用户
        return None

    # 处理 cookies（直接使用字符串）
    cookies_str = user.cookies or ""
    if isinstance(cookies_str, bytes):
        cookies_str = cookies_str.decode("utf-8")

    # 如果 cookies 是 JSON 格式，转换为标准 cookie 字符串
    if cookies_str.strip().startswith("{"):
        try:
            cookies_dict = json.loads(cookies_str)
            if isinstance(cookies_dict, dict):
                # 转换为 "key1=value1; key2=value2" 格式
                cookies_str = "; ".join(f"{k}={v}" for k, v in cookies_dict.items())
        except Exception:
            pass  # 使用原始字符串

    # 查询交易量
    try:
        # 使用共享的HTTP客户端进行并行查询
        volume_data = await get_user_volume_shared(headers, cookies_str)
        volume_list = volume_data.get("tradeVolumeInfoList", [])

        if target_token:
            # 查询指定代币
            token_info = await get_token_info_cached(target_token, headers, cookies_str)
            if not token_info:
                print(f"⚠️ 用户{user.id} 未找到代币信息: {target_token}")
                return None

            mul_point = int(token_info.get("mulPoint", 1) or 1)

            # 从 tradeVolumeInfoList 中查找目标代币
            for token_vol in volume_list:
                if token_vol.get("tokenName") == target_token:
                    displayed_volume = Decimal(str(token_vol.get("volume", 0)))
                    real_volume = displayed_volume / Decimal(str(mul_point))

                    return {
                        "user_id": user.id,
                        "name": user.name,
                        "token_volumes": {target_token: {
                            "displayed_volume": displayed_volume,
                            "real_volume": real_volume,
                        }},
                    }

            # 未找到该代币的交易量
            return {
                "user_id": user.id,
                "name": user.name,
                "token_volumes": {target_token: {
                    "displayed_volume": Decimal("0"),
                    "real_volume": Decimal("0"),
                }},
            }
        else:
            # 查询所有代币
            token_volumes = {}
            
            # 获取所有代币信息（用于mulPoint处理）
            all_tokens = set()
            for token_vol in volume_list:
                token_name = token_vol.get("tokenName")
                if token_name:
                    all_tokens.add(token_name)
            
            # 批量获取代币信息
            for token_name in all_tokens:
                try:
                    token_info = await get_token_info_cached(token_name, headers, cookies_str)
                    if token_info:
                        mul_point = int(token_info.get("mulPoint", 1) or 1)
                        
                        # 查找对应的交易量
                        for token_vol in volume_list:
                            if token_vol.get("tokenName") == token_name:
                                displayed_volume = Decimal(str(token_vol.get("volume", 0)))
                                real_volume = displayed_volume / Decimal(str(mul_point))
                                
                                token_volumes[token_name] = {
                                    "displayed_volume": displayed_volume,
                                    "real_volume": real_volume,
                                }
                                break
                except Exception:
                    # 如果获取代币信息失败，使用默认mulPoint=1
                    for token_vol in volume_list:
                        if token_vol.get("tokenName") == token_name:
                            displayed_volume = Decimal(str(token_vol.get("volume", 0)))
                            token_volumes[token_name] = {
                                "displayed_volume": displayed_volume,
                                "real_volume": displayed_volume,  # 默认mulPoint=1
                            }
                            break

            return {
                "user_id": user.id,
                "name": user.name,
                "token_volumes": token_volumes,
            }

    except Exception as e:
        print(f"⚠️ 用户{user.id} 查询交易量异常: {e}")
        return None


async def main(target_token: str | None = None):
    """主函数

    Args:
        target_token: 目标代币符号，如果为None则显示所有代币
    """
    # 不显示日志，只显示简化结果
    # setup_logging()

    # 获取所有用户
    users = []
    async for session in get_db():
        from sqlalchemy import select

        from binance.infrastructure.database.models import User as UserModel

        # 查询所有用户
        result = await session.execute(select(UserModel))
        user_models = result.scalars().all()

        # 转换为领域实体
        repo = UserRepositoryImpl(session)
        for user_model in user_models:
            user = repo._to_entity(user_model)
            users.append(user)
        break

    if not users:
        print("⚠️ 未找到任何用户")
        return

    # 并行查询所有用户
    print(f"🔍 开始并行查询 {len(users)} 个用户的交易量...")
    tasks = [query_single_user(user, target_token) for user in users]
    results = await asyncio.gather(*tasks)

    # 过滤掉失败的查询结果
    user_results = [r for r in results if r is not None]

    if not user_results:
        print("⚠️ 所有用户查询均失败")
        return

    # 打印报告
    if target_token:
        # 显示指定代币的报告
        print(f"\n{'=' * 50}")
        print(f"📊 {target_token} 交易量报告")
        print(f"{'=' * 50}")

        for result in user_results:
            user_name = result["name"] or "未命名"
            token_volumes = result["token_volumes"]
            if target_token in token_volumes:
                volume_str = str(token_volumes[target_token]["real_volume"])
            else:
                volume_str = "0"
            print(
                f"用户{result['user_id']:2d} | "
                f"{user_name:8s} | "
                f"{target_token:5s} | "
                f"{volume_str:>10s}"
            )
    else:
        # 显示所有代币的报告
        print(f"\n{'=' * 80}")
        print(f"📊 所有代币交易量报告")
        print(f"{'=' * 80}")

        # 收集所有代币名称
        all_tokens = set()
        for result in user_results:
            all_tokens.update(result["token_volumes"].keys())
        
        # 按代币名称排序
        sorted_tokens = sorted(all_tokens)

        # 显示表头
        header = "用户ID | 姓名     | "
        for token in sorted_tokens:
            header += f"{token:>10s} | "
        print(header)
        print("-" * len(header))

        # 显示每个用户的数据
        for result in user_results:
            user_name = result["name"] or "未命名"
            line = f"{result['user_id']:6d} | {user_name:8s} | "
            for token in sorted_tokens:
                if token in result["token_volumes"]:
                    volume_str = str(result["token_volumes"][token]["real_volume"])
                else:
                    volume_str = "0"
                line += f"{volume_str:>10s} | "
            print(line)

    print(f"{'=' * 80}\n")

    # 清理全局客户端
    await cleanup_global_client()


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="查询所有用户的实际交易量（自动处理mulPoint=4的代币）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python scripts/check_all_users_volume.py        # 显示所有代币
    python scripts/check_all_users_volume.py AOP    # 只显示AOP代币
    python scripts/check_all_users_volume.py USDT   # 只显示USDT代币
        """,
    )
    parser.add_argument(
        "token",
        nargs="?",
        default=None,
        help="目标代币符号，如果不指定则显示所有代币",
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(args.token))
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断执行")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        sys.exit(1)
