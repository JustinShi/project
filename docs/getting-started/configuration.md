# ⚙️ 配置说明

本指南详细介绍 Python 多项目平台的配置选项和设置方法。

## 🎯 配置概览

### **配置文件类型**
- **环境变量文件** (`.env`) - 环境特定配置
- **项目配置文件** (`pyproject.toml`) - 项目依赖和工具配置
- **Docker 配置** (`docker-compose.yml`) - 容器化服务配置
- **代码质量配置** (`.flake8`, `.pre-commit-config.yaml`) - 开发工具配置

### **配置优先级**
1. 环境变量 (最高优先级)
2. `.env` 文件
3. 默认值 (最低优先级)

## 🔧 环境变量配置

### **基础环境变量文件 (.env)**

```bash
# ========================================
# Python 多项目平台配置
# ========================================

# 项目基本信息
PROJECT_NAME=Python Multi-Project Platform
PROJECT_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_FORMAT=json
LOG_ROTATION=100 MB
LOG_RETENTION=30 days

# ========================================
# Redis 配置
# ========================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_SSL=false
REDIS_TIMEOUT=5.0
REDIS_MAX_CONNECTIONS=10

# ========================================
# 数据库配置
# ========================================
# MySQL 配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=my_platform
DB_CHARSET=utf8mb4
DB_COLLATION=utf8mb4_unicode_ci
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# PostgreSQL 配置（可选）
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=
PG_DB=my_platform
PG_SCHEMA=public
PG_POOL_SIZE=5
PG_MAX_OVERFLOW=10

# ========================================
# 网络配置
# ========================================
# HTTP 客户端配置
HTTP_TIMEOUT=30.0
HTTP_MAX_RETRIES=3
HTTP_RETRY_DELAY=1.0
HTTP_BACKOFF_FACTOR=2.0

# WebSocket 配置
WS_PING_INTERVAL=30
WS_PING_TIMEOUT=10
WS_CLOSE_TIMEOUT=10

# ========================================
# 安全配置
# ========================================
# JWT 配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRES_IN=3600
JWT_REFRESH_EXPIRES_IN=86400

# 密码配置
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGITS=true
PASSWORD_REQUIRE_SPECIAL=true

# ========================================
# 缓存配置
# ========================================
CACHE_DEFAULT_TTL=3600
CACHE_MAX_SIZE=1000
CACHE_ENABLE_COMPRESSION=true
CACHE_COMPRESSION_THRESHOLD=1024

# ========================================
# 性能配置
# ========================================
# 异步配置
ASYNC_MAX_WORKERS=10
ASYNC_QUEUE_SIZE=100
ASYNC_TIMEOUT=60.0

# 连接池配置
CONNECTION_POOL_SIZE=20
CONNECTION_POOL_MAX_OVERFLOW=30
CONNECTION_POOL_TIMEOUT=30.0
```

### **开发环境配置 (.env.development)**

```bash
# 开发环境配置
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# 本地服务配置
REDIS_HOST=localhost
REDIS_PORT=6379
DB_HOST=localhost
DB_PORT=3306

# 开发工具配置
ENABLE_HOT_RELOAD=true
ENABLE_DEBUG_TOOLBAR=true
ENABLE_PROFILING=false
```

### **测试环境配置 (.env.test)**

```bash
# 测试环境配置
ENVIRONMENT=test
DEBUG=false
LOG_LEVEL=WARNING

# 测试数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=my_platform_test
REDIS_DB=1

# 测试配置
ENABLE_TEST_LOGGING=false
TEST_TIMEOUT=30.0
```

### **生产环境配置 (.env.production)**

```bash
# 生产环境配置
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# 生产服务配置
REDIS_HOST=redis.production.com
REDIS_PORT=6379
REDIS_PASSWORD=strong_password_here
DB_HOST=db.production.com
DB_PORT=3306
DB_PASSWORD=strong_db_password

# 安全配置
JWT_SECRET_KEY=very-long-and-random-secret-key-here
ENABLE_HTTPS=true
ENABLE_CORS=false
```

## 📁 项目配置文件

### **pyproject.toml 配置**

```toml
[project]
name = "my_platform"
version = "1.0.0"
description = "Python Multi-Project Platform"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "redis>=4.5.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "loguru>=0.7.0",
    "sqlalchemy>=2.0.0",
    "pymysql>=1.1.0",
    "psycopg2-binary>=2.9.0",
    "aiohttp>=3.8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=5.0.0",
    "bandit>=1.7.0",
    "mypy>=1.3.0",
    "pre-commit>=3.0.0",
]

# 构建配置
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["common", "projects"]

# Black 代码格式化配置
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

# isort 导入排序配置
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["common", "projects"]
known_third_party = ["aiohttp", "redis", "sqlalchemy"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]

# pytest 测试配置
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "--disable-warnings",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

# mypy 类型检查配置
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "redis.*",
    "sqlalchemy.*",
    "aiohttp.*"
]
ignore_missing_imports = true

# bandit 安全检查配置
[tool.bandit]
exclude_dirs = ["tests", ".venv", "build", "dist"]
skips = ["B101", "B601"]
```

## 🐳 Docker 配置

### **docker-compose.yml 配置**

