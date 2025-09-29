# BinanceTools DDD结构设计

## 🏗️ DDD架构设计

### 📋 当前结构分析

```
src/BinanceTools/
├── application/          # 应用层
├── config/              # 配置层
├── infrastructure/      # 基础设施层
├── service/            # 服务层
├── utils/              # 工具层
└── examples/           # 示例
```

### 🎯 DDD目标结构

```
src/BinanceTools/
├── domain/                    # 领域层 (核心业务逻辑)
│   ├── entities/             # 实体
│   │   ├── user.py          # 用户实体
│   │   ├── wallet.py        # 钱包实体
│   │   ├── order.py         # 订单实体
│   │   └── trade.py         # 交易实体
│   ├── value_objects/        # 值对象
│   │   ├── money.py         # 金额值对象
│   │   ├── symbol.py        # 交易对值对象
│   │   └── timestamp.py     # 时间戳值对象
│   ├── aggregates/           # 聚合根
│   │   ├── trading_account.py # 交易账户聚合
│   │   └── portfolio.py     # 投资组合聚合
│   ├── repositories/         # 仓储接口
│   │   ├── user_repository.py
│   │   ├── wallet_repository.py
│   │   └── order_repository.py
│   ├── services/            # 领域服务
│   │   ├── trading_service.py
│   │   └── risk_service.py
│   └── events/              # 领域事件
│       ├── order_created.py
│       └── trade_executed.py
├── application/              # 应用层 (用例和应用服务)
│   ├── use_cases/           # 用例
│   │   ├── get_wallet_balance.py
│   │   ├── place_order.py
│   │   └── get_trading_volume.py
│   ├── services/            # 应用服务
│   │   ├── trading_application_service.py
│   │   └── portfolio_application_service.py
│   ├── dto/                 # 数据传输对象
│   │   ├── wallet_dto.py
│   │   ├── order_dto.py
│   │   └── trade_dto.py
│   └── interfaces/          # 应用接口
│       ├── trading_interface.py
│       └── portfolio_interface.py
├── infrastructure/           # 基础设施层 (外部依赖)
│   ├── repositories/        # 仓储实现
│   │   ├── binance_user_repository.py
│   │   ├── binance_wallet_repository.py
│   │   └── binance_order_repository.py
│   ├── external_services/   # 外部服务
│   │   ├── binance_api_client.py
│   │   └── binance_websocket_client.py
│   ├── config/              # 配置
│   │   ├── user_config.py
│   │   ├── api_config.py
│   │   └── proxy_config.py
│   └── adapters/            # 适配器
│       ├── http_adapter.py
│       └── websocket_adapter.py
├── interfaces/               # 接口层 (用户接口)
│   ├── cli/                 # 命令行接口
│   ├── api/                 # REST API接口
│   └── sdk/                 # SDK接口
└── shared/                   # 共享层
    ├── exceptions/          # 异常
    ├── utils/               # 工具函数
    └── constants/           # 常量
```

## 🔄 迁移计划

### 阶段1: 创建领域层
1. 创建实体 (User, Wallet, Order, Trade)
2. 创建值对象 (Money, Symbol, Timestamp)
3. 创建聚合根 (TradingAccount, Portfolio)
4. 定义仓储接口

### 阶段2: 重构应用层
1. 创建用例 (GetWalletBalance, PlaceOrder, GetTradingVolume)
2. 创建应用服务
3. 创建DTO对象
4. 定义应用接口

### 阶段3: 优化基础设施层
1. 实现仓储接口
2. 重构外部服务
3. 优化配置管理
4. 创建适配器

### 阶段4: 创建接口层
1. 创建CLI接口
2. 创建REST API接口
3. 创建SDK接口

### 阶段5: 测试和验证
1. 单元测试
2. 集成测试
3. 性能测试
4. 文档更新

## 🎯 DDD核心概念

### 实体 (Entities)
- **User**: 用户实体，包含用户身份和配置
- **Wallet**: 钱包实体，包含资产信息
- **Order**: 订单实体，包含订单状态和详情
- **Trade**: 交易实体，包含交易记录

### 值对象 (Value Objects)
- **Money**: 金额值对象，包含数值和货币类型
- **Symbol**: 交易对值对象，包含基础资产和报价资产
- **Timestamp**: 时间戳值对象，包含时间信息

### 聚合根 (Aggregates)
- **TradingAccount**: 交易账户聚合，管理用户的所有交易相关操作
- **Portfolio**: 投资组合聚合，管理用户的资产组合

### 领域服务 (Domain Services)
- **TradingService**: 交易领域服务，处理交易逻辑
- **RiskService**: 风险领域服务，处理风险控制

### 仓储 (Repositories)
- **UserRepository**: 用户仓储接口
- **WalletRepository**: 钱包仓储接口
- **OrderRepository**: 订单仓储接口

## 📊 优势

1. **清晰的职责分离**: 每层都有明确的职责
2. **高内聚低耦合**: 模块间依赖关系清晰
3. **易于测试**: 每层都可以独立测试
4. **易于维护**: 修改影响范围可控
5. **易于扩展**: 新功能可以按层添加
