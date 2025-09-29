"""
JSON 序列化/反序列化工具
提供统一的 JSON 处理接口
"""

import decimal
import json
from datetime import date, datetime
from typing import Any, Dict, Optional

from loguru import logger


class JsonUtil:
    """JSON 工具类"""

    @staticmethod
    def dumps(obj: Any, **kwargs) -> str:
        """序列化对象为 JSON 字符串"""
        try:
            return json.dumps(obj, cls=JsonUtil._CustomEncoder, **kwargs)
        except Exception as e:
            logger.error(f"JSON 序列化失败: {e}")
            raise

    @staticmethod
    def loads(s: str, **kwargs) -> Any:
        """反序列化 JSON 字符串为对象"""
        try:
            return json.loads(s, **kwargs)
        except Exception as e:
            logger.error(f"JSON 反序列化失败: {e}")
            raise

    @staticmethod
    def safe_dumps(obj: Any, default: str = "{}", **kwargs) -> str:
        """
        安全序列化，失败时返回默认值

        Args:
            obj: 要序列化的对象
            default: 失败时的默认返回值
            **kwargs: 其他参数

        Returns:
            JSON 字符串或默认值
        """
        try:
            return JsonUtil.dumps(obj, **kwargs)
        except Exception as e:
            logger.warning(f"JSON 安全序列化失败: {e}")
            return default

    @staticmethod
    def safe_loads(s: str, default: Any = None, **kwargs) -> Any:
        """
        安全反序列化，失败时返回默认值

        Args:
            s: JSON 字符串
            default: 失败时的默认返回值
            **kwargs: 其他参数

        Returns:
            反序列化后的对象或默认值
        """
        try:
            return JsonUtil.loads(s, **kwargs)
        except Exception as e:
            logger.warning(f"JSON 安全反序列化失败: {e}")
            return default

    @staticmethod
    def is_valid_json(s: str) -> bool:
        """
        检查字符串是否为有效的 JSON

        Args:
            s: 要检查的字符串

        Returns:
            是否为有效的 JSON
        """
        try:
            json.loads(s)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    @staticmethod
    def format_json(obj: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
        """
        格式化 JSON 字符串

        Args:
            obj: 要格式化的对象
            indent: 缩进空格数
            ensure_ascii: 是否确保 ASCII 编码

        Returns:
            格式化后的 JSON 字符串
        """
        return JsonUtil.dumps(
            obj, indent=indent, ensure_ascii=ensure_ascii, sort_keys=True
        )

    @staticmethod
    def minify_json(s: str) -> str:
        """
        压缩 JSON 字符串

        Args:
            s: JSON 字符串

        Returns:
            压缩后的 JSON 字符串
        """
        try:
            obj = json.loads(s)
            return json.dumps(obj, separators=(",", ":"))
        except Exception as e:
            logger.error(f"JSON 压缩失败: {e}")
            return s

    @staticmethod
    def merge_json(*json_strings: str) -> str:
        """
        合并多个 JSON 字符串

        Args:
            *json_strings: JSON 字符串列表

        Returns:
            合并后的 JSON 字符串
        """
        result = {}

        for json_str in json_strings:
            try:
                obj = json.loads(json_str)
                if isinstance(obj, dict):
                    result.update(obj)
            except Exception as e:
                logger.warning(f"合并 JSON 时跳过无效字符串: {e}")

        return JsonUtil.dumps(result)

    @staticmethod
    def extract_json_from_string(s: str) -> Optional[str]:
        """
        从字符串中提取 JSON 部分

        Args:
            s: 包含 JSON 的字符串

        Returns:
            提取的 JSON 字符串或 None
        """
        try:
            # 查找第一个 { 或 [
            start_idx = -1
            for i, char in enumerate(s):
                if char in "{[":
                    start_idx = i
                    break

            if start_idx == -1:
                return None

            # 从后往前查找匹配的 } 或 ]
            bracket_count = 0
            end_idx = -1
            open_bracket = s[start_idx]
            close_bracket = "}" if open_bracket == "{" else "]"

            for i in range(start_idx, len(s)):
                if s[i] == open_bracket:
                    bracket_count += 1
                elif s[i] == close_bracket:
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_idx = i
                        break

            if end_idx == -1:
                return None

            json_str = s[start_idx : end_idx + 1]

            # 验证是否为有效 JSON
            if JsonUtil.is_valid_json(json_str):
                return json_str

            return None

        except Exception as e:
            logger.error(f"提取 JSON 失败: {e}")
            return None

    class _CustomEncoder(json.JSONEncoder):
        """自定义 JSON 编码器"""

        def default(self, obj: Any) -> Any:
            """处理特殊类型的编码"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            elif isinstance(obj, decimal.Decimal):
                return float(obj)
            elif hasattr(obj, "__dict__"):
                return obj.__dict__
            else:
                return super().default(obj)

    @staticmethod
    def to_dict(obj: Any) -> Dict[str, Any]:
        """
        将对象转换为字典

        Args:
            obj: 要转换的对象

        Returns:
            字典表示
        """
        try:
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            elif isinstance(obj, (list, tuple)):
                return [JsonUtil.to_dict(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: JsonUtil.to_dict(value) for key, value in obj.items()}
            else:
                return obj
        except Exception as e:
            logger.error(f"对象转字典失败: {e}")
            return {}

    @staticmethod
    def from_dict(data: Dict[str, Any], target_class: type) -> Any:
        """
        从字典创建对象

        Args:
            data: 字典数据
            target_class: 目标类

        Returns:
            创建的对象
        """
        try:
            if hasattr(target_class, "__init__"):
                # 尝试使用字典参数创建对象
                return target_class(**data)
            else:
                # 创建空对象并设置属性
                obj = target_class()
                for key, value in data.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                return obj
        except Exception as e:
            logger.error(f"字典转对象失败: {e}")
            return None

    @staticmethod
    def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """
        深度合并两个字典

        Args:
            dict1: 第一个字典
            dict2: 第二个字典

        Returns:
            合并后的字典
        """
        result = dict1.copy()

        for key, value in dict2.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = JsonUtil.deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    @staticmethod
    def flatten_dict(data: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
        """
        扁平化字典

        Args:
            data: 要扁平化的字典
            separator: 键分隔符

        Returns:
            扁平化后的字典
        """
        result = {}

        def _flatten(obj: Any, prefix: str = ""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}{separator}{key}" if prefix else key
                    _flatten(value, new_key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_key = f"{prefix}{separator}{i}" if prefix else str(i)
                    _flatten(item, new_key)
            else:
                result[prefix] = obj

        _flatten(data)
        return result

    @staticmethod
    def unflatten_dict(data: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
        """
        反扁平化字典

        Args:
            data: 要反扁平化的字典
            separator: 键分隔符

        Returns:
            反扁平化后的字典
        """
        result = {}

        for key, value in data.items():
            keys = key.split(separator)
            current = result

            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]

            current[keys[-1]] = value

        return result
