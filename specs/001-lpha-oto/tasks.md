# Tasks: 币安多用户Alpha代币OTO订单自动交易系统

**Input**: 设计文档 `/specs/001-lpha-oto/`  
**Branch**: `001-lpha-oto`  
**Generated**: 2025-10-09

**Prerequisites**: 
- ✅ spec.md (功能规范)
- ✅ plan.md (实施计划)
- ✅ research.md (技术研究)
- ✅ data-model.md (数据模型)
- ✅ contracts/ (API合约)
- ✅ quickstart.md (快速开始指南)

**Tests**: 本项目采用TDD方法，每个用户故事的测试需在实现前编写并确保失败

**Organization**: 任务按用户故事分组，支持独立实施和增量交付

---

## 格式说明: `[ID] [P?] [Story] 描述`

- **[P]**: 可并行执行（不同文件，无依赖关系）
- **[Story]**: 所属用户故事（US1, US2, US3等）
- 任务描述包含精确的文件路径

---

## Phase 1: 项目初始化（Setup）

**目标**: 创建项目基础结构和开发环境

**前置条件**: 无

### 环境和项目结构

- [X] **T001** [P] 创建Python项目结构按照plan.md定义（`src/binance/`, `tests/`, `docs/`等）
- [X] **T002** [P] 初始化`pyproject.toml`并配置依赖（FastAPI, SQLAlchemy, websockets, redis, cryptography等）
- [X] **T003** [P] 配置`.env.example`环境变量模板（数据库URL、Redis URL、加密密钥等）
- [X] **T004** [P] 配置`pytest.ini`和测试框架（pytest, pytest-asyncio, pytest-cov）
- [X] **T005** [P] 配置代码质量工具（ruff, mypy, pre-commit）
- [X] **T006** [P] 创建`docker-compose.yml`用于PostgreSQL和Redis（按quickstart.md）
- [X] **T007** [P] 创建`.gitignore`文件（排除`.env`, `__pycache__`, `.pytest_cache`等）

### 文档和配置

- [X] **T008** [P] 更新根目录`README.md`（项目概述、快速开始链接）
- [X] **T009** [P] 创建`Dockerfile`用于应用容器化部署

**Checkpoint ✓**: 项目结构创建完成，开发环境可启动

---

## Phase 2: 基础设施层（Foundational - 阻塞所有用户故事）

**目标**: 核心基础设施，必须在任何用户故事开始前完成

**⚠️ 关键**: 此阶段未完成前，不能开始任何用户故事实施

### 数据库基础

- [X] **T010** 初始化Alembic数据库迁移工具（`alembic init alembic`）
- [X] **T011** 配置Alembic环境（`alembic/env.py`，使用异步引擎）
- [X] **T012** 创建基础配置模块`src/binance/config/settings.py`（Pydantic Settings）
- [X] **T013** 创建基础配置常量`src/binance/config/constants.py`（订单状态、价格偏移模式等枚举）
- [X] **T014** 创建数据库会话管理`src/binance/infrastructure/database/session.py`（异步SessionLocal）

### 核心数据模型（SQLAlchemy ORM - 按data-model.md）

所有核心实体的ORM模型必须先创建，因为多个用户故事依赖这些表：

- [X] **T015** [P] 创建`users`表ORM模型 → `src/binance/infrastructure/database/models.py`
- [X] **T016** [P] 创建`auth_credentials`表ORM模型（包含加密字段）
- [X] **T017** [P] 创建`trading_configs`表ORM模型
- [X] **T018** [P] 创建`token_mappings`表ORM模型
- [X] **T019** [P] 创建`token_precisions`表ORM模型
- [X] **T020** [P] 创建`oto_order_pairs`表ORM模型
- [X] **T021** [P] 创建`orders`表ORM模型
- [X] **T022** [P] 创建`trade_records`表ORM模型
- [X] **T023** [P] 创建`trading_statistics`表ORM模型
- [X] **T024** [P] 创建`price_history`表ORM模型

### 数据库迁移脚本

- [X] **T025** 生成初始数据库迁移脚本（`alembic revision --autogenerate -m "Initial schema"`）
- [X] **T026** 验证并调整迁移脚本（检查外键、索引、约束）
- [X] **T027** 应用数据库迁移 - SQLite数据库已创建，所有10个表已建立

### 加密服务

- [X] **T028** 实现加密服务`src/binance/infrastructure/encryption/crypto_service.py`（Fernet加密/解密，用于认证信息）

### 日志基础设施

- [X] **T029** 配置结构化日志`src/binance/infrastructure/logging/logger.py`（structlog，JSON格式）

### Redis缓存基础

- [X] **T030** 创建Redis客户端`src/binance/infrastructure/cache/redis_client.py`（异步redis-py）
- [X] **T031** 创建缓存管理器`src/binance/infrastructure/cache/cache_manager.py`（代币精度和符号映射缓存逻辑）

**Checkpoint ✓**: 基础设施就绪，用户故事可以并行开始实施

---

## Phase 3: User Story 1 - 查看账户状态和交易数据 (Priority: P1) 🎯 MVP

**目标**: 用户能够查看账户余额和历史交易量统计

**独立测试**: 通过API查询账户信息并验证余额和交易量数据的准确性

