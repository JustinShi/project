"""交易策略执行器"""

from __future__ import annotations

import asyncio
import json
import math
from decimal import ROUND_DOWN, Decimal
from typing import Any

import httpx

from binance.domain.value_objects.price import Price
from binance.infrastructure.binance_client.http_client import BinanceClient
from binance.infrastructure.binance_client.listen_key_manager import ListenKeyManager
from binance.infrastructure.binance_client.order_websocket import (
    OrderWebSocketConnector,
)
from binance.infrastructure.binance_client.oto_order_client import BinanceOTOOrderClient
from binance.infrastructure.cache.local_cache import LocalCache
from binance.infrastructure.config import SymbolMapper
from binance.infrastructure.config.strategy_config_manager import (
    StrategyConfig,
    StrategyConfigManager,
)
from binance.infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from binance.infrastructure.database.session import get_db
from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)


class AuthenticationError(Exception):
    """认证失败异常"""

    pass


class StrategyExecutor:
    """交易策略执行器"""

    def __init__(
        self,
        config_path: str = "config/trading_config.yaml",
    ):
        self.config_manager = StrategyConfigManager(config_path)
        self.cache = LocalCache()  # 全局缓存实例（单例模式）
        self.symbol_mapper = SymbolMapper()
        self._running_tasks: dict[str, asyncio.Task] = {}
        self._user_volumes: dict[
            int, dict[str, Decimal]
        ] = {}  # {user_id: {strategy_id: volume}}
        self._stop_flags: dict[str, bool] = {}
        self._force_stop = False

        # 共享的 HTTP 客户端（用于并发请求）
        self._shared_client: httpx.AsyncClient | None = None
        self._client_lock = asyncio.Lock()

        # 订单状态追踪
        self._order_status: dict[
            str, dict[str, Any]
        ] = {}  # {order_id: {status, side, quantity, etc}}
        self._order_events: dict[str, asyncio.Event] = {}  # {order_id: Event}

        # WebSocket 连接管理
        self._ws_connectors: dict[
            int, OrderWebSocketConnector
        ] = {}  # {user_id: connector}
        self._listen_key_managers: dict[
            int, ListenKeyManager
        ] = {}  # {user_id: manager}

        # 被阻止的用户（补充认证失败等）
        self._blocked_users: set[int] = set()

    async def _get_user_client(
        self, headers: dict[str, str], cookies: str
    ) -> httpx.AsyncClient:
        """为每个用户创建独立的 HTTP 客户端（避免认证信息混乱）"""
        # 为每个用户创建独立的客户端，避免共享认证信息
        limits = httpx.Limits(
            max_connections=10,  # 每个用户最大连接数
            max_keepalive_connections=5,  # 每个用户最大保持活动连接数
        )
        client_headers = headers.copy()
        if cookies:
            client_headers["cookie"] = cookies

        return httpx.AsyncClient(
            base_url="https://www.binance.com",
            headers=client_headers,
            timeout=30,
            follow_redirects=True,
            limits=limits,
        )

    async def _close_shared_client(self):
        """关闭共享的 HTTP 客户端"""
        async with self._client_lock:
            if self._shared_client:
                await self._shared_client.aclose()
                self._shared_client = None

    async def start_all_strategies(self) -> None:
        """启动所有启用的策略"""
        strategies = self.config_manager.get_enabled_strategies()
        logger.info("启动交易策略", count=len(strategies))

        # 启动所有策略，但不等待它们完成
        # 让每个策略独立运行，由主循环来管理
        for strategy in strategies:
            task = asyncio.create_task(self._run_strategy(strategy))
            self._running_tasks[strategy.strategy_id] = task

    async def start_strategy(self, strategy_id: str) -> bool:
        """启动指定策略

        Args:
            strategy_id: 策略ID

        Returns:
            是否成功启动
        """
        strategy = self.config_manager.get_strategy(strategy_id)
        if not strategy or not strategy.enabled:
            logger.error("策略不存在或未启用", strategy_id=strategy_id)
            return False

        if strategy_id in self._running_tasks:
            logger.warning("策略已在运行", strategy_id=strategy_id)
            return False

        # 创建包装任务，确保完成后自动清理
        async def _wrapped_strategy():
            try:
                await self._run_strategy(strategy)
            finally:
                # 任务完成后自动从运行列表中移除
                if strategy_id in self._running_tasks:
                    del self._running_tasks[strategy_id]
                logger.info("策略任务已清理", strategy_id=strategy_id)

        task = asyncio.create_task(_wrapped_strategy())
        self._running_tasks[strategy_id] = task
        logger.info("策略已启动", strategy_id=strategy_id)
        return True

    async def stop_strategy(self, strategy_id: str) -> None:
        """停止指定策略

        Args:
            strategy_id: 策略ID
        """
        logger.info("正在停止策略", strategy_id=strategy_id)
        self._stop_flags[strategy_id] = True

        task = self._running_tasks.get(strategy_id)
        if task:
            try:
                # 给任务一些时间优雅停止
                await asyncio.wait_for(task, timeout=5.0)
            except TimeoutError:
                logger.warning("策略停止超时，强制取消", strategy_id=strategy_id)
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            except Exception as e:
                logger.error(
                    "停止策略时发生异常", strategy_id=strategy_id, error=str(e)
                )

        if strategy_id in self._running_tasks:
            del self._running_tasks[strategy_id]
        logger.info("策略已停止", strategy_id=strategy_id)

    async def stop_all_strategies(self) -> None:
        """停止所有策略"""
        logger.info("停止所有策略", count=len(self._running_tasks))

        # 设置强制停止标志
        self._force_stop = True

        # 首先设置所有策略的停止标志
        for strategy_id in self._stop_flags:
            self._stop_flags[strategy_id] = True

        # 取消所有正在运行的任务
        for task in self._running_tasks.values():
            if not task.done():
                task.cancel()

        # 等待所有任务完成或取消（缩短超时时间）
        if self._running_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(
                        *self._running_tasks.values(), return_exceptions=True
                    ),
                    timeout=2.0,  # 缩短到2秒
                )
            except TimeoutError:
                logger.warning("部分任务停止超时，强制清理")
            except Exception as e:
                logger.error("停止任务时发生异常", error=str(e))

        # 清理任务列表
        self._running_tasks.clear()

        # 关闭所有WebSocket连接
        await self._cleanup_all_websocket_connections()

        # 关闭共享的 HTTP 客户端
        await self._close_shared_client()

        logger.info("所有策略已停止")

    async def _run_strategy(self, strategy: StrategyConfig) -> None:
        """运行单个策略

        Args:
            strategy: 策略配置
        """
        logger.info(
            "策略开始执行",
            strategy_id=strategy.strategy_id,
            strategy_name=strategy.strategy_name,
            target_token=strategy.target_token,
            target_volume=str(strategy.target_volume),
            user_count=len(strategy.user_ids),
        )

        self._stop_flags[strategy.strategy_id] = False

        try:
            # 为每个用户创建并发任务
            user_tasks = []
            for user_id in strategy.user_ids:
                user_strategy = self.config_manager.get_user_strategy_config(
                    user_id, strategy.strategy_id
                )
                if user_strategy:
                    task = asyncio.create_task(
                        self._run_user_strategy(user_id, user_strategy)
                    )
                    user_tasks.append(task)

            # 等待所有用户任务完成
            if user_tasks:
                results = await asyncio.gather(*user_tasks, return_exceptions=True)
                for idx, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(
                            "用户策略执行异常",
                            user_id=strategy.user_ids[idx],
                            error=str(result),
                        )

        finally:
            # 清理资源：从运行任务列表中移除已完成的策略
            if strategy.strategy_id in self._running_tasks:
                del self._running_tasks[strategy.strategy_id]
            logger.info(
                "策略主任务完成，用户任务可能仍在运行", strategy_id=strategy.strategy_id
            )

    async def _run_user_strategy(self, user_id: int, strategy: StrategyConfig) -> None:
        """运行单个用户的策略（新逻辑：循环批次执行）

        执行流程：
        1. 查询用户当前交易量
        2. 计算剩余交易量和所需循环次数
        3. 建立 WebSocket 连接
        4. 执行 N 次交易
        5. 重新查询交易量，判断是否达标
        6. 未达标继续循环，直至达标

        Args:
            user_id: 用户ID
            strategy: 策略配置
        """
        # 检查用户是否被阻止
        if user_id in self._blocked_users:
            logger.warning(
                "用户已被阻止，跳过策略执行",
                user_id=user_id,
                strategy_id=strategy.strategy_id,
                reason="补充认证失败或其他限制",
            )
            return

        logger.info(
            "用户策略开始",
            user_id=user_id,
            strategy_id=strategy.strategy_id,
            target_volume=str(strategy.target_volume),
            single_amount=str(strategy.single_trade_amount_usdt),
        )

        # 获取用户凭证
        credentials = await self._get_user_credentials(user_id)
        if not credentials:
            logger.error("用户凭证不存在", user_id=user_id)
            return

        headers, cookies = credentials

        # 建立 WebSocket 连接以监听订单状态
        ws_connected = await self._ensure_websocket_connection(
            user_id, headers, cookies
        )
        if not ws_connected:
            logger.warning("WebSocket连接失败，将跳过实时订单监听", user_id=user_id)
            # 不返回，继续执行策略，只是没有实时订单状态更新

        try:
            # 循环批次执行，直至达标
            while (
                not self._stop_flags.get(strategy.strategy_id, False)
                and not self._force_stop
            ):
                # 查询当前交易量
                current_volume = await self._query_user_current_volume(
                    user_id, strategy.target_token, headers, cookies
                )

                # 检查是否达标
                if current_volume >= strategy.target_volume:
                    logger.info(
                        "🎉 用户已达成目标交易量，策略完成",
                        user_id=user_id,
                        strategy_id=strategy.strategy_id,
                        current_volume=str(current_volume),
                        target_volume=str(strategy.target_volume),
                    )
                    break

                # 计算进度百分比（仅用于日志显示）
                # progress_percentage = (
                #     float(current_volume) / float(strategy.target_volume) * 100
                # )

                # 计算剩余交易量和循环次数
                remaining_volume = strategy.target_volume - current_volume
                loop_count = await self._calculate_loop_count(
                    user_id, strategy, remaining_volume, headers, cookies
                )

                logger.info(
                    "📊 开始批次交易",
                    user_id=user_id,
                    strategy_id=strategy.strategy_id,
                    current_volume=str(current_volume),
                    target_volume=str(strategy.target_volume),
                    remaining_volume=str(remaining_volume),
                    planned_loops=loop_count,
                    progress=f"{float(current_volume) / float(strategy.target_volume) * 100:.1f}%",
                )

                # 执行 N 次交易
                await self._execute_batch_trades(
                    user_id, strategy, loop_count, headers, cookies
                )

                # 批次完成，等待交易量数据更新
                logger.info(
                    "批次交易完成，等待交易量数据更新",
                    user_id=user_id,
                    strategy_id=strategy.strategy_id,
                    delay_seconds=strategy.volume_check_delay_seconds,
                )

                # 等待指定时间，让交易量数据在服务器端更新
                for _ in range(strategy.volume_check_delay_seconds * 10):
                    if (
                        self._stop_flags.get(strategy.strategy_id, False)
                        or self._force_stop
                    ):
                        logger.info("收到停止信号，终止等待", user_id=user_id)
                        return
                    await asyncio.sleep(0.1)

                logger.info(
                    "等待完成，重新查询交易量",
                    user_id=user_id,
                    strategy_id=strategy.strategy_id,
                )

        except AuthenticationError as e:
            # 认证失败，记录并优雅退出
            logger.error(
                "🚨 用户认证失败，停止交易",
                user_id=user_id,
                strategy_id=strategy.strategy_id,
                error=str(e),
            )
            logger.error(
                "⚠️  请运行以下命令更新凭证：",
                command="uv run python scripts/update_user_credentials_quick.py",
            )

        except Exception as e:
            # 其他异常
            logger.error(
                "用户策略执行异常",
                user_id=user_id,
                strategy_id=strategy.strategy_id,
                error=str(e),
            )

        finally:
            # 清理 WebSocket 连接（仅在连接存在时）
            if user_id in self._ws_connectors or user_id in self._listen_key_managers:
                await self._cleanup_websocket_connection(user_id)

        logger.info(
            "✅ 用户策略完全完成",
            user_id=user_id,
            strategy_id=strategy.strategy_id,
        )

    async def _query_user_current_volume(
        self,
        user_id: int,
        token_symbol: str,
        headers: dict[str, str],
        cookies: str,
    ) -> Decimal:
        """查询用户当前代币交易量（三次请求确保数据一致性）

        Args:
            user_id: 用户ID
            token_symbol: 代币符号（如 KOGE）
            headers: 请求头
            cookies: Cookies

        Returns:
            当前真实交易量（已除以 mulPoint）
        """
        try:
            # 获取代币信息（优先使用缓存）
            token_info_entry = await self._get_token_info_with_cache(
                token_symbol, headers, cookies
            )

            if not token_info_entry:
                logger.error("无法获取代币信息", token=token_symbol)
                return Decimal("0")

            mul_point = int(token_info_entry.get("mulPoint", 1) or 1)

            # 发起三次请求确保数据一致性
            volumes = []

            for i in range(3):
                # 为每次请求创建独立的客户端，确保使用正确的用户认证信息
                user_client = await self._get_user_client(headers, cookies)
                try:
                    response = await user_client.get(
                        "/bapi/defi/v1/private/wallet-direct/buw/wallet/today/user-volume"
                    )

                    if response.status_code == 200:
                        volume_data = response.json().get("data", {})
                        volume_list = volume_data.get("tradeVolumeInfoList", [])

                        for token_vol in volume_list:
                            if token_vol.get("tokenName") == token_symbol:
                                displayed_volume = Decimal(
                                    str(token_vol.get("volume", 0))
                                )
                                real_volume = displayed_volume / Decimal(str(mul_point))
                                volumes.append(real_volume)
                                break
                        else:
                            # 未找到该代币，添加0
                            volumes.append(Decimal("0"))
                    else:
                        logger.warning(
                            "获取用户交易量失败",
                            attempt=i + 1,
                            status_code=response.status_code,
                            user_id=user_id,
                        )
                        volumes.append(Decimal("0"))

                except Exception as e:
                    logger.warning(
                        "查询用户交易量请求失败",
                        attempt=i + 1,
                        user_id=user_id,
                        token=token_symbol,
                        error=str(e),
                    )
                    volumes.append(Decimal("0"))
                finally:
                    # 确保关闭客户端
                    await user_client.aclose()

                # 如果不是最后一次请求，等待0.5秒
                if i < 2:
                    await asyncio.sleep(0.5)

            # 检查数据一致性
            if len(volumes) == 3:
                # 计算平均值
                avg_volume = sum(volumes) / Decimal("3")

                # 检查数据一致性（允许0.1%的误差）
                max_volume = max(volumes)
                min_volume = min(volumes)
                if max_volume > Decimal("0"):
                    consistency_ratio = (max_volume - min_volume) / max_volume
                    if consistency_ratio > Decimal("0.001"):  # 0.1%误差
                        logger.warning(
                            "交易量数据不一致",
                            user_id=user_id,
                            token=token_symbol,
                            volumes=[str(v) for v in volumes],
                            avg_volume=str(avg_volume),
                            consistency_ratio=f"{float(consistency_ratio) * 100:.2f}%",
                        )
                    else:
                        logger.info(
                            "交易量数据一致",
                            user_id=user_id,
                            token=token_symbol,
                            volumes=[str(v) for v in volumes],
                            avg_volume=str(avg_volume),
                        )
                else:
                    logger.info(
                        "交易量数据一致（均为0）",
                        user_id=user_id,
                        token=token_symbol,
                        volumes=[str(v) for v in volumes],
                    )

                # 返回平均值
                logger.info(
                    "查询到用户代币交易量（三次请求平均值）",
                    user_id=user_id,
                    token=token_symbol,
                    displayed_volume=str(avg_volume * Decimal(str(mul_point))),
                    mul_point=mul_point,
                    real_volume=str(avg_volume),
                )
                return avg_volume
            else:
                logger.error(
                    "交易量查询失败，无法获取有效数据",
                    user_id=user_id,
                    token=token_symbol,
                    successful_requests=len(volumes),
                )
                return Decimal("0")

        except Exception as e:
            logger.error(
                "查询用户交易量失败",
                user_id=user_id,
                token=token_symbol,
                error=str(e),
            )
            return Decimal("0")

    async def _calculate_loop_count(
        self,
        user_id: int,
        strategy: StrategyConfig,
        remaining_volume: Decimal,
        headers: dict[str, str],
        cookies: str,
    ) -> int:
        """计算所需循环次数

        根据剩余交易量和单次交易金额，以及 mulPoint 倍数计算循环次数

        Args:
            user_id: 用户ID
            strategy: 策略配置
            remaining_volume: 剩余交易量
            headers: 请求头
            cookies: Cookies

        Returns:
            所需循环次数
        """
        try:
            # 获取代币信息（优先使用缓存）
            token_info_entry = await self._get_token_info_with_cache(
                strategy.target_token, headers, cookies
            )

            if not token_info_entry:
                logger.error("无法获取代币信息", token=strategy.target_token)
                return 1

            mul_point = int(token_info_entry.get("mulPoint", 1) or 1)

            # 单次交易的真实交易量就是配置的金额
            # mulPoint 只影响显示，不影响实际交易量
            single_real_volume = strategy.single_trade_amount_usdt

            # 计算循环次数（向上取整）
            loop_count = math.ceil(float(remaining_volume / single_real_volume))

            logger.info(
                "计算循环次数",
                user_id=user_id,
                remaining_volume=str(remaining_volume),
                single_trade_amount=str(strategy.single_trade_amount_usdt),
                mul_point=mul_point,
                single_real_volume=str(single_real_volume),
                loop_count=loop_count,
            )

            return max(1, loop_count)  # 至少执行 1 次

        except Exception as e:
            logger.error(
                "计算循环次数失败",
                user_id=user_id,
                error=str(e),
            )
            return 1

    async def _execute_batch_trades(
        self,
        user_id: int,
        strategy: StrategyConfig,
        loop_count: int,
        headers: dict[str, str],
        cookies: str,
    ) -> None:
        """执行批次交易

        Args:
            user_id: 用户ID
            strategy: 策略配置
            loop_count: 循环次数
            headers: 请求头
            cookies: Cookies
        """
        for i in range(loop_count):
            # 检查停止标志
            if self._stop_flags.get(strategy.strategy_id, False) or self._force_stop:
                logger.info("收到停止信号，终止批次交易", user_id=user_id)
                break

            logger.info(
                "执行批次交易",
                user_id=user_id,
                strategy_id=strategy.strategy_id,
                current_loop=i + 1,
                total_loops=loop_count,
            )

            # 执行一次交易
            try:
                success, trade_volume = await self._execute_single_trade(
                    user_id=user_id,
                    strategy=strategy,
                    headers=headers,
                    cookies=cookies,
                )

                if success:
                    logger.info(
                        "批次交易成功",
                        user_id=user_id,
                        strategy_id=strategy.strategy_id,
                        loop=f"{i + 1}/{loop_count}",
                        trade_volume=str(trade_volume),
                    )

                else:
                    logger.warning(
                        "批次交易失败",
                        user_id=user_id,
                        loop=f"{i + 1}/{loop_count}",
                    )
                    # 失败后等待重试间隔
                    for _ in range(strategy.trade_interval_seconds * 20):
                        if (
                            self._stop_flags.get(strategy.strategy_id, False)
                            or self._force_stop
                        ):
                            return
                        await asyncio.sleep(0.1)
                    continue

            except AuthenticationError as auth_exc:
                logger.error(
                    "用户认证失败，停止该用户交易",
                    user_id=user_id,
                    strategy_id=strategy.strategy_id,
                    loop=f"{i + 1}/{loop_count}",
                    error=str(auth_exc),
                )
                # 认证失败，直接返回，停止该用户的交易
                return
            except Exception as exc:
                logger.error(
                    "批次交易执行异常",
                    user_id=user_id,
                    strategy_id=strategy.strategy_id,
                    loop=f"{i + 1}/{loop_count}",
                    error=str(exc),
                )
                # 异常后等待重试间隔
                for _ in range(strategy.trade_interval_seconds * 20):
                    if (
                        self._stop_flags.get(strategy.strategy_id, False)
                        or self._force_stop
                    ):
                        return
                    await asyncio.sleep(0.1)
                continue

            # 等待交易间隔（可中断）
            for _ in range(strategy.trade_interval_seconds * 10):
                if (
                    self._stop_flags.get(strategy.strategy_id, False)
                    or self._force_stop
                ):
                    break
                await asyncio.sleep(0.1)

    async def _execute_single_trade(
        self,
        user_id: int,
        strategy: StrategyConfig,
        headers: dict[str, str],
        cookies: str,
    ) -> tuple[bool, Decimal]:
        """执行单次交易

        Args:
            user_id: 用户ID
            strategy: 策略配置
            headers: 请求头
            cookies: Cookies

        Returns:
            (是否成功, 交易量)
        """
        symbol = f"{strategy.target_token}USDT"

        # 获取代币信息（优先使用本地缓存）
        token_info_entry = await self._get_token_info_with_cache(
            strategy.target_token, headers, cookies
        )

        if not token_info_entry:
            logger.error("无法获取代币信息", token=strategy.target_token)
            return False, Decimal("0")

        last_price = Decimal(str(token_info_entry.get("price", "0")))
        if not last_price or last_price == Decimal("0"):
            logger.error("无法获取代币价格", token=strategy.target_token)
            return False, Decimal("0")

        mul_point = int(token_info_entry.get("mulPoint", 1) or 1)
        logger.info(
            "代币信息",
            token=strategy.target_token,
            price=str(last_price),
            mul_point=mul_point,
            alpha_id=token_info_entry.get("alphaId"),
        )

        # 确保精度信息已缓存
        await self._ensure_token_precision_cached(
            token_info_entry.get("alphaId") or f"ALPHA_{strategy.target_token.upper()}",
            headers,
            cookies,
        )

        # 获取符号映射（注意：需要在精度缓存之后调用，因为需要从缓存读取精度信息）
        # LocalCache 使用单例模式，所有地方共享同一份内存数据，因此总是获取最新数据
        mapping = self.symbol_mapper.get_mapping(
            strategy.target_token, strategy.target_chain
        )

        # 计算买入/卖出价格
        # 买入价格 = 市场价格 × (1 + buy_offset_percentage / 100) - 溢价买入
        buy_offset_multiplier = Decimal("1") + (
            strategy.buy_offset_percentage / Decimal("100")
        )
        buy_value = (last_price * buy_offset_multiplier).quantize(
            Decimal("1e-8"), rounding=ROUND_DOWN
        )

        # 卖出价格 = 市场价格 × (1 - sell_profit_percentage / 100) - 低价卖出
        sell_discount_multiplier = Decimal("1") - (
            strategy.sell_profit_percentage / Decimal("100")
        )
        sell_value = (last_price * sell_discount_multiplier).quantize(
            Decimal("1e-8"), rounding=ROUND_DOWN
        )

        # 计算数量
        quantity = (strategy.single_trade_amount_usdt / buy_value).quantize(
            Decimal("1e-8"), rounding=ROUND_DOWN
        )

        # 计算实际金额
        effective_amount = (quantity * buy_value).quantize(
            Decimal("1e-8"), rounding=ROUND_DOWN
        )

        # 下单
        async with BinanceOTOOrderClient(headers, cookies) as oto_client:
            buy_price = Price(buy_value, precision=mapping.price_precision)
            sell_price = Price(sell_value, precision=mapping.price_precision)

            success, message, order_info = await oto_client.place_oto_order(
                symbol=symbol,
                quantity=quantity,
                buy_price=buy_price,
                sell_price=sell_price,
                chain=strategy.target_chain,
            )

            if success and order_info:
                # 统一转换为字符串，与 WebSocket 推送的 order_id 类型一致
                working_order_id = str(order_info.get("workingOrderId"))
                pending_order_id = str(order_info.get("pendingOrderId"))

                logger.info(
                    "OTO订单下单成功",
                    user_id=user_id,
                    strategy_id=strategy.strategy_id,
                    token=strategy.target_token,
                    quantity=str(quantity),
                    buy_price=str(buy_value),
                    sell_price=str(sell_value),
                    amount=str(effective_amount),
                    working_order_id=working_order_id,
                    pending_order_id=pending_order_id,
                )

                # 等待买单成交
                logger.info("等待买单成交", order_id=working_order_id)
                buy_filled = await self._wait_for_order_filled(
                    working_order_id, user_id, timeout=strategy.order_timeout_seconds
                )

                if not buy_filled:
                    logger.warning("买单未成交", order_id=working_order_id)
                    return False, Decimal("0")

                logger.info("买单已成交", order_id=working_order_id)

                # 等待卖单成交
                logger.info("等待卖单成交", order_id=pending_order_id)
                sell_filled = await self._wait_for_order_filled(
                    pending_order_id, user_id, timeout=strategy.order_timeout_seconds
                )

                if not sell_filled:
                    logger.warning("卖单未成交", order_id=pending_order_id)
                    # 买单已成交但卖单未成交，仍算部分成功
                    # 真实交易量就是实际下单金额
                    return True, effective_amount

                logger.info("卖单已成交", order_id=pending_order_id)

                # 真实交易量就是实际下单金额
                # mulPoint 只影响服务器显示的交易量，不影响我们实际交易了多少
                # 例如：实际交易200 USDT，服务器显示 200×4=800，但真实贡献仍是200
                logger.info(
                    "OTO订单完全成交",
                    working_order_id=working_order_id,
                    pending_order_id=pending_order_id,
                    amount=str(effective_amount),
                    mul_point=mul_point,
                    real_trade_volume=str(effective_amount),
                )

                return True, effective_amount
            else:
                # 检查是否是认证失败错误
                is_auth_error = self._is_authentication_error(message)

                if is_auth_error:
                    logger.error(
                        "认证失败：用户凭证已过期",
                        user_id=user_id,
                        strategy_id=strategy.strategy_id,
                        message=message,
                        action="自动阻止用户交易",
                    )
                    # 自动阻止用户，不再抛出异常
                    self.block_user(user_id, f"补充认证失败: {message}")
                    return False, Decimal("0")
                else:
                    logger.error(
                        "OTO订单下单失败",
                        user_id=user_id,
                        strategy_id=strategy.strategy_id,
                        message=message,
                    )
                    return False, Decimal("0")

    async def _fetch_last_price(
        self, token_list: list[dict[str, Any]], symbol_short: str
    ) -> Decimal | None:
        """从 aggTicker24 获取代币价格

        Args:
            token_list: 代币列表
            symbol_short: 代币符号（如 KOGE）

        Returns:
            当前价格
        """
        for entry in token_list:
            if str(entry.get("symbol", "")).upper() == symbol_short.upper():
                return Decimal(entry.get("price", "0"))
        return None

    async def _get_mul_point(
        self, token_list: list[dict[str, Any]], symbol_short: str
    ) -> int:
        """获取代币的交易量倍数 (mulPoint)

        对于某些代币（如 AOP），币安会将交易量放大显示。
        例如 mulPoint=4 表示显示的交易量是真实交易量的4倍。
        我们需要用显示交易量除以 mulPoint 得到真实交易量。

        Args:
            token_list: 代币列表
            symbol_short: 代币符号（如 AOP）

        Returns:
            交易量倍数，默认为 1
        """
        for entry in token_list:
            if str(entry.get("symbol", "")).upper() == symbol_short.upper():
                mul_point = entry.get("mulPoint", 1)
                return int(mul_point) if mul_point else 1

        # 未找到代币信息，默认返回 1（不放大）
        logger.warning("未找到代币mulPoint信息，使用默认值1", token=symbol_short)
        return 1

    async def _ensure_token_precision_cached(
        self, alpha_symbol: str, headers: dict[str, str], cookies: str
    ) -> None:
        """确保代币精度信息已缓存

        Args:
            alpha_symbol: Alpha符号（如 ALPHA_382）
            headers: 请求头
            cookies: Cookies
        """
        symbol_with_quote = f"{alpha_symbol}USDT"

        # 检查缓存是否存在
        cached_precision = self.cache.get_token_precision(symbol_with_quote)
        if cached_precision:
            logger.debug(
                "使用缓存的精度信息",
                symbol=symbol_with_quote,
                source="cache",
            )
            return

        # 缓存不存在，请求 API 获取
        logger.info("精度缓存未命中，请求 API 获取", symbol=symbol_with_quote)

        try:
            async with BinanceClient(headers=headers, cookies=cookies) as client:
                exchange_info = await client.get_exchange_info()
                symbols_list = exchange_info.get("symbols", [])

                # 查找目标交易对
                for symbol_data in symbols_list:
                    if symbol_data.get("symbol") == symbol_with_quote:
                        # 保存到缓存
                        self.cache.set_token_precision(symbol_with_quote, symbol_data)
                        logger.info(
                            "精度信息已缓存",
                            symbol=symbol_with_quote,
                            price_precision=symbol_data.get("pricePrecision"),
                            quantity_precision=symbol_data.get("quantityPrecision"),
                            source="api",
                        )
                        return

                logger.warning(
                    "API 返回的交易对列表中未找到目标", symbol=symbol_with_quote
                )

        except Exception as e:
            logger.error(
                "获取精度信息失败",
                symbol=symbol_with_quote,
                error=str(e),
            )

    async def _get_token_info_with_cache(
        self, symbol_short: str, headers: dict[str, str], cookies: str
    ) -> dict[str, Any] | None:
        """获取代币信息（优先使用缓存）

        逻辑：
        1. 先尝试从本地缓存读取
        2. 如果缓存不存在或已过期，则请求 API
        3. 将 API 数据保存到缓存
        4. 返回代币信息

        Args:
            symbol_short: 代币符号（如 AOP）
            headers: 请求头
            cookies: Cookies

        Returns:
            代币信息字典，如果获取失败返回 None
        """
        symbol_upper = symbol_short.upper()

        # 1. 尝试从缓存读取
        cached_data = self.cache.get_token_info(symbol_upper)
        if cached_data:
            logger.info(
                "使用缓存的代币信息",
                token=symbol_short,
                alpha_id=cached_data.get("alphaId"),
                source="cache",
            )
            return cached_data

        # 2. 缓存不存在，请求 API
        logger.info("缓存未命中，请求 API 获取代币信息", token=symbol_short)

        try:
            # 使用独立客户端获取代币信息
            user_client = await self._get_user_client(headers, cookies)
            try:
                response = await user_client.get(
                    "/bapi/defi/v1/public/alpha-trade/aggTicker24?dataType=aggregate"
                )

                if response.status_code != 200:
                    logger.error(
                        "获取代币信息失败",
                        status_code=response.status_code,
                        token=symbol_short,
                    )
                    return None

                token_list = response.json().get("data", [])

                # 3. 在列表中查找目标代币
                for entry in token_list:
                    # 检查多个可能的字段来匹配代币
                    symbol_match = str(entry.get("symbol", "")).upper() == symbol_upper
                    token_name_match = (
                        str(entry.get("tokenName", "")).upper() == symbol_upper
                    )
                    alpha_id_match = (
                        str(entry.get("alphaId", "")).upper() == symbol_upper
                    )

                    if symbol_match or token_name_match or alpha_id_match:
                        # 4. 保存到缓存（使用原始简称作为key）
                        self.cache.set_token_info(symbol_upper, entry)
                        logger.info(
                            "代币信息已缓存",
                            token=symbol_short,
                            alpha_id=entry.get("alphaId"),
                            symbol=entry.get("symbol"),
                            source="api",
                        )
                        return entry

                logger.warning("API 返回的代币列表中未找到目标代币", token=symbol_short)
                return None
            finally:
                # 确保关闭客户端
                await user_client.aclose()

        except Exception as e:
            logger.error(
                "获取代币信息失败",
                token=symbol_short,
                error=str(e),
            )
            return None

    async def _get_user_credentials(
        self, user_id: int
    ) -> tuple[dict[str, str], str] | None:
        """获取用户凭证

        Args:
            user_id: 用户ID

        Returns:
            (headers, cookies) 或 None
        """
        async for session in get_db():
            user_repo = UserRepositoryImpl(session)
            user = await user_repo.get_by_id(user_id)
            if not user or not user.has_credentials():
                return None
            try:
                # 确保 headers 是字符串类型（处理可能的 bytes）
                headers_str = user.headers
                if isinstance(headers_str, bytes):
                    headers_str = headers_str.decode("utf-8")
                elif not isinstance(headers_str, str):
                    headers_str = str(headers_str)

                # 解析 JSON 格式的 headers
                headers = json.loads(headers_str)

                # 确保 headers 是字典类型
                if not isinstance(headers, dict):
                    logger.error(
                        "headers 解析后不是字典类型",
                        user_id=user_id,
                        parsed_type=type(headers).__name__,
                    )
                    headers = {}

            except Exception as e:
                logger.error(
                    "headers 解析失败",
                    user_id=user_id,
                    error=str(e),
                    headers_type=type(user.headers).__name__,
                )
                headers = {}

            # 处理 cookies（可能是 JSON 格式的字典，也可能是标准 cookie 字符串）
            cookies = user.cookies or ""
            if cookies:
                # 确保 cookies 是字符串类型
                if isinstance(cookies, bytes):
                    cookies = cookies.decode("utf-8")
                elif not isinstance(cookies, str):
                    cookies = str(cookies)

                # 如果 cookies 是 JSON 格式，转换为标准 cookie 字符串
                if cookies.strip().startswith("{"):
                    try:
                        cookies_dict = json.loads(cookies)
                        if isinstance(cookies_dict, dict):
                            # 转换为 "key1=value1; key2=value2" 格式
                            cookies = "; ".join(
                                f"{k}={v}" for k, v in cookies_dict.items()
                            )
                            logger.info(
                                "已将 JSON 格式的 cookies 转换为标准格式",
                                user_id=user_id,
                                cookies_count=len(cookies_dict),
                            )
                    except Exception as e:
                        logger.warning(
                            "cookies JSON 解析失败，使用原始字符串",
                            user_id=user_id,
                            error=str(e),
                        )

            return headers, cookies
        return None

    def get_strategy_status(self, strategy_id: str) -> dict[str, Any] | None:
        """获取策略状态

        Args:
            strategy_id: 策略ID

        Returns:
            策略状态信息
        """
        strategy = self.config_manager.get_strategy(strategy_id)
        if not strategy:
            return None

        is_running = strategy_id in self._running_tasks
        user_volumes = {}
        for user_id in strategy.user_ids:
            if (
                user_id in self._user_volumes
                and strategy_id in self._user_volumes[user_id]
            ):
                user_volumes[user_id] = str(self._user_volumes[user_id][strategy_id])

        total_volume = sum(
            self._user_volumes.get(uid, {}).get(strategy_id, Decimal("0"))
            for uid in strategy.user_ids
        )

        # 检查被阻止的用户
        blocked_users = [uid for uid in strategy.user_ids if uid in self._blocked_users]
        active_users = [
            uid for uid in strategy.user_ids if uid not in self._blocked_users
        ]

        return {
            "strategy_id": strategy_id,
            "strategy_name": strategy.strategy_name,
            "is_running": is_running,
            "enabled": strategy.enabled,
            "target_volume": str(strategy.target_volume),
            "total_volume": str(total_volume),
            "progress_percentage": float(total_volume / strategy.target_volume * 100)
            if strategy.target_volume > 0
            else 0,
            "user_volumes": user_volumes,
            "user_count": len(strategy.user_ids),
            "active_users": active_users,
            "blocked_users": blocked_users,
            "blocked_count": len(blocked_users),
        }

    def get_all_strategy_status(self) -> list[dict[str, Any]]:
        """获取所有策略状态"""
        return [
            self.get_strategy_status(s.strategy_id)
            for s in self.config_manager.get_all_strategies()
        ]

    async def _ensure_websocket_connection(
        self, user_id: int, headers: dict[str, str], cookies: str
    ) -> bool:
        """确保用户的 WebSocket 连接已建立

        Args:
            user_id: 用户ID
            headers: 请求头
            cookies: Cookies

        Returns:
            是否成功建立连接
        """
        # 如果已有连接且正常，直接返回
        if user_id in self._ws_connectors:
            if self._ws_connectors[user_id].is_connected():
                logger.debug("WebSocket连接已存在且正常", user_id=user_id)
                return True
            else:
                # 连接已断开，清理旧连接
                logger.debug("WebSocket连接已断开，清理旧连接", user_id=user_id)
                await self._cleanup_websocket_connection(user_id)

        try:
            # 创建 ListenKey 管理器
            listen_key_manager = ListenKeyManager(headers, cookies)
            success, message, listen_key = await listen_key_manager.get_listen_key()

            if not success or not listen_key:
                logger.error("获取ListenKey失败", user_id=user_id, message=message)
                return False

            # 创建 WebSocket 连接器
            connector = OrderWebSocketConnector(
                user_id=user_id,
                listen_key=listen_key,
                on_order_update=self._handle_order_update,
                on_connection_event=self._handle_connection_event,
            )

            # 启动连接（在后台任务中运行）
            asyncio.create_task(connector.start())

            # 等待连接建立
            await asyncio.sleep(2)

            if not connector.is_connected():
                logger.warning("WebSocket连接未建立", user_id=user_id)
                return False

            # 保存连接
            self._ws_connectors[user_id] = connector
            self._listen_key_managers[user_id] = listen_key_manager

            logger.info("WebSocket连接已建立", user_id=user_id)
            return True

        except Exception as e:
            logger.error("建立WebSocket连接异常", user_id=user_id, error=str(e))
            return False

    async def _cleanup_websocket_connection(self, user_id: int) -> None:
        """清理用户的 WebSocket 连接

        Args:
            user_id: 用户ID
        """
        # 防止重复清理
        if (
            user_id not in self._ws_connectors
            and user_id not in self._listen_key_managers
        ):
            return

        logger.debug("开始清理WebSocket连接", user_id=user_id)

        if user_id in self._ws_connectors:
            try:
                connector = self._ws_connectors[user_id]
                # 检查连接状态，如果已经断开则直接清理
                if not connector.is_connected():
                    logger.debug("WebSocket连接已断开，直接清理", user_id=user_id)
                else:
                    # 添加超时机制，防止WebSocket停止阻塞
                    await asyncio.wait_for(connector.stop(), timeout=3.0)
                    logger.debug("WebSocket连接已正常停止", user_id=user_id)
            except TimeoutError:
                logger.warning("WebSocket停止超时，强制清理", user_id=user_id)
            except (ConnectionResetError, AttributeError) as e:
                logger.warning("WebSocket连接重置，强制清理", user_id=user_id, error=str(e))
            except Exception as e:
                logger.warning("停止WebSocket连接异常", user_id=user_id, error=str(e))
            finally:
                del self._ws_connectors[user_id]

        if user_id in self._listen_key_managers:
            try:
                # 添加超时机制，防止ListenKey管理器关闭阻塞
                await asyncio.wait_for(
                    self._listen_key_managers[user_id].close(), timeout=2.0
                )
                logger.debug("ListenKey管理器已正常关闭", user_id=user_id)
            except TimeoutError:
                logger.warning("ListenKey管理器关闭超时，强制清理", user_id=user_id)
            except Exception as e:
                logger.warning("关闭ListenKey管理器异常", user_id=user_id, error=str(e))
            finally:
                del self._listen_key_managers[user_id]

        logger.debug("WebSocket连接清理完成", user_id=user_id)

    async def _cleanup_all_websocket_connections(self) -> None:
        """清理所有WebSocket连接"""
        logger.info("清理所有WebSocket连接", count=len(self._ws_connectors))

        # 并行清理所有WebSocket连接
        cleanup_tasks = []
        for user_id in list(self._ws_connectors.keys()):
            cleanup_tasks.append(self._cleanup_websocket_connection(user_id))

        if cleanup_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*cleanup_tasks, return_exceptions=True), timeout=3.0
                )
            except TimeoutError:
                logger.warning("WebSocket清理超时，强制清理")
            except Exception as e:
                logger.error("清理WebSocket连接异常", error=str(e))

    async def _handle_order_update(self, order_data: dict[str, Any]) -> None:
        """处理订单更新（WebSocket 回调）

        Args:
            order_data: 订单数据
        """
        order_id = order_data.get("order_id")
        user_id = order_data.get("user_id")
        if not order_id or not user_id:
            return

        # 使用 user_id:order_id 作为键，避免不同用户的订单状态混合
        order_key = f"{user_id}:{order_id}"

        # 更新订单状态
        self._order_status[order_key] = order_data

        logger.info(
            "订单状态更新",
            order_id=order_id,
            status=order_data.get("status"),
            side=order_data.get("side"),
            executed_quantity=order_data.get("executed_quantity"),
        )

        # 如果订单完全成交或取消，触发事件
        status = order_data.get("status")
        if status in ["FILLED", "CANCELED", "REJECTED", "EXPIRED"]:
            if order_key in self._order_events:
                self._order_events[order_key].set()

    async def _handle_connection_event(
        self, event_type: str, data: dict[str, Any]
    ) -> None:
        """处理 WebSocket 连接事件

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        logger.info("WebSocket连接事件", event_type=event_type, data=data)

    async def _wait_for_order_filled(
        self, order_id: str, user_id: int, timeout: int = 300
    ) -> bool:
        """等待订单完全成交

        Args:
            order_id: 订单ID（字符串）
            user_id: 用户ID
            timeout: 超时时间（秒）

        Returns:
            是否成交
        """
        # 使用 user_id:order_id 作为键，避免不同用户的订单状态混合
        order_key = f"{user_id}:{order_id}"

        # 先检查订单是否已经成交（避免时序问题）
        order_status = self._order_status.get(order_key, {})
        status = order_status.get("status")

        if status == "FILLED":
            logger.info(
                "订单已成交（检查时已完成）", order_id=order_id, user_id=user_id
            )
            return True
        elif status in ["CANCELED", "REJECTED", "EXPIRED"]:
            logger.warning(
                "订单未成交（检查时已终止）",
                order_id=order_id,
                user_id=user_id,
                status=status,
            )
            return False

        # 创建事件
        if order_key not in self._order_events:
            self._order_events[order_key] = asyncio.Event()

        try:
            # 等待订单完成（带超时）
            await asyncio.wait_for(
                self._order_events[order_key].wait(), timeout=timeout
            )

            # 检查订单状态
            order_status = self._order_status.get(order_key, {})
            status = order_status.get("status")

            if status == "FILLED":
                logger.info("订单已成交", order_id=order_id, user_id=user_id)
                return True
            else:
                logger.warning(
                    "订单未成交", order_id=order_id, user_id=user_id, status=status
                )
                return False

        except TimeoutError:
            logger.warning(
                "订单等待超时", order_id=order_id, user_id=user_id, timeout=timeout
            )
            return False
        finally:
            # 清理事件
            if order_key in self._order_events:
                del self._order_events[order_key]

    def _is_authentication_error(self, error_message: str | None) -> bool:
        """检测是否是认证失败错误

        Args:
            error_message: 错误消息

        Returns:
            是否是认证失败
        """
        if not error_message:
            return False

        # 常见的认证失败错误消息
        auth_error_keywords = [
            "补充认证失败",
            "您必须完成此认证才能进入下一步",
            "authentication failed",
            "unauthorized",
            "invalid credentials",
            "token expired",
            "session expired",
        ]

        error_message_lower = error_message.lower()
        return any(
            keyword.lower() in error_message_lower for keyword in auth_error_keywords
        )

    def block_user(self, user_id: int, reason: str = "补充认证失败") -> None:
        """阻止用户继续交易

        Args:
            user_id: 用户ID
            reason: 阻止原因
        """
        self._blocked_users.add(user_id)
        logger.warning(
            "用户已被阻止",
            user_id=user_id,
            reason=reason,
        )

    def unblock_user(self, user_id: int) -> None:
        """解除用户阻止状态

        Args:
            user_id: 用户ID
        """
        if user_id in self._blocked_users:
            self._blocked_users.remove(user_id)
            logger.info(
                "用户阻止状态已解除",
                user_id=user_id,
            )

    def get_blocked_users(self) -> set[int]:
        """获取被阻止的用户列表

        Returns:
            被阻止的用户ID集合
        """
        return self._blocked_users.copy()
