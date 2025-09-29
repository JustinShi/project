# 🚀 快速开始

本指南将帮助您在 5 分钟内快速上手 Python 多项目平台！

## ⚡ 5分钟快速上手

### **第1步: 启动服务 (1分钟)**
```bash
# 启动所有服务
docker-compose up -d

# 检查服务状态
docker-compose ps
```

### **第2步: 安装依赖 (1分钟)**
```bash
# 安装项目依赖
make install

# 或使用 uv
uv sync
```

### **第3步: 运行测试 (1分钟)**
```bash
# 运行所有测试
make test

# 检查代码质量
make check-format
```

### **第4步: 使用 HTTP 客户端 (1分钟)**
```python
# 创建测试文件 test_quick.py
import asyncio
from common.network.http_client import HTTPClient

async def quick_test():
    async with HTTPClient() as client:
        response = await client.get('https://httpbin.org/get')
        print(f"Status: {response['status_code']}")
        print(f"Data: {response['data']}")

# 运行测试
asyncio.run(quick_test())
```

### **第5步: 查看项目结构 (1分钟)**
```bash
# 查看项目结构
tree /f

# 查看可用命令
make help
```

## 🎯 核心功能体验

### **1. HTTP 客户端使用**
```python
from common.network.http_client import HTTPClient
import asyncio

async def http_example():
    # 创建客户端
    client = HTTPClient(
        base_url="https://api.example.com",
        timeout=30.0,
        max_retries=3
    )
    
    # 发送请求
    async with client:
        # GET 请求
        response = await client.get('/users')
        print(f"Users: {response['data']}")
        
        # POST 请求
        user_data = {'name': 'John', 'email': 'john@example.com'}
        response = await client.post('/users', json_data=user_data)
        print(f"Created user: {response['data']}")

# 运行示例
asyncio.run(http_example())
```

### **2. Redis 缓存使用**
```python
from common.storage.redis_client import RedisClient
from common.storage.cache import CacheManager

async def redis_example():
    # 使用 Redis 客户端
    redis_client = RedisClient()
    await redis_client.set('key', 'value', expire=3600)
    value = await redis_client.get('key')
    print(f"Redis value: {value}")
    
    # 使用缓存管理器
    cache = CacheManager()
    await cache.set('cache_key', {'data': 'cached_value'})
    cached_data = await cache.get('cache_key')
    print(f"Cached data: {cached_data}")

# 运行示例
asyncio.run(redis_example())
```

### **3. 数据库操作**
```python
from common.storage.db_client import DatabaseManager

async def database_example():
    db = DatabaseManager()
    
    # 执行查询
    result = await db.execute_query("SELECT * FROM users LIMIT 5")
    print(f"Users: {result}")
    
    # 执行更新
    affected = await db.execute_update(
        "UPDATE users SET status = %s WHERE id = %s",
        ('active', 1)
    )
    print(f"Updated {affected} rows")

# 运行示例
asyncio.run(database_example())
```

## 🔧 常用命令速查

### **项目管理**
```bash
make help              # 查看所有命令
make install           # 安装依赖
make clean             # 清理临时文件
```

### **代码质量**
```bash
make format            # 格式化代码
make check-all         # 运行所有检查
make lint              # 代码质量检查
```

### **测试运行**
```bash
make test              # 运行所有测试
uv run pytest tests/   # 运行特定测试
uv run pytest -v       # 详细输出
```

### **服务管理**
```bash
docker-compose up -d   # 启动服务
docker-compose down    # 停止服务
docker-compose logs    # 查看日志
```

## 📁 项目结构概览

```
my_platform/
├── common/                 # 公共模块
│   ├── config/            # 配置管理
│   ├── logging/           # 日志管理
│   ├── storage/           # 数据存储
│   ├── network/           # 网络通信
│   ├── utils/             # 工具函数
│   └── security/          # 安全工具
├── projects/               # 子项目
│   └── trading/           # 交易项目
├── tests/                  # 测试文件
├── docs/                   # 文档目录
├── docker-compose.yml      # Docker 配置
├── pyproject.toml         # 项目配置
└── Makefile               # 构建脚本
```

## 🚨 快速故障排除

### **问题: 服务启动失败**
```bash
# 检查端口占用
netstat -an | findstr :6379
netstat -an | findstr :3306

# 重启服务
docker-compose down
docker-compose up -d
```

### **问题: 依赖安装失败**
```bash
# 清理缓存
uv cache clean

# 重新安装
uv sync --reinstall
```

### **问题: 测试运行失败**
```bash
# 检查环境
uv run python -c "import common; print('OK')"

# 运行单个测试
uv run pytest tests/test_http_client.py -v
```

## 📚 下一步学习

快速体验完成后，建议您：

1. **深入学习**: [开发指南](../development/setup.md)
2. **API 参考**: [公共模块](../api/common.md)
3. **配置详解**: [配置说明](configuration.md)
4. **部署指南**: [Docker 部署](../deployment/docker.md)

## 🎉 恭喜！

您已经成功体验了 Python 多项目平台的核心功能！

**接下来您可以：**
- 开发自己的业务逻辑
- 扩展公共模块功能
- 添加新的子项目
- 部署到生产环境

---

🚀 **继续探索** → [开发指南](../development/setup.md)
