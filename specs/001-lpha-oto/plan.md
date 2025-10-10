# Implementation Plan: 币安多用户Alpha代币OTO订单自动交易系统

**Branch**: `001-lpha-oto` | **Date**: 2025-10-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-lpha-oto/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

构建一个币安Alpha代币的多用户OTO（One-Triggers-Other）订单自动交易系统。系统采用DDD架构，支持多个用户账户同时自动交易，通过WebSocket实时获取价格和订单状态，使用订单状态机防止重复下单，支持价格波动保护、余额检查、超时处理等风险控制机制。用户通过配置代币简称、目标交易量、价格偏移策略等参数，系统自动计算交易循环次数并执行双向交易。

**核心技术特点**:
- WebSocket实时数据流（价格数据、订单状态推送）
- 订单状态机控制交易流程
- 代币符号映射管理（支持不同API的符号格式转换）
- 精度信息本地缓存（减少API调用）
- 用户认证信息加密存储
- 多用户并发交易隔离

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: 
- FastAPI (Web框架和API服务)
- WebSockets (WebSocket客户端，用于币安数据推送)
- SQLAlchemy (ORM，数据库操作)
- Pydantic (数据验证和配置管理)
- Redis (本地缓存，用于代币精度信息缓存)
- Cryptography (认证信息加密)
- httpx (异步HTTP客户端，用于币安API调用)

**Storage**: 
- PostgreSQL (主数据库，存储用户账户、认证信息、配置、订单记录、交易统计等)
- Redis (缓存层，存储代币符号映射、精度信息、价格历史数据等)

**Testing**: 
- pytest (单元测试和集成测试)
- pytest-asyncio (异步测试支持)
- pytest-mock (Mock工具)
- pytest-cov (代码覆盖率)

**Target Platform**: Linux server (Docker容器化部署)

**Project Type**: Web application with backend + CLI management tools

**Performance Goals**: 
- WebSocket消息处理延迟: <100ms (p95)
- 价格更新到订单计算: <2秒 (NFR-001)
- 订单状态更新接收: <2秒内95%响应 (SC-005)
- 支持并发用户数: ≥10个用户同时交易 (NFR-002, SC-004)
- 订单数据准确率: 100% (NFR-003, SC-006)

**Constraints**: 
- 订单状态机必须保证同一时刻只有一个活跃OTO订单对 (NFR-003)
- 认证信息必须加密存储 (NFR-006)
- WebSocket连接中断时必须暂停交易，不自动恢复 (FR-016)
- 余额不足时必须暂停交易 (FR-017)
- 价格波动超过阈值时必须暂停交易 (FR-020)
- 交易所API请求频率必须控制，避免限流 (NFR-004)

**Scale/Scope**: 
- 用户规模: 初期支持10个并发用户，可扩展至100+用户
- 数据量: 每用户每日约1000笔交易记录
- 代币支持: 初期支持单一Alpha代币，架构支持扩展至多币种
- WebSocket连接数: 每用户2个WebSocket连接（价格数据+订单状态）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**注意**: 宪法文档为模板格式，以下基于Python项目的通用最佳实践进行检查：

### I. 模块化设计原则
✅ **通过**: 采用DDD架构，领域模型、应用服务、基础设施层清晰分离
- Domain层: 领域实体（User, Order, OTOOrderPair, TokenMapping等）
- Application层: 应用服务（TradingService, OrderService, PriceMonitorService等）
- Infrastructure层: 仓储实现、WebSocket客户端、API客户端、缓存等

### II. 测试优先
✅ **通过**: 计划采用TDD方法
- 单元测试: 领域模型、业务逻辑、状态机测试
- 集成测试: WebSocket连接、API调用、数据库操作
- 合约测试: 币安API接口模拟测试

### III. 可观测性
✅ **通过**: 计划实施结构化日志
- 日志记录: 交易决策、订单提交、状态变更、异常处理 (NFR-005)
- 关键指标: WebSocket延迟、API调用成功率、订单准确率
- 审计追踪: 所有交易操作的完整记录

### IV. 安全性
✅ **通过**: 认证信息加密存储，敏感数据保护 (NFR-006)
- 加密方案: 使用Cryptography库对headers和cookies进行对称加密
- 访问控制: 多用户数据隔离，基于用户ID的数据访问控制

