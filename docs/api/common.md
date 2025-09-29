# 🔧 公共模块 API 参考

本文档提供了公共模块 (common) 的完整 API 参考。

## 📚 模块概览

```
common/
├── config/              # 配置管理
│   ├── __init__.py     # 配置实例导出
│   └── settings.py     # 配置类定义
├── logging/             # 日志管理
│   ├── __init__.py     # 日志实例导出
│   └── logger.py       # 日志配置
├── storage/             # 数据存储
│   ├── __init__.py     # 存储模块导出
│   ├── redis_client.py # Redis 客户端
│   ├── db_client.py    # 数据库客户端
│   └── cache.py        # 缓存接口
├── network/             # 网络通信
│   ├── __init__.py     # 网络模块导出
│   ├── http_client.py  # HTTP 客户端
│   └── ws_client.py    # WebSocket 客户端
├── utils/               # 工具函数
│   ├── __init__.py     # 工具模块导出
│   ├── json_util.py    # JSON 工具
│   ├── time_util.py    # 时间工具
│   └── retry_util.py   # 重试工具
└── security/            # 安全工具
    ├── __init__.py     # 安全模块导出
    ├── hash_util.py    # 哈希工具
    └── jwt_util.py     # JWT 工具
```

## 🔧 配置管理 (config)

### **Settings 类**

#### **类定义**
```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # 数据库配置
    DB_HOST: str = Field(default="localhost", description="数据库主机")
    DB_PORT: int = Field(default=3306, description="数据库端口")
    DB_USER: str = Field(default="root", description="数据库用户名")
    DB_PASSWORD: str = Field(default="", description="数据库密码")
    DB_NAME: str = Field(default="my_platform", description="数据库名称")
    
    # Redis 配置
    REDIS_HOST: str = Field(default="localhost", description="Redis 主机")
    REDIS_PORT: int = Field(default=6379, description="Redis 端口")
    REDIS_DB: int = Field(default=0, description="Redis 数据库")
    REDIS_PASSWORD: str = Field(default="", description="Redis 密码")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FILE: str = Field(default="logs/app.log", description="日志文件路径")
    
    # 项目配置
    PROJECT_NAME: str = Field(default="Python Multi-Project Platform", description="项目名称")
    DEBUG: bool = Field(default=False, description="调试模式")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

#### **使用示例**
```python
from common.config.settings import config

# 访问配置
print(f"数据库主机: {config.DB_HOST}")
print(f"Redis 端口: {config.REDIS_PORT}")
print(f"日志级别: {config.LOG_LEVEL}")

# 环境变量覆盖
# export DB_HOST=production-db.com
# export LOG_LEVEL=DEBUG
```

## 📝 日志管理 (logging)

### **Logger 配置**

#### **基本使用**
```python
from common.logging.logger import logger

# 不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")

# 结构化日志
logger.info("用户登录", extra={
    "user_id": 123,
    "ip_address": "192.168.1.1",
    "action": "login"
})

# 异常日志
try:
    # 某些操作
    pass
except Exception as e:
    logger.exception("操作失败")
```

#### **配置选项**
```python
# 日志配置
LOG_CONFIG = {
    "handlers": [
        {
            "sink": "logs/app.log",
            "rotation": "100 MB",
            "retention": "30 days",
            "compression": "zip",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        },
        {
            "sink": "logs/error.log",
            "level": "ERROR",
            "rotation": "50 MB",
            "retention": "90 days"
        }
    ]
}
```

## 💾 数据存储 (storage)

### **Redis 客户端**

#### **RedisClient 类**
```python
from common.storage.redis_client import RedisClient

class RedisClient:
    def __init__(self, host: str = None, port: int = None, db: int = None, password: str = None):
        """初始化 Redis 客户端"""
        
    async def connect(self) -> None:
        """连接到 Redis 服务器"""
        
    async def disconnect(self) -> None:
        """断开 Redis 连接"""
        
    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """设置键值对"""
        
    async def get(self, key: str) -> Any:
        """获取键值"""
        
    async def delete(self, key: str) -> bool:
        """删除键"""
        
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        
    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        
    async def ttl(self, key: str) -> int:
        """获取剩余生存时间"""
```

#### **使用示例**
```python
import asyncio
from common.storage.redis_client import RedisClient

async def redis_example():
    # 创建客户端
    redis = RedisClient()
    
    try:
        # 连接
        await redis.connect()
        
        # 基本操作
        await redis.set("user:123", {"name": "John", "age": 30})
        user_data = await redis.get("user:123")
        print(f"用户数据: {user_data}")
        
        # 设置过期时间
        await redis.set("temp:key", "临时数据", expire=3600)
        
        # 检查键是否存在
        exists = await redis.exists("user:123")
        print(f"键存在: {exists}")
        
    finally:
        # 断开连接
        await redis.disconnect()

# 运行示例
asyncio.run(redis_example())
```

### **数据库客户端**

#### **DatabaseManager 类**
```python
from common.storage.db_client import DatabaseManager

