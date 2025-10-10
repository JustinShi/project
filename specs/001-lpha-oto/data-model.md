# Phase 1: Data Model Design
# 币安多用户Alpha代币OTO订单自动交易系统

**Branch**: `001-lpha-oto` | **Date**: 2025-10-09  
**Purpose**: 定义系统的完整数据模型，包括数据库表结构、关系和约束

---

## 数据模型概述

基于功能规范中的Key Entities章节，设计如下数据模型：

### 实体列表

| 实体 | 说明 | 主要用途 |
|------|------|---------|
| User | 用户账户 | 用户身份和基本信息 |
| AuthCredentials | 认证信息 | 加密存储的headers和cookies |
| TradingConfig | 交易配置 | 用户的交易策略参数 |
| TokenMapping | 代币符号映射 | 代币简称到API符号的转换 |
| TokenPrecision | 代币精度缓存 | 交易精度信息 |
| OTOOrderPair | OTO订单对 | 买单+卖单的组合 |
| Order | 订单 | 单个买单或卖单 |
| TradeRecord | 成交记录 | 订单成交明细 |
| TradingStatistics | 交易统计 | 用户交易量和进度统计 |
| PriceHistory | 价格历史 | 用于波动监控的价格数据 |

### ER图关系

```
User 1:1 AuthCredentials
User 1:1 TradingConfig
User 1:N OTOOrderPair
OTOOrderPair 1:2 Order (买单+卖单)
Order 1:N TradeRecord
User 1:1 TradingStatistics

TokenMapping N:N (全局查找表，无外键)
TokenPrecision N:N (全局缓存表，无外键)
PriceHistory (时序数据，按symbol分组)
```

---

## 表结构设计

### 1. users 表

用户账户基本信息

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT users_username_check CHECK (LENGTH(username) >= 3)
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active);
```

**字段说明**:
- `id`: 用户唯一标识
- `username`: 用户名，用于登录和标识
- `is_active`: 账户是否激活（软删除标记）
- `created_at/updated_at`: 时间戳审计

**对应规范**: User Account实体（FR-001）

---

### 2. auth_credentials 表

用户认证信息（加密存储）

```sql
CREATE TABLE auth_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    headers_encrypted TEXT NOT NULL,  -- Fernet加密后的headers JSON字符串
    cookies_encrypted TEXT NOT NULL,  -- Fernet加密后的cookies字符串
    last_verified_at TIMESTAMP,       -- 最后一次验证成功的时间
    is_valid BOOLEAN DEFAULT TRUE,    -- 是否仍然有效
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_auth_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE UNIQUE INDEX idx_auth_user_id ON auth_credentials(user_id);
```

**字段说明**:
- `headers_encrypted`: 加密后的HTTP headers（JSON格式）
- `cookies_encrypted`: 加密后的cookies
- `last_verified_at`: 用于检测认证是否过期
- `is_valid`: 认证失效后标记为FALSE，触发用户通知

**加密存储示例**:
```python
# 原始数据
headers = {"X-Token": "abc123", "User-Agent": "..."}
cookies = "session=xyz789"

# 加密存储
headers_json = json.dumps(headers)
headers_encrypted = crypto_service.encrypt(headers_json)
cookies_encrypted = crypto_service.encrypt(cookies)
```

**对应规范**: Authentication Credentials实体（FR-021, NFR-006）

---

### 3. trading_configs 表

交易配置参数

```sql
CREATE TABLE trading_configs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 代币配置
    token_symbol_short VARCHAR(20) NOT NULL,  -- 代币简称，如KOGE
    
    -- 交易量配置
    target_volume DECIMAL(18, 8) NOT NULL,    -- 目标交易量（USDT）
    current_volume DECIMAL(18, 8) DEFAULT 0,  -- 当前已完成交易量
    
    -- 价格偏移策略
    price_offset_mode VARCHAR(20) NOT NULL,   -- 'percentage' 或 'fixed'
    buy_offset_value DECIMAL(18, 8) NOT NULL, -- 买单偏移值（百分比或金额）
    sell_offset_value DECIMAL(18, 8) NOT NULL,-- 卖单偏移值
    
    -- 订单数量和超时
    order_quantity DECIMAL(18, 8) NOT NULL,   -- 每次订单数量
    timeout_seconds INTEGER DEFAULT 300,      -- 订单超时时间（秒）
    
    -- 风险控制
    price_volatility_threshold DECIMAL(5, 2) DEFAULT 2.0,  -- 价格波动阈值（百分比）
    
    -- 交易状态
    is_trading_active BOOLEAN DEFAULT FALSE,  -- 是否正在交易
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_config_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT chk_offset_mode CHECK (price_offset_mode IN ('percentage', 'fixed')),
    CONSTRAINT chk_target_volume CHECK (target_volume > 0),
    CONSTRAINT chk_order_quantity CHECK (order_quantity > 0),
    CONSTRAINT chk_volatility CHECK (price_volatility_threshold >= 0)
);