**功能需求**: FR-001, FR-002, FR-003

### 测试（TDD - 先写测试）

- [ ] **T032** [P] [US1] 合约测试：币安余额查询API Mock → `tests/contract/test_binance_balance_api.py`
- [ ] **T033** [P] [US1] 合约测试：币安交易量查询API Mock → `tests/contract/test_binance_volume_api.py`
- [ ] **T034** [P] [US1] 集成测试：查询用户余额完整流程 → `tests/integration/test_balance_service.py`
- [ ] **T035** [P] [US1] 集成测试：查询用户交易量统计 → `tests/integration/test_statistics_service.py`

**⚠️ 确认**: 运行测试，验证全部失败后再继续实现

### 领域层实现

- [X] **T036** [P] [US1] 创建User实体 → `src/binance/domain/entities/user.py`
- [X] **T037** [P] [US1] 创建AuthCredentials实体 → `src/binance/domain/entities/auth_credentials.py`
- [X] **T038** [P] [US1] ~~创建TradingStatistics实体~~ - 已删除，使用API实时查询
- [X] **T039** [P] [US1] 定义User仓储接口 → `src/binance/domain/repositories/user_repository.py`
- [X] **T040** [P] [US1] ~~定义Statistics仓储接口~~ - 已删除

### 基础设施层实现

- [X] **T041** [US1] 实现User仓储 → `src/binance/infrastructure/database/repositories/user_repository_impl.py`
- [X] **T042** [US1] ~~实现Statistics仓储~~ - 已删除
- [X] **T043** [US1] 创建币安HTTP客户端基础 → `src/binance/infrastructure/binance_client/http_client.py`（异步httpx）
- [X] **T044** [US1] 实现认证管理模块（集成在http_client和balance_service中）
- [X] **T045** [US1] 实现币安API余额查询 → `src/binance/infrastructure/binance_client/http_client.py:get_wallet_balance()`
- [X] **T046** [US1] 实现币安API交易量查询 → `src/binance/infrastructure/binance_client/http_client.py:get_user_volume()`

### 应用层实现

- [X] **T047** [US1] 创建BalanceService应用服务 → `src/binance/application/services/balance_service.py`
- [X] **T048** [US1] ~~创建StatisticsService应用服务~~ - 已合并到BalanceService
- [X] **T049** [US1] 定义用户DTO（使用Pydantic schemas替代）
- [X] **T050** [US1] 定义统计DTO（使用Pydantic schemas替代）

### API层实现

- [X] **T051** [US1] 创建FastAPI应用入口 → `src/binance/api/main.py`（基础app设置）
- [X] **T052** [US1] 配置依赖注入 → `src/binance/api/dependencies.py`（仓储、服务注入）
- [X] **T053** [US1] 定义用户Pydantic schemas → `src/binance/api/schemas/user_schema.py`
- [X] **T054** [US1] 实现用户路由 → `src/binance/api/routers/users.py`（GET /users/{userId}, GET /users/{userId}/balance, GET /users/{userId}/volume）
- [X] **T055** [US1] 添加错误处理和日志记录

### 验证

- [ ] **T056** [US1] 运行US1所有测试，确保通过
- [ ] **T057** [US1] 手动测试：启动服务，通过Swagger UI测试余额和统计API

**Checkpoint ✓**: US1完成，用户可以查看账户余额和交易统计

---

## Phase 4: User Story 2 - 配置交易目标和策略 (Priority: P1)

**目标**: 用户能够设置目标交易量、价格偏移策略等交易参数

**独立测试**: 通过API创建和更新交易配置，验证配置正确保存并应用

**功能需求**: FR-004, FR-007, FR-020, FR-021, FR-022, FR-023, FR-024, FR-025, FR-026

### 测试（TDD - 先写测试）

- [ ] **T058** [P] [US2] 单元测试：价格偏移计算（百分比模式） → `tests/unit/domain/test_price_calculator.py`
- [ ] **T059** [P] [US2] 单元测试：价格偏移计算（固定金额模式）
- [ ] **T060** [P] [US2] 合约测试：币安精度信息查询API Mock → `tests/contract/test_binance_precision_api.py`
- [ ] **T061** [P] [US2] 集成测试：创建交易配置完整流程 → `tests/integration/test_config_service.py`
- [ ] **T062** [P] [US2] 集成测试：代币符号映射查询和缓存 → `tests/integration/test_token_service.py`
- [ ] **T063** [P] [US2] 集成测试：代币精度信息缓存逻辑

**⚠️ 确认**: 运行测试，验证全部失败后再继续实现

### 领域层实现

- [ ] **T064** [P] [US2] 创建TradingConfig实体 → `src/binance/domain/entities/trading_config.py`
- [ ] **T065** [P] [US2] 创建TokenMapping实体 → `src/binance/domain/entities/token_mapping.py`
- [ ] **T066** [P] [US2] 创建TokenPrecision实体 → `src/binance/domain/entities/token_precision.py`
- [ ] **T067** [P] [US2] 创建Price值对象 → `src/binance/domain/value_objects/price.py`
- [ ] **T068** [P] [US2] 创建Quantity值对象 → `src/binance/domain/value_objects/quantity.py`
- [ ] **T069** [P] [US2] 创建Precision值对象 → `src/binance/domain/value_objects/precision.py`
- [ ] **T070** [P] [US2] 定义Config仓储接口 → `src/binance/domain/repositories/config_repository.py`
- [ ] **T071** [P] [US2] 定义Token仓储接口 → `src/binance/domain/repositories/token_repository.py`
- [ ] **T072** [US2] 实现价格计算领域服务 → `src/binance/domain/services/price_calculator.py`（支持百分比和固定金额偏移）
- [ ] **T073** [US2] 实现交易量计算领域服务 → `src/binance/domain/services/volume_calculator.py`（计算循环次数）