class DatabaseManager:
    def __init__(self, host: str = None, port: int = None, user: str = None, 
                 password: str = None, database: str = None):
        """初始化数据库管理器"""
        
    async def connect(self) -> None:
        """连接到数据库"""
        
    async def disconnect(self) -> None:
        """断开数据库连接"""
        
    async def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """执行查询语句"""
        
    async def execute_update(self, query: str, params: tuple = None) -> int:
        """执行更新语句"""
        
    async def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """批量执行语句"""
        
    async def begin_transaction(self):
        """开始事务"""
        
    async def commit_transaction(self):
        """提交事务"""
        
    async def rollback_transaction(self):
        """回滚事务"""
```

#### **使用示例**
```python
import asyncio
from common.storage.db_client import DatabaseManager

async def database_example():
    # 创建数据库管理器
    db = DatabaseManager()
    
    try:
        # 连接数据库
        await db.connect()
        
        # 查询数据
        users = await db.execute_query(
            "SELECT id, name, email FROM users WHERE status = %s",
            ('active',)
        )
        print(f"活跃用户: {users}")
        
        # 更新数据
        affected = await db.execute_update(
            "UPDATE users SET last_login = NOW() WHERE id = %s",
            (123,)
        )
        print(f"更新了 {affected} 行")
        
        # 事务操作
        async with db.begin_transaction():
            await db.execute_update(
                "INSERT INTO user_logs (user_id, action) VALUES (%s, %s)",
                (123, 'login')
            )
            await db.execute_update(
                "UPDATE users SET login_count = login_count + 1 WHERE id = %s",
                (123,)
            )
            # 自动提交或回滚
            
    finally:
        # 断开连接
        await db.disconnect()

# 运行示例
asyncio.run(database_example())
```

### **缓存管理器**

#### **Cache 接口和实现**
```python
from abc import ABC, abstractmethod
from typing import Any, Optional
from common.storage.cache import Cache, MemoryCache, RedisCache, CacheManager

# 抽象缓存接口
class Cache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """设置缓存值"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass

# 内存缓存实现
class MemoryCache(Cache):
    """基于内存的缓存实现"""
    
# Redis 缓存实现
class RedisCache(Cache):
    """基于 Redis 的缓存实现"""
    
# 缓存管理器
class CacheManager:
    """统一的缓存管理接口"""
```

#### **使用示例**
```python
import asyncio
from common.storage.cache import CacheManager

async def cache_example():
    # 创建缓存管理器
    cache = CacheManager()
    
    # 设置缓存
    await cache.set("user:profile:123", {
        "name": "John Doe",
        "email": "john@example.com",
        "preferences": {"theme": "dark", "language": "zh-CN"}
    }, expire=3600)
    
    # 获取缓存
    profile = await cache.get("user:profile:123")
    print(f"用户资料: {profile}")
    
    # 删除缓存
    await cache.delete("user:profile:123")
    
    # 检查缓存
    exists = await cache.get("user:profile:123")
    print(f"缓存存在: {exists is not None}")

# 运行示例
asyncio.run(cache_example())
```

## 🌐 网络通信 (network)

### **HTTP 客户端**

#### **HTTPClient 类**
```python
from common.network.http_client import HTTPClient, HTTPClientError

class HTTPClient:
    def __init__(self, base_url: str = None, timeout: float = 30.0, 
                 max_retries: int = 3, headers: Dict[str, str] = None):
        """初始化 HTTP 客户端"""
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        
    async def start(self) -> None:
        """启动客户端会话"""
        
    async def close(self) -> None:
        """关闭客户端会话"""
        
    async def get(self, url: str, params: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """发送 GET 请求"""
        
    async def post(self, url: str, data: Dict[str, Any] = None, 
                   json_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """发送 POST 请求"""
        
    async def put(self, url: str, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """发送 PUT 请求"""
        
    async def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """发送 DELETE 请求"""
```

#### **使用示例**
```python
import asyncio
from common.network.http_client import HTTPClient, HTTPClientError

async def http_example():
    # 基本使用
    async with HTTPClient() as client:
        # GET 请求
        response = await client.get('https://httpbin.org/get')
        print(f"状态码: {response['status_code']}")
        print(f"响应数据: {response['data']}")
        
        # POST 请求
        user_data = {'name': 'John', 'email': 'john@example.com'}
        response = await client.post('https://httpbin.org/post', json_data=user_data)
        print(f"创建用户响应: {response['data']}")
    
    # 自定义配置
    client = HTTPClient(
        base_url="https://api.example.com",
        timeout=60.0,
        max_retries=5,
        headers={"Authorization": "Bearer token123"}
    )
    
    async with client:
        # 使用基础 URL
        response = await client.get('/users')
        print(f"用户列表: {response['data']}")
        
        # 带参数的请求
        response = await client.get('/search', params={'q': 'python', 'page': 1})
        print(f"搜索结果: {response['data']}")

# 运行示例
asyncio.run(http_example())
```

### **WebSocket 客户端**

#### **WebSocketClient 类**
```python
from common.network.ws_client import WebSocketClient

class WebSocketClient:
    def __init__(self, url: str, headers: Dict[str, str] = None):
        """初始化 WebSocket 客户端"""
        
    async def connect(self) -> None:
        """连接到 WebSocket 服务器"""
        
    async def disconnect(self) -> None:
        """断开 WebSocket 连接"""
        
    async def send(self, message: str) -> None:
        """发送消息"""
        
    async def receive(self) -> str:
        """接收消息"""
        
    async def ping(self) -> None:
        """发送 ping"""
        
    async def pong(self) -> None:
        """发送 pong"""
```

## 🛠️ 工具函数 (utils)

### **JSON 工具**

#### **json_util 模块**
```python
from common.utils.json_util import safe_json_loads, safe_json_dumps, json_serialize

# 安全的 JSON 解析
def safe_json_loads(data: str, default: Any = None) -> Any:
    """安全地解析 JSON 字符串"""
    
# 安全的 JSON 序列化
def safe_json_dumps(obj: Any, default: str = None, **kwargs) -> str:
    """安全地序列化对象为 JSON 字符串"""
    
# JSON 序列化装饰器
def json_serialize(func):
    """装饰器：自动序列化函数返回值为 JSON"""
```

#### **使用示例**
```python
from common.utils.json_util import safe_json_loads, safe_json_dumps

# 安全解析
try:
    data = safe_json_loads('{"name": "John", "age": 30}')
    print(f"解析成功: {data}")
except Exception as e:
    print(f"解析失败: {e}")

# 安全序列化
try:
    json_str = safe_json_dumps({"name": "John", "age": 30})
    print(f"序列化成功: {json_str}")
except Exception as e:
    print(f"序列化失败: {e}")
```

### **时间工具**

#### **time_util 模块**
```python
from common.utils.time_util import get_timestamp, format_datetime, parse_datetime

# 获取时间戳
def get_timestamp() -> int:
    """获取当前时间戳（秒）"""
    
# 格式化日期时间
def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间为字符串"""
    