CREATE UNIQUE INDEX idx_config_user_id ON trading_configs(user_id);
CREATE INDEX idx_config_is_trading ON trading_configs(is_trading_active);
```

**字段说明**:
- `token_symbol_short`: 代币简称，用于查找TokenMapping
- `price_offset_mode`: 偏移计算模式（百分比或固定金额）
- `buy/sell_offset_value`: 偏移值（根据mode解释）
- `is_trading_active`: 交易是否运行中

**对应规范**: Trading Configuration实体（FR-004, FR-007, FR-020）

---

### 4. token_mappings 表

代币符号映射关系

```sql
CREATE TABLE token_mappings (
    id SERIAL PRIMARY KEY,
    symbol_short VARCHAR(20) UNIQUE NOT NULL,  -- 简称，如KOGE
    token_name VARCHAR(100),                   -- 完整名称
    order_api_symbol VARCHAR(50) NOT NULL,     -- 订单API符号，如ALPHA_123
    websocket_symbol VARCHAR(50) NOT NULL,     -- WebSocket符号，如alpha_123usdt
    alpha_id VARCHAR(50),                      -- Alpha ID，如ALPHA_123
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_token_symbol_short ON token_mappings(symbol_short);
CREATE INDEX idx_token_order_symbol ON token_mappings(order_api_symbol);
```

**示例数据**:
```sql
INSERT INTO token_mappings (symbol_short, token_name, order_api_symbol, websocket_symbol, alpha_id)
VALUES ('KOGE', 'Kog Coin', 'ALPHA_373', 'alpha_373usdt', 'ALPHA_373');
```

**对应规范**: Token Symbol Mapping实体（FR-022, FR-026）

---

### 5. token_precisions 表

代币精度信息缓存

```sql
CREATE TABLE token_precisions (
    id SERIAL PRIMARY KEY,
    symbol_short VARCHAR(20) UNIQUE NOT NULL,  -- 代币简称
    trade_decimal INTEGER NOT NULL,            -- 交易精度
    token_decimal INTEGER NOT NULL,            -- 代币精度
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 缓存时间
    expires_at TIMESTAMP NOT NULL,             -- 过期时间（24小时后）
    
    CONSTRAINT chk_trade_decimal CHECK (trade_decimal >= 0 AND trade_decimal <= 18),
    CONSTRAINT chk_token_decimal CHECK (token_decimal >= 0 AND token_decimal <= 18)
);

CREATE UNIQUE INDEX idx_precision_symbol ON token_precisions(symbol_short);
CREATE INDEX idx_precision_expires ON token_precisions(expires_at);
```

**数据示例**:
```sql
INSERT INTO token_precisions (symbol_short, trade_decimal, token_decimal, expires_at)
VALUES ('KOGE', 8, 18, NOW() + INTERVAL '24 hours');
```

**对应规范**: Token Precision Cache实体（FR-023, FR-024）

---

### 6. oto_order_pairs 表

OTO订单对

```sql
CREATE TABLE oto_order_pairs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 订单标识
    buy_order_id INTEGER,   -- 外键到orders表
    sell_order_id INTEGER,  -- 外键到orders表
    
    -- 状态
    status VARCHAR(30) NOT NULL,  -- idle, placing, pending, filled, timeout, cancelled
    state_machine_state VARCHAR(50),  -- 状态机当前状态（JSON序列化）
    
    -- 交易数据
    target_price DECIMAL(18, 8),      -- 目标价格（基准价）
    buy_price DECIMAL(18, 8),         -- 计算后的买单价格
    sell_price DECIMAL(18, 8),        -- 计算后的卖单价格
    quantity DECIMAL(18, 8),          -- 订单数量
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    placed_at TIMESTAMP,              -- 订单提交时间
    filled_at TIMESTAMP,              -- 完全成交时间
    cancelled_at TIMESTAMP,
    
    CONSTRAINT fk_oto_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT chk_oto_status CHECK (status IN ('idle', 'placing', 'pending', 'partially_filled', 'filled', 'timeout', 'cancelled'))
);

