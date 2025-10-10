# 币安Alpha代币OTO订单自动交易系统

一个基于DDD（领域驱动设计）的多用户币安Alpha代币OTO订单自动交易系统，支持实时价格监控、智能订单管理和多用户并发交易。

## ✨ 核心特性

- 🔐 **多用户支持**: 独立的用户认证和配置管理
- 📊 **实时价格监控**: WebSocket实时接收币安Alpha代币价格数据
- 🤖 **智能订单管理**: 自动化OTO（One-Triggers-the-Other）订单执行
- 💰 **余额监控**: 实时查询和显示用户账户余额
- 📈 **交易量管理**: 根据目标交易量自动计算交易循环次数
- 🔒 **安全加密**: 用户认证信息（headers/cookies）加密存储
- ⚡ **高性能**: 异步架构，支持10+用户并发交易
- 🛡️ **风险控制**: 价格波动监控、余额不足暂停、连接中断保护

## 🏗️ 架构设计

基于DDD（领域驱动设计）的清晰分层架构：

```
src/binance/
├── domain/              # 领域层 - 核心业务逻辑
│   ├── entities/       # 实体（User, Order等）
│   ├── value_objects/  # 值对象（Price, Balance等）
│   ├── aggregates/     # 聚合根（OTOOrderPair）
│   ├── repositories/   # 仓储接口
│   └── services/       # 领域服务
├── application/        # 应用层 - 用例编排
│   ├── services/       # 应用服务
│   ├── dto/            # 数据传输对象
│   └── commands/       # 命令处理
├── infrastructure/     # 基础设施层 - 技术实现
│   ├── database/       # 数据库（PostgreSQL + SQLAlchemy）
│   ├── cache/          # 缓存（Redis）
│   ├── binance_client/ # 币安API客户端
│   ├── encryption/     # 加密服务
│   └── logging/        # 日志管理
├── api/                # API接口层
│   ├── routers/        # FastAPI路由
│   └── schemas/        # API模式定义
└── cli/                # CLI命令行工具
    └── commands/       # 管理命令
```

## 🚀 快速开始

### 前置要求

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose（可选）

### 1. 安装依赖

```bash
# 使用 uv 安装依赖
uv sync

# 安装开发依赖
uv sync --dev
```

### 2. 环境配置

```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件，配置数据库和Redis连接
# 生成加密密钥：
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. 启动基础设施

```bash
# 使用 Docker Compose 启动 PostgreSQL 和 Redis
docker-compose up -d postgres redis

# 等待服务健康检查通过
docker-compose ps
```

### 4. 数据库初始化

```bash
# 运行数据库迁移
uv run alembic upgrade head
```

### 5. 运行应用

```bash
# 启动 API 服务
uv run uvicorn binance.api.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 CLI 工具
uv run python -m binance.cli --help
```

## 📖 详细文档

- 📋 [功能规范](specs/001-lpha-oto/spec.md) - 完整的功能需求和用户故事
- 🗺️ [实施计划](specs/001-lpha-oto/plan.md) - 技术栈和架构决策
- 📊 [数据模型](specs/001-lpha-oto/data-model.md) - 实体关系和数据结构
- 🔬 [技术研究](specs/001-lpha-oto/research.md) - 技术选型和最佳实践
- 🚀 [快速开始指南](specs/001-lpha-oto/quickstart.md) - 开发环境设置
- 📝 [任务清单](specs/001-lpha-oto/tasks.md) - 详细的实施任务分解

## 🛠️ 开发工具

### 代码质量

```bash
# 代码格式化
uv run ruff format .

# 代码检查
uv run ruff check . --fix

# 类型检查
uv run mypy src/binance

# 运行所有检查
uv run pre-commit run --all-files
```

### 测试

```bash
# 运行所有测试
uv run pytest

# 运行单元测试
uv run pytest -m unit

# 运行集成测试
uv run pytest -m integration

# 生成覆盖率报告
uv run pytest --cov=src/binance --cov-report=html
```

## 🐳 Docker部署

```bash
# 构建并启动所有服务（包括API）
docker-compose --profile production up -d

# 查看日志
docker-compose logs -f api

# 停止服务
docker-compose down
```

## 📊 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| **Web框架** | FastAPI | REST API服务 |
| **数据库** | PostgreSQL 16 | 主数据存储 |
| **ORM** | SQLAlchemy 2.0 | 数据库操作 |
| **缓存** | Redis 7 | 代币信息缓存、价格数据 |
| **WebSocket** | websockets | 实时价格和订单推送 |
| **HTTP客户端** | httpx | 币安API调用 |
| **加密** | cryptography | 认证信息加密 |
| **日志** | structlog | 结构化日志 |
| **限流** | aiolimiter | API请求频率控制 |
| **CLI** | typer | 命令行工具 |
| **测试** | pytest | 单元和集成测试 |
| **代码质量** | ruff, mypy | 代码检查和类型验证 |

## 🔒 安全特性

- ✅ 用户认证信息（headers/cookies）使用Fernet加密存储
- ✅ API请求频率限制（10 requests/second/user）
- ✅ 数据库连接池管理
- ✅ 环境变量管理，敏感信息不进版本控制
- ✅ SQL注入防护（SQLAlchemy ORM）
- ✅ WebSocket安全连接

## 📈 性能指标

- WebSocket消息处理延迟: <100ms (p95)
- 价格更新到订单计算: <2秒
- 订单状态更新接收: <2秒内95%响应
- 支持并发用户数: ≥10个用户同时交易
- 订单数据准确率: 100%

## 🤝 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [币安API文档](https://binance-docs.github.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Domain-Driven Design](https://domainlanguage.com/ddd/)
