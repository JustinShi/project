# 🚀 生产环境部署指南

本文档介绍如何将 Python 多项目平台部署到生产环境。

## 📋 生产环境要求

### 系统要求

- **操作系统**: Ubuntu 20.04 LTS 或 CentOS 8+
- **CPU**: 4 核心以上 (推荐 8 核心)
- **内存**: 16GB RAM 以上 (推荐 32GB)
- **存储**: 100GB SSD 以上 (推荐 NVMe SSD)
- **网络**: 稳定的网络连接，推荐专线

### 软件要求

- **Python**: 3.9+ (推荐 3.11)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Nginx**: 1.18+
- **Redis**: 6.0+
- **MySQL**: 8.0+ 或 PostgreSQL 13+

## 🏗️ 生产环境架构

### 推荐架构

```
                    [负载均衡器]
                         |
                    [Nginx 反向代理]
                         |
        ┌────────────────┼────────────────┐
        |                |                |
    [Web 服务器]    [Web 服务器]    [Web 服务器]
        |                |                |
    [应用容器]      [应用容器]      [应用容器]
        |                |                |
    ┌─────────────────────────────────────────┐
    |             共享服务层                    |
    |  [Redis]  [MySQL]  [PostgreSQL]        |
    └─────────────────────────────────────────┘
```

### 容器化部署

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  # 应用服务
  app:
    build: .
    image: myplatform:latest
    container_name: myplatform_app
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - REDIS_HOST=redis
      - MYSQL_HOST=mysql
      - POSTGRES_HOST=postgres
    depends_on:
      - redis
      - mysql
      - postgres
    networks:
      - app_network
    volumes:
      - app_data:/app/data
      - app_logs:/app/logs

  # Redis 服务
  redis:
    image: redis:7-alpine
    container_name: myplatform_redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - app_network

  # MySQL 服务
  mysql:
    image: mysql:8.0
    container_name: myplatform_mysql
    restart: unless-stopped
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DATABASE}
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app_network

  # PostgreSQL 服务
  postgres:
    image: postgres:15-alpine
    container_name: myplatform_postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app_network

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: myplatform_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - app_logs:/var/log/nginx
    depends_on:
      - app
    networks:
      - app_network

volumes:
  app_data:
  app_logs:
  redis_data:
  mysql_data:
  postgres_data:

networks:
  app_network:
    driver: bridge
```

## 🔧 生产环境配置

### 环境变量配置

```bash
# .env.production
# 应用配置
NODE_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# 数据库配置
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=myplatform_prod
MYSQL_USERNAME=myplatform_user
MYSQL_PASSWORD=strong_password_here
MYSQL_ROOT_PASSWORD=very_strong_root_password

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DATABASE=myplatform_prod
POSTGRES_USERNAME=myplatform_user
POSTGRES_PASSWORD=strong_password_here

# Redis 配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=strong_redis_password
REDIS_DB=0

# 安全配置
SECRET_KEY=your_super_secret_key_here
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here

# 外部服务配置
API_RATE_LIMIT=1000
SESSION_TIMEOUT=3600
```

### Nginx 配置

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # 基本设置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # 上游服务器
    upstream app_servers {
        server app:8000;
        # 可以添加更多应用服务器
        # server app2:8000;
        # server app3:8000;
    }

    # HTTP 服务器
    server {
        listen 80;
        server_name your-domain.com;
        
        # 重定向到 HTTPS
        return 301 https://$server_name$request_uri;
    }

    # HTTPS 服务器
    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL 证书
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # 安全头
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;

        # 客户端最大请求大小
        client_max_body_size 100M;

        # 代理设置
        location / {
            proxy_pass http://app_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 超时设置
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # 静态文件
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # 健康检查
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### 应用配置

```python
# config/production.py
from common.config.settings import BaseSettings

class ProductionSettings(BaseSettings):
    """生产环境配置"""
    
    # 环境标识
    ENV: str = "production"
    DEBUG: bool = False
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/app.log"
    LOG_MAX_SIZE: str = "100MB"
    LOG_BACKUP_COUNT: int = 5
    
    # 安全配置
    SECRET_KEY: str
    JWT_SECRET: str
    ENCRYPTION_KEY: str
    
    # 数据库配置
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str
    MYSQL_USERNAME: str
    MYSQL_PASSWORD: str
    
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DATABASE: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    
    # Redis 配置
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str
    REDIS_DB: int = 0
    
    # 性能配置
    WORKER_PROCESSES: int = 4
    WORKER_THREADS: int = 2
    MAX_REQUESTS: int = 1000
    MAX_REQUESTS_JITTER: int = 100
    
    # 监控配置
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    HEALTH_CHECK_INTERVAL: int = 30
    
    class Config:
        env_file = ".env.production"