CREATE INDEX idx_oto_user_id ON oto_order_pairs(user_id);
CREATE INDEX idx_oto_status ON oto_order_pairs(status);
CREATE INDEX idx_oto_created_at ON oto_order_pairs(created_at DESC);
```

**对应规范**: OTO Order Pair实体（FR-008, FR-011）

---

### 7. orders 表

单个订单（买单或卖单）

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    oto_pair_id INTEGER NOT NULL REFERENCES oto_order_pairs(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 订单基本信息
    exchange_order_id VARCHAR(100) UNIQUE,  -- 交易所返回的订单ID
    side VARCHAR(10) NOT NULL,              -- 'BUY' 或 'SELL'
    order_type VARCHAR(20) DEFAULT 'LIMIT', -- 订单类型
    
    -- 价格和数量
    price DECIMAL(18, 8) NOT NULL,
    quantity DECIMAL(18, 8) NOT NULL,
    filled_quantity DECIMAL(18, 8) DEFAULT 0,  -- 已成交数量
    
    -- 状态
    status VARCHAR(30) NOT NULL,  -- NEW, PARTIALLY_FILLED, FILLED, CANCELLED, PENDING
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP,       -- 提交到交易所时间
    filled_at TIMESTAMP,          -- 完全成交时间
    cancelled_at TIMESTAMP,
    
    CONSTRAINT fk_order_oto FOREIGN KEY (oto_pair_id) REFERENCES oto_order_pairs(id),
    CONSTRAINT fk_order_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT chk_side CHECK (side IN ('BUY', 'SELL')),
    CONSTRAINT chk_order_status CHECK (status IN ('NEW', 'PENDING', 'PARTIALLY_FILLED', 'FILLED', 'CANCELLED'))
);

CREATE INDEX idx_order_user_id ON orders(user_id);
CREATE INDEX idx_order_oto_pair ON orders(oto_pair_id);
CREATE INDEX idx_order_exchange_id ON orders(exchange_order_id);
CREATE INDEX idx_order_status ON orders(status);
```

**对应规范**: Order实体（FR-009, FR-010, FR-013）

---

### 8. trade_records 表

订单成交明细

```sql
CREATE TABLE trade_records (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 成交信息
    exchange_trade_id VARCHAR(100),  -- 交易所成交ID
    price DECIMAL(18, 8) NOT NULL,
    quantity DECIMAL(18, 8) NOT NULL,
    total_value DECIMAL(18, 8) NOT NULL,  -- 成交总额（price * quantity）
    
    -- 手续费
    commission DECIMAL(18, 8),
    commission_asset VARCHAR(20),
    
    -- 时间
    trade_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_trade_order FOREIGN KEY (order_id) REFERENCES orders(id),
    CONSTRAINT fk_trade_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_trade_order_id ON trade_records(order_id);
CREATE INDEX idx_trade_user_id ON trade_records(user_id);
CREATE INDEX idx_trade_time ON trade_records(trade_time DESC);
```

**对应规范**: Trade Record实体（FR-013）

---

### 9. trading_statistics 表

用户交易统计

```sql
CREATE TABLE trading_statistics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 交易量统计
    total_volume DECIMAL(18, 8) DEFAULT 0,       -- 累计交易量（USDT）
    today_volume DECIMAL(18, 8) DEFAULT 0,       -- 今日交易量
    total_trade_count INTEGER DEFAULT 0,         -- 总交易笔数
    today_trade_count INTEGER DEFAULT 0,         -- 今日交易笔数
    
    -- 订单统计
    total_orders INTEGER DEFAULT 0,
    filled_orders INTEGER DEFAULT 0,
    cancelled_orders INTEGER DEFAULT 0,
    
    -- 进度
    target_volume DECIMAL(18, 8),                -- 目标交易量（从config同步）
    completion_percentage DECIMAL(5, 2),         -- 完成百分比
    
    -- 时间
    last_trade_at TIMESTAMP,
    stats_date DATE DEFAULT CURRENT_DATE,        -- 统计日期（用于每日重置）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_stats_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE UNIQUE INDEX idx_stats_user_id ON trading_statistics(user_id);
CREATE INDEX idx_stats_date ON trading_statistics(stats_date);
```

**对应规范**: Trading Statistics实体（FR-003, FR-014, SC-007）

---

### 10. price_history 表

价格历史数据（波动监控）