### 基础设施层实现

- [ ] **T074** [US2] 实现Config仓储 → `src/binance/infrastructure/database/repositories/config_repository_impl.py`
- [ ] **T075** [US2] 实现Token仓储 → `src/binance/infrastructure/database/repositories/token_repository_impl.py`
- [ ] **T076** [US2] 实现币安API精度查询 → `src/binance/infrastructure/binance_client/http_client.py:get_exchange_info()`
- [ ] **T077** [US2] 实现代币符号映射缓存逻辑（Redis） → `src/binance/infrastructure/cache/cache_manager.py:get_token_mapping()`
- [ ] **T078** [US2] 实现代币精度缓存逻辑（优先缓存，失效则API） → `src/binance/infrastructure/cache/cache_manager.py:get_token_precision()`

### 应用层实现

- [ ] **T079** [US2] 创建TokenService应用服务 → `src/binance/application/services/token_service.py`（管理符号映射和精度）
- [ ] **T080** [US2] 创建ConfigService应用服务 → `src/binance/application/services/config_service.py`（创建、更新、查询配置）
- [ ] **T081** [US2] 定义配置DTO → `src/binance/application/dto/config_dto.py`
- [ ] **T082** [US2] 定义代币DTO → `src/binance/application/dto/token_dto.py`
- [ ] **T083** [US2] 实现创建配置命令 → `src/binance/application/commands/update_config_command.py`

### API层实现

- [ ] **T084** [US2] 定义配置Pydantic schemas → `src/binance/api/schemas/config_schema.py`
- [ ] **T085** [US2] 实现配置路由 → `src/binance/api/routers/config.py`（GET/PUT /users/{userId}/config）
- [ ] **T086** [US2] 实现代币路由 → `src/binance/api/routers/tokens.py`（GET/POST /tokens/mappings）
- [ ] **T087** [US2] 添加配置验证逻辑（价格偏移模式、阈值范围等）

### CLI工具实现

- [ ] **T088** [US2] 创建CLI入口 → `src/binance/cli/main.py`（Click框架）
- [ ] **T089** [US2] 实现代币管理CLI命令 → `src/binance/cli/commands/token_commands.py`（add, list, refresh-precision）

### 验证

- [ ] **T090** [US2] 运行US2所有测试，确保通过
- [ ] **T091** [US2] 手动测试：通过API创建配置，验证代币映射和精度缓存生效

**Checkpoint ✓**: US2完成，用户可以配置交易策略和代币信息

---

## Phase 5: User Story 3 - 实时监控市场成交价格 (Priority: P2)

**目标**: 系统实时接收并处理Alpha代币价格数据，支持价格波动监控

**独立测试**: 连接WebSocket价格流，验证价格更新实时性和波动检测准确性

**功能需求**: FR-006, FR-020

### 测试（TDD - 先写测试）

- [ ] **T092** [P] [US3] 单元测试：价格波动监控算法（滑动窗口） → `tests/unit/domain/test_price_volatility_monitor.py`
- [ ] **T093** [P] [US3] 集成测试：WebSocket价格连接和消息解析 → `tests/integration/test_price_websocket.py`
- [ ] **T094** [P] [US3] 集成测试：价格历史存储和查询（Redis）
- [ ] **T095** [P] [US3] 集成测试：价格波动检测触发暂停 → `tests/integration/test_price_monitor_service.py`

**⚠️ 确认**: 运行测试，验证全部失败后再继续实现

### 领域层实现

- [ ] **T096** [P] [US3] 创建PriceData实体 → `src/binance/domain/entities/price_data.py`（价格、时间戳、波动计算）
- [ ] **T097** [US3] 实现价格波动监控领域服务 → `src/binance/domain/services/price_volatility_monitor.py`（滑动窗口算法）

### 基础设施层实现

- [ ] **T098** [US3] 创建WebSocket客户端基础 → `src/binance/infrastructure/binance_client/websocket_client.py`（websockets库，异步）
- [ ] **T099** [US3] 实现价格WebSocket连接器 → `src/binance/infrastructure/binance_client/price_websocket.py`（订阅aggTrade流）
- [ ] **T100** [US3] 实现价格消息解析器 → `src/binance/infrastructure/binance_client/models.py:AggTradeMessage`
- [ ] **T101** [US3] 实现WebSocket重连逻辑（指数退避策略）
- [ ] **T102** [US3] 实现价格历史Redis存储 → `src/binance/infrastructure/cache/cache_manager.py:add_price_history()`（Sorted Set，1分钟窗口）

### 应用层实现

