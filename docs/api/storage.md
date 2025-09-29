# 💾 存储模块 API 参考

本文档介绍存储模块的 API 接口和使用方法，包括 Redis、数据库、缓存等组件。

## 📋 模块概述

存储模块 (`common/storage/`) 提供数据存储、缓存、持久化等核心功能。

### 主要功能

- **Redis 客户端**: 高性能内存数据库客户端
- **数据库管理**: MySQL/PostgreSQL 数据库连接和操作
- **缓存管理**: 多级缓存策略和接口
- **数据持久化**: 数据备份和恢复

## 🏗️ 模块结构

```
common/storage/
├── __init__.py
├── redis_client.py      # Redis 客户端
├── db_client.py         # 数据库客户端
└── cache.py             # 缓存管理
```

## 🔧 核心组件

### RedisClient

Redis 客户端，提供高性能的内存数据存储和缓存功能。

```python
from common.storage.redis_client import RedisClient

# 创建 Redis 客户端
redis_client = RedisClient()

# 基本操作
redis_client.set("key", "value", expire=3600)
value = redis_client.get("key")
redis_client.delete("key")

# 哈希操作
redis_client.hset("hash_key", "field", "value")
value = redis_client.hget("hash_key", "field")
all_fields = redis_client.hgetall("hash_key")

# 列表操作
redis_client.lpush("list_key", "item1")
redis_client.rpush("list_key", "item2")
items = redis_client.lrange("list_key", 0, -1)

# 集合操作
redis_client.sadd("set_key", "member1")
redis_client.sadd("set_key", "member2")
members = redis_client.smembers("set_key")
```

#### 主要方法

##### 字符串操作

- `set(key, value, expire=None)`: 设置键值对
- `get(key, default=None)`: 获取值
- `delete(key)`: 删除键
- `exists(key)`: 检查键是否存在
- `expire(key, seconds)`: 设置过期时间
- `ttl(key)`: 获取剩余生存时间

##### 哈希操作

- `hset(key, field, value)`: 设置哈希字段
- `hget(key, field, default=None)`: 获取哈希字段值
- `hgetall(key)`: 获取所有哈希字段
- `hdel(key, *fields)`: 删除哈希字段
- `hexists(key, field)`: 检查哈希字段是否存在
- `hkeys(key)`: 获取所有哈希字段名
- `hvals(key)`: 获取所有哈希字段值

##### 列表操作

- `lpush(key, *values)`: 从左侧推入值
- `rpush(key, *values)`: 从右侧推入值
- `lpop(key)`: 从左侧弹出值
- `rpop(key)`: 从右侧弹出值
- `lrange(key, start, end)`: 获取列表范围
- `llen(key)`: 获取列表长度

##### 集合操作

- `sadd(key, *members)`: 添加集合成员
- `srem(key, *members)`: 删除集合成员
- `smembers(key)`: 获取所有成员
- `sismember(key, member)`: 检查成员是否存在
- `scard(key)`: 获取集合大小

##### 有序集合操作

- `zadd(key, mapping)`: 添加有序集合成员
- `zrange(key, start, end, withscores=False)`: 获取有序集合范围
- `zscore(key, member)`: 获取成员分数
- `zrank(key, member)`: 获取成员排名

### DatabaseManager

数据库管理器，提供 MySQL 和 PostgreSQL 数据库连接和操作。

```python
from common.storage.db_client import DatabaseManager

# 创建数据库管理器
db_manager = DatabaseManager()

# 获取数据库连接
with db_manager.get_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

# 执行查询
users = db_manager.query("SELECT * FROM users WHERE active = %s", (True,))

# 执行更新
affected_rows = db_manager.execute(
    "UPDATE users SET last_login = %s WHERE id = %s",
    (datetime.now(), user_id)
)

# 批量插入
data = [("user1", "pass1"), ("user2", "pass2")]
db_manager.executemany(
    "INSERT INTO users (username, password) VALUES (%s, %s)",
    data
)
```

#### 主要方法

##### 连接管理