```sql
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,               -- 代币符号
    price DECIMAL(18, 8) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 聚合数据（可选，用于性能优化）
    minute_bucket TIMESTAMP,  -- 按分钟聚合的时间桶
    
    CONSTRAINT chk_price_positive CHECK (price > 0)
);

CREATE INDEX idx_price_symbol_time ON price_history(symbol, timestamp DESC);
CREATE INDEX idx_price_minute_bucket ON price_history(minute_bucket);

-- 自动清理策略：保留最近24小时数据
CREATE OR REPLACE FUNCTION cleanup_old_prices() RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM price_history 
    WHERE timestamp < NOW() - INTERVAL '24 hours';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_cleanup_prices
AFTER INSERT ON price_history
EXECUTE FUNCTION cleanup_old_prices();
```

**对应规范**: Price Data实体（FR-006, FR-020）

---

## 数据关系图

```
┌─────────────┐
│   users     │
└──────┬──────┘
       │ 1:1
       ├────────────┬─────────────┬────────────────┬──────────────┐
       │            │             │                │              │
       ▼ 1:1        ▼ 1:1         ▼ 1:N            ▼ 1:1          ▼ 1:N
┌──────────────┐ ┌───────────┐ ┌──────────────┐ ┌──────────┐ ┌─────────┐
│auth_         │ │trading_   │ │oto_order_    │ │trading_  │ │orders   │
│credentials   │ │configs    │ │pairs         │ │statistics│ └─────────┘
└──────────────┘ └───────────┘ └──────┬───────┘ └──────────┘
                                       │ 1:2
                                       ▼
                                 ┌──────────┐
                                 │orders    │
                                 └────┬─────┘
                                      │ 1:N
                                      ▼
                                 ┌──────────────┐
                                 │trade_records │
                                 └──────────────┘

全局查找表（无外键关系）:
┌─────────────────┐   ┌──────────────────┐   ┌──────────────┐
│token_mappings   │   │token_precisions  │   │price_history │
└─────────────────┘   └──────────────────┘   └──────────────┘
```

---

## 数据验证规则

### 领域约束

基于功能需求的数据验证：

1. **余额检查** (FR-017):
   ```sql
   -- 下单前检查：order_quantity * price <= user.available_balance
   ```

2. **精度验证** (FR-023, FR-024):
   ```python
   # 价格和数量必须符合精度要求
   def validate_precision(value: Decimal, precision: int) -> bool:
       # 检查小数位数不超过precision
       return value.as_tuple().exponent >= -precision
   ```

3. **状态转换验证** (FR-011):
   ```python
   # 使用状态机确保合法转换
   # 非法转换会抛出异常
   ```

4. **价格波动检查** (FR-020):
   ```python
   # 1分钟内价格变动 > threshold → 暂停交易
   volatility = (max_price - min_price) / min_price * 100
   if volatility > config.price_volatility_threshold:
       pause_trading()
   ```

---

## 数据库迁移脚本示例

使用Alembic创建迁移：

```bash
# 初始化Alembic
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Initial schema"

# 应用迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

**首次迁移脚本预览** (`alembic/versions/001_initial_schema.py`):
```python
def upgrade():
    # 创建users表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        # ... 其他列
    )
    
    # 创建auth_credentials表
    # ... (完整脚本见实际迁移文件)
```

---

## 性能优化策略

### 索引策略

1. **查询优化索引**:
   - `idx_order_user_status`: 按用户和状态查询订单
   - `idx_oto_user_created`: 按用户查询最近订单对

2. **复合索引**:
   ```sql
   CREATE INDEX idx_order_user_status ON orders(user_id, status, created_at DESC);
   ```

3. **部分索引**（仅活跃订单）:
   ```sql
   CREATE INDEX idx_active_orders ON orders(user_id)
   WHERE status IN ('NEW', 'PENDING', 'PARTIALLY_FILLED');
   ```

### 查询优化

1. **避免N+1查询**:
   ```python
   # 使用SQLAlchemy的joinedload
   orders = session.query(OTOOrderPair)\
       .options(joinedload(OTOOrderPair.buy_order))\
       .options(joinedload(OTOOrderPair.sell_order))\
       .filter_by(user_id=user_id).all()
   ```

2. **批量操作**:
   ```python
   # 批量插入trade_records
   session.bulk_insert_mappings(TradeRecord, trade_data_list)
   ```

---

## 数据模型完成

✅ 所有表结构已定义  
✅ 关系和约束已明确  
✅ 索引策略已规划  
✅ 迁移工具已确定（Alembic）

**Phase 1: Data Model 完成标记**: ✅ 2025-10-09

下一步: 创建API合约定义（contracts/）

