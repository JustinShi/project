"""交易策略配置管理器"""

from __future__ import annotations

import yaml
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Optional, Dict, Any, List


@dataclass
class GlobalSettings:
    """全局设置"""
    default_buy_offset_percentage: Decimal
    default_sell_profit_percentage: Decimal
    default_trade_interval_seconds: int
    default_single_trade_amount_usdt: Decimal
    max_concurrent_users: int
    max_price_volatility_percentage: Decimal
    max_retry_attempts: int
    retry_delay_seconds: int
    order_timeout_seconds: int
    websocket_reconnect_delay_seconds: int


@dataclass
class StrategyConfig:
    """策略配置"""
    strategy_id: str
    strategy_name: str
    enabled: bool
    target_token: str
    target_chain: str
    target_volume: Decimal
    single_trade_amount_usdt: Decimal
    trade_interval_seconds: int
    buy_offset_percentage: Decimal
    sell_profit_percentage: Decimal
    user_ids: List[int]
    price_volatility_threshold: Optional[Decimal] = None
    max_retry_attempts: Optional[int] = None


@dataclass
class UserStrategyOverride:
    """用户策略覆盖配置"""
    user_id: int
    strategy_overrides: Dict[str, Dict[str, Any]]


class StrategyConfigManager:
    """交易策略配置管理器"""
    
    def __init__(self, config_path: str = "config/trading_config.yaml"):
        self.config_path = Path(config_path)
        self._config: Optional[Dict[str, Any]] = None
        self._global_settings: Optional[GlobalSettings] = None
        self._strategies: Dict[str, StrategyConfig] = {}
        self._user_overrides: Dict[int, UserStrategyOverride] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)
        
        self._parse_global_settings()
        self._parse_strategies()
        self._parse_user_overrides()
    
    def _parse_global_settings(self) -> None:
        """解析全局设置"""
        settings = self._config.get("global_settings", {})
        self._global_settings = GlobalSettings(
            default_buy_offset_percentage=Decimal(str(settings.get("default_buy_offset_percentage", 0.5))),
            default_sell_profit_percentage=Decimal(str(settings.get("default_sell_profit_percentage", 1.0))),
            default_trade_interval_seconds=int(settings.get("default_trade_interval_seconds", 1)),
            default_single_trade_amount_usdt=Decimal(str(settings.get("default_single_trade_amount_usdt", 30))),
            max_concurrent_users=int(settings.get("max_concurrent_users", 10)),
            max_price_volatility_percentage=Decimal(str(settings.get("max_price_volatility_percentage", 5.0))),
            max_retry_attempts=int(settings.get("max_retry_attempts", 3)),
            retry_delay_seconds=int(settings.get("retry_delay_seconds", 5)),
            order_timeout_seconds=int(settings.get("order_timeout_seconds", 300)),
            websocket_reconnect_delay_seconds=int(settings.get("websocket_reconnect_delay_seconds", 3)),
        )
    
    def _parse_strategies(self) -> None:
        """解析策略配置"""
        strategies = self._config.get("strategies", [])
        for strategy in strategies:
            strategy_config = StrategyConfig(
                strategy_id=strategy.get("strategy_id"),
                strategy_name=strategy.get("strategy_name"),
                enabled=strategy.get("enabled", False),
                target_token=strategy.get("target_token"),
                target_chain=strategy.get("target_chain"),
                target_volume=Decimal(str(strategy.get("target_volume", 0))),
                single_trade_amount_usdt=Decimal(str(strategy.get("single_trade_amount_usdt", 30))),
                trade_interval_seconds=int(strategy.get("trade_interval_seconds", 1)),
                buy_offset_percentage=Decimal(str(strategy.get("buy_offset_percentage", 0.5))),
                sell_profit_percentage=Decimal(str(strategy.get("sell_profit_percentage", 1.0))),
                user_ids=strategy.get("user_ids", []),
                price_volatility_threshold=Decimal(str(strategy.get("price_volatility_threshold"))) 
                    if strategy.get("price_volatility_threshold") else None,
                max_retry_attempts=strategy.get("max_retry_attempts"),
            )
            self._strategies[strategy_config.strategy_id] = strategy_config
    
    def _parse_user_overrides(self) -> None:
        """解析用户覆盖配置"""
        overrides = self._config.get("user_overrides", [])
        for override in overrides:
            user_id = override.get("user_id")
            strategy_overrides = override.get("strategies", {})
            self._user_overrides[user_id] = UserStrategyOverride(
                user_id=user_id,
                strategy_overrides=strategy_overrides,
            )
    
    def get_global_settings(self) -> GlobalSettings:
        """获取全局设置"""
        return self._global_settings
    
    def get_strategy(self, strategy_id: str) -> Optional[StrategyConfig]:
        """获取策略配置"""
        return self._strategies.get(strategy_id)
    
    def get_all_strategies(self) -> List[StrategyConfig]:
        """获取所有策略配置"""
        return list(self._strategies.values())
    
    def get_enabled_strategies(self) -> List[StrategyConfig]:
        """获取所有启用的策略"""
        return [s for s in self._strategies.values() if s.enabled]
    
    def get_user_strategy_config(
        self, 
        user_id: int, 
        strategy_id: str
    ) -> Optional[StrategyConfig]:
        """获取用户的策略配置（应用用户覆盖）
        
        Args:
            user_id: 用户ID
            strategy_id: 策略ID
            
        Returns:
            应用了用户覆盖后的策略配置
        """
        # 获取基础策略配置
        base_strategy = self.get_strategy(strategy_id)
        if not base_strategy:
            return None
        
        # 检查用户是否在策略的用户列表中
        if user_id not in base_strategy.user_ids:
            return None
        
        # 应用用户覆盖
        user_override = self._user_overrides.get(user_id)
        if not user_override:
            return base_strategy
        
        strategy_override = user_override.strategy_overrides.get(strategy_id)
        if not strategy_override:
            return base_strategy
        
        # 创建新的策略配置，应用覆盖
        return StrategyConfig(
            strategy_id=base_strategy.strategy_id,
            strategy_name=base_strategy.strategy_name,
            enabled=strategy_override.get("enabled", base_strategy.enabled),
            target_token=strategy_override.get("target_token", base_strategy.target_token),
            target_chain=strategy_override.get("target_chain", base_strategy.target_chain),
            target_volume=Decimal(str(strategy_override.get("target_volume", base_strategy.target_volume))),
            single_trade_amount_usdt=Decimal(str(strategy_override.get(
                "single_trade_amount_usdt", 
                base_strategy.single_trade_amount_usdt
            ))),
            trade_interval_seconds=int(strategy_override.get(
                "trade_interval_seconds", 
                base_strategy.trade_interval_seconds
            )),
            buy_offset_percentage=Decimal(str(strategy_override.get(
                "buy_offset_percentage", 
                base_strategy.buy_offset_percentage
            ))),
            sell_profit_percentage=Decimal(str(strategy_override.get(
                "sell_profit_percentage", 
                base_strategy.sell_profit_percentage
            ))),
            user_ids=base_strategy.user_ids,
            price_volatility_threshold=Decimal(str(strategy_override.get(
                "price_volatility_threshold"
            ))) if strategy_override.get("price_volatility_threshold") 
                else base_strategy.price_volatility_threshold,
            max_retry_attempts=strategy_override.get(
                "max_retry_attempts", 
                base_strategy.max_retry_attempts
            ),
        )
    
    def get_user_strategies(self, user_id: int) -> List[StrategyConfig]:
        """获取用户的所有策略配置（应用覆盖）
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户参与的所有策略配置列表
        """
        strategies = []
        for strategy in self.get_enabled_strategies():
            if user_id in strategy.user_ids:
                user_strategy = self.get_user_strategy_config(user_id, strategy.strategy_id)
                if user_strategy and user_strategy.enabled:
                    strategies.append(user_strategy)
        return strategies
    
    def reload(self) -> None:
        """重新加载配置文件"""
        self._strategies.clear()
        self._user_overrides.clear()
        self._load_config()


