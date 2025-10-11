"""代币符号映射工具"""

from __future__ import annotations

from dataclasses import dataclass

from binance.infrastructure.cache import LocalCache


@dataclass(frozen=True)
class SymbolMapping:
    """标准化后的代币符号映射信息"""

    short_symbol: str
    chain: str | None
    alpha_id: str
    order_api_symbol: str
    websocket_symbol: str
    base_asset: str
    quote_asset: str
    price_precision: int
    quantity_precision: int
    lot_size: dict[str, str] | None
    price_filter: dict[str, str] | None


class SymbolMapper:
    """从本地缓存构建代币符号映射"""

    def __init__(self, cache: LocalCache | None = None) -> None:
        self._cache = cache or LocalCache()
        self._memory: dict[str, SymbolMapping] = {}

    def get_mapping(self, short_symbol: str, chain: str | None = None) -> SymbolMapping:
        """根据代币简称获取完整的符号映射"""

        short_symbol_upper = short_symbol.upper()
        cache_key = f"{(chain or 'DEFAULT').upper()}::{short_symbol_upper}"

        mapping = self._memory.get(cache_key)
        if mapping:
            return mapping

        info_entry = self._cache.get_token_info(short_symbol_upper)
        info_data = info_entry or {}

        alpha_id = info_data.get("alphaId")
        trade_decimal = info_data.get("tradeDecimal", 8)
        chain_name = info_data.get("chainName") or chain

        base_asset = alpha_id or f"ALPHA_{short_symbol_upper}"
        order_symbol = f"{base_asset}USDT"

        precision_entry = self._cache.get_token_precision(order_symbol)
        precision_data = precision_entry or {}

        lot_size: dict[str, str] | None = None
        price_filter: dict[str, str] | None = None
        filters = precision_data.get("filters") or []
        for entry in filters:
            if entry.get("filterType") == "LOT_SIZE":
                lot_size = entry
            if entry.get("filterType") == "PRICE_FILTER":
                price_filter = entry

        mapping = SymbolMapping(
            short_symbol=short_symbol_upper,
            chain=chain_name,
            alpha_id=precision_data.get("baseAsset", base_asset),
            order_api_symbol=precision_data.get("symbol", order_symbol),
            websocket_symbol=precision_data.get("symbol", order_symbol).lower(),
            base_asset=precision_data.get("baseAsset", base_asset),
            quote_asset=precision_data.get("quoteAsset", "USDT"),
            price_precision=precision_data.get("pricePrecision", trade_decimal),
            quantity_precision=precision_data.get("quantityPrecision", trade_decimal),
            lot_size=lot_size,
            price_filter=price_filter,
        )

        self._memory[cache_key] = mapping
        return mapping

