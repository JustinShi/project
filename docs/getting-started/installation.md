# 📦 安装指南

本指南将帮助您完整安装 Python 多项目平台及其所有依赖。

## 🎯 系统要求

### **操作系统**
- ✅ Windows 10/11 (推荐)
- ✅ macOS 10.15+
- ✅ Ubuntu 18.04+ / CentOS 7+

### **Python 版本**
- **必需**: Python 3.8+
- **推荐**: Python 3.9+ 或 3.10+
- **最新**: Python 3.11+ (最佳性能)

### **内存要求**
- **最低**: 4GB RAM
- **推荐**: 8GB+ RAM
- **开发**: 16GB+ RAM

### **磁盘空间**
- **基础安装**: 500MB
- **完整开发环境**: 2GB+
- **Docker 镜像**: 额外 1-2GB

## 🚀 快速安装

### **1. 克隆项目**
```bash
git clone https://github.com/your-repo/my_platform.git
cd my_platform
```

### **2. 安装 uv 包管理器**
```bash
# Windows (PowerShell)
winget install uv

# macOS
brew install uv

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### **3. 安装项目依赖**
```bash
# 同步依赖
uv sync

# 或使用 make 命令
make install
```

### **4. 启动服务**
```bash
# 启动 Docker 服务
docker-compose up -d

# 或使用启动脚本
python start.py
```

## 🔧 详细安装步骤

### **步骤 1: 环境准备**

#### **检查 Python 版本**
```bash
python --version
# 或
python3 --version
```

#### **检查 uv 安装**
```bash
uv --version
```

#### **检查 Docker**
```bash
docker --version
docker-compose --version
```

### **步骤 2: 项目设置**

#### **创建虚拟环境**
```bash
# 使用 uv 创建虚拟环境
uv venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 激活虚拟环境 (macOS/Linux)
source .venv/bin/activate
```

#### **安装依赖**
```bash
# 安装所有依赖
uv sync

# 安装开发依赖
uv sync --dev
```

### **步骤 3: 配置环境**

#### **复制环境变量文件**
```bash
cp .env.example .env
```

#### **编辑 .env 文件**
```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=my_platform

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### **步骤 4: 启动服务**

#### **启动 Docker 服务**
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### **验证服务状态**
```bash
# 检查 Redis 连接
uv run python -c "from common.storage.redis_client import RedisClient; print('Redis OK')"

# 检查数据库连接
uv run python -c "from common.storage.db_client import DatabaseManager; print('Database OK')"
```

## 🐛 常见问题

### **问题 1: Python 版本不兼容**
```bash
# 错误: Python 3.7 or earlier is not supported
# 解决: 升级到 Python 3.8+
```

### **问题 2: uv 命令未找到**
```bash
# Windows: 重启 PowerShell 或添加环境变量
# macOS/Linux: 重新加载 shell 配置
source ~/.bashrc
```

### **问题 3: Docker 服务启动失败**
```bash
# 检查端口占用
netstat -an | findstr :6379
netstat -an | findstr :3306

# 停止占用端口的服务
# 或修改 docker-compose.yml 中的端口映射
```

### **问题 4: 依赖安装失败**
```bash
# 清理缓存
uv cache clean

# 重新安装
uv sync --reinstall
```

## ✅ 安装验证

### **运行测试**
```bash
# 运行所有测试
make test

# 运行代码质量检查
make check-all
```

### **检查项目结构**
```bash
# 查看项目结构
tree /f

# 检查关键文件
ls -la common/
ls -la projects/
```

### **验证功能**
```bash
# 测试 HTTP 客户端
uv run python -c "from common.network.http_client import HTTPClient; print('HTTP Client OK')"

# 测试配置加载
uv run python -c "from common.config.settings import config; print('Config OK')"
```

## 🔄 更新安装

### **更新项目代码**
```bash
git pull origin main
```

### **更新依赖**
```bash
uv sync --upgrade
```

### **更新 Docker 镜像**
```bash
docker-compose pull
docker-compose up -d
```

## 📚 下一步

安装完成后，您可以：

1. [快速开始](quickstart.md) - 学习基本使用方法
2. [配置说明](configuration.md) - 了解详细配置选项
3. [开发指南](../development/setup.md) - 设置开发环境
4. [API 参考](../api/common.md) - 查看功能接口

---

🎉 **恭喜！您已成功安装 Python 多项目平台！**