### V. 简洁性原则
✅ **通过**: 从最简单的实现开始
- 初期仅支持单一Alpha代币（明确Out of Scope）
- 初期不支持复杂的策略优化（Out of Scope）
- 缓存策略采用简单的TTL机制

**Phase 0前检查结果**: ✅ 所有门禁通过，可以进入研究阶段

## Project Structure

### Documentation (this feature)

```
specs/001-lpha-oto/
├── spec.md              # 功能规范（已完成）
├── clarification-summary.md  # 澄清总结（已完成）
├── plan.md              # 本文件（实施计划）
├── research.md          # Phase 0 输出（技术研究和决策）
├── data-model.md        # Phase 1 输出（数据模型设计）
├── quickstart.md        # Phase 1 输出（快速开始指南）
├── contracts/           # Phase 1 输出（API合约定义）
│   ├── binance-api.yaml # 币安API接口定义
│   ├── internal-api.yaml # 系统内部API定义
│   └── websocket-messages.yaml # WebSocket消息格式定义
└── tasks.md             # Phase 2 输出（任务分解 - 由/speckit.tasks创建）
```

### Source Code (repository root)

```
src/
└── binance/                        # 币安交易系统根目录
    ├── __init__.py
    ├── domain/                     # 领域层（DDD - 核心业务逻辑）
    │   ├── __init__.py
    │   ├── entities/               # 领域实体
    │   │   ├── __init__.py
    │   │   ├── user.py            # 用户账户实体
    │   │   ├── auth_credentials.py # 认证信息实体
    │   │   ├── trading_config.py  # 交易配置实体
    │   │   ├── token_mapping.py   # 代币符号映射实体
    │   │   ├── token_precision.py # 代币精度信息实体
    │   │   ├── order.py           # 订单实体
    │   │   ├── oto_order_pair.py  # OTO订单对实体
    │   │   └── trade_statistics.py # 交易统计实体
    │   ├── value_objects/          # 值对象
    │   │   ├── __init__.py
    │   │   ├── price.py           # 价格值对象
    │   │   ├── quantity.py        # 数量值对象
    │   │   ├── symbol.py          # 代币符号值对象
    │   │   └── precision.py       # 精度值对象
    │   ├── aggregates/             # 聚合根
    │   │   ├── __init__.py
    │   │   └── trading_session.py # 交易会话聚合（包含订单对、状态机、配置等）
    │   ├── repositories/           # 仓储接口（DDD仓储模式）
    │   │   ├── __init__.py
    │   │   ├── user_repository.py
    │   │   ├── order_repository.py
    │   │   ├── token_repository.py
    │   │   └── config_repository.py
    │   └── services/               # 领域服务
    │       ├── __init__.py
    │       ├── order_state_machine.py # 订单状态机
    │       ├── price_calculator.py    # 价格计算服务
    │       └── volume_calculator.py   # 交易量计算服务
    ├── application/                # 应用层（用例编排）
    │   ├── __init__.py
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── trading_service.py     # 交易服务（核心交易流程）
    │   │   ├── order_service.py       # 订单管理服务
    │   │   ├── price_monitor_service.py # 价格监控服务
    │   │   ├── balance_service.py     # 余额查询服务
    │   │   ├── auth_service.py        # 认证服务
    │   │   ├── token_service.py       # 代币信息服务
    │   │   └── notification_service.py # 通知服务
    │   ├── dto/                    # 数据传输对象
    │   │   ├── __init__.py
    │   │   ├── order_dto.py
    │   │   ├── config_dto.py
    │   │   └── statistics_dto.py
    │   └── commands/               # 命令对象（CQRS模式）
    │       ├── __init__.py
    │       ├── create_order_command.py
    │       ├── cancel_order_command.py
    │       └── update_config_command.py
    ├── infrastructure/             # 基础设施层（技术实现细节）
    │   ├── __init__.py
    │   ├── database/
    │   │   ├── __init__.py
    │   │   ├── models.py          # SQLAlchemy ORM模型
    │   │   ├── session.py         # 数据库会话管理
    │   │   └── repositories/      # 仓储实现
    │   │       ├── __init__.py
    │   │       ├── user_repository_impl.py
    │   │       ├── order_repository_impl.py
    │   │       ├── token_repository_impl.py
    │   │       └── config_repository_impl.py
    │   ├── cache/
    │   │   ├── __init__.py
    │   │   ├── redis_client.py    # Redis客户端
    │   │   └── cache_manager.py   # 缓存管理（代币精度、符号映射）
    │   ├── binance_client/
    │   │   ├── __init__.py
    │   │   ├── http_client.py     # HTTP API客户端
    │   │   ├── websocket_client.py # WebSocket客户端（价格+订单）
    │   │   ├── auth.py            # 认证管理（header+cookies）
    │   │   └── models.py          # 币安API响应模型
    │   ├── encryption/
    │   │   ├── __init__.py
    │   │   └── crypto_service.py  # 加密解密服务
    │   └── logging/
    │       ├── __init__.py
    │       └── logger.py          # 结构化日志配置
    ├── api/                        # API接口层（FastAPI）
    │   ├── __init__.py
    │   ├── main.py                # FastAPI应用入口
    │   ├── dependencies.py        # 依赖注入配置
    │   ├── routers/
    │   │   ├── __init__.py
    │   │   ├── users.py           # 用户管理路由
    │   │   ├── trading.py         # 交易管理路由
    │   │   ├── orders.py          # 订单查询路由
    │   │   └── config.py          # 配置管理路由
    │   └── schemas/               # Pydantic schemas（请求/响应）
    │       ├── __init__.py
    │       ├── user_schema.py
    │       ├── trading_schema.py
    │       └── order_schema.py
    ├── cli/                        # CLI工具（管理和维护）
    │   ├── __init__.py
    │   ├── main.py                # CLI入口
    │   ├── commands/
    │   │   ├── __init__.py
    │   │   ├── user_commands.py   # 用户管理命令
    │   │   ├── token_commands.py  # 代币映射配置命令
    │   │   └── trading_commands.py # 交易控制命令
    │   └── utils.py
    └── config/                     # 配置文件
        ├── __init__.py
        ├── settings.py            # 应用配置（Pydantic Settings）
        └── constants.py           # 常量定义

tests/
├── __init__.py
├── conftest.py                    # pytest配置和fixtures
├── unit/                          # 单元测试
│   ├── __init__.py
│   ├── domain/
│   │   ├── test_order_state_machine.py
│   │   ├── test_price_calculator.py
│   │   └── test_entities.py
│   └── application/
│       ├── test_trading_service.py
│       └── test_order_service.py
├── integration/                   # 集成测试
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_binance_client.py
│   ├── test_websocket.py
│   └── test_cache.py
└── contract/                      # 合约测试（API模拟）
    ├── __init__.py
    ├── binance_api_mock.py
    └── test_binance_contracts.py

common/                            # 共享工具库（如果需要）
└── ...

docs/
└── binance/
    └── api.md                     # 币安API文档（已存在）

# 项目配置文件（根目录）
pyproject.toml                     # Python项目配置和依赖
pytest.ini                         # pytest配置
.env.example                       # 环境变量示例
docker-compose.yml                 # Docker编排配置
Dockerfile                         # Docker镜像定义
README.md                          # 项目说明
```

