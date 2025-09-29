# 🐳 Docker 部署指南

本指南介绍如何使用 Docker 部署 Python 多项目平台。

## 🎯 部署概览

### **服务架构**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Python App   │    │     Redis       │    │    MySQL       │
│   (Port 8000)  │◄──►│   (Port 6379)   │    │   (Port 3306)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Docker Compose │
                    │   (Orchestrator)│
                    └─────────────────┘
```

### **容器服务**
- **应用容器**: Python 多项目平台
- **Redis 容器**: 缓存和状态管理
- **MySQL 容器**: 主数据库
- **PostgreSQL 容器**: 可选数据库

## 🚀 快速部署

### **1. 启动所有服务**
```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
```

### **2. 停止服务**
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### **3. 重启服务**
```bash
# 重启特定服务
docker-compose restart redis

# 重启所有服务
docker-compose restart
```

## 🔧 Docker Compose 配置

### **docker-compose.yml**
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
    command: redis-server --appendonly yes
    restart: unless-stopped
    networks:
      - my_platform_network

  # MySQL 服务
  mysql:
    image: mysql:8.0
    container_name: my_platform_mysql
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: my_platform
      MYSQL_USER: app_user
      MYSQL_PASSWORD: app_password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    networks:
      - my_platform_network

  # PostgreSQL 服务（可选）
  postgres:
    image: postgres:15-alpine
    container_name: my_platform_postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: my_platform
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: app_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - my_platform_network

  # Python 应用服务
  app:
    build: .
    container_name: my_platform_app
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USER=app_user
      - DB_PASSWORD=app_password
      - DB_NAME=my_platform
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

volumes:
  redis_data:
  mysql_data:
  postgres_data:
  app_logs:

networks:
  my_platform_network:
    driver: bridge
```

## 🐳 Dockerfile 配置

### **Dockerfile**
```dockerfile
# 使用 Python 3.11 官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv 包管理器
RUN pip install uv

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY common/ ./common/
COPY projects/ ./projects/
COPY tests/ ./tests/
COPY start.py ./

# 安装 Python 依赖
RUN uv sync --frozen

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "import common; print('OK')" || exit 1

# 启动命令
CMD ["uv", "run", "python", "start.py"]
```

## 🔧 环境配置

### **环境变量文件 (.env)**
```bash
# 应用配置
PROJECT_NAME=Python Multi-Project Platform
DEBUG=false
LOG_LEVEL=INFO

# Redis 配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# MySQL 配置
DB_HOST=mysql
DB_PORT=3306
DB_USER=app_user
DB_PASSWORD=app_password
DB_NAME=my_platform

# PostgreSQL 配置（可选）
PG_HOST=postgres
PG_PORT=5432
PG_USER=app_user
PG_PASSWORD=app_password
PG_DB=my_platform

# 应用端口
APP_PORT=8000
```

### **数据库初始化脚本 (init.sql)**
```sql
-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建用户日志表
CREATE TABLE IF NOT EXISTS user_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 插入示例数据
INSERT INTO users (username, email, password_hash) VALUES
('admin', 'admin@example.com', 'hashed_password_here'),
('test_user', 'test@example.com', 'hashed_password_here');
```

## 🚀 部署步骤

### **步骤 1: 环境准备**
```bash
# 确保 Docker 和 Docker Compose 已安装
docker --version
docker-compose --version

# 克隆项目
git clone https://github.com/your-repo/my_platform.git
cd my_platform
```

### **步骤 2: 配置环境**
```bash
# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
# 根据需要修改 .env 文件中的配置
```

### **步骤 3: 启动服务**
```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看启动日志
docker-compose logs -f app
```

