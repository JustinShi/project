# Common 模块

这是多项目平台的公共模块，提供各个子项目共享的基础功能。

## 📚 完整文档

**详细的 API 文档和使用示例请查看：**

- 📖 [公共模块 API 文档](../docs/api/common.md) - 完整的 API 参考
- 💡 [HTTP 客户端示例](../docs/examples/http-client.md) - HTTP 客户端使用案例
- 🔴 [Redis 使用示例](../docs/examples/redis-usage.md) - Redis 操作示例
- 🗄️ [数据库使用示例](../docs/examples/database.md) - 数据库操作示例

## 🏗️ 模块结构

```
common/
├── __init__.py          # 模块初始化，导出公共接口
├── config/              # 配置管理
│   ├── __init__.py
│   └── settings.py      # 环境变量、Redis配置
├── logging/             # 日志系统
│   ├── __init__.py
│   └── logger.py        # 基于 loguru 的日志
├── storage/             # 数据存储
│   ├── __init__.py
│   ├── redis_client.py  # Redis 客户端
│   ├── db_client.py     # 数据库管理
│   └── cache.py         # 缓存管理
├── network/             # 网络通信
│   ├── __init__.py
│   ├── http_client.py   # 异步 HTTP 客户端
│   └── ws_client.py     # WebSocket 客户端
├── utils/               # 工具函数
│   ├── __init__.py
│   ├── json_util.py     # JSON 工具
│   ├── retry_util.py    # 重试工具
│   └── time_util.py     # 时间工具
├── security/            # 安全工具
│   ├── __init__.py
│   ├── hash_util.py     # 哈希工具
│   └── jwt_util.py      # JWT 工具
└── README.md            # 本文件
```

## 🚀 快速开始

### 基本导入

```python
from common import (
    config,              # 配置管理
    get_logger,          # 日志记录器
    DatabaseManager,     # 数据库管理
    RedisClient,         # Redis 客户端
    HTTPClient,          # HTTP 客户端
)
```

### 简单使用

```python
# 获取日志记录器
logger = get_logger(__name__)
logger.info("应用启动")

# 使用 HTTP 客户端
async with HTTPClient() as client:
    response = await client.get("https://api.example.com/data")
    print(response['data'])
```

## 📋 主要模块

- **config**: 配置管理（环境变量、设置）
- **logging**: 日志系统（基于 loguru）
- **storage**: 数据存储（Redis、数据库、缓存）
- **network**: 网络通信（HTTP、WebSocket）
- **utils**: 工具函数（JSON、重试、时间）
- **security**: 安全工具（哈希、JWT）

## 🔧 环境配置

主要配置项通过环境变量设置：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=my_platform
DB_USER=root
DB_PASSWORD=password

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/my_platform.log
```

## 🧪 测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行特定模块测试
uv run pytest tests/test_http_client.py -v
```

## 📖 更多信息

- 📖 [完整 API 文档](../docs/api/common.md)
- 💡 [使用示例](../docs/examples/)
- 🚀 [快速开始指南](../docs/getting-started/quickstart.md)