- `get_connection()`: 获取数据库连接
- `close_connection()`: 关闭数据库连接
- `ping()`: 测试数据库连接

##### 查询操作

- `query(sql, params=None)`: 执行查询并返回结果
- `query_one(sql, params=None)`: 执行查询并返回单条结果
- `execute(sql, params=None)`: 执行更新操作
- `executemany(sql, params_list)`: 批量执行操作

##### 事务管理

- `begin_transaction()`: 开始事务
- `commit_transaction()`: 提交事务
- `rollback_transaction()`: 回滚事务

### CacheManager

缓存管理器，提供多级缓存策略和统一接口。

```python
from common.storage.cache import CacheManager, MemoryCache, RedisCache

# 创建缓存管理器
cache_manager = CacheManager()

# 添加缓存层
cache_manager.add_layer("memory", MemoryCache(max_size=1000))
cache_manager.add_layer("redis", RedisCache())

# 设置缓存
cache_manager.set("user:123", user_data, ttl=3600)

# 获取缓存
user_data = cache_manager.get("user:123")

# 删除缓存
cache_manager.delete("user:123")

# 清空缓存
cache_manager.clear()
```

#### 缓存接口

```python
from abc import ABC, abstractmethod

class Cache(ABC):
    """缓存接口"""
    
    @abstractmethod
    def get(self, key: str, default=None):
        """获取缓存值"""
        pass
    
    @abstractmethod
    def set(self, key: str, value, ttl=None):
        """设置缓存值"""
        pass
    
    @abstractmethod
    def delete(self, key: str):
        """删除缓存"""
        pass
    
    @abstractmethod
    def clear(self):
        """清空缓存"""
        pass
    
    @abstractmethod
    def exists(self, key: str):
        """检查键是否存在"""
        pass
```

#### 缓存实现

##### MemoryCache

内存缓存，适用于临时数据存储。

```python
from common.storage.cache import MemoryCache

# 创建内存缓存
memory_cache = MemoryCache(max_size=1000)

# 设置缓存
memory_cache.set("key", "value", ttl=60)

# 获取缓存
value = memory_cache.get("key")

# 检查过期
is_expired = memory_cache.is_expired("key")
```

##### RedisCache

Redis 缓存，适用于分布式缓存。

```python
from common.storage.cache import RedisCache

# 创建 Redis 缓存
redis_cache = RedisCache()

# 设置缓存
redis_cache.set("key", "value", ttl=3600)

# 获取缓存
value = redis_cache.get("key")

# 批量操作
redis_cache.mset({"key1": "value1", "key2": "value2"})
values = redis_cache.mget(["key1", "key2"])
```

## 🚀 使用示例

### Redis 使用示例

```python
from common.storage.redis_client import RedisClient

# 创建客户端
redis = RedisClient()

# 用户会话管理
def create_user_session(user_id, session_data):
    """创建用户会话"""
    key = f"session:{user_id}"
    redis.set(key, session_data, expire=3600)
    return key

def get_user_session(user_id):
    """获取用户会话"""
    key = f"session:{user_id}"
    return redis.get(key)

def delete_user_session(user_id):
    """删除用户会话"""
    key = f"session:{user_id}"
    redis.delete(key)

# 缓存管理
def cache_user_profile(user_id, profile_data):
    """缓存用户资料"""
    key = f"profile:{user_id}"
    redis.set(key, profile_data, expire=1800)

def get_cached_profile(user_id):
    """获取缓存的用户资料"""
    key = f"profile:{user_id}"
    return redis.get(key)

# 计数器
def increment_user_visits(user_id):
    """增加用户访问次数"""
    key = f"visits:{user_id}"
    return redis.incr(key)

def get_user_visits(user_id):
    """获取用户访问次数"""
    key = f"visits:{user_id}"
    return redis.get(key) or 0
```

### 数据库使用示例

