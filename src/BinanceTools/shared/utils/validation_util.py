"""
验证工具

数据验证相关的工具函数。
"""

import re
from typing import Any, List, Optional, Union
from decimal import Decimal


class ValidationUtil:
    """验证工具类"""
    
    @staticmethod
    def is_valid_symbol(symbol: str) -> bool:
        """验证交易对格式"""
        if not symbol or not isinstance(symbol, str):
            return False
        
        # 基本格式检查
        if len(symbol) < 3:
            return False
        
        # 检查是否包含特殊字符
        if not re.match(r'^[A-Z0-9_]+$', symbol):
            return False
        
        return True
    
    @staticmethod
    def is_valid_quantity(quantity: Union[str, int, float, Decimal]) -> bool:
        """验证数量"""
        try:
            qty = Decimal(str(quantity))
            return qty > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_price(price: Union[str, int, float, Decimal]) -> bool:
        """验证价格"""
        try:
            p = Decimal(str(price))
            return p > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_user_id(user_id: str) -> bool:
        """验证用户ID"""
        if not user_id or not isinstance(user_id, str):
            return False
        
        # 检查长度
        if len(user_id) < 1 or len(user_id) > 50:
            return False
        
        # 检查字符
        if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
            return False
        
        return True
    
    @staticmethod
    def is_valid_order_id(order_id: Union[str, int]) -> bool:
        """验证订单ID"""
        try:
            oid = int(order_id)
            return oid > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_trade_id(trade_id: Union[str, int]) -> bool:
        """验证交易ID"""
        try:
            tid = int(trade_id)
            return tid > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_alpha_id(alpha_id: str) -> bool:
        """验证Alpha ID"""
        if not alpha_id or not isinstance(alpha_id, str):
            return False
        
        # 检查格式: ALPHA_数字
        if not re.match(r'^ALPHA_\d+$', alpha_id):
            return False
        
        return True
    
    @staticmethod
    def is_valid_contract_address(address: str) -> bool:
        """验证合约地址"""
        if not address or not isinstance(address, str):
            return False
        
        # 检查以太坊地址格式
        if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return False
        
        return True
    
    @staticmethod
    def is_valid_chain_id(chain_id: Union[str, int]) -> bool:
        """验证链ID"""
        try:
            cid = int(chain_id)
            return cid > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_side(side: str) -> bool:
        """验证订单方向"""
        return side in ["BUY", "SELL"]
    
    @staticmethod
    def is_valid_order_type(order_type: str) -> bool:
        """验证订单类型"""
        return order_type in ["LIMIT", "MARKET"]
    
    @staticmethod
    def is_valid_time_in_force(time_in_force: str) -> bool:
        """验证订单有效期"""
        return time_in_force in ["GTC", "IOC", "FOK"]
    
    @staticmethod
    def is_valid_order_status(status: str) -> bool:
        """验证订单状态"""
        return status in ["NEW", "PENDING", "PARTIALLY_FILLED", "FILLED", "CANCELED", "REJECTED"]
    
    @staticmethod
    def is_valid_currency(currency: str) -> bool:
        """验证货币类型"""
        if not currency or not isinstance(currency, str):
            return False
        
        # 检查长度
        if len(currency) < 1 or len(currency) > 10:
            return False
        
        # 检查字符
        if not re.match(r'^[A-Z0-9]+$', currency):
            return False
        
        return True
    
    @staticmethod
    def is_valid_decimal(value: Union[str, int, float, Decimal], precision: int = 8) -> bool:
        """验证小数精度"""
        try:
            decimal_value = Decimal(str(value))
            
            # 检查小数位数
            if decimal_value.as_tuple().exponent < -precision:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_percentage(percentage: Union[str, int, float, Decimal]) -> bool:
        """验证百分比"""
        try:
            pct = Decimal(str(percentage))
            return -100 <= pct <= 100
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_positive_number(value: Union[str, int, float, Decimal]) -> bool:
        """验证正数"""
        try:
            num = Decimal(str(value))
            return num > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_non_negative_number(value: Union[str, int, float, Decimal]) -> bool:
        """验证非负数"""
        try:
            num = Decimal(str(value))
            return num >= 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_range(value: Union[str, int, float, Decimal], min_val: Union[str, int, float, Decimal], max_val: Union[str, int, float, Decimal]) -> bool:
        """验证数值范围"""
        try:
            val = Decimal(str(value))
            min_value = Decimal(str(min_val))
            max_value = Decimal(str(max_val))
            
            return min_value <= val <= max_value
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_list(value: Any, min_length: int = 0, max_length: Optional[int] = None) -> bool:
        """验证列表"""
        if not isinstance(value, list):
            return False
        
        if len(value) < min_length:
            return False
        
        if max_length is not None and len(value) > max_length:
            return False
        
        return True
    
    @staticmethod
    def is_valid_dict(value: Any, required_keys: Optional[List[str]] = None) -> bool:
        """验证字典"""
        if not isinstance(value, dict):
            return False
        
        if required_keys:
            for key in required_keys:
                if key not in value:
                    return False
        
        return True