- [ ] **T103** [US3] 创建PriceMonitorService应用服务 → `src/binance/application/services/price_monitor_service.py`
  - 启动价格WebSocket连接
  - 接收价格更新
  - 调用波动监控服务
  - 触发暂停交易事件（如超过阈值）
- [ ] **T104** [US3] 创建NotificationService应用服务 → `src/binance/application/services/notification_service.py`（暂停交易通知、余额不足通知等）

### API层实现

- [ ] **T105** [US3] 实现价格查询路由 → `src/binance/api/routers/prices.py`（GET /tokens/{symbol}/price, GET /tokens/{symbol}/price-history）
- [ ] **T106** [US3] 添加WebSocket连接状态监控端点（GET /monitoring/websocket-status）

### 验证

- [ ] **T107** [US3] 运行US3所有测试，确保通过
- [ ] **T108** [US3] 手动测试：启动价格监控，观察WebSocket连接和价格更新日志
- [ ] **T109** [US3] 模拟价格剧烈波动，验证暂停交易机制触发

**Checkpoint ✓**: US3完成，系统可实时监控价格并检测异常波动

---

## Phase 6: User Story 4 - 自动执行OTO买卖订单 (Priority: P1)

**目标**: 系统自动创建并提交OTO订单对到币安交易所

**独立测试**: 配置交易参数，触发下单，验证OTO订单正确创建和提交

**功能需求**: FR-005, FR-007, FR-008, FR-009, FR-017

### 测试（TDD - 先写测试）

- [ ] **T110** [P] [US4] 单元测试：OTO订单价格计算（集成价格计算服务） → `tests/unit/domain/test_oto_order_pair.py`
- [ ] **T111** [P] [US4] 合约测试：币安OTO订单提交API Mock → `tests/contract/test_binance_oto_order_api.py`
- [ ] **T112** [P] [US4] 集成测试：创建OTO订单完整流程 → `tests/integration/test_order_service.py`
- [ ] **T113** [P] [US4] 集成测试：余额不足检测和暂停交易
- [ ] **T114** [P] [US4] 集成测试：订单数量精度验证

**⚠️ 确认**: 运行测试，验证全部失败后再继续实现

### 领域层实现

- [ ] **T115** [P] [US4] 创建Order实体 → `src/binance/domain/entities/order.py`（买单/卖单）
- [ ] **T116** [P] [US4] 创建OTOOrderPair聚合根 → `src/binance/domain/entities/oto_order_pair.py`（包含买单+卖单）
- [ ] **T117** [P] [US4] 定义Order仓储接口 → `src/binance/domain/repositories/order_repository.py`

### 基础设施层实现

- [ ] **T118** [US4] 实现Order仓储 → `src/binance/infrastructure/database/repositories/order_repository_impl.py`
- [ ] **T119** [US4] 实现币安API下单接口 → `src/binance/infrastructure/binance_client/http_client.py:place_oto_order()`
- [ ] **T120** [US4] 实现API限流控制 → `src/binance/infrastructure/binance_client/rate_limiter.py`（aiolimiter，10 req/s）

### 应用层实现

- [ ] **T121** [US4] 创建OrderService应用服务 → `src/binance/application/services/order_service.py`
  - 创建OTO订单对
  - 计算买卖单价格（调用PriceCalculator）
  - 验证订单数量精度
  - 检查用户余额
  - 提交订单到币安
  - 记录订单到数据库
- [ ] **T122** [US4] 定义订单DTO → `src/binance/application/dto/order_dto.py`
- [ ] **T123** [US4] 实现创建订单命令 → `src/binance/application/commands/create_order_command.py`

### API层实现

- [ ] **T124** [US4] 定义订单Pydantic schemas → `src/binance/api/schemas/order_schema.py`
- [ ] **T125** [US4] 实现订单路由 → `src/binance/api/routers/orders.py`
  - GET /users/{userId}/orders（查询订单列表）
  - GET /users/{userId}/oto-orders/{otoOrderId}（订单详情）
  - POST /users/{userId}/oto-orders/{otoOrderId}/cancel（取消订单）

### 验证

- [ ] **T126** [US4] 运行US4所有测试，确保通过
- [ ] **T127** [US4] 手动测试（使用Mock API）：创建OTO订单，验证价格计算和订单结构
- [ ] **T128** [US4] 测试余额不足场景，验证暂停交易逻辑

**Checkpoint ✓**: US4完成，系统可自动创建和提交OTO订单

---

## Phase 7: User Story 5 - 监控订单状态并等待完全成交 (Priority: P1)

**目标**: 实时监控订单状态，实现订单状态机，支持超时处理和下一轮交易触发

**独立测试**: 提交订单，通过WebSocket接收状态更新，验证状态机转换正确性

**功能需求**: FR-010, FR-011, FR-012, FR-013, FR-016, FR-018

### 测试（TDD - 先写测试）

- [ ] **T129** [P] [US5] 单元测试：订单状态机完整状态转换 → `tests/unit/domain/test_order_state_machine.py`
- [ ] **T130** [P] [US5] 单元测试：状态机防止重复下单逻辑
- [ ] **T131** [P] [US5] 单元测试：订单超时检测和处理
- [ ] **T132** [P] [US5] 集成测试：WebSocket订单推送连接和消息解析 → `tests/integration/test_order_websocket.py`
- [ ] **T133** [P] [US5] 集成测试：订单状态机与WebSocket集成
- [ ] **T134** [P] [US5] 集成测试：完全成交触发下一轮交易