```python
from common.storage.db_client import DatabaseManager

# 创建数据库管理器
db = DatabaseManager()

# 用户管理
def create_user(username, email, password_hash):
    """创建用户"""
    sql = """
    INSERT INTO users (username, email, password_hash, created_at)
    VALUES (%s, %s, %s, %s)
    """
    return db.execute(sql, (username, email, password_hash, datetime.now()))

def get_user_by_id(user_id):
    """根据ID获取用户"""
    sql = "SELECT * FROM users WHERE id = %s"
    return db.query_one(sql, (user_id,))

def update_user_last_login(user_id):
    """更新用户最后登录时间"""
    sql = "UPDATE users SET last_login = %s WHERE id = %s"
    return db.execute(sql, (datetime.now(), user_id))

def get_active_users():
    """获取活跃用户列表"""
    sql = "SELECT * FROM users WHERE active = %s ORDER BY last_login DESC"
    return db.query(sql, (True,))

# 事务示例
def transfer_money(from_account, to_account, amount):
    """转账操作"""
    try:
        db.begin_transaction()
        
        # 扣除源账户
        sql1 = "UPDATE accounts SET balance = balance - %s WHERE id = %s"
        db.execute(sql1, (amount, from_account))
        
        # 增加目标账户
        sql2 = "UPDATE accounts SET balance = balance + %s WHERE id = %s"
        db.execute(sql2, (amount, to_account))
        
        # 记录交易
        sql3 = """
        INSERT INTO transactions (from_account, to_account, amount, created_at)
        VALUES (%s, %s, %s, %s)
        """
        db.execute(sql3, (from_account, to_account, amount, datetime.now()))
        
        db.commit_transaction()
        return True
        
    except Exception as e:
        db.rollback_transaction()
        raise e
```

### 缓存使用示例

```python
from common.storage.cache import CacheManager, MemoryCache, RedisCache

# 创建缓存管理器
cache_manager = CacheManager()

# 添加缓存层
cache_manager.add_layer("memory", MemoryCache(max_size=1000))
cache_manager.add_layer("redis", RedisCache())

# 用户资料缓存
def get_user_profile(user_id):
    """获取用户资料（带缓存）"""
    cache_key = f"profile:{user_id}"
    
    # 尝试从缓存获取
    profile = cache_manager.get(cache_key)
    if profile:
        return profile
    
    # 从数据库获取
    profile = get_user_from_database(user_id)
    if profile:
        # 缓存 30 分钟
        cache_manager.set(cache_key, profile, ttl=1800)
    
    return profile

def update_user_profile(user_id, profile_data):
    """更新用户资料"""
    # 更新数据库
    update_user_in_database(user_id, profile_data)
    
    # 更新缓存
    cache_key = f"profile:{user_id}"
    cache_manager.set(cache_key, profile_data, ttl=1800)

# 多级缓存策略
def get_expensive_data(key):
    """获取昂贵的数据（多级缓存）"""
    # 第一级：内存缓存
    data = cache_manager.get(key, layer="memory")
    if data:
        return data
    
    # 第二级：Redis 缓存
    data = cache_manager.get(key, layer="redis")
    if data:
        # 同步到内存缓存
        cache_manager.set(key, data, ttl=300, layer="memory")
        return data
    
    # 第三级：数据库
    data = get_data_from_database(key)
    if data:
        # 同步到所有缓存层
        cache_manager.set(key, data, ttl=3600, layer="redis")
        cache_manager.set(key, data, ttl=300, layer="memory")
    
    return data
```

## 🔧 配置选项

### Redis 配置

```python
# 环境变量配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_SSL=false
REDIS_TIMEOUT=5
REDIS_RETRY_ON_TIMEOUT=true
```

### 数据库配置

```python
# MySQL 配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=mydb
MYSQL_USERNAME=myuser
MYSQL_PASSWORD=mypassword
MYSQL_CHARSET=utf8mb4

# PostgreSQL 配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=mydb
POSTGRES_USERNAME=myuser
POSTGRES_PASSWORD=mypassword
```

### 缓存配置

```python
# 内存缓存配置
MEMORY_CACHE_MAX_SIZE=1000
MEMORY_CACHE_TTL=300

# Redis 缓存配置
REDIS_CACHE_TTL=3600
REDIS_CACHE_PREFIX=cache:
```

## 📊 性能优化

