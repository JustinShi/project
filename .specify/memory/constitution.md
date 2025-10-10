# Python Trading System Constitution

本宪法定义币安Alpha代币OTO交易系统及所有后续Python交易项目的核心开发原则。

## Core Principles

### I. 领域驱动设计（Domain-Driven Design）

**强制要求**:
- 所有特性必须采用DDD分层架构：Domain（领域层）、Application（应用层）、Infrastructure（基础设施层）、API（接口层）
- Domain层不得依赖任何外部技术实现（纯业务逻辑）
- 领域实体必须自包含验证逻辑和业务规则
- 值对象必须是不可变的
- 聚合根负责维护内部一致性

**验证检查点**:
- [ ] 项目结构遵循`src/{domain}/domain/`, `src/{domain}/application/`, `src/{domain}/infrastructure/`分层
- [ ] Domain层无外部依赖（SQLAlchemy、FastAPI等导入禁止出现在domain/目录）
- [ ] 所有Repository接口定义在`domain/repositories/`，实现在`infrastructure/database/repositories/`

### II. 测试驱动开发（Test-Driven Development - NON-NEGOTIABLE）

**强制要求**:
- TDD循环严格执行：编写测试 → 用户确认 → 测试失败 → 实现代码 → 测试通过 → 重构
- 每个用户故事必须先编写测试任务，再编写实现任务
- 测试必须独立可运行，不依赖外部服务的实际连接（使用Mock/Stub）
- 最低代码覆盖率：单元测试80%，集成测试关键路径100%

**测试分类要求**:
- **合约测试**: 外部API（如币安API）必须有Mock合约测试
- **单元测试**: 领域模型、业务逻辑、状态机等纯逻辑测试
- **集成测试**: WebSocket连接、数据库操作、缓存交互等技术集成测试
- **端到端测试**: 关键用户场景的完整流程测试

**验证检查点**:
- [ ] 每个用户故事的tasks.md中，测试任务编号小于实现任务编号
- [ ] 运行`pytest --cov`达到80%+覆盖率
- [ ] CI/CD pipeline包含测试门禁（测试失败则阻止部署）

### III. 可观测性（Observability - Mandatory）

**强制要求**:
- 使用结构化日志（structlog），输出JSON格式
- 所有关键业务操作必须记录日志：交易决策、订单提交、状态变更、异常处理
- 日志级别规范：
  - ERROR: 需要人工介入的错误
  - WARNING: 异常但系统可自动处理（如暂停交易、重连）
  - INFO: 业务关键操作（订单提交、状态转换）
  - DEBUG: 技术细节（API调用、数据库查询）
- 敏感数据脱敏：不得在日志中记录完整的headers、cookies、密钥

**审计追踪要求**:
- 所有交易操作必须有完整审计日志（who, what, when, result）
- 配置变更必须记录（old_value, new_value, changed_by）
- 认证信息更新必须记录（timestamp, user_id）

**监控指标要求**:
- WebSocket连接状态和延迟
- API调用成功率和响应时间
- 订单成功率和准确率
- 活跃用户数和并发交易数

**验证检查点**:
- [ ] `src/{domain}/infrastructure/logging/logger.py`配置structlog
- [ ] 所有service层方法包含`logger.info`或`logger.error`调用
- [ ] 运行时日志输出为JSON格式
- [ ] 敏感字段（headers、cookies）通过过滤器脱敏

### IV. 安全优先（Security-First）

**强制要求**:
- 所有敏感数据（认证信息、密钥）必须加密存储
- 使用经过验证的加密库（cryptography.Fernet）
- 密钥管理：从环境变量读取，不得硬编码
- 数据库查询必须使用参数化查询（ORM自动处理），禁止字符串拼接
- API访问控制：多用户系统必须验证user_id隔离

**加密标准**:
- 认证信息加密：Fernet（AES-128-CBC + HMAC）
- 密钥长度：最少32字节（256位）
- 密钥轮换：支持双密钥解密（过渡期）

**验证检查点**:
- [ ] `auth_credentials`表的敏感字段名为`*_encrypted`
- [ ] 加密密钥通过`os.getenv("ENCRYPTION_KEY")`读取
- [ ] 所有API端点验证`user_id`参数与请求用户一致
- [ ] 代码审查检查：无硬编码密钥、无SQL字符串拼接

### V. 简洁性原则（Simplicity - YAGNI）

**强制要求**:
- 从最简单的实现开始，避免过度设计
- 明确定义Out of Scope，拒绝未验证的需求
- MVP优先：先交付核心功能，再迭代扩展
- 技术选型：优先使用成熟、广泛采用的库，避免实验性技术