```

## 🚀 部署流程

### 1. 环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y curl wget git unzip

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 创建应用目录
sudo mkdir -p /opt/myplatform
sudo chown $USER:$USER /opt/myplatform
cd /opt/myplatform
```

### 2. 代码部署

```bash
# 克隆代码
git clone https://github.com/your-username/myplatform.git .

# 切换到生产分支
git checkout production

# 创建生产环境配置
cp .env.example .env.production
# 编辑 .env.production 文件

# 创建 SSL 证书目录
mkdir -p ssl
# 将 SSL 证书文件放入 ssl 目录
```

### 3. 构建和启动

```bash
# 构建镜像
docker-compose -f docker-compose.production.yml build

# 启动服务
docker-compose -f docker-compose.production.yml up -d

# 检查服务状态
docker-compose -f docker-compose.production.yml ps

# 查看日志
docker-compose -f docker-compose.production.yml logs -f
```

### 4. 数据库初始化

```bash
# 等待数据库服务启动
sleep 30

# 运行数据库迁移
docker-compose -f docker-compose.production.yml exec app python manage.py migrate

# 创建超级用户
docker-compose -f docker-compose.production.yml exec app python manage.py createsuperuser

# 初始化基础数据
docker-compose -f docker-compose.production.yml exec app python manage.py loaddata initial_data
```

## 📊 监控和日志

### 应用监控

```python
# monitoring/app_monitor.py
import psutil
import time
from common.logging.logger import get_logger

logger = get_logger(__name__)

class AppMonitor:
    """应用监控器"""
    
    def __init__(self):
        self.logger = logger
    
    def get_system_metrics(self):
        """获取系统指标"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict()
        }
    
    def get_process_metrics(self):
        """获取进程指标"""
        process = psutil.Process()
        return {
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "num_threads": process.num_threads(),
            "open_files": len(process.open_files()),
            "connections": len(process.connections())
        }
    
    def log_metrics(self):
        """记录监控指标"""
        system_metrics = self.get_system_metrics()
        process_metrics = self.get_process_metrics()
        
        self.logger.info("System metrics", extra={
            "system": system_metrics,
            "process": process_metrics
        })
    
    def start_monitoring(self, interval=60):
        """开始监控"""
        while True:
            try:
                self.log_metrics()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(interval)
```

### 日志管理

```python
# logging/production_logger.py
import logging
import logging.handlers
import os
from datetime import datetime

def setup_production_logging():
    """设置生产环境日志"""
    
    # 创建日志目录
    log_dir = "/app/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # 应用日志
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    
    # 文件处理器
    app_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=100*1024*1024,  # 100MB
        backupCount=5
    )
    
    # 格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    app_handler.setFormatter(formatter)
    
    app_logger.addHandler(app_handler)
    
    # 错误日志
    error_logger = logging.getLogger("error")
    error_logger.setLevel(logging.ERROR)
    
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "error.log"),
        maxBytes=100*1024*1024,
        backupCount=5
    )
    error_handler.setFormatter(formatter)
    
    error_logger.addHandler(error_handler)
    
    return app_logger, error_logger
```

### 健康检查

