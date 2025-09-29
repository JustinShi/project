# 🔴 Redis 使用示例

本文档介绍 Redis 在 Python 多项目平台中的使用方法和最佳实践。

## 📋 Redis 概述

### 什么是 Redis

Redis (Remote Dictionary Server) 是一个开源的内存数据结构存储系统，可以用作：

- **数据库**: 持久化数据存储
- **缓存**: 高性能数据缓存
- **消息代理**: 发布/订阅消息系统
- **会话存储**: 用户会话管理
- **计数器**: 实时计数和统计

### Redis 优势

- **高性能**: 基于内存操作，速度极快
- **数据结构丰富**: 支持字符串、哈希、列表、集合、有序集合
- **原子操作**: 支持事务和 Lua 脚本
- **持久化**: 支持 RDB 和 AOF 两种持久化方式
- **集群支持**: 支持主从复制和集群模式

## 🚀 快速开始

### 安装和启动

```bash
# 使用 Docker 启动 Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 或者使用 docker-compose
docker-compose up -d redis

# 测试连接
redis-cli ping
# 返回: PONG
```

### 基本连接

```python
from common.storage.redis_client import RedisClient

# 创建 Redis 客户端
redis_client = RedisClient()

# 测试连接
try:
    redis_client.ping()
    print("Redis 连接成功")
except Exception as e:
    print(f"Redis 连接失败: {e}")
```

## 🔧 基本操作

### 字符串操作

```python
from common.storage.redis_client import RedisClient

redis_client = RedisClient()

# 设置值
redis_client.set("user:1:name", "张三")
redis_client.set("user:1:age", "25")
redis_client.set("user:1:email", "zhangsan@example.com")

# 获取值
name = redis_client.get("user:1:name")
age = redis_client.get("user:1:age")
email = redis_client.get("user:1:email")

print(f"用户: {name}, 年龄: {age}, 邮箱: {email}")

# 设置过期时间 (30 秒)
redis_client.set("temp:key", "临时数据", expire=30)

# 检查键是否存在
if redis_client.exists("user:1:name"):
    print("用户名称存在")

# 删除键
redis_client.delete("temp:key")

# 批量操作
redis_client.mset({
    "user:2:name": "李四",
    "user:2:age": "30",
    "user:2:email": "lisi@example.com"
})

# 批量获取
user2_data = redis_client.mget(["user:2:name", "user:2:age", "user:2:email"])
print(f"用户2数据: {user2_data}")
```

### 哈希操作

```python
# 设置哈希字段
redis_client.hset("user:1", "name", "张三")
redis_client.hset("user:1", "age", "25")
redis_client.hset("user:1", "email", "zhangsan@example.com")

# 获取哈希字段
name = redis_client.hget("user:1", "name")
age = redis_client.hget("user:1", "age")

# 获取所有字段
all_fields = redis_client.hgetall("user:1")
print(f"用户1所有字段: {all_fields}")

# 检查字段是否存在
if redis_client.hexists("user:1", "name"):
    print("用户名称字段存在")

# 获取所有字段名
field_names = redis_client.hkeys("user:1")
print(f"字段名: {field_names}")

# 获取所有字段值
field_values = redis_client.hvals("user:1")
print(f"字段值: {field_values}")

# 获取字段数量
field_count = redis_client.hlen("user:1")
print(f"字段数量: {field_count}")

# 批量设置哈希字段
redis_client.hmset("user:3", {
    "name": "王五",
    "age": "35",
    "email": "wangwu@example.com",
    "city": "北京"
})

# 批量获取哈希字段
user3_data = redis_client.hmget("user:3", ["name", "age", "city"])
print(f"用户3数据: {user3_data}")
```

### 列表操作

