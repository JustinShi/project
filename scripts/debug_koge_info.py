"""调试脚本：获取KOGE代币信息并写入本地缓存"""

import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any

from binance.infrastructure.database.session import get_db
from binance.infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from binance.infrastructure.binance_client.http_client import BinanceClient
from binance.infrastructure.cache.local_cache import LocalCache
from binance.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


def _find_token_entry(token_list: list[Dict[str, Any]], symbol_short: str) -> Optional[Dict[str, Any]]:
    symbol_short_upper = symbol_short.upper()
    for item in token_list:
        symbol = str(item.get("symbol", "")).upper()
        token_name = str(item.get("tokenName", "")).upper()
        alpha_id = str(item.get("alphaId", "")).upper()
        if (
            symbol == symbol_short_upper
            or token_name == symbol_short_upper
            or alpha_id == symbol_short_upper
        ):
            return item
    return None


async def _fetch_credentials() -> Optional[Dict[str, Any]]:
    async for session in get_db():
        user_repo = UserRepositoryImpl(session)
        user = await user_repo.get_by_id(1)
        if not user or not user.has_credentials():
            return None
        try:
            headers = json.loads(user.headers)
        except Exception:
            headers = {}
        cookies = user.cookies
        return {"headers": headers, "cookies": cookies}
    return None


async def main() -> None:
    symbol_short = "KOGE"
    credentials = await _fetch_credentials()
    if not credentials:
        logger.error("未找到有效的用户凭证")
        return

    cache = LocalCache()

    cached_info = cache.get_token_info(symbol_short)
    if cached_info:
        logger.info("缓存命中：代币信息")
    else:
        logger.info("缓存未命中：代币信息，准备从API获取")

    cached_precision = cache.get_token_precision(symbol_short)
    if cached_precision:
        logger.info("缓存命中：精度信息")
    else:
        logger.info("缓存未命中：精度信息，准备从API获取")

    async with BinanceClient(
        headers=credentials["headers"], cookies=credentials["cookies"]
    ) as client:
        token_list = await client.get_token_info()
        if token_list:
            all_info = {
                str(item.get("symbol", item.get("tokenName", "RAW")) or f"TOKEN_{idx}"):
                item
                for idx, item in enumerate(token_list)
            }
            cache.set_all_token_info(all_info)
            logger.info("已缓存代币信息", count=len(all_info))

        exchange_info = await client.get_exchange_info()
        symbols = exchange_info.get("symbols") or []
        if symbols:
            all_precision = {
                str(entry.get("symbol", f"PAIR_{idx}")): entry
                for idx, entry in enumerate(symbols)
            }
            cache.set_all_token_precision(all_precision)
            logger.info("已缓存交易精度记录", count=len(all_precision))

        entry = _find_token_entry(token_list, symbol_short) if token_list else None
        if entry:
            cached_info = entry

        precision = None
        symbol_upper = f"{symbol_short.upper()}USDT"
        cached_alpha = str(cached_info.get("alphaId", "")).upper() if cached_info else None
        for entry in symbols:
            entry_symbol = str(entry.get("symbol", "")).upper()
            entry_alpha = str(entry.get("alphaId", "")).upper()
            if entry_symbol == symbol_upper or (cached_alpha and entry_alpha == cached_alpha):
                precision = entry
                break

        if precision:
            cached_precision = precision

    if cached_info:
        logger.info("代币信息", data=cached_info)

    if cached_precision:
        logger.info("精度信息", data=cached_precision)
    else:
        logger.warning("未获得精度信息，后续请手动确认")

    logger.info(
        "缓存文件路径",
        token_info=str(Path("data/cache/token_info.json").resolve()),
        token_precision=str(Path("data/cache/token_precision.json").resolve())
    )


if __name__ == "__main__":
    asyncio.run(main())