**⚠️ 确认**: 运行测试，验证全部失败后再继续实现

### 领域层实现

- [ ] **T135** [US5] 创建OrderStateMachine领域服务 → `src/binance/domain/services/order_state_machine.py`（python-statemachine）
  - 状态: idle, placing, pending, partially_filled, filled, timeout, cancelling, cancelled
  - 转换: place_order, order_placed, partial_fill, complete_fill, timeout_check, cancel等
  - 守卫: 防止重复下单（只允许idle状态下单）
- [ ] **T136** [P] [US5] 创建TradeRecord实体 → `src/binance/domain/entities/trade_record.py`

### 基础设施层实现

- [ ] **T137** [US5] 实现ListenKey管理 → `src/binance/infrastructure/binance_client/listen_key_manager.py`
  - 获取ListenKey
  - 定时续期（每30分钟）
  - 过期检测和自动刷新
- [ ] **T138** [US5] 实现订单WebSocket连接器 → `src/binance/infrastructure/binance_client/order_websocket.py`
  - 订阅alpha@{listenKey}
  - 解析executionReport消息
  - 处理连接中断（立即暂停交易，不自动恢复）
- [ ] **T139** [US5] 实现订单消息解析器 → `src/binance/infrastructure/binance_client/models.py:ExecutionReportMessage`

### 应用层实现

- [ ] **T140** [US5] 扩展OrderService支持订单状态监控
  - 启动订单WebSocket连接
  - 接收订单状态更新
  - 更新本地订单状态机
  - 检测订单超时（配置的timeout_seconds）
  - 处理部分成交超时：取消未成交部分，重新下单
  - 处理完全成交：触发下一轮交易
- [ ] **T141** [US5] 创建TradingService应用服务（核心交易流程编排） → `src/binance/application/services/trading_service.py`
  - 启动/停止自动交易
  - 管理交易循环（根据目标交易量计算循环次数）
  - 协调PriceMonitor、OrderService、StateMachine
  - 处理异常暂停（余额不足、连接中断、价格波动、认证失效）

### API层实现

- [ ] **T142** [US5] 实现交易控制路由 → `src/binance/api/routers/trading.py`
  - POST /users/{userId}/trading/start（启动自动交易）
  - POST /users/{userId}/trading/stop（停止自动交易）
  - GET /users/{userId}/trading/status（查询交易状态）

### CLI工具实现

- [ ] **T143** [US5] 实现交易控制CLI命令 → `src/binance/cli/commands/trading_commands.py`（start, stop, status）

### 验证

- [ ] **T144** [US5] 运行US5所有测试，确保通过
- [ ] **T145** [US5] 手动测试：启动交易，模拟订单状态变化（NEW → PARTIALLY_FILLED → FILLED）
- [ ] **T146** [US5] 测试订单超时场景，验证取消和重新下单逻辑
- [ ] **T147** [US5] 测试WebSocket连接中断，验证暂停交易和手动恢复流程

**Checkpoint ✓**: US5完成，系统可实时监控订单状态并自动执行交易循环

---

## Phase 8: User Story 6 - 多用户并发交易管理 (Priority: P2)

**目标**: 支持多个用户同时自动交易，用户间数据和交易完全隔离

**独立测试**: 配置多个用户账户，同时启动交易，验证数据隔离和独立性

**功能需求**: FR-001（多用户隔离），NFR-002（并发支持）

### 测试（TDD - 先写测试）

- [ ] **T148** [P] [US6] 集成测试：多用户同时交易数据隔离 → `tests/integration/test_multi_user_trading.py`
- [ ] **T149** [P] [US6] 集成测试：单用户异常不影响其他用户
- [ ] **T150** [P] [US6] 负载测试：10个用户并发交易（性能基准） → `tests/performance/test_concurrent_users.py`

**⚠️ 确认**: 运行测试，验证全部失败后再继续实现

### 应用层实现

- [ ] **T151** [US6] 扩展TradingService支持多用户并发
  - 为每个用户创建独立的交易协程
  - 用户级锁防止并发修改配置
  - 用户级WebSocket连接管理（每用户2个连接：价格+订单）
- [ ] **T152** [US6] 创建TradingManager → `src/binance/application/services/trading_manager.py`
  - 管理所有用户的交易任务（Dict[user_id, asyncio.Task]）
  - 启动/停止单个用户交易
  - 全局监控所有用户交易状态
  - 异常隔离（单用户异常不影响其他用户）

### API层实现

- [ ] **T153** [US6] 扩展FastAPI应用支持后台任务（BackgroundTasks）
- [ ] **T154** [US6] 实现全局监控端点 → `src/binance/api/routers/monitoring.py`
  - GET /monitoring/active-users（查询活跃交易用户列表）
  - GET /monitoring/system-status（系统整体状态）

### CLI工具实现

- [ ] **T155** [US6] 实现用户管理CLI命令 → `src/binance/cli/commands/user_commands.py`
  - create（创建用户）
  - list（列出所有用户）
  - show（查看用户详情）
  - set-credentials（更新认证信息）

### 验证