```python
# 从左侧推入元素
redis_client.lpush("queue:orders", "order:001")
redis_client.lpush("queue:orders", "order:002")
redis_client.lpush("queue:orders", "order:003")

# 从右侧推入元素
redis_client.rpush("queue:orders", "order:004")
redis_client.rpush("queue:orders", "order:005")

# 获取列表长度
queue_length = redis_client.llen("queue:orders")
print(f"队列长度: {queue_length}")

# 获取列表范围
all_orders = redis_client.lrange("queue:orders", 0, -1)
print(f"所有订单: {all_orders}")

# 从左侧弹出元素
first_order = redis_client.lpop("queue:orders")
print(f"第一个订单: {first_order}")

# 从右侧弹出元素
last_order = redis_client.rpop("queue:orders")
print(f"最后一个订单: {last_order}")

# 获取指定位置的元素
second_order = redis_client.lindex("queue:orders", 1)
print(f"第二个订单: {second_order}")

# 设置指定位置的元素
redis_client.lset("queue:orders", 0, "order:999")

# 修剪列表 (保留前3个元素)
redis_client.ltrim("queue:orders", 0, 2)
```

### 集合操作

```python
# 添加集合成员
redis_client.sadd("tags:python", "web", "data", "ai", "automation")
redis_client.sadd("tags:java", "web", "enterprise", "android")
redis_client.sadd("tags:javascript", "web", "frontend", "nodejs")

# 获取集合成员
python_tags = redis_client.smembers("tags:python")
print(f"Python 标签: {python_tags}")

# 检查成员是否存在
if redis_client.sismember("tags:python", "web"):
    print("Python 标签包含 web")

# 获取集合大小
python_tag_count = redis_client.scard("tags:python")
print(f"Python 标签数量: {python_tag_count}")

# 移除成员
redis_client.srem("tags:python", "automation")

# 集合运算
# 交集
common_tags = redis_client.sinter("tags:python", "tags:java")
print(f"Python 和 Java 共同标签: {common_tags}")

# 并集
all_tags = redis_client.sunion("tags:python", "tags:javascript")
print(f"Python 和 JavaScript 所有标签: {all_tags}")

# 差集
python_only = redis_client.sdiff("tags:python", "tags:java")
print(f"Python 独有标签: {python_only}")

# 随机获取成员
random_tag = redis_client.srandmember("tags:python")
print(f"随机标签: {random_tag}")

# 随机弹出成员
popped_tag = redis_client.spop("tags:python")
print(f"弹出的标签: {popped_tag}")
```

### 有序集合操作

```python
# 添加有序集合成员 (带分数)
redis_client.zadd("leaderboard", {
    "player:1": 1000,
    "player:2": 1500,
    "player:3": 800,
    "player:4": 2000,
    "player:5": 1200
})

# 获取成员分数
score = redis_client.zscore("leaderboard", "player:1")
print(f"玩家1分数: {score}")

# 获取成员排名 (从高到低)
rank = redis_client.zrank("leaderboard", "player:1")
print(f"玩家1排名: {rank}")

# 获取成员排名 (从低到高)
reverse_rank = redis_client.zrevrank("leaderboard", "player:1")
print(f"玩家1倒序排名: {reverse_rank}")

# 获取排行榜前3名
top_players = redis_client.zrevrange("leaderboard", 0, 2, withscores=True)
print(f"前三名: {top_players}")

# 获取分数范围内的成员
high_score_players = redis_client.zrangebyscore("leaderboard", 1000, 2000, withscores=True)
print(f"高分玩家: {high_score_players}")

# 增加成员分数
redis_client.zincrby("leaderboard", 100, "player:1")
new_score = redis_client.zscore("leaderboard", "player:1")
print(f"玩家1新分数: {new_score}")

# 获取集合大小
player_count = redis_client.zcard("leaderboard")
print(f"玩家数量: {player_count}")

# 获取分数范围内的成员数量
high_score_count = redis_client.zcount("leaderboard", 1000, 2000)
print(f"高分玩家数量: {high_score_count}")
```

## 🚀 高级功能

### 事务操作

