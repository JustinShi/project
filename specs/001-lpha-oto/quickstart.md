# Quick Start Guide
# 币安Alpha代币OTO交易系统 - 开发环境搭建

**Branch**: `001-lpha-oto` | **Date**: 2025-10-09

---

## 目录

1. [环境要求](#环境要求)
2. [快速安装](#快速安装)
3. [数据库设置](#数据库设置)
4. [配置说明](#配置说明)
5. [运行系统](#运行系统)
6. [测试验证](#测试验证)
7. [常见问题](#常见问题)

---

## 环境要求

### 必需软件

| 软件 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 应用运行时 |
| PostgreSQL | 14+ | 主数据库 |
| Redis | 7.0+ | 缓存层 |
| uv | 最新版 | Python包管理器 |

### 可选工具

- Docker & Docker Compose（推荐，用于快速启动数据库）
- Postman/Insomnia（API测试）
- Redis Desktop Manager（Redis可视化）

---

## 快速安装

### 1. 克隆代码（假设已完成）

```bash
cd C:\Users\JustinShi\Pyproject
```

### 2. 安装Python依赖

使用`uv`安装项目依赖：

```bash
# 安装所有依赖
uv sync

# 或者分步安装
uv pip install -e .
```

**主要依赖** (将在`pyproject.toml`中定义):

```toml
[project]
name = "binance-alpha-oto-trading"
version = "0.1.0"
description = "币安Alpha代币OTO订单自动交易系统"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.29.0",  # PostgreSQL异步驱动
    "redis>=5.0.0",
    "websockets>=12.0",
    "httpx>=0.25.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-statemachine>=2.1.0",
    "cryptography>=41.0.0",
    "structlog>=23.2.0",
    "alembic>=1.12.0",
    "click>=8.1.0",  # CLI工具
    "aiolimiter>=1.1.0",  # API限流
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "ruff>=0.1.0",  # 代码格式化和linting
    "mypy>=1.7.0",  # 类型检查
    "pre-commit>=3.5.0",
]
```

### 3. 启动数据库（Docker方式）

创建`docker-compose.yml`（如果不存在）：

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    container_name: binance_postgres
    environment:
      POSTGRES_DB: binance_trading
      POSTGRES_USER: trader
      POSTGRES_PASSWORD: trader_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U trader"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: binance_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

启动数据库：

```bash
docker-compose up -d
```

验证服务运行：

```bash
docker-compose ps
```

---

## 数据库设置

### 1. 创建数据库（如果使用Docker，已自动创建）

如果手动安装PostgreSQL：

```bash
# Windows (PowerShell)
psql -U postgres
CREATE DATABASE binance_trading;
CREATE USER trader WITH PASSWORD 'trader_password';
GRANT ALL PRIVILEGES ON DATABASE binance_trading TO trader;
```

### 2. 配置环境变量

创建`.env`文件（复制`.env.example`）：

```bash
# .env 文件内容

# 数据库配置
DATABASE_URL=postgresql+asyncpg://trader:trader_password@localhost:5432/binance_trading

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 加密密钥（使用以下命令生成）
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-generated-32-byte-base64-key-here

# 应用配置
APP_ENV=development
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# 币安API配置（可选，测试时可用mock）
BINANCE_BASE_URL=https://www.binance.com
BINANCE_WS_PRICE_URL=wss://nbstream.binance.com/w3w/wsa/stream
BINANCE_WS_ORDER_URL=wss://nbstream.binance.com/w3w/stream
```

### 3. 生成加密密钥

```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

将输出的密钥复制到`.env`的`ENCRYPTION_KEY`字段。

### 4. 运行数据库迁移

初始化Alembic（首次）：

```bash
uv run alembic init alembic
```

配置`alembic.ini`：

```ini
# alembic.ini
sqlalchemy.url = postgresql+asyncpg://trader:trader_password@localhost:5432/binance_trading
```

或者使用环境变量（推荐）：

修改`alembic/env.py`：

```python
from binance.config.settings import settings

config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))
```

创建初始迁移：

```bash
uv run alembic revision --autogenerate -m "Initial schema"
```

应用迁移：

```bash
uv run alembic upgrade head
```

---

## 配置说明

### 系统配置文件

**位置**: `src/binance/config/settings.py`

使用Pydantic Settings管理配置：

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # 数据库
    database_url: str
    
    # Redis
    redis_url: str
    
    # 加密
    encryption_key: str
    
    # 应用
    app_env: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # 币安API
    binance_base_url: str = "https://www.binance.com"
    binance_ws_price_url: str = "wss://nbstream.binance.com/w3w/wsa/stream"
    binance_ws_order_url: str = "wss://nbstream.binance.com/w3w/stream"

settings = Settings()
```

### 初始化代币映射数据

在数据库中预置常用代币映射：

```bash
uv run python -m src.binance.cli.main token add \
  --symbol-short KOGE \
  --token-name "Kog Coin" \
  --order-api-symbol ALPHA_373 \
  --websocket-symbol alpha_373usdt \
  --alpha-id ALPHA_373
```

或使用SQL直接插入：

```sql
INSERT INTO token_mappings (symbol_short, token_name, order_api_symbol, websocket_symbol, alpha_id)
VALUES 
  ('KOGE', 'Kog Coin', 'ALPHA_373', 'alpha_373usdt', 'ALPHA_373'),
  -- 添加更多代币...
```

---

## 运行系统

### 1. 启动API服务

```bash
# 开发模式（热重载）
uv run uvicorn src.binance.api.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uv run uvicorn src.binance.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. 访问API文档

浏览器打开：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 创建测试用户

使用CLI工具或API创建用户：

```bash
# CLI方式
uv run python -m src.binance.cli.main user create \
  --username testuser \
  --display-name "Test User" \
  --email test@example.com

# 或使用API (curl示例)
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "displayName": "Test User"}'
```

### 4. 配置用户认证信息

```bash
# CLI方式
uv run python -m src.binance.cli.main user set-credentials \
  --user-id 1 \
  --headers-json '{"X-Token": "abc123"}' \
  --cookies "session=xyz789"

# 或使用API
curl -X PUT http://localhost:8000/api/v1/users/1/credentials \
  -H "Content-Type: application/json" \
  -d '{
    "headers": {"X-Token": "abc123"},
    "cookies": "session=xyz789"
  }'
```

### 5. 配置交易参数

```bash
curl -X PUT http://localhost:8000/api/v1/users/1/config \
  -H "Content-Type: application/json" \
  -d '{
    "tokenSymbolShort": "KOGE",
    "targetVolume": "10000.0",
    "priceOffsetMode": "percentage",
    "buyOffsetValue": "0.5",
    "sellOffsetValue": "0.5",
    "orderQuantity": "100.0",
    "timeoutSeconds": 300,
    "priceVolatilityThreshold": "2.0"
  }'
```

### 6. 启动自动交易

```bash
curl -X POST http://localhost:8000/api/v1/users/1/trading/start
```

### 7. 查看交易状态

```bash
curl http://localhost:8000/api/v1/users/1/trading/status
```

---

## 测试验证

### 1. 运行单元测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/unit/domain/test_order_state_machine.py

# 运行测试并查看覆盖率
uv run pytest --cov=src/binance --cov-report=html
```

### 2. 运行集成测试

```bash
# 需要先启动数据库和Redis
uv run pytest tests/integration/
```

### 3. 运行合约测试

```bash
# 测试币安API合约（使用mock）
uv run pytest tests/contract/test_binance_contracts.py
```

### 4. 代码质量检查

```bash
# Linting和格式化
uv run ruff check src/
uv run ruff format src/

# 类型检查
uv run mypy src/binance/
```

---

## 开发工作流

### 1. 创建功能分支

```bash
git checkout -b feature/001-lpha-oto-implementation
```

### 2. 开发循环

```bash
# 1. 编写测试
# tests/unit/domain/test_new_feature.py

# 2. 运行测试（应该失败）
uv run pytest tests/unit/domain/test_new_feature.py

# 3. 实现功能
# src/binance/domain/...

# 4. 再次运行测试（应该通过）
uv run pytest tests/unit/domain/test_new_feature.py

# 5. 代码质量检查
uv run ruff check src/
uv run mypy src/binance/
```

### 3. 数据库迁移工作流

```bash
# 1. 修改ORM模型
# src/binance/infrastructure/database/models.py

# 2. 生成迁移脚本
uv run alembic revision --autogenerate -m "Add new field to users table"

# 3. 检查生成的迁移脚本
# alembic/versions/xxx_add_new_field.py

# 4. 应用迁移
uv run alembic upgrade head

# 5. 如需回滚
uv run alembic downgrade -1
```

### 4. 提交代码

```bash
git add .
git commit -m "feat: implement order state machine"
git push origin feature/001-lpha-oto-implementation
```

---

## CLI命令参考

系统提供CLI工具用于管理和维护：

### 用户管理

```bash
# 创建用户
uv run python -m src.binance.cli.main user create --username john --email john@example.com

# 列出所有用户
uv run python -m src.binance.cli.main user list

# 查看用户详情
uv run python -m src.binance.cli.main user show --user-id 1

# 更新认证信息
uv run python -m src.binance.cli.main user set-credentials --user-id 1 --headers-json '{}' --cookies 'session=xxx'
```

### 代币映射管理

```bash
# 添加代币映射
uv run python -m src.binance.cli.main token add \
  --symbol-short KOGE \
  --order-api-symbol ALPHA_373 \
  --websocket-symbol alpha_373usdt

# 列出所有映射
uv run python -m src.binance.cli.main token list

# 刷新精度缓存
uv run python -m src.binance.cli.main token refresh-precision --symbol KOGE
```

### 交易控制

```bash
# 启动交易
uv run python -m src.binance.cli.main trading start --user-id 1

# 停止交易
uv run python -m src.binance.cli.main trading stop --user-id 1

# 查看状态
uv run python -m src.binance.cli.main trading status --user-id 1
```

### 统计查询

```bash
# 查看用户统计
uv run python -m src.binance.cli.main stats show --user-id 1

# 查看订单历史
uv run python -m src.binance.cli.main orders list --user-id 1 --limit 20
```

---

## 常见问题

### Q1: 数据库连接失败

**错误**: `asyncpg.exceptions.ConnectionRefusedError`

**解决**:
```bash
# 检查PostgreSQL是否运行
docker-compose ps

# 重启PostgreSQL
docker-compose restart postgres

# 检查连接字符串
echo $DATABASE_URL
```

### Q2: Redis连接失败

**错误**: `redis.exceptions.ConnectionError`

**解决**:
```bash
# 检查Redis是否运行
docker-compose ps

# 测试Redis连接
redis-cli ping

# 重启Redis
docker-compose restart redis
```

### Q3: 迁移失败

**错误**: `alembic.util.exc.CommandError`

**解决**:
```bash
# 检查当前数据库版本
uv run alembic current

# 查看迁移历史
uv run alembic history

# 手动回滚到特定版本
uv run alembic downgrade <revision_id>

# 删除所有表重新开始（警告：会丢失数据）
# psql -U trader -d binance_trading -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
# uv run alembic upgrade head
```

### Q4: 加密密钥错误

**错误**: `cryptography.fernet.InvalidToken`

**解决**:
```bash
# 重新生成密钥
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 更新.env文件
# 注意：更改密钥会导致已加密数据无法解密，需重新设置用户认证信息
```

### Q5: WebSocket连接失败（开发阶段）

**解决**:
```python
# 在开发阶段，可以使用mock模式
# 在.env中设置
MOCK_WEBSOCKET=true

# 或在代码中使用测试替身
# tests/integration/test_websocket.py 中有mock示例
```

---

## 下一步

开发环境搭建完成后，您可以：

1. ✅ 查看[实施计划](./plan.md)了解整体架构
2. ✅ 查看[数据模型设计](./data-model.md)了解数据结构
3. ✅ 查看[API合约](./contracts/)了解接口定义
4. ✅ 开始实施（等待`/speckit.tasks`生成任务分解）

**注意**: 本指南基于规划阶段，实际文件路径和命令在实施后可能需要调整。

---

**文档版本**: 1.0.0  
**最后更新**: 2025-10-09

