"""Binance ListenKey管理器"""

import asyncio
import contextlib
from datetime import datetime, timedelta
from typing import Any

import httpx

from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)


class ListenKeyManager:
    """ListenKey管理器"""

    def __init__(self, headers: dict[str, str], cookies: str):
        self.headers = headers.copy()
        self.cookies = cookies
        self.base_url = "https://www.binance.com"
        self._client: httpx.AsyncClient | None = None
        self._listen_key: str | None = None
        self._key_expires_at: datetime | None = None
        self._keep_alive_task: asyncio.Task | None = None

    async def __aenter__(self):
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

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
                headers=self.headers, cookies=cookies_dict, timeout=30.0
            )

    async def get_listen_key(self) -> tuple[bool, str, str | None]:
        """获取ListenKey"""
        try:
            await self._ensure_client()

            logger.info("获取ListenKey...")

            response = await self._client.post(
                f"{self.base_url}/bapi/defi/v1/private/alpha-trade/get-listen-key"
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"ListenKey API响应: {result}")

                # 处理不同的响应格式
                # 格式1: {"code": "000000", "data": {"listenKey": "xxx"}}
                # 格式2: {"success": true, "data": {"listenKey": "xxx"}}
                # 格式3: {"listenKey": "xxx"}
                # 格式4: "xxx" (直接返回字符串)

                listen_key = None

                # 如果返回的是字符串，直接使用
                if isinstance(result, str):
                    listen_key = result
                elif isinstance(result, dict):
                    # 检查是否有 code 字段（新格式）
                    if "code" in result and result["code"] == "000000":
                        data = result.get("data", {})
                        if isinstance(data, dict):
                            listen_key = data.get("listenKey")
                        else:
                            listen_key = data  # data 可能直接是 listenKey 字符串
                    # 检查是否有 success 字段
                    elif result.get("success", False):
                        data = result.get("data", {})
                        if isinstance(data, dict):
                            listen_key = data.get("listenKey")
                        else:
                            listen_key = data
                    # 直接返回 listenKey
                    elif "listenKey" in result:
                        listen_key = result.get("listenKey")

                if listen_key:
                    self._listen_key = listen_key
                    # ListenKey通常有效期为60分钟
                    self._key_expires_at = datetime.now() + timedelta(minutes=55)

                    # 启动保活任务
                    await self._start_keep_alive()

                    logger.info(f"ListenKey获取成功: {listen_key[:20]}...")
                    return True, "ListenKey获取成功", listen_key
                else:
                    error_msg = f"ListenKey为空或响应格式错误: {result}"
                    logger.error(f"ListenKey获取失败: {error_msg}")
                    return False, error_msg, None
            else:
                error_msg = f"HTTP错误: {response.status_code}"
                logger.error(f"ListenKey请求失败: {error_msg}")
                return False, error_msg, None

        except Exception as e:
            error_msg = f"获取ListenKey异常: {e!s}"
            logger.error(f"ListenKey异常: {error_msg}")
            return False, error_msg, None

    async def _start_keep_alive(self):
        """启动ListenKey保活任务"""
        if self._keep_alive_task and not self._keep_alive_task.done():
            self._keep_alive_task.cancel()

        self._keep_alive_task = asyncio.create_task(self._keep_alive_loop())

    async def _keep_alive_loop(self):
        """ListenKey保活循环"""
        while self._listen_key and self._key_expires_at:
            try:
                # 检查是否接近过期时间（提前5分钟续期）
                if datetime.now() >= self._key_expires_at - timedelta(minutes=5):
                    await self._extend_listen_key()

                # 每30分钟检查一次
                await asyncio.sleep(30 * 60)

            except asyncio.CancelledError:
                logger.info("ListenKey保活任务被取消")
                break
            except Exception as e:
                logger.error(f"ListenKey保活异常: {e}")
                await asyncio.sleep(60)  # 异常时等待1分钟再重试

    async def _extend_listen_key(self) -> bool:
        """延长ListenKey有效期"""
        if not self._listen_key:
            return False

        try:
            await self._ensure_client()

            logger.info(f"延长ListenKey有效期: {self._listen_key}")

            response = await self._client.put(
                f"{self.base_url}/bapi/defi/v1/private/alpha-trade/userDataStream",
                params={"listenKey": self._listen_key},
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success", False):
                    # 更新过期时间
                    self._key_expires_at = datetime.now() + timedelta(minutes=55)
                    logger.info("ListenKey有效期延长成功")
                    return True
                else:
                    error_msg = result.get("message", "延长ListenKey失败")
                    logger.error(f"ListenKey延长失败: {error_msg}")
                    return False
            else:
                error_msg = f"HTTP错误: {response.status_code}"
                logger.error(f"ListenKey延长请求失败: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"延长ListenKey异常: {e}")
            return False

    async def delete_listen_key(self) -> bool:
        """删除ListenKey

        注意: 币安 Alpha API 没有标准的删除 ListenKey 接口。
        ListenKey 会在 60 分钟后自动过期，因此这里只做清理本地状态。
        """
        if not self._listen_key:
            return True

        try:
            logger.info(f"清理ListenKey（自动过期）: {self._listen_key[:20]}...")

            # 币安 Alpha API 没有 DELETE ListenKey 端点
            # ListenKey 会在有效期（60分钟）后自动过期
            # 这里只需要清理本地状态

            # 清理本地状态
            self._listen_key = None
            self._key_expires_at = None

            logger.info("ListenKey 本地状态已清理（将自动过期）")
            return True

        except Exception as e:
            logger.error(f"清理ListenKey异常: {e}")
            return False

    def get_current_listen_key(self) -> str | None:
        """获取当前ListenKey（同步方法）"""
        return self._listen_key

    def is_key_valid(self) -> bool:
        """检查ListenKey是否有效"""
        if not self._listen_key or not self._key_expires_at:
            return False
        return datetime.now() < self._key_expires_at

    def get_key_info(self) -> dict[str, Any]:
        """获取ListenKey信息"""
        return {
            "listen_key": self._listen_key,
            "expires_at": self._key_expires_at.isoformat()
            if self._key_expires_at
            else None,
            "is_valid": self.is_key_valid(),
            "keep_alive_running": self._keep_alive_task is not None
            and not self._keep_alive_task.done(),
        }

    async def close(self):
        """关闭管理器"""
        # 停止保活任务
        if self._keep_alive_task and not self._keep_alive_task.done():
            self._keep_alive_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._keep_alive_task

        # 删除ListenKey
        if self._listen_key:
            await self.delete_listen_key()

        # 关闭HTTP客户端
        if self._client:
            await self._client.aclose()
            self._client = None

        self._listen_key = None
        self._key_expires_at = None
