"""Binance OTO订单客户端"""

from datetime import datetime
from decimal import ROUND_DOWN, Decimal
from typing import NamedTuple

import httpx

from binance.domain.value_objects.price import Price
from binance.infrastructure.config import SymbolMapper
from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)


class ResolvedSymbol(NamedTuple):
    base_asset: str
    quote_asset: str
    price_precision: int
    quantity_precision: int
    lot_size: dict[str, str] | None
    price_filter: dict[str, str] | None
    original_symbol: str


class BinanceOTOOrderClient:
    """Binance OTO订单客户端"""

    def __init__(self, headers: dict[str, str], cookies: str):
        self.headers = headers.copy()
        self.cookies = cookies
        self.base_url = "https://www.binance.com"
        self._client: httpx.AsyncClient | None = None
        self._symbol_mapper = SymbolMapper()

    async def __aenter__(self):
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def _ensure_client(self):
        """确保HTTP客户端已初始化"""
        if not self._client:
            # 解析cookies字符串为字典
            cookies_dict = {}
            if self.cookies:
                for cookie in self.cookies.split(";"):
                    if "=" in cookie:
                        key, value = cookie.strip().split("=", 1)
                        cookies_dict[key] = value

            self._client = httpx.AsyncClient(
                headers=self.headers,
                cookies=cookies_dict,
                timeout=30.0
            )

    async def place_oto_order(
        self,
        symbol: str,
        quantity: Decimal,
        buy_price: Price,
        sell_price: Price,
        precision: int | None = None,
        chain: str | None = None
    ) -> tuple[bool, str, dict | None]:
        """下OTO订单"""
        try:
            await self._ensure_client()

            resolved_symbol = self._resolve_alpha_symbol(symbol, chain=chain)
            lot_step = None
            min_qty = None
            if resolved_symbol.lot_size:
                lot_step_str = resolved_symbol.lot_size.get("stepSize")
                min_qty_str = resolved_symbol.lot_size.get("minQty")
                if lot_step_str:
                    lot_step = Decimal(lot_step_str)
                if min_qty_str:
                    min_qty = Decimal(min_qty_str)

            effective_precision = precision or resolved_symbol.price_precision
            quantity_precision = resolved_symbol.quantity_precision

            # 格式化价格和数量
            price_tick = self._extract_tick_size(resolved_symbol.price_filter)
            buy_price_decimal = self._quantize_decimal(
                buy_price.value,
                effective_precision,
                tick=price_tick,
            )
            sell_price_decimal = self._quantize_decimal(
                sell_price.value,
                effective_precision,
                tick=price_tick,
            )
            quantity_decimal = self._quantize_decimal(
                quantity,
                quantity_precision,
                step=lot_step,
                minimum=min_qty,
            )
            if min_qty and quantity_decimal < min_qty:
                raise ValueError(f"数量低于最小下单量: {quantity_decimal} < {min_qty}")

            # 计算总金额，确保精度一致
            # 使用Decimal进行精确计算，然后转换为字符串
            total_amount_decimal = buy_price_decimal * quantity_decimal
            total_amount_decimal = total_amount_decimal.quantize(Decimal(f"1e-{effective_precision}"), rounding=ROUND_DOWN)

            # 构建OTO订单参数 - 使用正确的API格式
            order_data = {
                "baseAsset": resolved_symbol.base_asset,
                "quoteAsset": resolved_symbol.quote_asset,
                "workingSide": "BUY",
                "workingPrice": self._decimal_to_payload(buy_price_decimal, effective_precision),
                "workingQuantity": self._decimal_to_payload(quantity_decimal, quantity_precision),
                "paymentDetails": [{
                    "amount": self._decimal_to_payload(total_amount_decimal, effective_precision),
                    "paymentWalletType": "CARD"
                }],
                "pendingPrice": self._decimal_to_payload(sell_price_decimal, effective_precision)
            }

            logger.info(
                "下OTO订单",
                symbol=resolved_symbol.original_symbol,
                alpha_symbol=resolved_symbol.base_asset,
                precision=effective_precision,
                quantity_precision=quantity_precision,
                quantity=self._decimal_to_payload(quantity_decimal, quantity_precision),
                buy_price=self._decimal_to_payload(buy_price_decimal, effective_precision),
                sell_price=self._decimal_to_payload(sell_price_decimal, effective_precision),
                amount=self._decimal_to_payload(total_amount_decimal, effective_precision),
            )

            # 发送订单请求到正确的API端点
            response = await self._client.post(
                f"{self.base_url}/bapi/asset/v1/private/alpha-trade/oto-order/place",
                json=order_data
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success", False):
                    order_info = result.get("data", {})
                    logger.info(f"OTO订单下单成功: {order_info}")
                    return True, "订单下单成功", order_info
                else:
                    error_msg = result.get("message", "未知错误")
                    logger.error(f"OTO订单下单失败: {error_msg}")
                    return False, error_msg, None
            else:
                error_msg = f"HTTP错误: {response.status_code}"
                logger.error(f"OTO订单请求失败: {error_msg}")
                return False, error_msg, None

        except httpx.TimeoutException:
            error_msg = "请求超时"
            logger.error(f"OTO订单请求超时: {error_msg}")
            return False, error_msg, None
        except Exception as e:
            if str(e).startswith("InvalidOperation") or "quantize" in str(e):
                error_msg = "参数精度错误，请检查数量与价格是否符合精度限制"
            else:
                error_msg = f"下单异常: {e!s}"
            logger.error(f"OTO订单异常: {error_msg}")
            return False, error_msg, None

    def _resolve_alpha_symbol(self, symbol: str, chain: str | None = None) -> ResolvedSymbol:
        """解析交易对对应的Alpha交易符号及精度信息"""

        upper_symbol = symbol.upper()
        short_symbol = upper_symbol.replace("USDT", "")

        mapping = self._symbol_mapper.get_mapping(short_symbol, chain)

        lot_size = mapping.lot_size
        price_filter = mapping.price_filter
        resolved = ResolvedSymbol(
            base_asset=mapping.base_asset,
            quote_asset=mapping.quote_asset,
            price_precision=mapping.price_precision,
            quantity_precision=mapping.quantity_precision,
            lot_size=lot_size,
            price_filter=price_filter,
            original_symbol=mapping.order_api_symbol
        )

        return resolved

    @staticmethod
    def _extract_tick_size(price_filter: dict[str, str] | None) -> Decimal | None:
        if not price_filter:
            return None
        tick_size = price_filter.get("tickSize")
        if not tick_size:
            return None
        return Decimal(tick_size)

    @staticmethod
    def _decimal_to_payload(value: Decimal, precision: int) -> str:
        quantized = value.quantize(Decimal(f"1e-{precision}"), rounding=ROUND_DOWN)
        return format(quantized, f".{precision}f")

    @staticmethod
    def _quantize_decimal(
        value: Decimal | str | float,
        precision: int,
        tick: Decimal | None = None,
        step: Decimal | None = None,
        minimum: Decimal | None = None,
    ) -> Decimal:
        decimal_value = Decimal(str(value))
        quantize_unit = Decimal(f"1e-{precision}")

        if tick:
            quantize_unit = tick
        decimal_value = decimal_value.quantize(quantize_unit, rounding=ROUND_DOWN)

        if step:
            steps = (decimal_value / step).to_integral_value(rounding=ROUND_DOWN)
            decimal_value = steps * step

        if minimum is not None and decimal_value < minimum:
            decimal_value = minimum

        return decimal_value.quantize(quantize_unit, rounding=ROUND_DOWN)

    async def cancel_order(self, symbol: str, order_id: str) -> tuple[bool, str]:
        """取消订单"""
        try:
            await self._ensure_client()

            cancel_data = {
                "symbol": symbol,
                "orderId": order_id
            }

            logger.info(f"取消订单: {symbol}, 订单ID: {order_id}")

            response = await self._client.post(
                f"{self.base_url}/bapi/defi/v1/private/alpha-trade/order/cancel",
                json=cancel_data
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success", False):
                    logger.info(f"订单取消成功: {order_id}")
                    return True, "订单取消成功"
                else:
                    error_msg = result.get("message", "取消订单失败")
                    logger.error(f"订单取消失败: {error_msg}")
                    return False, error_msg
            else:
                error_msg = f"HTTP错误: {response.status_code}"
                logger.error(f"取消订单请求失败: {error_msg}")
                return False, error_msg

        except Exception as e:
            error_msg = f"取消订单异常: {e!s}"
            logger.error(f"取消订单异常: {error_msg}")
            return False, error_msg

    async def get_order_status(self, symbol: str, order_id: str) -> tuple[bool, str, dict | None]:
        """查询订单状态

        注意：此接口不存在于私有API文档中。
        订单状态应通过 WebSocket 推送获取（wss://nbstream.binance.com/w3w/stream）
        订阅格式：{"method":"SUBSCRIBE","params":["alpha@{listenKey}"],"id":2}

        此方法已废弃，保留仅为兼容性。实际使用时应使用 WebSocket 订阅订单更新。
        """
        logger.warning(f"get_order_status 已废弃，订单状态应通过 WebSocket 获取: {order_id}")
        return False, "此接口已废弃，请使用 WebSocket 订阅订单状态", None

    async def get_open_orders(self, symbol: str | None = None) -> tuple[bool, str, list | None]:
        """获取未成交订单列表"""
        try:
            await self._ensure_client()

            params = {}
            if symbol:
                params["symbol"] = symbol

            response = await self._client.get(
                f"{self.base_url}/bapi/defi/v1/private/alpha-trade/order/get-open-order",
                params=params
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success", False):
                    orders = result.get("data", [])
                    logger.info(f"获取未成交订单成功: {len(orders)}个订单")
                    return True, "查询成功", orders
                else:
                    error_msg = result.get("message", "获取未成交订单失败")
                    logger.error(f"获取未成交订单失败: {error_msg}")
                    return False, error_msg, None
            else:
                error_msg = f"HTTP错误: {response.status_code}"
                logger.error(f"获取未成交订单请求失败: {error_msg}")
                return False, error_msg, None

        except Exception as e:
            error_msg = f"获取未成交订单异常: {e!s}"
            logger.error(f"获取未成交订单异常: {error_msg}")
            return False, error_msg, None

    async def get_order_history(
        self,
        symbol: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100
    ) -> tuple[bool, str, list | None]:
        """获取订单历史"""
        try:
            await self._ensure_client()

            params = {"limit": limit}
            if symbol:
                params["symbol"] = symbol
            if start_time:
                params["startTime"] = int(start_time.timestamp() * 1000)
            if end_time:
                params["endTime"] = int(end_time.timestamp() * 1000)

            response = await self._client.get(
                f"{self.base_url}/bapi/defi/v1/private/alpha-trade/order/history",
                params=params
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success", False):
                    orders = result.get("data", [])
                    logger.info(f"获取订单历史成功: {len(orders)}个订单")
                    return True, "查询成功", orders
                else:
                    error_msg = result.get("message", "获取订单历史失败")
                    logger.error(f"获取订单历史失败: {error_msg}")
                    return False, error_msg, None
            else:
                error_msg = f"HTTP错误: {response.status_code}"
                logger.error(f"获取订单历史请求失败: {error_msg}")
                return False, error_msg, None

        except Exception as e:
            error_msg = f"获取订单历史异常: {e!s}"
            logger.error(f"获取订单历史异常: {error_msg}")
            return False, error_msg, None

    def parse_order_info(self, order_data: dict) -> dict:
        """解析订单信息"""
        return {
            "order_id": order_data.get("orderId"),
            "symbol": order_data.get("symbol"),
            "side": order_data.get("side"),
            "type": order_data.get("type"),
            "status": order_data.get("status"),
            "price": Decimal(str(order_data.get("price", "0"))),
            "quantity": Decimal(str(order_data.get("origQty", "0"))),
            "executed_quantity": Decimal(str(order_data.get("executedQty", "0"))),
            "time": datetime.fromtimestamp(order_data.get("time", 0) / 1000),
            "update_time": datetime.fromtimestamp(order_data.get("updateTime", 0) / 1000),
        }

    async def close(self):
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None
