# BinanceTools 简化结构设计

## 🎯 目标：个人开发友好的轻量级结构

### 📋 简化原则

1. **减少层次** - 合并过度细分的层次
2. **移除抽象** - 去掉不必要的抽象层
3. **保持核心** - 保留核心业务功能
4. **易于理解** - 结构清晰，便于个人维护

### 🏗️ 简化后的结构

```
src/BinanceTools/
├── models/                   # 数据模型 (合并实体和值对象)
│   ├── user.py              # 用户模型
│   ├── wallet.py            # 钱包模型
│   ├── order.py             # 订单模型
│   └── trade.py             # 交易模型
├── services/                 # 业务服务 (合并领域服务和应用服务)
│   ├── trading_service.py   # 交易服务
│   ├── wallet_service.py    # 钱包服务
│   └── user_service.py      # 用户服务
├── api/                      # API接口 (简化应用层)
│   ├── binance_api.py       # Binance API接口
│   └── endpoints.py         # API端点
├── infrastructure/           # 基础设施 (保留核心)
│   ├── http_client.py       # HTTP客户端
│   └── websocket_client.py  # WebSocket客户端
├── config/                   # 配置 (保留)
│   └── user_config.py       # 用户配置
└── utils/                    # 工具 (保留)
    └── helpers.py           # 辅助函数
```

### 🔄 简化策略

#### 1. 合并层次
- **领域层 + 应用层** → **services/**
- **实体 + 值对象** → **models/**
- **用例 + DTO** → **api/**

#### 2. 移除复杂抽象
- 移除聚合根
- 移除领域事件
- 移除仓储接口
- 简化领域服务

#### 3. 保留核心功能
- 保留业务逻辑
- 保留数据模型
- 保留API接口
- 保留基础设施

### 📊 简化对比

| 原DDD结构 | 简化后结构 | 说明 |
|-----------|------------|------|
| domain/entities/ | models/ | 合并实体和值对象 |
| domain/value_objects/ | models/ | 合并到数据模型 |
| domain/aggregates/ | 移除 | 过度抽象 |
| domain/repositories/ | 移除 | 直接使用服务 |
| domain/services/ | services/ | 保留核心服务 |
| domain/events/ | 移除 | 过度复杂 |
| application/use_cases/ | api/ | 简化为API接口 |
| application/dto/ | api/ | 合并到API层 |

### 🎯 简化后的优势

1. **结构清晰** - 层次简单，易于理解
2. **开发效率** - 减少抽象，提高开发速度
3. **维护简单** - 文件少，关系简单
4. **个人友好** - 适合个人开发和维护
5. **功能完整** - 保留所有核心功能

### 📝 实现计划

1. **创建简化结构** - 创建新的目录结构
2. **迁移核心功能** - 将核心功能迁移到简化结构
3. **移除复杂抽象** - 删除过度复杂的抽象层
4. **测试验证** - 确保功能正常
5. **更新文档** - 更新使用文档