- [ ] **T156** [US6] 运行US6所有测试，确保通过
- [ ] **T157** [US6] 手动测试：创建3个用户，同时启动交易，观察日志和数据隔离
- [ ] **T158** [US6] 性能测试：运行10个用户并发交易30分钟，验证稳定性

**Checkpoint ✓**: US6完成，系统支持多用户并发交易

---

## Phase 9: User Story 7 - 交易进度追踪和统计 (Priority: P3)

**目标**: 提供交易进度可视化和详细统计数据

**独立测试**: 执行若干轮交易，查询统计数据并验证准确性

**功能需求**: FR-014

### 测试（TDD - 先写测试）

- [ ] **T159** [P] [US7] 单元测试：交易统计计算逻辑 → `tests/unit/domain/test_trading_statistics.py`
- [ ] **T160** [P] [US7] 集成测试：交易进度实时更新 → `tests/integration/test_statistics_update.py`
- [ ] **T161** [P] [US7] 集成测试：统计数据准确性验证

**⚠️ 确认**: 运行测试，验证全部失败后再继续实现

### 应用层实现

- [ ] **T162** [US7] 扩展StatisticsService支持进度计算
  - 计算完成百分比
  - 预估剩余循环次数
  - 聚合交易记录统计
- [ ] **T163** [US7] 实现统计实时更新逻辑（订单成交后自动更新）

### API层实现

- [ ] **T164** [US7] 扩展统计路由 → `src/binance/api/routers/users.py`
  - GET /users/{userId}/statistics（增强版，包含进度和预估）
  - GET /users/{userId}/orders（分页查询，支持状态筛选和时间范围）

### CLI工具实现

- [ ] **T165** [US7] 实现统计查询CLI命令 → `src/binance/cli/commands/stats_commands.py`
  - show（查看统计）
  - orders list（查看订单历史）

### 验证

- [ ] **T166** [US7] 运行US7所有测试，确保通过
- [ ] **T167** [US7] 手动测试：执行5轮交易，查询统计并验证数据准确性

**Checkpoint ✓**: US7完成，用户可查看详细的交易进度和统计

---

## Phase 10: 优化和跨领域功能（Polish & Cross-Cutting Concerns）

**目标**: 提升代码质量、性能和安全性

### 安全强化

- [ ] **T168** [P] 实现API访问控制（基于用户ID的权限验证）
- [ ] **T169** [P] 添加敏感数据脱敏日志（不记录完整headers/cookies）
- [ ] **T170** [P] 实现加密密钥轮换支持（双密钥解密过渡期）

### 性能优化

- [ ] **T171** [P] 优化数据库查询（添加复合索引，避免N+1查询）
- [ ] **T172** [P] 实现数据库连接池调优（pool_size, max_overflow）
- [ ] **T173** [P] Redis缓存性能测试和调优

### 可观测性增强

- [ ] **T174** [P] 添加关键指标监控（订单成功率、WebSocket延迟、API调用成功率）
- [ ] **T175** [P] 实现审计日志完整记录（所有交易操作、配置变更）
- [ ] **T176** [P] 添加健康检查端点（GET /health，检查数据库、Redis、WebSocket连接）

### 文档完善

- [ ] **T177** [P] 更新README.md（包含架构图、快速开始、部署说明）
- [ ] **T178** [P] 生成API文档（Swagger/ReDoc已自动，补充使用示例）
- [ ] **T179** [P] 编写运维文档（部署、监控、故障排查）

### 代码质量

- [ ] **T180** 代码重构和清理（消除重复代码，提取公共逻辑）
- [ ] **T181** 运行完整测试套件并达到80%+覆盖率
- [ ] **T182** 运行类型检查（mypy）并修复所有错误
- [ ] **T183** 运行Linting（ruff）并修复所有警告

### 验证quickstart.md

- [ ] **T184** 按照quickstart.md从零搭建开发环境，验证文档准确性
- [ ] **T185** 执行quickstart.md中的所有示例命令，确保无误

### 部署准备

- [ ] **T186** [P] 优化Dockerfile（多阶段构建，减小镜像大小）
- [ ] **T187** [P] 创建生产环境docker-compose.yml
- [ ] **T188** [P] 编写Kubernetes部署配置（可选）

**Checkpoint ✓**: 系统优化完成，生产就绪

---

## 依赖关系和执行顺序

### Phase依赖关系

```
Phase 1 (Setup) 
    ↓
Phase 2 (Foundational) ← ⚠️ 阻塞所有用户故事
    ↓
    ├──→ Phase 3 (US1 - P1) ── 可并行
    ├──→ Phase 4 (US2 - P1) ── 可并行
    ├──→ Phase 5 (US3 - P2) ── 可并行
    ├──→ Phase 6 (US4 - P1) ── 依赖US2（价格计算）和US3（价格数据）
    └──→ Phase 7 (US5 - P1) ── 依赖US4（订单创建）
         ├──→ Phase 8 (US6 - P2) ── 依赖US5（交易流程完整）
         └──→ Phase 9 (US7 - P3) ── 依赖US5（交易数据生成）
                  ↓
         Phase 10 (Polish)
```

### 用户故事依赖分析

