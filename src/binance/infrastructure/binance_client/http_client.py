"""币安HTTP客户端"""

from typing import Any

import httpx
from aiolimiter import AsyncLimiter

from binance.config import get_settings
from binance.config.constants import API_TIMEOUT_DEFAULT, BINANCE_API_BASE_URL
from binance.infrastructure.logging import get_logger


logger = get_logger(__name__)


class BinanceClient:
    """币安API客户端（异步HTTP）"""

    def __init__(
        self,
        headers: dict[str, str],
        cookies: str | None = None,
        rate_limiter: AsyncLimiter | None = None,
    ):
        """初始化币安客户端

        Args:
            headers: HTTP请求头（包含认证信息）
            cookies: Cookies字符串
            rate_limiter: API限流器（可选）
        """
        self._headers = headers.copy() if headers else {}
        self._cookies = cookies
        self._settings = get_settings()

        # 将cookies添加到headers中（币安API可能需要这样）
        if cookies:
            self._headers["cookie"] = cookies

        # API限流器（每用户10请求/秒）
        self._rate_limiter = rate_limiter or AsyncLimiter(
            max_rate=self._settings.api_rate_limit_per_user,
            time_period=self._settings.api_rate_limit_period,
        )

        # 创建HTTP客户端
        self._client = httpx.AsyncClient(
            base_url=BINANCE_API_BASE_URL,
            headers=self._headers,
            timeout=API_TIMEOUT_DEFAULT,
            follow_redirects=True,
        )

    @staticmethod
    def _parse_cookies(cookie_string: str | None) -> dict[str, str] | None:
        """解析cookie字符串为字典

        Args:
            cookie_string: Cookie字符串，格式如 "key1=value1; key2=value2"

        Returns:
            Cookie字典
        """
        if not cookie_string:
            return None

        cookies = {}
        for item in cookie_string.split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                cookies[key.strip()] = value.strip()
        return cookies

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """发送HTTP请求（带限流）

        Args:
            method: HTTP方法（GET, POST等）
            path: API路径
            **kwargs: httpx请求参数

        Returns:
            API响应JSON

        Raises:
            httpx.HTTPError: HTTP请求错误
            ValueError: API返回错误码
        """
        async with self._rate_limiter:
            try:
                response = await self._client.request(method, path, **kwargs)
                response.raise_for_status()

                data = response.json()

                # 检查API返回的业务状态
                if not data.get("success", False):
                    error_code = data.get("code", "UNKNOWN")
                    error_msg = data.get("message", "Unknown error")
                    logger.error(
                        "binance_api_error",
                        path=path,
                        code=error_code,
                        message=error_msg,
                    )
                    raise ValueError(f"API错误 [{error_code}]: {error_msg}")

                logger.debug("binance_api_success", path=path, data=data)
                return data

            except httpx.HTTPError as e:
                logger.error("binance_http_error", path=path, error=str(e))
                raise

    async def get_wallet_balance(self) -> dict[str, Any]:
        """查询Alpha钱包余额

        Returns:
            余额数据，格式：
            {
                "totalValuation": "47.52",
                "list": [
                    {
                        "symbol": "BR",
                        "tokenId": "ALPHA_118",
                        "free": "0.006657",
                        "freeze": "0",
                        "locked": "0",
                        "amount": "0.006657",
                        "valuation": "0.00051714"
                    }
                ]
            }

        Raises:
            ValueError: API返回错误
        """
        path = "/bapi/defi/v1/private/wallet-direct/cloud-wallet/alpha"
        params = {"includeCex": 1}

        logger.info("get_wallet_balance", path=path)
        response = await self._request("GET", path, params=params)
        return response.get("data", {})

    async def get_user_volume(self) -> dict[str, Any]:
        """查询用户今日交易量

        Returns:
            交易量数据，格式：
            {
                "totalVolume": 604467.94,
                "tradeVolumeInfoList": [
                    {
                        "tokenName": "ALEO",
                        "volume": 604467.94
                    }
                ]
            }

        Raises:
            ValueError: API返回错误
        """
        path = "/bapi/defi/v1/private/wallet-direct/buw/wallet/today/user-volume"

        logger.info("get_user_volume", path=path)
        response = await self._request("GET", path)
        return response.get("data", {})

    async def get_token_info(
        self, data_type: str = "aggregate"
    ) -> list[dict[str, Any]]:
        """查询代币信息

        Args:
            data_type: 数据类型，默认为aggregate

        Returns:
            代币信息列表

        Raises:
            ValueError: API返回错误
        """
        path = "/bapi/defi/v1/public/alpha-trade/aggTicker24"
        params = {"dataType": data_type}

        logger.info("get_token_info", path=path, data_type=data_type)
        response = await self._request("GET", path, params=params)
        return response.get("data", [])

    async def get_exchange_info(self) -> dict[str, Any]:
        """查询交易所公开的精度与符号配置"""
        path = "/bapi/defi/v1/public/alpha-trade/get-exchange-info"

        logger.info("get_exchange_info", path=path)
        response = await self._request("GET", path)
        return response.get("data", {})

    async def get_open_orders(self) -> list[dict[str, Any]]:
        """查询挂起的订单

        Returns:
            挂起订单列表

        Raises:
            ValueError: API返回错误
        """
        path = "/bapi/defi/v1/private/alpha-trade/order/get-open-order"

        logger.info("get_open_orders", path=path)
        response = await self._request("GET", path)
        return response.get("data", [])

    async def extract_trade_symbols(self) -> list[dict[str, Any]]:
        """获取交易所符号详细信息列表"""
        exchange_info = await self.get_exchange_info()
        return exchange_info.get("symbols", [])

    async def get_alpha_token_list(self) -> list[dict[str, Any]]:
        """获取Alpha代币列表

        Returns:
            Alpha代币列表信息

        Raises:
            ValueError: API返回错误
        """
        path = "/bapi/defi/v1/public/alpha-trade/token/list"

        logger.info("get_alpha_token_list", path=path)
        response = await self._request("GET", path)
        return response.get("data", [])

    async def close(self) -> None:
        """关闭HTTP客户端"""
        await self._client.aclose()

    async def __aenter__(self) -> "BinanceClient":
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """异步上下文管理器退出"""
        await self.close()
