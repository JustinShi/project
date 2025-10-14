"""查询所有用户的实际交易量（处理mulPoint=4的代币）

用法:
    python scripts/check_all_users_volume.py [TOKEN]
    
示例:
    python scripts/check_all_users_volume.py AOP
    python scripts/check_all_users_volume.py USDT
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

from binance.infrastructure.database.session import get_db
from binance.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from binance.infrastructure.binance_client.http_client import BinanceClient

logger = structlog.get_logger(__name__)


async def query_single_user(
    user,
    target_token: str,
) -> dict | None:
    """查询单个用户的完整信息（并行查询用）
    
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
                cookies_str = "; ".join(
                    f"{k}={v}" for k, v in cookies_dict.items()
                )
        except Exception:
            pass  # 使用原始字符串
    
    # 获取token信息
    try:
        async with BinanceClient(headers=headers, cookies=cookies_str) as client:
            token_list = await client.get_token_info()
            token_info = None
            for entry in token_list:
                if str(entry.get("symbol", "")).upper() == target_token.upper():
                    token_info = entry
                    break
            
            if not token_info:
                print(f"⚠️ 用户{user.id} 未找到代币信息: {target_token}")
                return None
    except Exception as e:
        print(f"⚠️ 用户{user.id} 获取代币信息失败: {e}")
        return None
    
    # 查询交易量
    try:
        mul_point = int(token_info.get("mulPoint", 1) or 1)
        
        async with BinanceClient(headers=headers, cookies=cookies_str) as client:
            volume_data = await client.get_user_volume()
            
            # 从 tradeVolumeInfoList 中查找目标代币
            volume_list = volume_data.get("tradeVolumeInfoList", [])
            for token_vol in volume_list:
                if token_vol.get("tokenName") == target_token:
                    displayed_volume = Decimal(str(token_vol.get("volume", 0)))
                    real_volume = displayed_volume / Decimal(str(mul_point))
                    
                    return {
                        "user_id": user.id,
                        "name": user.name,
                        "displayed_volume": displayed_volume,
                        "real_volume": real_volume,
                    }
            
            # 未找到该代币的交易量
            return {
                "user_id": user.id,
                "name": user.name,
                "displayed_volume": Decimal("0"),
                "real_volume": Decimal("0"),
            }
        
    except Exception as e:
        print(f"⚠️ 用户{user.id} 查询交易量异常: {e}")
        return None


async def main(target_token: str = "AOP"):
    """主函数
    
    Args:
        target_token: 目标代币符号（默认AOP）
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
    
    # 打印简化报告
    print(f"\n{'='*50}")
    print(f"📊 {target_token} 交易量报告")
    print(f"{'='*50}")
    
    # 按用户显示（简化格式）
    for result in user_results:
        user_name = result['name'] or "未命名"
        volume_str = str(result['real_volume'])
        print(
            f"用户{result['user_id']:2d} | "
            f"{user_name:8s} | "
            f"{target_token:5s} | "
            f"{volume_str:>10s}"
        )
    
    print(f"{'='*50}\n")


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="查询所有用户的实际交易量（自动处理mulPoint=4的代币）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python scripts/check_all_users_volume.py AOP
    python scripts/check_all_users_volume.py USDT
        """,
    )
    parser.add_argument(
        "token",
        nargs="?",
        default="AOP",
        help="目标代币符号 (默认: AOP)",
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