**Structure Decision**: 

采用 **DDD分层架构** + **Clean Architecture** 结合的项目结构：

1. **Domain层（领域层）**: 包含核心业务逻辑，不依赖任何外部技术实现
   - Entities: 业务实体（用户、订单、代币等）
   - Value Objects: 不可变值对象（价格、数量、精度等）
   - Repositories: 仓储接口定义
   - Domain Services: 领域服务（状态机、价格计算等）

2. **Application层（应用层）**: 编排用例流程，协调领域对象
   - Services: 应用服务（交易服务、订单服务等）
   - Commands/Queries: CQRS模式（可选，初期简化）
   - DTOs: 数据传输对象

3. **Infrastructure层（基础设施层）**: 技术实现细节
   - Database: 数据库访问（SQLAlchemy + PostgreSQL）
   - Cache: 缓存实现（Redis）
   - External APIs: 币安API客户端（HTTP + WebSocket）
   - Encryption: 加密服务
   - Logging: 日志服务

4. **API层**: 对外接口（FastAPI RESTful API）

5. **CLI层**: 命令行工具（管理和维护）

**依赖方向**: API/CLI → Application → Domain ← Infrastructure
- Domain层不依赖其他层（纯业务逻辑）
- Application层依赖Domain接口
- Infrastructure层实现Domain接口
- API/CLI层依赖Application层