```yaml
version: '3.8'

services:
  # Redis 服务
  redis:
    image: redis:7-alpine
    container_name: my_platform_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    restart: unless-stopped
    networks:
      - my_platform_network
    environment:
      - TZ=Asia/Shanghai

  # MySQL 服务
  mysql:
    image: mysql:8.0
    container_name: my_platform_mysql
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
      TZ: Asia/Shanghai
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    networks:
      - my_platform_network
    command: >
      --default-authentication-plugin=mysql_native_password
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --innodb-buffer-pool-size=256M
      --max-connections=200

  # Python 应用服务
  app:
    build: .
    container_name: my_platform_app
    ports:
      - "${APP_PORT:-8000}:8000"
    environment:
      # 从 .env 文件加载环境变量
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=${DB_NAME}
      - LOG_LEVEL=${LOG_LEVEL}
      - DEBUG=${DEBUG}
    volumes:
      - .:/app
      - app_logs:/app/logs
    depends_on:
      - redis
      - mysql
    restart: unless-stopped
    networks:
      - my_platform_network
    command: uv run python start.py
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

volumes:
  redis_data:
  mysql_data:
  app_logs:

networks:
  my_platform_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 🛠️ 代码质量工具配置

### **.flake8 配置**

```ini
[flake8]
max-line-length = 88
extend-ignore = 
    E203,  # whitespace before ':'
    W503,  # line break before binary operator
    E501,  # line too long (handled by black)
    F401,  # imported but unused
    F403,  # wildcard import
    F405   # name may be undefined, or defined from star imports
exclude = 
    .git,
    __pycache__,
    .venv,
    .mypy_cache,
    build,
    dist,
    *.egg-info
per-file-ignores =
    __init__.py:F401
    tests/*:F401,F403,F405
max-complexity = 10
statistics = True
count = True
```

### **.pre-commit-config.yaml 配置**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements
      - id: check-case-conflict
      - id: check-docstring-first
      - id: check-json
      - id: check-toml

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503,E501,F401,F403,F405]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, ., -f, json, -o, bandit-report.json]
        exclude: tests/

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports, --no-strict-optional]
```

## 🔐 安全配置

### **JWT 配置**

```python
# JWT 配置示例
JWT_CONFIG = {
    "secret_key": os.getenv("JWT_SECRET_KEY", "default-secret-key"),
    "algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
    "expires_in": int(os.getenv("JWT_EXPIRES_IN", 3600)),
    "refresh_expires_in": int(os.getenv("JWT_REFRESH_EXPIRES_IN", 86400)),
    "issuer": os.getenv("JWT_ISSUER", "my_platform"),
    "audience": os.getenv("JWT_AUDIENCE", "my_platform_users"),
}
```

### **密码策略配置**

```python
# 密码策略配置
PASSWORD_POLICY = {
    "min_length": int(os.getenv("PASSWORD_MIN_LENGTH", 8)),
    "require_uppercase": os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true",
    "require_lowercase": os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true",
    "require_digits": os.getenv("PASSWORD_REQUIRE_DIGITS", "true").lower() == "true",
    "require_special": os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true",
    "max_length": int(os.getenv("PASSWORD_MAX_LENGTH", 128)),
}
```

## 📊 监控和日志配置

### **日志配置**

```python
# 日志配置示例
LOG_CONFIG = {
    "handlers": [
        {
            "sink": os.getenv("LOG_FILE", "logs/app.log"),
            "rotation": os.getenv("LOG_ROTATION", "100 MB"),
            "retention": os.getenv("LOG_RETENTION", "30 days"),
            "compression": "zip",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            "level": os.getenv("LOG_LEVEL", "INFO"),
        },
        {
            "sink": "logs/error.log",
            "level": "ERROR",
            "rotation": "50 MB",
            "retention": "90 days",
            "compression": "zip",
        },
        {
            "sink": "logs/access.log",
            "level": "INFO",
            "rotation": "100 MB",
            "retention": "30 days",
            "compression": "zip",
            "filter": lambda record: "access" in record["extra"],
        }
    ],
    "extra": {
        "project": os.getenv("PROJECT_NAME", "my_platform"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": os.getenv("PROJECT_VERSION", "1.0.0"),
    }
}
```

### **性能监控配置**

```python
# 性能监控配置
PERFORMANCE_CONFIG = {
    "enable_profiling": os.getenv("ENABLE_PROFILING", "false").lower() == "true",
    "profile_output_dir": "profiles",
    "max_profile_files": 10,
    "enable_metrics": os.getenv("ENABLE_METRICS", "true").lower() == "true",
    "metrics_interval": int(os.getenv("METRICS_INTERVAL", 60)),
}
```

## 🔄 配置管理最佳实践

### **1. 环境分离**
- 使用不同的 `.env` 文件管理不同环境
- 生产环境敏感信息通过环境变量注入
- 开发环境使用本地配置文件

### **2. 配置验证**
- 使用 Pydantic 验证配置值
- 设置合理的默认值
- 验证必需配置项

### **3. 安全考虑**
- 敏感信息不提交到版本控制
- 使用强密码和密钥
- 定期轮换密钥和密码

### **4. 配置文档**
- 记录所有配置选项
- 说明配置项的作用和影响
- 提供配置示例

## 🚨 常见配置问题

### **问题 1: 环境变量未生效**
```bash
# 检查环境变量文件
cat .env

# 重新加载环境变量
source .env

# 或在 Python 中重新加载
import os
from dotenv import load_dotenv
load_dotenv(override=True)
```

### **问题 2: 配置值类型错误**
```python
# 使用 Pydantic 验证配置类型
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    DB_PORT: int = 3306
    
    @validator('DB_PORT')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
```

### **问题 3: 配置文件路径问题**
```python
# 使用绝对路径或相对于项目根目录的路径
import os
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).parent.parent

# 配置文件路径
CONFIG_FILE = BASE_DIR / ".env"
LOG_DIR = BASE_DIR / "logs"
```

## 📚 相关链接

- [安装指南](installation.md)
- [快速开始](quickstart.md)
- [Docker 部署](../deployment/docker.md)
- [代码质量工具](../development/code-quality.md)

---

⚙️ **开始配置** → 复制 `.env.example` 到 `.env` 并修改配置
