"""手动发起一次 OTO 下单请求，使用指定参数"""

import asyncio
import json
from typing import Dict

import httpx

from binance.infrastructure.database.session import get_db
from binance.infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from binance.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

PAYLOAD = {
    "quoteAsset": "USDT",
    "baseAsset": "ALPHA_22",
    "pendingPrice": "0.01",
    "paymentDetails": [
        {
            "paymentWalletType": "CARD",
            "amount": "9.99782633",
        }
    ],
    "workingQuantity": "0.2082",
    "workingPrice": "48.0202994",
    "workingSide": "BUY",
}


def _parse_cookies(raw: str) -> Dict[str, str]:
    cookies: Dict[str, str] = {}
    if not raw:
        return cookies
    for item in raw.split(";"):
        item = item.strip()
        if not item or "=" not in item:
            continue
        key, value = item.split("=", 1)
        cookies[key.strip()] = value.strip()
    return cookies


async def _fetch_credentials(user_id: int) -> tuple[Dict[str, str], Dict[str, str]]:
    async for session in get_db():
        repo = UserRepositoryImpl(session)
        user = await repo.get_by_id(user_id)
        if not user or not user.has_credentials():
            raise RuntimeError("未找到有效的用户凭证")
        try:
            headers = json.loads(user.headers)
        except Exception:
            headers = {}
        cookies = _parse_cookies(user.cookies)
        return headers, cookies
    raise RuntimeError("数据库会话未返回凭证")


async def main() -> None:
    headers, cookies = await _fetch_credentials(1)

    async with httpx.AsyncClient(
        base_url="https://www.binance.com",
        headers=headers,
        cookies=cookies,
        timeout=30.0,
    ) as client:
        response = await client.post(
            "/bapi/asset/v1/private/alpha-trade/oto-order/place",
            json=PAYLOAD,
        )

    logger.info("OTO订单请求完成", status=response.status_code)
    try:
        logger.info("响应数据", response=response.json())
    except Exception:
        logger.warning("响应解析失败", response_text=response.text)


if __name__ == "__main__":
    asyncio.run(main())