```python
# 使用管道执行事务
def transfer_points(from_user, to_user, points):
    """转移积分"""
    try:
        # 开始事务
        with redis_client.pipeline() as pipe:
            # 监视用户积分
            pipe.watch(f"points:{from_user}")
            pipe.watch(f"points:{to_user}")
            
            # 获取当前积分
            from_points = int(pipe.get(f"points:{from_user}") or 0)
            to_points = int(pipe.get(f"points:{to_user}") or 0)
            
            # 检查余额
            if from_points < points:
                raise ValueError("积分不足")
            
            # 执行事务
            pipe.multi()
            pipe.set(f"points:{from_user}", from_points - points)
            pipe.set(f"points:{to_user}", to_points + points)
            pipe.execute()
            
            print(f"成功转移 {points} 积分从 {from_user} 到 {to_user}")
            return True
            
    except Exception as e:
        print(f"转移失败: {e}")
        return False

# 使用示例
redis_client.set("points:user1", 1000)
redis_client.set("points:user2", 500)

transfer_points("user1", "user2", 200)

print(f"用户1积分: {redis_client.get('points:user1')}")
print(f"用户2积分: {redis_client.get('points:user2')}")
```

### 发布/订阅

```python
import asyncio
from common.storage.redis_client import RedisClient

class MessageBroker:
    """消息代理"""
    
    def __init__(self):
        self.redis_client = RedisClient()
        self.pubsub = None
    
    async def publish(self, channel, message):
        """发布消息"""
        try:
            await self.redis_client.publish(channel, message)
            print(f"消息已发布到 {channel}: {message}")
        except Exception as e:
            print(f"发布失败: {e}")
    
    async def subscribe(self, channels):
        """订阅频道"""
        try:
            self.pubsub = await self.redis_client.pubsub()
            await self.pubsub.subscribe(*channels)
            
            print(f"已订阅频道: {channels}")
            
            # 监听消息
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    print(f"收到消息: {message['data']} 来自 {message['channel']}")
                    
        except Exception as e:
            print(f"订阅失败: {e}")
    
    async def unsubscribe(self, channels):
        """取消订阅"""
        if self.pubsub:
            await self.pubsub.unsubscribe(*channels)
            print(f"已取消订阅: {channels}")

# 使用示例
async def main():
    broker = MessageBroker()
    
    # 启动订阅者
    subscriber_task = asyncio.create_task(
        broker.subscribe(['news', 'updates'])
    )
    
    # 等待订阅建立
    await asyncio.sleep(1)
    
    # 发布消息
    await broker.publish('news', '重要新闻: 系统升级完成')
    await broker.publish('updates', '系统更新: 新增功能上线')
    
    # 等待消息处理
    await asyncio.sleep(2)
    
    # 取消订阅
    await broker.unsubscribe(['news', 'updates'])
    
    # 取消任务
    subscriber_task.cancel()

# 运行示例
# asyncio.run(main())
```

### Lua 脚本

```python
# 原子性操作: 检查并设置
lua_script = """
local key = KEYS[1]
local expected_value = ARGV[1]
local new_value = ARGV[2]

local current_value = redis.call('GET', key)
if current_value == expected_value then
    redis.call('SET', key, new_value)
    return 1
else
    return 0
end
"""

# 执行 Lua 脚本
def check_and_set(key, expected_value, new_value):
    """检查并设置值"""
    try:
        result = redis_client.eval(lua_script, 1, key, expected_value, new_value)
        if result == 1:
            print(f"成功更新 {key}: {expected_value} -> {new_value}")
            return True
        else:
            print(f"更新失败: 当前值不是 {expected_value}")
            return False
    except Exception as e:
        print(f"执行脚本失败: {e}")
        return False

# 使用示例
redis_client.set("counter", "100")
check_and_set("counter", "100", "200")
check_and_set("counter", "100", "300")  # 会失败
```

## 💡 实际应用场景

### 用户会话管理

