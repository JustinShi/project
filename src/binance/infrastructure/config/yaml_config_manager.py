"""YAML配置管理器"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

from binance.config.constants import PriceOffsetMode


@dataclass
class TradingTarget:
    """交易目标配置"""
    token_symbol_short: str
    chain: Optional[str]
    target_volume: Decimal
    current_volume: Decimal
    volume_multiplier: Decimal
    price_offset_mode: PriceOffsetMode
    buy_offset_value: Decimal
    sell_offset_value: Decimal
    order_quantity: Decimal
    timeout_seconds: int
    price_volatility_threshold: Decimal
    is_trading_active: bool


@dataclass
class UserConfig:
    """用户配置"""
    user_id: int
    trading_targets: List[TradingTarget]


@dataclass
class GlobalSettings:
    """全局设置"""
    default_price_offset_mode: PriceOffsetMode
    default_buy_offset_value: Decimal
    default_sell_offset_value: Decimal
    default_order_quantity: Decimal
    default_timeout_seconds: int
    default_price_volatility_threshold: Decimal
    max_concurrent_orders: int
    order_retry_attempts: int
    retry_delay_seconds: int


class YAMLConfigManager:
    """YAML配置管理器"""
    
    def __init__(self, config_path: str = "config/trading_config.yaml"):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self._config_cache: Optional[Dict[str, Any]] = None
        self._last_modified: Optional[float] = None
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        # 检查文件是否被修改
        current_modified = self.config_path.stat().st_mtime
        if (self._config_cache is None or 
            self._last_modified is None or 
            current_modified > self._last_modified):
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config_cache = yaml.safe_load(f)
            self._last_modified = current_modified
        
        return self._config_cache
    
    def get_user_config(self, user_id: int) -> Optional[UserConfig]:
        """获取用户配置
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户配置，不存在则返回None
        """
        config = self._load_config()
        users = config.get('users', [])
        
        for user_data in users:
            if user_data.get('user_id') == user_id:
                trading_targets = []
                for target_data in user_data.get('trading_targets', []):
                    target = TradingTarget(
                        token_symbol_short=target_data['token_symbol_short'],
                        chain=target_data.get('chain'),
                        target_volume=Decimal(str(target_data['target_volume'])),
                        current_volume=Decimal(str(target_data['current_volume'])),
                        volume_multiplier=Decimal(str(target_data['volume_multiplier'])),
                        price_offset_mode=PriceOffsetMode(target_data['price_offset_mode']),
                        buy_offset_value=Decimal(str(target_data['buy_offset_value'])),
                        sell_offset_value=Decimal(str(target_data['sell_offset_value'])),
                        order_quantity=Decimal(str(target_data['order_quantity'])),
                        timeout_seconds=target_data['timeout_seconds'],
                        price_volatility_threshold=Decimal(str(target_data['price_volatility_threshold'])),
                        is_trading_active=target_data['is_trading_active']
                    )
                    trading_targets.append(target)
                
                return UserConfig(
                    user_id=user_data['user_id'],
                    trading_targets=trading_targets
                )
        
        return None
    
    def get_trading_target(self, user_id: int, token_symbol_short: str) -> Optional[TradingTarget]:
        """获取特定代币的交易目标
        
        Args:
            user_id: 用户ID
            token_symbol_short: 代币简称
            
        Returns:
            交易目标配置，不存在则返回None
        """
        user_config = self.get_user_config(user_id)
        if not user_config:
            return None
        
        for target in user_config.trading_targets:
            if target.token_symbol_short == token_symbol_short:
                return target
        
        return None
    
    def get_global_settings(self) -> GlobalSettings:
        """获取全局设置
        
        Returns:
            全局设置
        """
        config = self._load_config()
        global_data = config.get('global_settings', {})
        
        return GlobalSettings(
            default_price_offset_mode=PriceOffsetMode(global_data.get('default_price_offset_mode', 'PERCENTAGE')),
            default_buy_offset_value=Decimal(str(global_data.get('default_buy_offset_value', 0.5))),
            default_sell_offset_value=Decimal(str(global_data.get('default_sell_offset_value', 0.5))),
            default_order_quantity=Decimal(str(global_data.get('default_order_quantity', 10.0))),
            default_timeout_seconds=global_data.get('default_timeout_seconds', 1800),
            default_price_volatility_threshold=Decimal(str(global_data.get('default_price_volatility_threshold', 5.0))),
            max_concurrent_orders=global_data.get('max_concurrent_orders', 5),
            order_retry_attempts=global_data.get('order_retry_attempts', 3),
            retry_delay_seconds=global_data.get('retry_delay_seconds', 30)
        )
    
    def update_current_volume(self, user_id: int, token_symbol_short: str, new_volume: Decimal) -> bool:
        """更新当前交易量
        
        Args:
            user_id: 用户ID
            token_symbol_short: 代币简称
            new_volume: 新的当前交易量
            
        Returns:
            是否更新成功
        """
        try:
            config = self._load_config()
            users = config.get('users', [])
            
            for user_data in users:
                if user_data.get('user_id') == user_id:
                    for target_data in user_data.get('trading_targets', []):
                        if target_data['token_symbol_short'] == token_symbol_short:
                            target_data['current_volume'] = float(new_volume)
                            
                            # 保存配置文件
                            with open(self.config_path, 'w', encoding='utf-8') as f:
                                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                            
                            # 清除缓存
                            self._config_cache = None
                            self._last_modified = None
                            
                            return True
            
            return False
            
        except Exception:
            return False
    
    def get_all_users(self) -> List[UserConfig]:
        """获取所有用户配置
        
        Returns:
            所有用户配置列表
        """
        config = self._load_config()
        users = config.get('users', [])
        
        result = []
        for user_data in users:
            trading_targets = []
            for target_data in user_data.get('trading_targets', []):
                target = TradingTarget(
                    token_symbol_short=target_data['token_symbol_short'],
                    chain=target_data.get('chain'),
                    target_volume=Decimal(str(target_data['target_volume'])),
                    current_volume=Decimal(str(target_data['current_volume'])),
                    volume_multiplier=Decimal(str(target_data['volume_multiplier'])),
                    price_offset_mode=PriceOffsetMode(target_data['price_offset_mode']),
                    buy_offset_value=Decimal(str(target_data['buy_offset_value'])),
                    sell_offset_value=Decimal(str(target_data['sell_offset_value'])),
                    order_quantity=Decimal(str(target_data['order_quantity'])),
                    timeout_seconds=target_data['timeout_seconds'],
                    price_volatility_threshold=Decimal(str(target_data['price_volatility_threshold'])),
                    is_trading_active=target_data['is_trading_active']
                )
                trading_targets.append(target)
            
            user_config = UserConfig(
                user_id=user_data['user_id'],
                trading_targets=trading_targets
            )
            result.append(user_config)
        
        return result
