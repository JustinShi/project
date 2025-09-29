"""
Redis客户端封装工具
提供Redis操作的便捷接口
"""

import json
from typing import Any, Dict, List, Optional

import redis

from ..config import config
from ..logging import get_logger


logger = get_logger(__name__)


class RedisClient:
    """Redis客户端封装类"""

    def __init__(self):
        self.client = None
        # 延迟初始化，不在构造函数中连接

    def _init_client(self):
        """初始化Redis客户端"""
        if self.client is not None:
            return

        try:
            # 创建Redis连接
            self.client = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                password=config.redis_password,
                db=config.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )

            # 测试连接
            self.client.ping()
            logger.info(f"Redis连接成功: {config.redis_host}:{config.redis_port}")

        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise

    def get_client(self) -> redis.Redis:
        """获取Redis客户端实例"""
        self._init_client()
        return self.client

    # 基础操作
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置键值

        Args:
            key: 键名
            value: 值
            ttl: 过期时间（秒）

        Returns:
            是否成功
        """
        try:
            client = self.get_client()

            # 序列化值
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif not isinstance(value, (str, int, float, bool)):
                value = str(value)

            if ttl:
                return client.setex(key, ttl, value)
            else:
                return client.set(key, value)

        except Exception as e:
            logger.error(f"设置键值失败: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """
        获取键值

        Args:
            key: 键名

        Returns:
            值或None
        """
        try:
            client = self.get_client()
            value = client.get(key)

            if value is None:
                return None

            # 尝试解析JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        except Exception as e:
            logger.error(f"获取键值失败: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """
        删除键

        Args:
            key: 键名

        Returns:
            是否成功
        """
        try:
            client = self.get_client()
            result = client.delete(key)
            return result > 0

        except Exception as e:
            logger.error(f"删除键失败: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        检查键是否存在

        Args:
            key: 键名

        Returns:
            是否存在
        """
        try:
            client = self.get_client()
            return client.exists(key) > 0

        except Exception as e:
            logger.error(f"检查键存在性失败: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """
        设置键过期时间

        Args:
            key: 键名
            ttl: 过期时间（秒）

        Returns:
            是否成功
        """
        try:
            client = self.get_client()
            return client.expire(key, ttl)

        except Exception as e:
            logger.error(f"设置过期时间失败: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """
        获取键剩余过期时间

        Args:
            key: 键名

        Returns:
            剩余时间（秒），-1表示永不过期，-2表示键不存在
        """
        try:
            client = self.get_client()
            return client.ttl(key)

        except Exception as e:
            logger.error(f"获取过期时间失败: {e}")
            return -2

    # 哈希操作
    async def hset(self, key: str, field: str, value: Any) -> bool:
        """
        设置哈希字段

        Args:
            key: 哈希键名
            field: 字段名
            value: 字段值

        Returns:
            是否成功
        """
        try:
            client = self.get_client()

            # 序列化值
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif not isinstance(value, (str, int, float, bool)):
                value = str(value)

            return client.hset(key, field, value)

        except Exception as e:
            logger.error(f"设置哈希字段失败: {e}")
            return False

    async def hget(self, key: str, field: str) -> Optional[Any]:
        """
        获取哈希字段

        Args:
            key: 哈希键名
            field: 字段名

        Returns:
            字段值或None
        """
        try:
            client = self.get_client()
            value = client.hget(key, field)

            if value is None:
                return None

            # 尝试解析JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        except Exception as e:
            logger.error(f"获取哈希字段失败: {e}")
            return None

    async def hgetall(self, key: str) -> Dict[str, Any]:
        """
        获取所有哈希字段

        Args:
            key: 哈希键名

        Returns:
            字段字典
        """
        try:
            client = self.get_client()
            return client.hgetall(key)

        except Exception as e:
            logger.error(f"获取所有哈希字段失败: {e}")
            return {}

    async def hdel(self, key: str, field: str) -> bool:
        """
        删除哈希字段

        Args:
            key: 哈希键名
            field: 字段名

        Returns:
            是否成功
        """
        try:
            client = self.get_client()
            result = client.hdel(key, field)
            return result > 0

        except Exception as e:
            logger.error(f"删除哈希字段失败: {e}")
            return False

    # 列表操作
    async def lpush(self, key: str, *values: Any) -> int:
        """
        从左侧推入列表

        Args:
            key: 列表键名
            *values: 要推入的值

        Returns:
            推入后的列表长度
        """
        try:
            client = self.get_client()

            # 序列化值
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value))
                elif not isinstance(value, (str, int, float, bool)):
                    serialized_values.append(str(value))
                else:
                    serialized_values.append(value)

            return client.lpush(key, *serialized_values)

        except Exception as e:
            logger.error(f"推入列表失败: {e}")
            return 0

    async def rpush(self, key: str, *values: Any) -> int:
        """
        从右侧推入列表

        Args:
            key: 列表键名
            *values: 要推入的值

        Returns:
            推入后的列表长度
        """
        try:
            client = self.get_client()

            # 序列化值
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value))
                elif not isinstance(value, (str, int, float, bool)):
                    serialized_values.append(str(value))
                else:
                    serialized_values.append(value)

            return client.rpush(key, *serialized_values)

        except Exception as e:
            logger.error(f"推入列表失败: {e}")
            return 0

    async def lpop(self, key: str) -> Optional[Any]:
        """
        从左侧弹出列表元素

        Args:
            key: 列表键名

        Returns:
            弹出的元素或None
        """
        try:
            client = self.get_client()
            value = client.lpop(key)

            if value is None:
                return None

            # 尝试解析JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        except Exception as e:
            logger.error(f"弹出列表元素失败: {e}")
            return None

    async def rpop(self, key: str) -> Optional[Any]:
        """
        从右侧弹出列表元素

        Args:
            key: 列表键名

        Returns:
            弹出的元素或None
        """
        try:
            client = self.get_client()
            value = client.rpop(key)

            if value is None:
                return None

            # 尝试解析JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        except Exception as e:
            logger.error(f"弹出列表元素失败: {e}")
            return None

    async def lrange(self, key: str, start: int, end: int) -> List[Any]:
        """
        获取列表范围

        Args:
            key: 列表键名
            start: 开始索引
            end: 结束索引

        Returns:
            列表元素列表
        """
        try:
            client = self.get_client()
            values = client.lrange(key, start, end)

            # 尝试解析JSON
            result = []
            for value in values:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(value)

            return result

        except Exception as e:
            logger.error(f"获取列表范围失败: {e}")
            return []

    # 集合操作
    async def sadd(self, key: str, *values: Any) -> int:
        """
        添加集合元素

        Args:
            key: 集合键名
            *values: 要添加的值

        Returns:
            添加的元素数量
        """
        try:
            client = self.get_client()

            # 序列化值
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value))
                elif not isinstance(value, (str, int, float, bool)):
                    serialized_values.append(str(value))
                else:
                    serialized_values.append(value)

            return client.sadd(key, *serialized_values)

        except Exception as e:
            logger.error(f"添加集合元素失败: {e}")
            return 0

    async def smembers(self, key: str) -> set:
        """
        获取集合所有成员

        Args:
            key: 集合键名

        Returns:
            成员集合
        """
        try:
            client = self.get_client()
            return client.smembers(key)

        except Exception as e:
            logger.error(f"获取集合成员失败: {e}")
            return set()

    async def srem(self, key: str, *values: Any) -> int:
        """
        删除集合元素

        Args:
            key: 集合键名
            *values: 要删除的值

        Returns:
            删除的元素数量
        """
        try:
            client = self.get_client()

            # 序列化值
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value))
                elif not isinstance(value, (str, int, float, bool)):
                    serialized_values.append(str(value))
                else:
                    serialized_values.append(value)

            return client.srem(key, *serialized_values)

        except Exception as e:
            logger.error(f"删除集合元素失败: {e}")
            return 0

    # 有序集合操作
    async def zadd(self, key: str, mapping: Dict[Any, float]) -> int:
        """
        添加有序集合元素

        Args:
            key: 有序集合键名
            mapping: 元素和分数的映射

        Returns:
            添加的元素数量
        """
        try:
            client = self.get_client()

            # 序列化键
            serialized_mapping = {}
            for member, score in mapping.items():
                if isinstance(member, (dict, list)):
                    member = json.dumps(member)
                elif not isinstance(member, (str, int, float, bool)):
                    member = str(member)
                serialized_mapping[member] = score

            return client.zadd(key, serialized_mapping)

        except Exception as e:
            logger.error(f"添加有序集合元素失败: {e}")
            return 0

    async def zrange(
        self, key: str, start: int, end: int, withscores: bool = False
    ) -> List[Any]:
        """
        获取有序集合范围

        Args:
            key: 有序集合键名
            start: 开始索引
            end: 结束索引
            withscores: 是否包含分数

        Returns:
            元素列表
        """
        try:
            client = self.get_client()
            result = client.zrange(key, start, end, withscores=withscores)

            if withscores:
                # 返回 (元素, 分数) 元组列表
                return [
                    (
                        json.loads(item)
                        if item.startswith("{") or item.startswith("[")
                        else item,
                        score,
                    )
                    for item, score in result
                ]
            else:
                # 返回元素列表
                return [
                    json.loads(item)
                    if item.startswith("{") or item.startswith("[")
                    else item
                    for item in result
                ]

        except Exception as e:
            logger.error(f"获取有序集合范围失败: {e}")
            return []

    # 其他操作
    async def keys(self, pattern: str = "*") -> List[str]:
        """
        获取匹配模式的键列表

        Args:
            pattern: 匹配模式

        Returns:
            键列表
        """
        try:
            client = self.get_client()
            return client.keys(pattern)

        except Exception as e:
            logger.error(f"获取键列表失败: {e}")
            return []

    async def flushdb(self) -> bool:
        """
        清空当前数据库

        Returns:
            是否成功
        """
        try:
            client = self.get_client()
            client.flushdb()
            return True

        except Exception as e:
            logger.error(f"清空数据库失败: {e}")
            return False

    async def ping(self) -> bool:
        """
        测试连接

        Returns:
            是否连接正常
        """
        try:
            client = self.get_client()
            return client.ping()

        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False

    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            logger.info("Redis连接已关闭")

    def __del__(self):
        """析构函数"""
        self.close()


# 全局Redis客户端实例
redis_client = RedisClient()


def get_redis_client() -> RedisClient:
    """获取Redis客户端实例"""
    return redis_client