```python
import time
from common.storage.redis_client import RedisClient

class SessionManager:
    """会话管理器"""
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.session_prefix = "session:"
        self.default_expire = 3600  # 1小时
    
    def create_session(self, user_id, session_data):
        """创建用户会话"""
        session_id = f"session_{user_id}_{int(time.time())}"
        key = f"{self.session_prefix}{session_id}"
        
        # 存储会话数据
        self.redis_client.hmset(key, session_data)
        self.redis_client.expire(key, self.default_expire)
        
        return session_id
    
    def get_session(self, session_id):
        """获取会话数据"""
        key = f"{self.session_prefix}{session_id}"
        session_data = self.redis_client.hgetall(key)
        
        if session_data:
            # 刷新过期时间
            self.redis_client.expire(key, self.default_expire)
            return session_data
        
        return None
    
    def update_session(self, session_id, updates):
        """更新会话数据"""
        key = f"{self.session_prefix}{session_id}"
        
        if self.redis_client.exists(key):
            self.redis_client.hmset(key, updates)
            self.redis_client.expire(key, self.default_expire)
            return True
        
        return False
    
    def delete_session(self, session_id):
        """删除会话"""
        key = f"{self.session_prefix}{session_id}"
        return self.redis_client.delete(key)
    
    def get_user_sessions(self, user_id):
        """获取用户所有会话"""
        pattern = f"{self.session_prefix}session_{user_id}_*"
        keys = self.redis_client.keys(pattern)
        
        sessions = []
        for key in keys:
            session_data = self.redis_client.hgetall(key)
            session_id = key.replace(self.session_prefix, "")
            sessions.append({
                "session_id": session_id,
                "data": session_data
            })
        
        return sessions

# 使用示例
session_manager = SessionManager(redis_client)

# 创建会话
session_data = {
    "user_id": "123",
    "username": "张三",
    "login_time": str(time.time()),
    "ip_address": "192.168.1.100"
}

session_id = session_manager.create_session("123", session_data)
print(f"创建会话: {session_id}")

# 获取会话
session = session_manager.get_session(session_id)
print(f"会话数据: {session}")

# 更新会话
updates = {"last_activity": str(time.time())}
session_manager.update_session(session_id, updates)

# 删除会话
session_manager.delete_session(session_id)
```

### 缓存管理

```python
import time
from common.storage.redis_client import RedisClient

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.cache_prefix = "cache:"
        self.default_ttl = 1800  # 30分钟
    
    def set_cache(self, key, value, ttl=None):
        """设置缓存"""
        cache_key = f"{self.cache_prefix}{key}"
        ttl = ttl or self.default_ttl
        
        if isinstance(value, (dict, list)):
            # 复杂对象序列化
            import json
            value = json.dumps(value, ensure_ascii=False)
        
        self.redis_client.set(cache_key, value, expire=ttl)
    
    def get_cache(self, key, default=None):
        """获取缓存"""
        cache_key = f"{self.cache_prefix}{key}"
        value = self.redis_client.get(cache_key)
        
        if value is None:
            return default
        
        try:
            # 尝试反序列化
            import json
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def delete_cache(self, key):
        """删除缓存"""
        cache_key = f"{self.cache_prefix}{key}"
        return self.redis_client.delete(cache_key)
    
    def clear_pattern(self, pattern):
        """清除匹配模式的缓存"""
        pattern = f"{self.cache_prefix}{pattern}"
        keys = self.redis_client.keys(pattern)
        
        if keys:
            return self.redis_client.delete(*keys)
        return 0
    
    def get_cache_info(self, key):
        """获取缓存信息"""
        cache_key = f"{self.cache_prefix}{key}"
        
        info = {}
        if self.redis_client.exists(cache_key):
            info["exists"] = True
            info["ttl"] = self.redis_client.ttl(cache_key)
            info["type"] = self.redis_client.type(cache_key)
        else:
            info["exists"] = False
        
        return info

# 使用示例
cache_manager = CacheManager(redis_client)

# 缓存用户数据
user_data = {
    "id": "123",
    "name": "张三",
    "email": "zhangsan@example.com",
    "roles": ["user", "admin"]
}

cache_manager.set_cache("user:123", user_data, ttl=3600)

# 获取缓存
cached_user = cache_manager.get_cache("user:123")
print(f"缓存的用户: {cached_user}")

# 获取缓存信息
cache_info = cache_manager.get_cache_info("user:123")
print(f"缓存信息: {cache_info}")

# 清除用户相关缓存
cache_manager.clear_pattern("user:*")
```

