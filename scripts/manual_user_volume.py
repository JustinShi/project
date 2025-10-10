"""查询用户交易量 (GET /bapi/defi/v1/private/wallet-direct/buw/wallet/today/user-volume)"""

import asyncio
import json
from typing import Dict

from binance.infrastructure.binance_client.http_client import BinanceClient
from binance.infrastructure.database.session import get_db
from binance.infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from binance.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


async def _fetch_headers(user_id: int) -> Dict[str, str]:
    async for session in get_db():
        repo = UserRepositoryImpl(session)
        user = await repo.get_by_id(user_id)
        if not user or not user.has_credentials():
            raise RuntimeError("未找到有效的用户凭证")
        try:
            return json.loads(user.headers)
        except Exception:  # noqa: BLE001
            raise RuntimeError("用户 headers 非 JSON 格式，请检查数据库存储")
    raise RuntimeError("数据库会话未返回用户凭证")


async def main() -> None:
    headers = await _fetch_headers(1)

    async with BinanceClient(headers=headers) as client:
        data = await client.get_user_volume()

    logger.info("用户交易量查询成功", data=data)


if __name__ == "__main__":
    asyncio.run(main())

