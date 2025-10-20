# 币安Alpha代币OTO订单自动交易系统

一个基于配置驱动的多用户币安Alpha代币OTO刷量交易系统，支持实时订单监控、智能成交检测和批次交易管理。

## ✨ 核心特性

- 🔐 **多用户支持**: 独立的用户认证和策略配置
- 📊 **实时订单监控**: WebSocket实时接收订单成交状态推送
- 🤖 **智能OTO交易**: 自动化OTO订单下单，等待买单和卖单完全成交
- 📈 **刷量策略**: 支持高买低卖的刷量策略，自动达标停止
- 💯 **mulPoint处理**: 自动识别4倍交易量代币，精确计算真实交易量
- ⚡ **批次执行**: 智能批次管理，每笔成交后实时检测是否达标
- 🎯 **精确停止**: 达到目标交易量后立即停止，避免超额执行
- 🛡️ **风险控制**: 订单超时保护、价格波动监控、优雅停止支持

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
- PostgreSQL 16+（用于用户凭证存储）
- uv（Python包管理器）

### 1. 安装依赖

```bash
# 使用 uv 安装依赖
uv sync
```

### 2. 数据库初始化

```bash
# 初始化数据库（创建用户表）
uv run python -m binance.infrastructure.database.init_db
```

### 3. 配置交易策略

编辑 `config/trading_config.yaml`：

```yaml
# 全局设置
global_settings:
  default_buy_offset_percentage: 10      # 买入溢价10%（高于市价）
  default_sell_profit_percentage: 10     # 卖出折扣10%（低于买价）
  default_single_trade_amount_usdt: 200  # 单次交易200 USDT
  
# 策略配置
strategies:
  - strategy_id: "my_strategy"
    enabled: true
    target_token: AOP                    # 目标代币
    target_chain: BSC                    # BSC链
    target_volume: 12000                 # 目标交易量（真实USDT）
    user_ids: [1]                        # 用户ID列表
```

### 4. 更新用户凭证

```bash
# 运行凭证更新工具
uv run python scripts/update_user_credentials_quick.py

# 按提示输入从移动端抓包获取的 headers 和 cookies
```

### 5. 运行交易策略

```bash
# 运行指定策略
uv run python scripts/run_trading_strategy.py --strategy my_strategy

# 或运行所有启用的策略
uv run python scripts/run_trading_strategy.py
```

### 6. 日志管理

```bash
# 查看日志文件
tail -f logs/trading.log

# 手动清理过期日志（保留7天）
make cleanup-logs

# 自定义保留天数
make cleanup-logs DAYS=3

# 设置Windows自动清理任务（需要管理员权限）
scripts/setup_log_cleanup.bat
```

## 📖 详细文档

- 📖 [运行指南](docs/how_to_run.md) - 完整的运行和配置说明
- 📈 [交易策略指南](docs/trading_strategy_guide.md) - 策略配置和使用说明
- 💰 [价格计算](docs/price_calculation.md) - OTO订单价格计算逻辑
- 📊 [mulPoint处理](docs/mulpoint_handling.md) - 4倍交易量代币处理
- 🔄 [策略执行流程](docs/strategy_execution_flow.md) - 批次执行和达标检测逻辑

## 📂 项目结构

```
Pyproject/
├── config/                          # 配置文件
│   └── trading_config.yaml         # 交易策略配置
├── src/binance/                     # 源代码
│   ├── application/                # 应用层
│   │   └── services/               # 策略执行器
│   ├── domain/                     # 领域层
│   │   ├── entities/               # 实体（User等）
│   │   └── repositories/           # 仓储接口
│   └── infrastructure/             # 基础设施层
│       ├── binance_client/         # Binance API客户端
│       ├── database/               # 数据库
│       ├── config/                 # 配置管理
│       └── logging/                # 日志系统
├── scripts/                         # 运行脚本
│   ├── run_trading_strategy.py     # 主执行脚本
│   └── update_user_credentials_quick.py  # 凭证更新工具
├── docs/                           # 文档
└── logs/                           # 日志文件
```

## 📊 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| **数据库** | PostgreSQL 16 | 用户凭证存储 |
| **ORM** | SQLAlchemy 2.0 | 数据库操作 |
| **WebSocket** | websockets | 实时订单状态推送 |
| **HTTP客户端** | httpx | 币安Alpha API调用 |
| **日志** | structlog | 结构化日志 |
| **异步框架** | asyncio | 异步IO和并发 |
| **配置管理** | YAML | 策略配置文件 |
| **包管理** | uv | Python依赖管理 |

## 🔒 安全特性

- ✅ 用户认证信息（headers/cookies）数据库加密存储
- ✅ 数据库连接池管理
- ✅ 环境变量管理，敏感信息不进版本控制
- ✅ SQL注入防护（SQLAlchemy ORM）
- ✅ WebSocket TLS加密连接

## 📈 核心功能

### 1. 批次执行逻辑
- 自动计算剩余交易量和所需循环次数
- 每笔交易成功后立即检测是否达标
- 达到目标交易量后立即停止，避免超额执行

### 2. OTO订单管理
- 自动下单：买入价 = 市价 × (1 + 溢价%)
- 自动下单：卖出价 = 买入价 × (1 - 折扣%)
- WebSocket实时监听订单成交状态
- 买单和卖单完全成交后才继续下一单

### 3. mulPoint 处理
- 自动识别4倍交易量代币（如 AOP）
- 显示交易量 ÷ mulPoint = 真实交易量
- 目标交易量基于真实交易量计算

### 4. 日志管理
- **每日日志文件**: 自动按日期轮转，避免单个文件过大
- **自动清理**: 保留7天日志，自动删除过期文件
- **双日志系统**: 主日志(app.log)和交易日志(trading.log)分离
- **结构化日志**: JSON格式，便于分析和监控

### 5. 性能指标
- WebSocket订单推送延迟: <100ms
- 单笔OTO订单成交时间: 0.5-2秒
- 支持并发用户数: ≥10个用户同时交易
- 订单成交准确率: 100%

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