| 用户故事 | 优先级 | 依赖 | 可否独立测试 |
|---------|-------|-----|-------------|
| US1: 账户状态 | P1 | 仅依赖Foundational | ✅ 是 |
| US2: 配置策略 | P1 | 仅依赖Foundational | ✅ 是 |
| US3: 价格监控 | P2 | 依赖US2（代币映射） | ✅ 是（可Mock代币数据） |
| US4: OTO下单 | P1 | 依赖US2（价格计算）、US3（价格数据） | ⚠️ 部分（需Mock价格） |
| US5: 订单监控 | P1 | 依赖US4（订单创建） | ⚠️ 部分（需Mock订单） |
| US6: 多用户 | P2 | 依赖US5（完整交易流程） | ✅ 是（独立测试隔离性） |
| US7: 统计 | P3 | 依赖US5（交易数据） | ✅ 是（可Mock交易数据） |

### 推荐实施顺序

#### 🎯 MVP（最小可行产品）路线

**目标**: 快速验证核心交易流程

```
1. Phase 1: Setup（T001-T009）
2. Phase 2: Foundational（T010-T031）← 关键阻塞点
3. Phase 4: US2 配置策略（T058-T091）← 先配置，再查询
4. Phase 3: US1 账户状态（T032-T057）
5. Phase 5: US3 价格监控（T092-T109）
6. Phase 6: US4 OTO下单（T110-T128）
7. Phase 7: US5 订单监控（T129-T147）← 核心交易循环完成
8. 验证：执行完整的自动交易循环测试
```

**MVP交付物**: 单用户自动交易系统，支持配置、下单、监控、循环交易

#### 📈 完整功能路线

```
9. Phase 8: US6 多用户（T148-T158）
10. Phase 9: US7 统计（T159-T167）
11. Phase 10: Polish（T168-T188）
```

### 并行执行机会

#### Phase 2 内并行（T015-T024）

所有ORM模型可以并行创建：

```bash
# 10个模型可同时创建（不同文件）
T015 [P] users表模型
T016 [P] auth_credentials表模型
T017 [P] trading_configs表模型
T018 [P] token_mappings表模型
T019 [P] token_precisions表模型
T020 [P] oto_order_pairs表模型
T021 [P] orders表模型
T022 [P] trade_records表模型
T023 [P] trading_statistics表模型
T024 [P] price_history表模型
```

#### 用户故事并行（Foundation完成后）

如果团队有多人，Foundation完成后可并行：

```
Developer A: US1 + US2（基础功能）
Developer B: US3（价格监控）
Developer C: US7（统计，可先用Mock数据）

完成后再合并进行US4、US5的集成
```

---

## 测试依赖顺序（按spec.md测试策略）

根据spec.md定义的API测试依赖顺序，测试阶段如下：

### 第一阶段：代币信息测试

- T060: 币安精度信息查询API Mock
- T061: 创建交易配置完整流程（包含代币映射）
- T062: 代币符号映射查询和缓存
- T063: 代币精度信息缓存逻辑

**验证**: 确保代币简称（KOGE）能正确映射到API符号

### 第二阶段：代币价格测试

- T092-T095: 价格WebSocket和波动监控测试

**前置依赖**: 需要第一阶段的代币符号

### 第三阶段：订单下单测试

- T110-T114: OTO订单创建和提交测试

**前置依赖**: 需要第一阶段的代币符号 + 第二阶段的价格数据

### 第四阶段：完整交易流程测试

- T144-T147: 订单状态监控和交易循环测试
- T148-T150: 多用户并发测试

**前置依赖**: 前三阶段所有功能正常

---

## 并行执行示例

### US2配置策略 - 领域层并行

```bash
# 同时创建所有实体和值对象（不同文件）
Task: "T064 [P] [US2] 创建TradingConfig实体"
Task: "T065 [P] [US2] 创建TokenMapping实体"
Task: "T066 [P] [US2] 创建TokenPrecision实体"
Task: "T067 [P] [US2] 创建Price值对象"
Task: "T068 [P] [US2] 创建Quantity值对象"
Task: "T069 [P] [US2] 创建Precision值对象"
Task: "T070 [P] [US2] 定义Config仓储接口"
Task: "T071 [P] [US2] 定义Token仓储接口"
```

### US5订单监控 - 测试并行

```bash
# 同时运行所有单元测试和集成测试（独立测试）
Task: "T129 [P] [US5] 单元测试：订单状态机完整状态转换"
Task: "T130 [P] [US5] 单元测试：状态机防止重复下单逻辑"
Task: "T131 [P] [US5] 单元测试：订单超时检测和处理"
Task: "T132 [P] [US5] 集成测试：WebSocket订单推送连接和消息解析"
Task: "T133 [P] [US5] 集成测试：订单状态机与WebSocket集成"
Task: "T134 [P] [US5] 集成测试：完全成交触发下一轮交易"
```

---

## 实施策略建议

### 🎯 策略1: MVP优先（推荐单人或小团队）

**目标**: 最快时间验证核心价值

1. **Week 1**: Setup + Foundational（T001-T031）
2. **Week 2-3**: US2 配置 + US1 账户（T032-T091）
3. **Week 4**: US3 价格监控（T092-T109）
4. **Week 5-6**: US4 OTO下单 + US5 订单监控（T110-T147）
5. **Week 7**: 集成测试和Bug修复
6. **Week 8**: US6 多用户 + US7 统计（T148-T167）
7. **Week 9**: Polish和部署准备（T168-T188）