这种结构支持：
- ✅ 清晰的关注点分离
- ✅ 业务逻辑可独立测试
- ✅ 技术实现可替换（如更换数据库）
- ✅ 符合DDD用户需求
- ✅ 易于扩展（如后续支持多币种）

## Complexity Tracking

*当前无宪法违规需要记录*

本项目遵循简洁性原则，采用标准DDD架构模式，无特殊复杂性引入。

---

## Phase 0 完成状态 ✅

**Phase 0 研究已完成** - 详见 [research.md](./research.md)

### 已完成的研究主题

✅ **WebSocket客户端库选择** → 决策: `websockets` v12.0+  
✅ **状态机实现方案** → 决策: `python-statemachine` v2.1+  
✅ **认证信息加密方案** → 决策: `cryptography (Fernet)`  
✅ **Redis缓存策略** → TTL策略和命名规范已定义  
✅ **币安WebSocket API集成** → 双连接模式 + ListenKey管理  
✅ **多用户并发处理** → Asyncio协程 + FastAPI BackgroundTasks  
✅ **数据库设计和迁移** → PostgreSQL 14+ + Alembic  
✅ **价格波动监控实现** → 滑动窗口算法 + Redis时序数据  
✅ **日志和可观测性** → structlog结构化日志  
✅ **HTTP客户端选择** → httpx异步客户端

---

## Phase 1 完成状态 ✅

**Phase 1 设计已完成** - 详见以下文档

### 已生成的设计文档

✅ **数据模型设计** - [data-model.md](./data-model.md)
- 10个核心实体表设计
- 完整的关系定义和约束
- 索引策略和性能优化方案
- Alembic迁移脚本指南

✅ **API合约定义** - [contracts/](./contracts/)
- [binance-api.yaml](./contracts/binance-api.yaml) - 币安私有API接口定义
- [internal-api.yaml](./contracts/internal-api.yaml) - 系统内部REST API
- [websocket-messages.yaml](./contracts/websocket-messages.yaml) - WebSocket消息格式

✅ **快速开始指南** - [quickstart.md](./quickstart.md)
- 环境要求和依赖安装
- 数据库设置和迁移
- 配置说明和CLI命令参考
- 开发工作流和常见问题

✅ **Agent上下文更新** - `.cursor\rules\specify-rules.mdc`
- Python 3.11+技术栈已添加
- 项目类型: Web application with backend + CLI

---

## Constitution Check (Phase 1后重新评估)

✅ **所有宪法门禁依然通过**

- ✅ 模块化设计: DDD分层架构清晰
- ✅ 测试优先: 测试策略已在quickstart.md定义
- ✅ 可观测性: 结构化日志和审计追踪
- ✅ 安全性: Fernet加密方案
- ✅ 简洁性: 从MVP开始，避免过度设计

---

## 实施准备就绪

### 下一步: `/speckit.tasks`

规划阶段（Phase 0和Phase 1）已全部完成，系统已准备好进入任务分解阶段：

**准备执行**: `/speckit.tasks` 命令将根据本计划生成详细的实施任务清单

### 可交付成果清单

| 文档 | 状态 | 位置 |
|------|------|------|
| 实施计划 | ✅ 完成 | specs/001-lpha-oto/plan.md |
| 技术研究 | ✅ 完成 | specs/001-lpha-oto/research.md |
| 数据模型 | ✅ 完成 | specs/001-lpha-oto/data-model.md |
| API合约 | ✅ 完成 | specs/001-lpha-oto/contracts/*.yaml |
| 快速开始 | ✅ 完成 | specs/001-lpha-oto/quickstart.md |

---

**Phase 0 & Phase 1 完成时间**: 2025-10-09  
**规划质量**: 高度详细，无遗留未决问题  
**实施就绪状态**: ✅ 可以开始编码