### 限流器

```python
import time
from common.storage.redis_client import RedisClient

class RateLimiter:
    """限流器"""
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.limit_prefix = "rate_limit:"
    
    def is_allowed(self, key, limit, window):
        """检查是否允许请求"""
        current_time = int(time.time())
        window_start = current_time - window
        
        # 使用滑动窗口算法
        window_key = f"{self.limit_prefix}{key}:{current_time // window}"
        
        # 获取当前窗口的请求数
        current_count = int(self.redis_client.get(window_key) or 0)
        
        if current_count >= limit:
            return False
        
        # 增加计数
        pipe = self.redis_client.pipeline()
        pipe.incr(window_key)
        pipe.expire(window_key, window)
        pipe.execute()
        
        return True
    
    def get_remaining(self, key, limit, window):
        """获取剩余请求数"""
        current_time = int(time.time())
        window_key = f"{self.limit_prefix}{key}:{current_time // window}"
        
        current_count = int(self.redis_client.get(window_key) or 0)
        return max(0, limit - current_count)
    
    def reset(self, key):
        """重置限流器"""
        pattern = f"{self.limit_prefix}{key}:*"
        keys = self.redis_client.keys(pattern)
        
        if keys:
            return self.redis_client.delete(*keys)
        return 0

# 使用示例
rate_limiter = RateLimiter(redis_client)

# 限制每分钟最多10次请求
def api_call(user_id):
    if rate_limiter.is_allowed(f"api:{user_id}", 10, 60):
        print(f"用户 {user_id} 的请求被允许")
        return True
    else:
        remaining = rate_limiter.get_remaining(f"api:{user_id}", 10, 60)
        print(f"用户 {user_id} 的请求被拒绝，剩余 {remaining} 次")
        return False

# 测试限流
for i in range(12):
    api_call("user123")
    time.sleep(0.1)
```

## 🔒 安全最佳实践

### 密码和认证

```python
# 设置 Redis 密码
# 在 redis.conf 中设置
# requirepass your_strong_password

# 连接时使用密码
redis_client = RedisClient(password="your_strong_password")

# 或者通过环境变量
import os
redis_client = RedisClient(password=os.getenv("REDIS_PASSWORD"))
```

### 网络安全

```python
# 绑定到本地地址
# 在 redis.conf 中设置
# bind 127.0.0.1

# 禁用危险命令
# 在 redis.conf 中设置
# rename-command FLUSHDB ""
# rename-command FLUSHALL ""
# rename-command CONFIG ""
```

### 数据加密

```python
from cryptography.fernet import Fernet

class EncryptedRedisClient:
    """加密的 Redis 客户端"""
    
    def __init__(self, redis_client, encryption_key):
        self.redis_client = redis_client
        self.cipher = Fernet(encryption_key)
    
    def set(self, key, value, **kwargs):
        """加密存储值"""
        encrypted_value = self.cipher.encrypt(str(value).encode())
        return self.redis_client.set(key, encrypted_value, **kwargs)
    
    def get(self, key, default=None):
        """解密获取值"""
        encrypted_value = self.redis_client.get(key)
        
        if encrypted_value is None:
            return default
        
        try:
            decrypted_value = self.cipher.decrypt(encrypted_value)
            return decrypted_value.decode()
        except Exception:
            return default

# 使用示例
# encryption_key = Fernet.generate_key()
# encrypted_client = EncryptedRedisClient(redis_client, encryption_key)
# encrypted_client.set("secret:key", "敏感数据")
```

## 📊 性能优化

### 连接池配置

```python
# 配置连接池
redis_client = RedisClient(
    host="localhost",
    port=6379,
    db=0,
    max_connections=20,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True
)
```