### 连接池配置

```python
# Redis 连接池
REDIS_POOL_SIZE=10
REDIS_POOL_TIMEOUT=20

# 数据库连接池
DB_POOL_SIZE=5
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### 批量操作

```python
# Redis 批量操作
def batch_set_keys(key_value_pairs):
    """批量设置键值对"""
    pipeline = redis_client.pipeline()
    for key, value in key_value_pairs:
        pipeline.set(key, value, expire=3600)
    pipeline.execute()

# 数据库批量操作
def batch_insert_users(users_data):
    """批量插入用户"""
    sql = "INSERT INTO users (username, email) VALUES (%s, %s)"
    db_manager.executemany(sql, users_data)
```

### 缓存策略

```python
# 缓存预热
def warm_up_cache():
    """缓存预热"""
    # 预加载热门数据
    hot_users = get_hot_users_from_database()
    for user in hot_users:
        cache_key = f"profile:{user['id']}"
        cache_manager.set(cache_key, user, ttl=3600)

# 缓存穿透保护
def get_user_profile_with_protection(user_id):
    """带保护的获取用户资料"""
    cache_key = f"profile:{user_id}"
    
    # 尝试获取缓存
    profile = cache_manager.get(cache_key)
    if profile is not None:  # 包括空值
        return profile
    
    # 防止缓存穿透
    lock_key = f"lock:{user_id}"
    if cache_manager.set(lock_key, 1, ttl=10, nx=True):
        try:
            # 从数据库获取
            profile = get_user_from_database(user_id)
            # 缓存结果（包括空值）
            cache_manager.set(cache_key, profile, ttl=1800)
            return profile
        finally:
            cache_manager.delete(lock_key)
    else:
        # 等待其他进程处理
        time.sleep(0.1)
        return get_user_profile_with_protection(user_id)
```

## 🚨 错误处理

### 连接错误处理

```python
from common.storage.redis_client import RedisConnectionError
from common.storage.db_client import DatabaseConnectionError

try:
    # Redis 操作
    redis_client.set("key", "value")
except RedisConnectionError as e:
    logger.error(f"Redis 连接错误: {e}")
    # 降级到内存缓存
    fallback_to_memory_cache()
except Exception as e:
    logger.error(f"Redis 操作错误: {e}")

try:
    # 数据库操作
    db_manager.query("SELECT * FROM users")
except DatabaseConnectionError as e:
    logger.error(f"数据库连接错误: {e}")
    # 重试连接
    db_manager.reconnect()
except Exception as e:
    logger.error(f"数据库操作错误: {e}")
```

### 重试机制

```python
from common.utils.retry_util import retry

@retry(max_retries=3, delay=1)
def reliable_redis_operation():
    """可靠的 Redis 操作"""
    return redis_client.set("key", "value")

@retry(max_retries=3, delay=1)
def reliable_db_operation():
    """可靠的数据库操作"""
    return db_manager.query("SELECT * FROM users")
```

## 🔒 安全考虑

### 数据加密

```python
from common.security.hash_util import hash_data

# 敏感数据加密存储
def store_sensitive_data(key, data):
    """存储敏感数据"""
    encrypted_data = encrypt_data(data)
    redis_client.set(key, encrypted_data, expire=3600)

def get_sensitive_data(key):
    """获取敏感数据"""
    encrypted_data = redis_client.get(key)
    if encrypted_data:
        return decrypt_data(encrypted_data)
    return None
```

### 访问控制

```python
# 基于角色的访问控制
def check_cache_access(user_id, cache_key):
    """检查缓存访问权限"""
    user_role = get_user_role(user_id)
    
    if user_role == "admin":
        return True
    
    if cache_key.startswith(f"user:{user_id}"):
        return True
    
    return False
```

## 📚 下一步

- 查看 [公共模块 API](common.md)
- 了解 [交易模块 API](trading.md)
- 阅读 [部署指南](../deployment/docker.md)

## 🤝 获取帮助

如果遇到问题：

1. 检查连接配置
2. 查看错误日志
3. 验证权限设置
4. 联系技术支持
