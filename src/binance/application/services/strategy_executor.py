"""交易策略执行器"""

from __future__ import annotations

import asyncio
import json
import math
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Any

from binance.infrastructure.config.strategy_config_manager import (
    StrategyConfigManager,
    StrategyConfig,
    GlobalSettings,
)
from binance.infrastructure.database.session import get_db
from binance.infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from binance.infrastructure.binance_client.http_client import BinanceClient
from binance.infrastructure.binance_client.oto_order_client import BinanceOTOOrderClient
from binance.infrastructure.binance_client.order_websocket import OrderWebSocketConnector
from binance.infrastructure.binance_client.listen_key_manager import ListenKeyManager
from binance.infrastructure.config import SymbolMapper
from binance.domain.value_objects.price import Price
from binance.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class AuthenticationError(Exception):
    """认证失败异常"""
    pass


class StrategyExecutor:
    """交易策略执行器"""
    
    def __init__(self, config_path: str = "config/trading_config.yaml"):
        self.config_manager = StrategyConfigManager(config_path)
        self.symbol_mapper = SymbolMapper()
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._user_volumes: Dict[int, Dict[str, Decimal]] = {}  # {user_id: {strategy_id: volume}}
        self._stop_flags: Dict[str, bool] = {}
        
        # 订单状态追踪
        self._order_status: Dict[str, Dict[str, Any]] = {}  # {order_id: {status, side, quantity, etc}}
        self._order_events: Dict[str, asyncio.Event] = {}  # {order_id: Event}
        
        # WebSocket 连接管理
        self._ws_connectors: Dict[int, OrderWebSocketConnector] = {}  # {user_id: connector}
        self._listen_key_managers: Dict[int, ListenKeyManager] = {}  # {user_id: manager}
    
    async def start_all_strategies(self) -> None:
        """启动所有启用的策略"""
        strategies = self.config_manager.get_enabled_strategies()
        logger.info("启动交易策略", count=len(strategies))
        
        tasks = []
        for strategy in strategies:
            task = asyncio.create_task(self._run_strategy(strategy))
            self._running_tasks[strategy.strategy_id] = task
            tasks.append(task)
        
        # 等待所有策略完成
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
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
        self._stop_flags[strategy_id] = True
        task = self._running_tasks.get(strategy_id)
        if task:
            await task
            del self._running_tasks[strategy_id]
        logger.info("策略已停止", strategy_id=strategy_id)
    
    async def stop_all_strategies(self) -> None:
        """停止所有策略"""
        logger.info("停止所有策略", count=len(self._running_tasks))
        for strategy_id in list(self._running_tasks.keys()):
            await self.stop_strategy(strategy_id)
    
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
        
        logger.info("策略执行完成", strategy_id=strategy.strategy_id)
    
    async def _run_user_strategy(
        self, 
        user_id: int, 
        strategy: StrategyConfig
    ) -> None:
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
        ws_connected = await self._ensure_websocket_connection(user_id, headers, cookies)
        if not ws_connected:
            logger.error("WebSocket连接失败", user_id=user_id)
            return
        
        try:
            # 循环批次执行，直至达标
            while not self._stop_flags.get(strategy.strategy_id, False):
                # 查询当前交易量
                current_volume = await self._query_user_current_volume(
                    user_id, strategy.target_token, headers, cookies
                )
                
                # 检查是否达标
                if current_volume >= strategy.target_volume:
                    logger.info(
                        "用户已达成目标交易量",
                        user_id=user_id,
                        strategy_id=strategy.strategy_id,
                        current_volume=str(current_volume),
                        target_volume=str(strategy.target_volume),
                    )
                    break
                
                # 计算剩余交易量和循环次数
                remaining_volume = strategy.target_volume - current_volume
                loop_count = await self._calculate_loop_count(
                    user_id, strategy, remaining_volume, headers, cookies
                )
                
                logger.info(
                    "开始批次交易",
                    user_id=user_id,
                    strategy_id=strategy.strategy_id,
                    current_volume=str(current_volume),
                    remaining_volume=str(remaining_volume),
                    planned_loops=loop_count,
                )
                
                # 执行 N 次交易
                early_stop = await self._execute_batch_trades(
                    user_id, strategy, loop_count, headers, cookies
                )
                
                # 如果批次中提前达标，直接退出
                if early_stop:
                    logger.info(
                        "批次中已达标，终止策略",
                        user_id=user_id,
                        strategy_id=strategy.strategy_id,
                    )
                    break
                
                # 批次完成，重新查询（循环回到开头）
                logger.info(
                    "批次交易完成，重新查询交易量",
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
            
        finally:
            # 清理 WebSocket 连接
            await self._cleanup_websocket_connection(user_id)
        
        logger.info(
            "用户策略完成",
            user_id=user_id,
            strategy_id=strategy.strategy_id,
        )
    
    async def _query_user_current_volume(
        self,
        user_id: int,
        token_symbol: str,
        headers: Dict[str, str],
        cookies: str,
    ) -> Decimal:
        """查询用户当前代币交易量
        
        Args:
            user_id: 用户ID
            token_symbol: 代币符号（如 KOGE）
            headers: 请求头
            cookies: Cookies
            
        Returns:
            当前真实交易量（已除以 mulPoint）
        """
        try:
            async with BinanceClient(headers=headers, cookies=cookies) as client:
                volume_data = await client.get_user_volume()
                token_info = await client.get_token_info()
                
                # 从 tradeVolumeInfoList 中查找目标代币
                volume_list = volume_data.get("tradeVolumeInfoList", [])
                for token_vol in volume_list:
                    if token_vol.get("tokenName") == token_symbol:
                        displayed_volume = Decimal(str(token_vol.get("volume", 0)))
                        
                        # 获取 mulPoint 并计算真实交易量
                        mul_point = await self._get_mul_point(token_info, token_symbol)
                        real_volume = displayed_volume / Decimal(str(mul_point))
                        
                        logger.info(
                            "查询到用户代币交易量",
                            user_id=user_id,
                            token=token_symbol,
                            displayed_volume=str(displayed_volume),
                            mul_point=mul_point,
                            real_volume=str(real_volume),
                        )
                        return real_volume
                
                # 未找到该代币的交易量，返回 0
                logger.info(
                    "用户暂无此代币交易量",
                    user_id=user_id,
                    token=token_symbol,
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
        headers: Dict[str, str],
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
            # 获取代币的 mulPoint
            async with BinanceClient(headers=headers, cookies=cookies) as client:
                token_info = await client.get_token_info()
                mul_point = await self._get_mul_point(token_info, strategy.target_token)
            
            # 单次交易的真实交易量 = single_trade_amount_usdt / mulPoint
            single_real_volume = strategy.single_trade_amount_usdt / Decimal(str(mul_point))
            
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
        headers: Dict[str, str],
        cookies: str,
    ) -> bool:
        """执行批次交易
        
        Args:
            user_id: 用户ID
            strategy: 策略配置
            loop_count: 循环次数
            headers: 请求头
            cookies: Cookies
            
        Returns:
            是否提前达标（True=达标提前终止，False=正常完成批次）
        """
        for i in range(loop_count):
            # 检查停止标志
            if self._stop_flags.get(strategy.strategy_id, False):
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
                    
                    # 每笔交易成功后，检查是否已达标
                    current_volume = await self._query_user_current_volume(
                        user_id, strategy.target_token, headers, cookies
                    )
                    
                    if current_volume >= strategy.target_volume:
                        logger.info(
                            "批次交易中达成目标，提前终止",
                            user_id=user_id,
                            strategy_id=strategy.strategy_id,
                            current_volume=str(current_volume),
                            target_volume=str(strategy.target_volume),
                            completed_loops=i + 1,
                            total_loops=loop_count,
                        )
                        return True  # 提前达标
                    
                else:
                    logger.warning(
                        "批次交易失败",
                        user_id=user_id,
                        loop=f"{i + 1}/{loop_count}",
                    )
                    # 失败后等待重试间隔
                    for _ in range(strategy.trade_interval_seconds * 20):
                        if self._stop_flags.get(strategy.strategy_id, False):
                            return False
                        await asyncio.sleep(0.1)
                    continue
                
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
                    if self._stop_flags.get(strategy.strategy_id, False):
                        return False
                    await asyncio.sleep(0.1)
                continue
            
            # 等待交易间隔（可中断）
            for _ in range(strategy.trade_interval_seconds * 10):
                if self._stop_flags.get(strategy.strategy_id, False):
                    break
                await asyncio.sleep(0.1)
        
        return False  # 批次正常完成，未提前达标
    
    async def _execute_single_trade(
        self,
        user_id: int,
        strategy: StrategyConfig,
        headers: Dict[str, str],
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
        
        # 获取当前价格和代币信息
        async with BinanceClient(headers=headers, cookies=cookies) as client:
            token_info = await client.get_token_info()
            last_price = await self._fetch_last_price(token_info, strategy.target_token)
            if not last_price:
                logger.error("无法获取代币价格", token=strategy.target_token)
                return False, Decimal("0")
            
            # 获取 mulPoint（交易量倍数）
            mul_point = await self._get_mul_point(token_info, strategy.target_token)
            logger.info(
                "代币交易量倍数",
                token=strategy.target_token,
                mul_point=mul_point,
            )
        
        # 获取符号映射
        mapping = self.symbol_mapper.get_mapping(
            strategy.target_token, 
            strategy.target_chain
        )
        
        # 计算买入/卖出价格
        # 买入价格 = 市场价格 × (1 + buy_offset_percentage / 100) - 溢价买入
        buy_offset_multiplier = Decimal("1") + (strategy.buy_offset_percentage / Decimal("100"))
        buy_value = (last_price * buy_offset_multiplier).quantize(
            Decimal("1e-8"), rounding=ROUND_DOWN
        )
        
        # 卖出价格 = 买入价格 × (1 - sell_profit_percentage / 100) - 低价卖出
        sell_discount_multiplier = Decimal("1") - (strategy.sell_profit_percentage / Decimal("100"))
        sell_value = (buy_value * sell_discount_multiplier).quantize(
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
                    working_order_id,
                    timeout=strategy.order_timeout_seconds
                )
                
                if not buy_filled:
                    logger.warning("买单未成交", order_id=working_order_id)
                    return False, Decimal("0")
                
                logger.info("买单已成交", order_id=working_order_id)
                
                # 等待卖单成交
                logger.info("等待卖单成交", order_id=pending_order_id)
                sell_filled = await self._wait_for_order_filled(
                    pending_order_id,
                    timeout=strategy.order_timeout_seconds
                )
                
                if not sell_filled:
                    logger.warning("卖单未成交", order_id=pending_order_id)
                    # 买单已成交但卖单未成交，仍算部分成功
                    # 计算真实交易量（考虑 mulPoint）
                    real_trade_volume = effective_amount / Decimal(str(mul_point))
                    return True, real_trade_volume
                
                logger.info("卖单已成交", order_id=pending_order_id)
                
                # 计算真实交易量（考虑 mulPoint）
                # 对于 mulPoint=4 的代币，实际交易量 = 名义交易量 / 4
                real_trade_volume = effective_amount / Decimal(str(mul_point))
                
                logger.info(
                    "OTO订单完全成交",
                    working_order_id=working_order_id,
                    pending_order_id=pending_order_id,
                    amount=str(effective_amount),
                    mul_point=mul_point,
                    real_trade_volume=str(real_trade_volume),
                )
                
                return True, real_trade_volume
            else:
                # 检查是否是认证失败错误
                is_auth_error = self._is_authentication_error(message)
                
                if is_auth_error:
                    logger.error(
                        "认证失败：用户凭证已过期",
                        user_id=user_id,
                        strategy_id=strategy.strategy_id,
                        message=message,
                        action="停止当前用户交易，请更新凭证",
                    )
                    # 抛出特殊异常，让上层捕获并优雅处理
                    raise AuthenticationError(f"用户 {user_id} 认证失败，需要更新凭证")
                else:
                    logger.error(
                        "OTO订单下单失败",
                        user_id=user_id,
                        strategy_id=strategy.strategy_id,
                        message=message,
                    )
                    return False, Decimal("0")
    
    async def _fetch_last_price(
        self, 
        token_list: List[Dict[str, Any]], 
        symbol_short: str
    ) -> Optional[Decimal]:
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
        self, 
        token_list: List[Dict[str, Any]], 
        symbol_short: str
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
    
    async def _get_user_credentials(
        self, 
        user_id: int
    ) -> Optional[tuple[Dict[str, str], str]]:
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
                headers = json.loads(user.headers)
            except Exception:
                headers = {}
            return headers, user.cookies
        return None
    
    def get_strategy_status(self, strategy_id: str) -> Optional[Dict[str, Any]]:
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
            if user_id in self._user_volumes and strategy_id in self._user_volumes[user_id]:
                user_volumes[user_id] = str(self._user_volumes[user_id][strategy_id])
        
        total_volume = sum(
            self._user_volumes.get(uid, {}).get(strategy_id, Decimal("0"))
            for uid in strategy.user_ids
        )
        
        return {
            "strategy_id": strategy_id,
            "strategy_name": strategy.strategy_name,
            "is_running": is_running,
            "enabled": strategy.enabled,
            "target_volume": str(strategy.target_volume),
            "total_volume": str(total_volume),
            "progress_percentage": float(total_volume / strategy.target_volume * 100) if strategy.target_volume > 0 else 0,
            "user_volumes": user_volumes,
            "user_count": len(strategy.user_ids),
        }
    
    def get_all_strategy_status(self) -> List[Dict[str, Any]]:
        """获取所有策略状态"""
        return [
            self.get_strategy_status(s.strategy_id)
            for s in self.config_manager.get_all_strategies()
        ]
    
    async def _ensure_websocket_connection(
        self, 
        user_id: int, 
        headers: Dict[str, str], 
        cookies: str
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
                return True
            else:
                # 连接已断开，清理旧连接
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
        if user_id in self._ws_connectors:
            try:
                await self._ws_connectors[user_id].stop()
            except Exception as e:
                logger.warning("停止WebSocket连接异常", user_id=user_id, error=str(e))
            del self._ws_connectors[user_id]
        
        if user_id in self._listen_key_managers:
            try:
                await self._listen_key_managers[user_id].close()
            except Exception as e:
                logger.warning("关闭ListenKey管理器异常", user_id=user_id, error=str(e))
            del self._listen_key_managers[user_id]
    
    async def _handle_order_update(self, order_data: Dict[str, Any]) -> None:
        """处理订单更新（WebSocket 回调）
        
        Args:
            order_data: 订单数据
        """
        order_id = order_data.get("order_id")
        if not order_id:
            return
        
        # 确保 order_id 是字符串
        order_id = str(order_id)
        
        # 更新订单状态
        self._order_status[order_id] = order_data
        
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
            if order_id in self._order_events:
                self._order_events[order_id].set()
    
    async def _handle_connection_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """处理 WebSocket 连接事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
        """
        logger.info("WebSocket连接事件", event_type=event_type, data=data)
    
    async def _wait_for_order_filled(
        self, 
        order_id: str, 
        timeout: int = 300
    ) -> bool:
        """等待订单完全成交
        
        Args:
            order_id: 订单ID（字符串）
            timeout: 超时时间（秒）
            
        Returns:
            是否成交
        """
        # 确保 order_id 是字符串
        order_id = str(order_id)
        
        # 创建事件
        if order_id not in self._order_events:
            self._order_events[order_id] = asyncio.Event()
        
        try:
            # 等待订单完成（带超时）
            await asyncio.wait_for(
                self._order_events[order_id].wait(),
                timeout=timeout
            )
            
            # 检查订单状态
            order_status = self._order_status.get(order_id, {})
            status = order_status.get("status")
            
            if status == "FILLED":
                logger.info("订单已成交", order_id=order_id)
                return True
            else:
                logger.warning("订单未成交", order_id=order_id, status=status)
                return False
                
        except asyncio.TimeoutError:
            logger.warning("订单等待超时", order_id=order_id, timeout=timeout)
            return False
        finally:
            # 清理事件
            if order_id in self._order_events:
                del self._order_events[order_id]
    
    def _is_authentication_error(self, error_message: Optional[str]) -> bool:
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
        return any(keyword.lower() in error_message_lower for keyword in auth_error_keywords)