# 解析日期时间
def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析字符串为日期时间对象"""
```

### **重试工具**

#### **retry_util 模块**
```python
from common.utils.retry_util import retry, RetryConfig

# 重试装饰器
def retry(max_attempts: int = 3, delay: float = 1.0, 
          backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """重试装饰器"""
    
# 重试配置类
class RetryConfig:
    def __init__(self, max_attempts: int = 3, delay: float = 1.0, 
                 backoff: float = 2.0, exceptions: tuple = (Exception,)):
        """重试配置"""
```

#### **使用示例**
```python
from common.utils.retry_util import retry

@retry(max_attempts=3, delay=1.0, backoff=2.0)
async def unreliable_function():
    """不可靠的函数，需要重试"""
    import random
    if random.random() < 0.7:  # 70% 失败率
        raise Exception("随机失败")
    return "成功！"

# 使用重试
result = await unreliable_function()
print(f"结果: {result}")
```

## 🔐 安全工具 (security)

### **哈希工具**

#### **hash_util 模块**
```python
from common.security.hash_util import hash_password, verify_password, generate_salt

# 哈希密码
def hash_password(password: str, salt: str = None) -> str:
    """哈希密码"""
    
# 验证密码
def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    
# 生成盐值
def generate_salt(length: int = 16) -> str:
    """生成随机盐值"""
```

### **JWT 工具**

#### **jwt_util 模块**
```python
from common.security.jwt_util import create_token, verify_token, decode_token

# 创建 JWT 令牌
def create_token(payload: Dict[str, Any], secret: str, 
                 algorithm: str = "HS256", expires_in: int = 3600) -> str:
    """创建 JWT 令牌"""
    
# 验证 JWT 令牌
def verify_token(token: str, secret: str, algorithm: str = "HS256") -> bool:
    """验证 JWT 令牌"""
    
# 解码 JWT 令牌
def decode_token(token: str, secret: str, algorithm: str = "HS256") -> Dict[str, Any]:
    """解码 JWT 令牌"""
```

## 📚 完整导入示例

```python
# 配置管理
from common.config.settings import config

# 日志管理
from common.logging.logger import logger

# 存储模块
from common.storage.redis_client import RedisClient
from common.storage.db_client import DatabaseManager
from common.storage.cache import CacheManager

# 网络模块
from common.network.http_client import HTTPClient, HTTPClientError
from common.network.ws_client import WebSocketClient

# 工具模块
from common.utils.json_util import safe_json_loads, safe_json_dumps
from common.utils.time_util import get_timestamp, format_datetime
from common.utils.retry_util import retry

# 安全模块
from common.security.hash_util import hash_password, verify_password
from common.security.jwt_util import create_token, verify_token
```

## 🔗 相关链接

- [配置说明](../getting-started/configuration.md)
- [快速开始](../getting-started/quickstart.md)
- [代码质量工具](../development/code-quality.md)
- [使用示例](../examples/http-client.md)

---

🔧 **开始使用** → 查看 [快速开始](../getting-started/quickstart.md) 指南