### 批量操作

```python
# 使用管道批量操作
def batch_set_users(users_data):
    """批量设置用户数据"""
    with redis_client.pipeline() as pipe:
        for user_id, user_data in users_data.items():
            pipe.hmset(f"user:{user_id}", user_data)
            pipe.expire(f"user:{user_id}", 3600)
        
        # 执行所有操作
        results = pipe.execute()
        return results

# 使用示例
users = {
    "1": {"name": "张三", "age": "25"},
    "2": {"name": "李四", "age": "30"},
    "3": {"name": "王五", "age": "35"}
}

batch_set_users(users)
```

### 内存优化

```python
# 使用压缩存储
import gzip
import json

class CompressedRedisClient:
    """压缩的 Redis 客户端"""
    
    def __init__(self, redis_client, compression_threshold=100):
        self.redis_client = redis_client
        self.compression_threshold = compression_threshold
    
    def set(self, key, value, **kwargs):
        """压缩存储值"""
        if isinstance(value, str) and len(value) > self.compression_threshold:
            # 压缩大字符串
            compressed_value = gzip.compress(value.encode())
            compressed_value = b"gzip:" + compressed_value
            return self.redis_client.set(key, compressed_value, **kwargs)
        else:
            return self.redis_client.set(key, value, **kwargs)
    
    def get(self, key, default=None):
        """解压获取值"""
        value = self.redis_client.get(key)
        
        if value is None:
            return default
        
        if isinstance(value, bytes) and value.startswith(b"gzip:"):
            # 解压数据
            try:
                compressed_data = value[5:]  # 移除 "gzip:" 前缀
                decompressed_value = gzip.decompress(compressed_data)
                return decompressed_value.decode()
            except Exception:
                return default
        
        return value

# 使用示例
# compressed_client = CompressedRedisClient(redis_client)
# large_text = "很长的文本..." * 1000
# compressed_client.set("large:text", large_text)
```

## 🚨 故障排除

### 常见问题

#### 1. 连接超时

```python
# 检查网络连接
import socket

def check_redis_connection(host, port):
    """检查 Redis 连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("Redis 连接正常")
            return True
        else:
            print("Redis 连接失败")
            return False
    except Exception as e:
        print(f"检查连接时出错: {e}")
        return False

# 使用示例
check_redis_connection("localhost", 6379)
```

#### 2. 内存不足

```python
# 检查 Redis 内存使用
def check_redis_memory():
    """检查 Redis 内存使用情况"""
    try:
        info = redis_client.info("memory")
        
        used_memory = info.get("used_memory_human", "N/A")
        max_memory = info.get("maxmemory_human", "N/A")
        memory_policy = info.get("maxmemory_policy", "N/A")
        
        print(f"已用内存: {used_memory}")
        print(f"最大内存: {max_memory}")
        print(f"内存策略: {memory_policy}")
        
        return info
    except Exception as e:
        print(f"获取内存信息失败: {e}")
        return None

# 使用示例
check_redis_memory()
```

#### 3. 键过期问题

```python
# 检查键的过期时间
def check_key_expiry(key):
    """检查键的过期时间"""
    try:
        ttl = redis_client.ttl(key)
        
        if ttl == -1:
            print(f"键 {key} 永不过期")
        elif ttl == -2:
            print(f"键 {key} 不存在")
        else:
            print(f"键 {key} 将在 {ttl} 秒后过期")
        
        return ttl
    except Exception as e:
        print(f"检查过期时间失败: {e}")
        return None

# 使用示例
check_key_expiry("user:1:name")
```

## 📚 下一步

- 查看 [存储模块 API](../api/storage.md)
- 了解 [数据库使用示例](database.md)
- 阅读 [快速开始](../getting-started/quickstart.md)

## 🤝 获取帮助

如果遇到 Redis 问题：

1. 检查连接配置
2. 查看错误日志
3. 验证网络连接
4. 联系技术支持