```python
# health/health_check.py
import asyncio
import aiohttp
from common.storage.redis_client import RedisClient
from common.storage.db_client import DatabaseManager

class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.redis_client = RedisClient()
        self.db_manager = DatabaseManager()
    
    async def check_redis(self):
        """检查 Redis 连接"""
        try:
            await self.redis_client.ping()
            return {"status": "healthy", "service": "redis"}
        except Exception as e:
            return {"status": "unhealthy", "service": "redis", "error": str(e)}
    
    async def check_database(self):
        """检查数据库连接"""
        try:
            self.db_manager.ping()
            return {"status": "healthy", "service": "database"}
        except Exception as e:
            return {"status": "unhealthy", "service": "database", "error": str(e)}
    
    async def check_external_apis(self):
        """检查外部 API"""
        results = []
        
        # 检查示例 API
        apis = [
            "https://httpbin.org/status/200",
            "https://jsonplaceholder.typicode.com/posts/1"
        ]
        
        async with aiohttp.ClientSession() as session:
            for api in apis:
                try:
                    async with session.get(api, timeout=5) as response:
                        if response.status == 200:
                            results.append({
                                "status": "healthy",
                                "service": api,
                                "response_time": response.headers.get("X-Response-Time", "N/A")
                            })
                        else:
                            results.append({
                                "status": "unhealthy",
                                "service": api,
                                "error": f"HTTP {response.status}"
                            })
                except Exception as e:
                    results.append({
                        "status": "unhealthy",
                        "service": api,
                        "error": str(e)
                    })
        
        return results
    
    async def comprehensive_check(self):
        """综合健康检查"""
        redis_status = await self.check_redis()
        db_status = await self.check_database()
        api_status = await self.check_external_apis()
        
        overall_status = "healthy"
        if any(result["status"] == "unhealthy" for result in [redis_status, db_status] + api_status):
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "redis": redis_status,
                "database": db_status,
                "external_apis": api_status
            }
        }
```

## 🔒 安全配置

### 防火墙配置

```bash
# 安装 UFW
sudo apt install ufw

# 设置默认策略
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 允许 SSH
sudo ufw allow ssh

# 允许 HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# 允许应用端口
sudo ufw allow 8000

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### SSL 证书配置

```bash
# 使用 Let's Encrypt 获取免费证书
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

### 安全头配置

```nginx
# 在 nginx.conf 中添加安全头
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;
```

## 📈 性能优化

### 应用优化

```python
# 异步处理
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 线程池
executor = ThreadPoolExecutor(max_workers=10)

async def process_data_async(data_list):
    """异步处理数据"""
    tasks = []
    for data in data_list:
        task = asyncio.create_task(process_single_item(data))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

def process_single_item(data):
    """处理单个数据项"""
    # 处理逻辑
    pass
```

### 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 分区表
CREATE TABLE logs (
    id INT AUTO_INCREMENT,
    log_date DATE,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (YEAR(log_date)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025)
);
```

### 缓存优化

```python
# 多级缓存策略
from common.storage.cache import CacheManager

cache_manager = CacheManager()

# 内存缓存 (快速访问)
cache_manager.add_layer("memory", MemoryCache(max_size=1000, ttl=300))

# Redis 缓存 (持久化)
cache_manager.add_layer("redis", RedisCache(ttl=3600))

# 数据库 (最终存储)
def get_data_with_cache(key):
    """带缓存的数据获取"""
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

## 🚨 故障排除

### 常见问题

#### 1. 服务无法启动

```bash
# 检查日志
docker-compose -f docker-compose.production.yml logs app

# 检查端口占用
sudo netstat -tlnp | grep :8000

# 检查配置文件
docker-compose -f docker-compose.production.yml config
```

#### 2. 数据库连接失败

```bash
# 检查数据库状态
docker-compose -f docker-compose.production.yml exec mysql mysql -u root -p -e "SHOW PROCESSLIST;"

# 检查网络连接
docker-compose -f docker-compose.production.yml exec app ping mysql

# 检查环境变量
docker-compose -f docker-compose.production.yml exec app env | grep MYSQL
```

#### 3. Redis 连接失败

```bash
# 检查 Redis 状态
docker-compose -f docker-compose.production.yml exec redis redis-cli ping

# 检查密码配置
docker-compose -f docker-compose.production.yml exec redis redis-cli -a your_password ping

# 检查内存使用
docker-compose -f docker-compose.production.yml exec redis redis-cli info memory
```

### 性能问题诊断

```bash
# 查看容器资源使用
docker stats

# 查看系统资源使用
htop
iotop
nethogs

# 查看网络连接
ss -tuln
netstat -i
```

## 📚 下一步

- 查看 [Docker 部署指南](docker.md)
- 了解 [监控指南](monitoring.md)
- 阅读 [快速开始](../getting-started/quickstart.md)

## 🤝 获取帮助

如果遇到部署问题：

1. 检查系统日志
2. 查看容器日志
3. 验证配置文件
4. 联系技术支持