**复杂度管控**:
- 单个函数/方法最大行数：50行（超过则拆分）
- 单个类最大行数：300行（超过则考虑拆分）
- 嵌套层级：最多3层（超过则提取方法）
- 依赖注入：优先使用FastAPI的依赖注入，避免复杂的DI框架

**验证检查点**:
- [ ] spec.md包含明确的"Out of Scope"章节
- [ ] 代码审查：超过50行的函数要求说明或重构
- [ ] 新增外部依赖必须在plan.md中说明理由

---

## 技术约束

### 语言和框架

**Python版本**: 3.11+（利用新特性：类型提示、async改进）

**核心框架**:
- Web: FastAPI（异步、自动文档、类型安全）
- ORM: SQLAlchemy 2.0+（async支持）
- 测试: pytest + pytest-asyncio
- 日志: structlog（结构化日志）

### 数据库和缓存

**主数据库**: PostgreSQL 14+
- 原因：成熟的ACID支持，JSON类型，丰富索引

**缓存**: Redis 7.0+
- 用途：代币精度缓存、价格历史（时序数据）

### 代码质量工具

**强制使用**:
- ruff（linting + formatting，替代flake8+black）
- mypy（静态类型检查）
- pre-commit（提交前自动检查）

**验证门禁**:
- `ruff check src/` 无错误
- `mypy src/` 无类型错误
- 测试覆盖率 ≥ 80%

---

## 开发工作流

### 功能开发流程

1. **规范阶段** (`/speckit.specify`)
   - 编写功能规范（spec.md）
   - 明确用户故事和验收标准
   - 定义Out of Scope

2. **澄清阶段** (`/speckit.clarify`)
   - 解决规范中的模糊点
   - 记录所有澄清决策

3. **规划阶段** (`/speckit.plan`)
   - 技术选型和架构设计
   - 数据模型设计
   - API合约定义

4. **任务分解** (`/speckit.tasks`)
   - 生成详细的任务列表
   - 按用户故事分组
   - TDD顺序：测试先行

5. **实施阶段**
   - 按任务顺序执行
   - TDD循环：测试 → 实现 → 重构
   - 每个用户故事完成后独立验收

### 代码审查要求

**必须审查项**:
- [ ] Constitution原则合规性
- [ ] 测试覆盖充分（新功能必须有测试）
- [ ] 日志记录完整（关键操作有日志）
- [ ] 敏感数据保护（无硬编码密钥）
- [ ] 类型提示完整（公共API必须有类型）

### 质量门禁

**阻止合并的条件**:
- ❌ 测试未通过
- ❌ 代码覆盖率下降
- ❌ ruff或mypy报错
- ❌ 违反Constitution原则且无充分理由

---

## 性能和规模标准

### 响应时间要求

| 操作类型 | 目标延迟 | 最大延迟 |
|---------|---------|---------|
| API查询请求 | <200ms (p95) | <500ms (p99) |
| WebSocket消息处理 | <100ms (p95) | <200ms (p99) |
| 价格更新到订单计算 | <2秒 (平均) | <5秒 (p99) |
| 数据库查询 | <50ms (简单查询) | <200ms (复杂聚合) |

### 并发支持

- 最少支持：10个用户同时交易
- 目标支持：100个用户同时交易
- 扩展策略：水平扩展（多实例 + 负载均衡）

### 数据准确性

- 订单数据准确率：**100%**（不可妥协）
- 防止重复下单：通过状态机强制保证
- 状态一致性：基于WebSocket推送维护

---

## Governance

### Constitution权威性

本Constitution是所有开发决策的最高准则：
- 所有PR必须验证Constitution合规性
- 违反原则必须在PR中明确说明理由并获得批准
- Constitution修改需要正式提案和团队共识

### 复杂度说明要求

当引入以下复杂度时，必须在设计文档中说明理由：
- 新增外部依赖库
- 引入新的架构模式
- 超过简洁性原则限制（如超长函数）
- 偏离标准技术栈

### 例外处理

Constitution原则在以下情况可申请例外：
1. 外部系统强制要求（如币安API协议）
2. 性能关键路径的优化需求
3. 安全漏洞的紧急修复

**例外流程**:
1. 在spec.md或plan.md中明确标注`[Constitution Exception]`
2. 说明违反的原则和理由
3. 提供替代方案评估
4. 获得团队批准后记录在案

---

**Version**: 1.0.0  
**Ratified**: 2025-10-09  
**Last Amended**: 2025-10-09  
**Applicable Projects**: 币安Alpha代币OTO交易系统及后续Python交易项目