**交付**: 9周完整功能

### 📈 策略2: 增量交付（推荐多人团队）

**目标**: 每2周交付一个可用功能

- **Sprint 1**: Setup + Foundational → 基础设施就绪
- **Sprint 2**: US1 + US2 → 账户和配置管理可用
- **Sprint 3**: US3 + US4 → 价格监控和下单可用（手动触发）
- **Sprint 4**: US5 → 自动交易循环可用（单用户MVP）✅
- **Sprint 5**: US6 → 多用户支持
- **Sprint 6**: US7 + Polish → 完整功能和生产优化

**每个Sprint结束都有可演示的增量**

### 🚀 策略3: 并行开发（3+开发者团队）

**Foundation完成后**:

- **Dev A**: US1 + US2 + US7（数据层重点）
- **Dev B**: US3 + US4（价格和订单重点）
- **Dev C**: US5 + US6（状态机和并发重点）

**最后集成和Polish阶段合作**

---

## 验收标准

每个用户故事完成时的验收检查清单：

### US1: 账户状态

- [ ] 可通过API查询用户余额（可用、冻结、总额）
- [ ] 可查询用户交易量统计（累计、今日）
- [ ] 多用户数据正确隔离
- [ ] 所有测试通过（T032-T035）

### US2: 配置策略

- [ ] 可创建和更新交易配置（API）
- [ ] 支持百分比和固定金额两种价格偏移模式
- [ ] 代币符号映射和精度信息正确缓存
- [ ] 缓存未命中时自动调用API更新
- [ ] 所有测试通过（T058-T063）

### US3: 价格监控

- [ ] WebSocket价格连接稳定
- [ ] 价格更新延迟<1秒
- [ ] 价格波动检测准确（1分钟窗口）
- [ ] 超过阈值时正确暂停交易
- [ ] 连接中断时暂停交易并通知
- [ ] 所有测试通过（T092-T095）

### US4: OTO下单

- [ ] 可创建OTO订单对（买单+卖单）
- [ ] 订单价格计算符合配置策略
- [ ] 订单数量符合精度要求
- [ ] 余额不足时暂停交易
- [ ] 订单成功提交到交易所（或Mock）
- [ ] 所有测试通过（T110-T114）

### US5: 订单监控

- [ ] WebSocket订单推送连接稳定
- [ ] 订单状态机正确转换
- [ ] 部分成交状态正确跟踪
- [ ] 超时订单正确取消和重新下单
- [ ] 完全成交后触发下一轮交易
- [ ] 防止重复下单（状态机守卫）
- [ ] 连接中断时暂停交易，需手动恢复
- [ ] 所有测试通过（T129-T134）

### US6: 多用户

- [ ] 支持至少10个用户同时交易
- [ ] 用户间数据完全隔离
- [ ] 单用户异常不影响其他用户
- [ ] 性能测试通过（10用户30分钟稳定运行）
- [ ] 所有测试通过（T148-T150）

### US7: 统计

- [ ] 显示准确的交易统计（交易量、次数、进度）
- [ ] 完成百分比计算准确
- [ ] 订单历史查询支持分页和筛选
- [ ] 所有测试通过（T159-T161）

---

## 总任务统计

- **总任务数**: 188个
- **Setup阶段**: 9个任务
- **Foundational阶段**: 21个任务（关键阻塞）
- **US1 (P1)**: 26个任务
- **US2 (P1)**: 34个任务
- **US3 (P2)**: 18个任务
- **US4 (P1)**: 19个任务
- **US5 (P1)**: 19个任务
- **US6 (P2)**: 11个任务
- **US7 (P3)**: 9个任务
- **Polish阶段**: 22个任务

### 并行机会

- **Setup阶段**: 7个任务可并行（T002-T007, T009）
- **Foundational阶段**: 10个ORM模型可并行（T015-T024）
- **US1-US7**: 每个故事内的测试和模型创建都可并行（标记[P]）
- **用户故事间**: Foundation完成后，US1/US2/US3/US7可并行（取决于团队规模）

### 测试覆盖

- **合约测试**: 4个（币安API Mock）
- **单元测试**: 6个（状态机、价格计算、波动监控等）
- **集成测试**: 20+个（覆盖所有关键流程）
- **性能测试**: 1个（10用户并发）

---

## 注意事项

1. **[P]标记**: 标记为[P]的任务可以并行执行（不同文件，无依赖）
2. **[Story]标记**: 每个任务都标记所属用户故事，便于跟踪和增量交付
3. **TDD顺序**: 每个用户故事的测试必须先编写并验证失败，再实现
4. **Checkpoint**: 每个Phase结束都有明确的验收标准
5. **依赖关系**: Foundational阶段是关键路径，必须优先完成
6. **独立性**: 每个用户故事应尽量独立可测试
7. **提交建议**: 每完成一个任务或一组相关任务后提交代码
8. **文档更新**: 实施过程中如发现spec或plan需要调整，及时更新

---

**任务分解完成时间**: 2025-10-09  
**准备开始实施**: ✅  
**推荐起点**: T001（项目初始化）

