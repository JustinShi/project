# 🛠️ 开发环境设置

本文档介绍如何设置 Python 多项目平台的开发环境。

## 📋 系统要求

- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8+ (推荐 3.9+)
- **内存**: 最少 4GB RAM (推荐 8GB+)
- **磁盘空间**: 最少 2GB 可用空间

## 🚀 快速设置

### 1. 安装 Python

```bash
# Windows: 从 python.org 下载安装包
# macOS: 使用 Homebrew
brew install python

# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. 安装 uv

```bash
# Windows
pip install uv

# macOS
brew install uv

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. 克隆项目

```bash
git clone <your-repository-url>
cd Pyproject
```

### 4. 安装依赖

```bash
# 安装根项目依赖
uv pip install -e .

# 安装开发依赖
uv pip install -e ".[dev]"
```

## 🔧 详细设置

### 虚拟环境管理

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 依赖管理

```bash
# 查看依赖
uv pip list

# 添加新依赖
uv pip install package-name

# 添加开发依赖
uv pip install -D package-name

# 更新依赖
uv pip install --upgrade package-name
```

### 代码质量工具配置

#### Black 格式化器

```bash
# 格式化代码
uv run black .

# 检查格式
uv run black --check .
```

#### isort 导入排序

```bash
# 排序导入
uv run isort .

# 检查导入顺序
uv run isort --check-only .
```

#### flake8 代码检查

```bash
# 运行检查
uv run flake8 .

# 生成报告
uv run flake8 --format=html --htmldir=flake8-report .
```

#### mypy 类型检查

```bash
# 类型检查
uv run mypy .

# 生成类型检查报告
uv run mypy --html-report mypy-report .
```

#### bandit 安全检查

```bash
# 安全检查
uv run bandit -r .

# 生成安全报告
uv run bandit -r . -f json -o bandit-report.json
```

## 🎯 IDE 配置

### VS Code / Cursor

#### 推荐扩展

- **Python**: Microsoft Python 扩展
- **Python Indent**: Python 缩进支持
- **Python Docstring Generator**: 文档字符串生成
- **Python Type Hint**: 类型提示支持
- **Black Formatter**: 代码格式化
- **isort**: 导入排序

#### 设置配置

```json
{
    "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.banditEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm

#### 配置 Python 解释器

1. 打开 `File` → `Settings` → `Project` → `Python Interpreter`
2. 选择项目虚拟环境
3. 配置代码质量工具路径

#### 代码质量工具集成

1. 安装 `black`, `isort`, `flake8`, `mypy`, `bandit`
2. 在 `External Tools` 中配置工具
3. 设置文件观察器自动运行

## 🔍 环境验证

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_http_client.py

# 生成覆盖率报告
uv run pytest --cov=common --cov-report=html
```

### 代码质量检查

```bash
# 运行所有检查
make quality

# 或使用 Python 脚本
python check_quality.py
```

### 服务启动测试

```bash
# 启动 Redis
docker-compose up -d redis

# 测试连接
uv run python -c "from common.storage.redis_client import RedisClient; print('Redis 连接成功')"
```

## 🚨 常见问题

### 依赖冲突

```bash
# 清理依赖
uv pip uninstall -y -r <(uv pip freeze)

# 重新安装
uv pip install -e .
```

### 虚拟环境问题

```bash
# 删除虚拟环境
rm -rf .venv

# 重新创建
uv venv
```

### 权限问题

```bash
# Windows: 以管理员身份运行 PowerShell
# Linux/macOS: 使用 sudo
sudo uv pip install -e .
```

### 网络问题

```bash
# 使用国内镜像
uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -e .
```

## 📚 下一步

- 阅读 [快速开始指南](../getting-started/quickstart.md)
- 查看 [代码质量工具](../development/code-quality.md)
- 了解 [配置说明](../getting-started/configuration.md)

## 🤝 获取帮助

如果遇到问题：

1. 检查 [常见问题](#-常见问题) 部分
2. 查看项目 Issues
3. 联系项目维护者
4. 查看相关工具文档
