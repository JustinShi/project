"""
JSON工具

JSON相关的工具函数。
"""

import json
from typing import Any, Dict, List, Optional
from decimal import Decimal
from datetime import datetime


class JsonUtil:
    """JSON工具类"""
    
    @staticmethod
    def to_json(data: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
        """转换为JSON字符串"""
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, default=JsonUtil._json_serializer)
    
    @staticmethod
    def from_json(json_str: str) -> Any:
        """从JSON字符串解析"""
        return json.loads(json_str, parse_float=Decimal)
    
    @staticmethod
    def to_dict(obj: Any) -> Dict[str, Any]:
        """转换为字典"""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return obj
    
    @staticmethod
    def from_dict(data: Dict[str, Any], cls: type) -> Any:
        """从字典创建对象"""
        if hasattr(cls, 'from_dict'):
            return cls.from_dict(data)
        else:
            return cls(**data)
    
    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """JSON序列化器"""
        if isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    @staticmethod
    def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """安全获取字典值"""
        return data.get(key, default)
    
    @staticmethod
    def safe_get_nested(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
        """安全获取嵌套字典值"""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    
    @staticmethod
    def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
        """合并字典"""
        result = {}
        for d in dicts:
            result.update(d)
        return result
    
    @staticmethod
    def filter_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
        """过滤字典，只保留指定的键"""
        return {k: v for k, v in data.items() if k in keys}
    
    @staticmethod
    def remove_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
        """移除值为None的项"""
        return {k: v for k, v in data.items() if v is not None}