### **步骤 4: 验证部署**
```bash
# 检查 Redis 连接
docker-compose exec app uv run python -c "
from common.storage.redis_client import RedisClient
import asyncio

async def test_redis():
    redis = RedisClient()
    await redis.connect()
    await redis.set('test', 'Hello Redis!')
    value = await redis.get('test')
    print(f'Redis test: {value}')
    await redis.disconnect()

asyncio.run(test_redis())
"

# 检查数据库连接
docker-compose exec app uv run python -c "
from common.storage.db_client import DatabaseManager
import asyncio

async def test_db():
    db = DatabaseManager()
    await db.connect()
    result = await db.execute_query('SELECT COUNT(*) as count FROM users')
    print(f'Database test: {result}')
    await db.disconnect()

asyncio.run(test_db())
"
```

## 📊 监控和管理

### **查看服务状态**
```bash
# 查看所有容器状态
docker-compose ps

# 查看特定服务日志
docker-compose logs -f redis
docker-compose logs -f mysql
docker-compose logs -f app

# 查看资源使用情况
docker stats
```

### **服务管理命令**
```bash
# 重启特定服务
docker-compose restart app

# 停止特定服务
docker-compose stop mysql

# 启动特定服务
docker-compose start mysql

# 重新构建服务
docker-compose build app
```

### **数据备份和恢复**
```bash
# 备份 MySQL 数据
docker-compose exec mysql mysqldump -u root -p my_platform > backup.sql

# 备份 Redis 数据
docker-compose exec redis redis-cli SAVE
docker cp my_platform_redis:/data/dump.rdb ./redis_backup.rdb

# 恢复 MySQL 数据
docker-compose exec -T mysql mysql -u root -p my_platform < backup.sql
```

## 🔒 安全配置

### **生产环境安全**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  redis:
    environment:
      - REDIS_PASSWORD=strong_password_here
    command: redis-server --requirepass ${REDIS_PASSWORD}
    
  mysql:
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      # 移除 init.sql 挂载（生产环境）
      
  app:
    environment:
      - DEBUG=false
      - LOG_LEVEL=WARNING
    # 移除源代码挂载（生产环境）
    # volumes:
    #   - .:/app
```

### **网络安全**
```yaml
# 限制端口暴露
services:
  app:
    ports:
      - "127.0.0.1:8000:8000"  # 只允许本地访问
      
  redis:
    ports: []  # 不暴露端口到主机
    
  mysql:
    ports: []  # 不暴露端口到主机
```

## 🚨 故障排除

### **常见问题**

#### **问题 1: 服务启动失败**
```bash
# 查看详细错误日志
docker-compose logs service_name

# 检查端口占用
netstat -an | grep :8000
netstat -an | grep :6379
netstat -an | grep :3306

# 清理并重新启动
docker-compose down
docker-compose up -d --build
```

#### **问题 2: 数据库连接失败**
```bash
# 检查数据库服务状态
docker-compose exec mysql mysql -u root -p -e "SHOW DATABASES;"

# 检查网络连接
docker-compose exec app ping mysql
docker-compose exec app ping redis
```

#### **问题 3: 应用启动失败**
```bash
# 检查依赖安装
docker-compose exec app uv sync

# 检查 Python 环境
docker-compose exec app python --version
docker-compose exec app uv run python -c "import common"
```

### **调试模式**
```bash
# 以调试模式启动
docker-compose run --rm app uv run python -c "
import common
print('Common module loaded successfully')
from common.config.settings import config
print(f'Config loaded: {config.PROJECT_NAME}')
"
```

## 📈 性能优化

### **资源限制**
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
          
  redis:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
```

### **缓存优化**
```yaml
services:
  redis:
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

## 🔄 更新部署

### **滚动更新**
```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose up -d --build

# 检查更新状态
docker-compose ps
```

### **零停机部署**
```yaml
# docker-compose.yml
services:
  app:
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

## 📚 相关链接

- [快速开始](../getting-started/quickstart.md)
- [配置说明](../getting-started/configuration.md)
- [API 参考](../api/common.md)
- [生产环境部署](production.md)

---

🐳 **开始部署** → 运行 `docker-compose up -d` 启动所有服务
