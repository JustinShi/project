# 🚀 Python 多项目平台

一个基于 Python 的多项目平台，专注于交易策略执行和状态管理。

## 📚 文档

**完整的项目文档请查看 [docs/](docs/) 目录：**

- 📖 [文档总览](docs/README.md) - 完整的文档导航
- 🚀 [快速开始](docs/getting-started/quickstart.md) - 5分钟快速上手
- ⚙️ [安装指南](docs/getting-started/installation.md) - 详细安装步骤
- 🔧 [配置说明](docs/getting-started/configuration.md) - 环境配置
- 🛠️ [开发指南](docs/development/) - 开发环境设置和代码质量
- 📖 [API 参考](docs/api/) - 模块 API 文档
- 🐳 [部署指南](docs/deployment/) - Docker 和生产环境部署
- 💡 [使用示例](docs/examples/) - 实际使用案例

## 🏗️ 项目结构

```
Pyproject/
├── common/                 # 公共模块
│   ├── config/            # 配置管理
│   ├── logging/           # 日志管理
│   ├── storage/           # 数据存储 (Redis, 数据库)
│   ├── network/           # 网络通信 (HTTP, WebSocket)
│   ├── utils/             # 工具函数
│   └── security/          # 安全工具
├── projects/               # 子项目
│   └── trading/           # 交易项目
├── tests/                  # 测试文件
├── docs/                   # 📚 完整文档
└── 配置文件
```

## ⚡ 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 配置环境
cp env.example .env

# 3. 启动服务
docker-compose up -d

# 4. 运行项目
uv run -m projects.trading.main
```

## 🛠️ 开发命令

```bash
# 代码质量
make format              # 格式化代码
make check-all          # 完整质量检查

# 测试
make test               # 运行测试

# 清理
make clean              # 清理临时文件
```

## 🎯 核心功能

- **公共模块**: 配置、日志、存储、网络、工具、安全
- **交易项目**: 策略执行、状态管理、Redis 缓存
- **代码质量**: Black, isort, flake8, bandit, mypy
- **容器化**: Docker Compose 一键部署

## 📖 更多信息

- 详细文档: [docs/README.md](docs/README.md)
- 快速开始: [docs/getting-started/quickstart.md](docs/getting-started/quickstart.md)
- API 参考: [docs/api/](docs/api/)
- 使用示例: [docs/examples/](docs/examples/)
