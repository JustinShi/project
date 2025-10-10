"""集成测试：基于缓存符号映射完成两次 OTO 买卖流程

运行方式：
    uv run python scripts/test_oto_trade.py --user 1 --symbol KOGEUSDT --trades 2

注意：真实交易，请确保凭证有效、风险可控。
"""

from __future__ import annotations

import argparse
import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from typing import Any, Dict, List, Optional, Tuple

from binance.config.constants import PriceOffsetMode
from binance.domain.entities.price_data import PriceData
from binance.domain.value_objects.price import Price
from binance.infrastructure.config import YAMLConfigManager, SymbolMapper, TradingTarget
from binance.infrastructure.database.session import get_db
from binance.infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from binance.infrastructure.binance_client.http_client import BinanceClient
from binance.infrastructure.binance_client.oto_order_client import BinanceOTOOrderClient
from binance.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def user_credentials(user_id: int):
    """获取指定用户的 headers 与 cookies"""

    async for session in get_db():
        user_repo = UserRepositoryImpl(session)
        user = await user_repo.get_by_id(user_id)
        if not user or not user.has_credentials():
            raise RuntimeError("用户凭证不存在或不完整")

        try:
            headers = json.loads(user.headers)
        except Exception:
            headers = {}

        yield headers, user.cookies


async def fetch_last_price(client: BinanceClient, short_symbol: str) -> Decimal:
    """从 aggTicker24 缓存中获取代币价格"""

    data = await client.get_token_info()
    for entry in data:
        if str(entry.get("symbol", "")).upper() == short_symbol.upper():
            return Decimal(entry.get("price", "0"))
    raise RuntimeError(f"行情中找不到 {short_symbol}")


def build_price_data(symbol: str, price: Decimal) -> PriceData:
    return PriceData(
        symbol=symbol,
        price=Price(price, precision=8),
        volume=Decimal("0"),
        timestamp=datetime.now(),
    )


async def execute_trade(
    user_id: int,
    symbol: str,
    headers: Dict[str, str],
    cookies: str,
    trade_index: int,
    amount_usdt: Decimal,
) -> Dict[str, Any]:
    short_symbol = symbol.replace("USDT", "").upper()

    config_manager = YAMLConfigManager()
    user_config = config_manager.get_trading_target(user_id, short_symbol)

    symbol_mapper = SymbolMapper()
    mapping = symbol_mapper.get_mapping(short_symbol, user_config.chain if user_config else None)

    if user_config is None:
        user_config = TradingTarget(
            token_symbol_short=short_symbol,
            chain=mapping.chain,
            target_volume=Decimal("1000"),
            current_volume=Decimal("0"),
            volume_multiplier=Decimal("1"),
            price_offset_mode=PriceOffsetMode.PERCENTAGE,
            buy_offset_value=Decimal("0.5"),
            sell_offset_value=Decimal("0.5"),
            order_quantity=Decimal("10"),
            timeout_seconds=1800,
            price_volatility_threshold=Decimal("5"),
            is_trading_active=True,
        )

    async with BinanceClient(headers=headers, cookies=cookies) as http_client:
        last_price = await fetch_last_price(http_client, short_symbol)

    # 基于实际市场价格和 USDT 金额计算买入价格和数量
    # 买入价格设为当前价格的 1.005 倍（0.5% 溢价以确保成交）
    buy_value = (last_price * Decimal("1.005")).quantize(Decimal("1e-8"), rounding=ROUND_DOWN)
    
    # 根据 USDT 金额计算数量
    quantity = (amount_usdt / buy_value).quantize(Decimal("1e-8"), rounding=ROUND_DOWN)
    
    # 计算实际 USDT 金额
    raw_amount = quantity * buy_value
    effective_amount = raw_amount.quantize(Decimal("1e-8"), rounding=ROUND_DOWN)
    
    # 卖出价格设为买入价格的 1.01 倍（1% 利润）
    sell_value = (buy_value * Decimal("1.01")).quantize(Decimal("1e-8"), rounding=ROUND_DOWN)

    price_data = build_price_data(symbol, last_price)

    async with BinanceOTOOrderClient(headers, cookies) as oto_client:
        buy_price = Price(buy_value, precision=mapping.price_precision)
        sell_price = Price(sell_value, precision=mapping.price_precision)

        success, message, order_info = await oto_client.place_oto_order(
            symbol=symbol,
            quantity=quantity,
            buy_price=buy_price,
            sell_price=sell_price,
            chain=user_config.chain,
        )

        # 订单状态应通过 WebSocket 推送获取，不再轮询 HTTP API
        status_info = None

    return {
        "index": trade_index,
        "success": success,
        "message": message,
        "order_info": order_info,
        "status_info": status_info,
        "price": str(price_data.price.value),
        "buy_price": str(buy_price.value),
        "sell_price": str(sell_price.value),
        "quantity": str(quantity),
        "amount_usdt": str(effective_amount),
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description="执行 OTO 交易测试")
    parser.add_argument("--user", type=int, required=True, help="用户ID")
    parser.add_argument("--symbol", type=str, default="KOGEUSDT", help="交易符号 (默认 KOGEUSDT)")
    parser.add_argument("--trades", type=int, default=2, choices=range(1, 11), help="执行次数 (1-10)")
    parser.add_argument("--usdt", type=Decimal, default=Decimal("10"), help="每次交易对应的 USDT 金额")
    args = parser.parse_args()

    results: List[Dict[str, Any]] = []

    async with user_credentials(args.user) as (headers, cookies):
        for idx in range(1, args.trades + 1):
            try:
                result = await execute_trade(args.user, args.symbol, headers, cookies, idx, args.usdt)
                results.append(result)
            except Exception as exc:
                logger.error("交易执行异常", index=idx, error=str(exc))
                results.append({"index": idx, "success": False, "error": str(exc)})

            if idx < args.trades:
                await asyncio.sleep(2)

    logger.info("交易测试完成", results=results)


if __name__ == "__main__":
    asyncio.run(main())

