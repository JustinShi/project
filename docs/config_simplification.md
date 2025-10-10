# 配置文件简化说明

## 📋 简化前后对比

### ❌ 简化前（109 行，大量重复）

```yaml
global_settings:
  # 基础交易参数（7个）
  default_buy_offset_value: 0.5
  default_sell_offset_value: 0.5
  default_order_quantity: 10.0
  default_price_offset_mode: PERCENTAGE
  default_price_volatility_threshold: 5.0
  default_timeout_seconds: 1800
  
  # 策略专用参数（4个，与上面重复）
  default_buy_offset_percentage: 0.5      # 与 default_buy_offset_value 重复
  default_sell_profit_percentage: 1.0     # 与 default_sell_offset_value 重复
  default_trade_interval_seconds: 1
  default_single_trade_amount_usdt: 30
  
  # 风控参数（5个，部分重复）
  max_concurrent_orders: 5
  max_concurrent_users: 10
  max_retry_attempts: 3
  order_retry_attempts: 3                 # 与 max_retry_attempts 重复
  retry_delay_seconds: 5
  
  # 超时设置（2个）
  order_timeout_seconds: 300
  websocket_reconnect_delay_seconds: 3

# 用户基础配置（现在基本不用了）
users:
  - user_id: 1
    trading_targets:
      - token_symbol_short: KOGE
        chain: BSC
        target_volume: 1000.0
        current_volume: 300.0
        order_quantity: 10.0
        buy_offset_value: 0.5
        sell_offset_value: 0.5
        price_offset_mode: PERCENTAGE
        price_volatility_threshold: 5.0
        timeout_seconds: 1800
        volume_multiplier: 1.0
        is_trading_active: true

# 策略配置
strategies:
  - strategy_id: "koge_volume_boost"
    strategy_name: "KOGE 刷量策略"
    enabled: true
    target_token: KOGE
    target_chain: BSC
    target_volume: 16384
    single_trade_amount_usdt: 30          # 已在全局默认
    trade_interval_seconds: 1             # 已在全局默认
    buy_offset_percentage: 0.5            # 已在全局默认
    sell_profit_percentage: 1.0           # 已在全局默认
    user_ids: [1]
    price_volatility_threshold: 5.0       # 已在全局默认
    max_retry_attempts: 3                 # 已在全局默认

# 用户覆盖（重复策略默认值）
user_overrides:
  - user_id: 1
    strategies:
      koge_volume_boost:
        enabled: true                     # 已在策略中配置
        single_trade_amount_usdt: 30      # 已在策略中配置
        trade_interval_seconds: 1         # 已在策略中配置
```

**问题**:
- ❌ 109 行配置
- ❌ 大量重复的参数定义
- ❌ `users` 部分现在基本不用
- ❌ `user_overrides` 重复了策略默认值
- ❌ 策略中重复了全局默认值

---

### ✅ 简化后（45 行，去除所有冗余）

```yaml
# 全局设置
global_settings:
  # 交易参数
  default_buy_offset_percentage: 0.5
  default_sell_profit_percentage: 1.0
  default_trade_interval_seconds: 1
  default_single_trade_amount_usdt: 30
  
  # 风控参数
  max_concurrent_users: 10
  max_price_volatility_percentage: 5.0
  max_retry_attempts: 3
  retry_delay_seconds: 5
  order_timeout_seconds: 300

# 策略配置
strategies:
  # KOGE 刷量策略
  - strategy_id: "koge_volume_boost"
    strategy_name: "KOGE 刷量策略"
    enabled: true
    target_token: KOGE
    target_chain: BSC
    target_volume: 16384
    user_ids: [1]
    # 其他参数使用全局默认值

  # AOP 测试策略
  - strategy_id: "aop_test"
    strategy_name: "AOP 测试策略"
    enabled: false
    target_token: AOP
    target_chain: BSC
    target_volume: 1000
    single_trade_amount_usdt: 10          # 仅覆盖需要的参数
    trade_interval_seconds: 2
    user_ids: [1]

# 用户自定义配置（可选）
user_overrides: []
  # 示例：
  # - user_id: 1
  #   strategies:
  #     koge_volume_boost:
  #       single_trade_amount_usdt: 50
```

**优点**:
- ✅ 45 行配置（减少 59%）
- ✅ 清晰的参数继承关系
- ✅ 只配置需要的参数
- ✅ 易于维护和理解

---

## 🎯 配置优先级

```
全局默认值 (global_settings)
    ↓ 被覆盖
策略配置 (strategies)
    ↓ 被覆盖
用户覆盖 (user_overrides) ← 最高优先级
```

### 示例：参数解析流程

**配置**:
```yaml
global_settings:
  default_single_trade_amount_usdt: 30

strategies:
  - strategy_id: "koge"
    target_volume: 16384
    user_ids: [1]
    # single_trade_amount_usdt 未配置

user_overrides:
  - user_id: 1
    strategies:
      koge:
        single_trade_amount_usdt: 50
```

**解析结果**:
- 用户 1 的 `single_trade_amount_usdt` = **50** (来自 user_overrides)
- 用户 2 的 `single_trade_amount_usdt` = **30** (来自 global_settings)

---

## 📝 配置指南

### 1. 最小化配置（推荐）

仅配置必需参数，其他使用默认值：

```yaml
global_settings:
  default_buy_offset_percentage: 0.5
  default_sell_profit_percentage: 1.0
  default_trade_interval_seconds: 1
  default_single_trade_amount_usdt: 30
  max_concurrent_users: 10
  max_retry_attempts: 3

strategies:
  - strategy_id: "my_strategy"
    strategy_name: "我的策略"
    enabled: true
    target_token: KOGE
    target_chain: BSC
    target_volume: 10000
    user_ids: [1]

user_overrides: []
```

### 2. 策略覆盖全局默认值

只覆盖需要不同值的参数：

```yaml
strategies:
  - strategy_id: "fast_strategy"
    target_token: KOGE
    target_volume: 5000
    trade_interval_seconds: 0.5          # 覆盖：比全局默认更快
    user_ids: [1]

  - strategy_id: "large_strategy"
    target_token: AOP
    target_volume: 20000
    single_trade_amount_usdt: 100        # 覆盖：比全局默认更大
    user_ids: [1]
```

### 3. 用户自定义配置

针对特定用户覆盖策略参数：

```yaml
user_overrides:
  - user_id: 1
    strategies:
      my_strategy:
        single_trade_amount_usdt: 50     # VIP 用户，单次金额更大

  - user_id: 2
    strategies:
      my_strategy:
        single_trade_amount_usdt: 10     # 普通用户，单次金额较小
```

---

## 🔍 必需参数 vs 可选参数

### 必需参数（每个策略必须配置）

```yaml
strategies:
  - strategy_id: "xxx"           # ✅ 必需：策略唯一标识
    strategy_name: "xxx"         # ✅ 必需：策略名称
    enabled: true/false          # ✅ 必需：是否启用
    target_token: "XXX"          # ✅ 必需：目标代币
    target_chain: "BSC"          # ✅ 必需：目标链
    target_volume: 1000          # ✅ 必需：目标交易量
    user_ids: [1, 2]             # ✅ 必需：参与用户
```

### 可选参数（可继承全局默认值）

```yaml
    single_trade_amount_usdt: 30          # ⭕ 可选
    trade_interval_seconds: 1             # ⭕ 可选
    buy_offset_percentage: 0.5            # ⭕ 可选
    sell_profit_percentage: 1.0           # ⭕ 可选
    price_volatility_threshold: 5.0       # ⭕ 可选
    max_retry_attempts: 3                 # ⭕ 可选
```

---

## 🚀 快速开始

### 新建策略模板

```yaml
strategies:
  - strategy_id: "my_new_strategy"
    strategy_name: "我的新策略"
    enabled: true
    target_token: TOKEN_SYMBOL      # 替换为实际代币符号
    target_chain: BSC              # 或其他链
    target_volume: 10000           # 目标交易量
    user_ids: [1]                  # 参与用户列表
```

### 测试配置

```bash
# 查看策略状态
uv run python scripts/run_trading_strategy.py --status

# 启动策略
uv run python scripts/run_trading_strategy.py --strategy my_new_strategy
```

---

## 📊 简化效果总结

| 项目 | 简化前 | 简化后 | 减少 |
|------|--------|--------|------|
| 总行数 | 109 | 45 | 59% ⬇️ |
| global_settings 参数 | 18 | 8 | 56% ⬇️ |
| 策略重复参数 | 6 | 0 | 100% ⬇️ |
| user_overrides 冗余 | 3 | 0 | 100% ⬇️ |
| 维护复杂度 | 高 | 低 | ⬇️⬇️⬇️ |

---

## ⚠️ 迁移说明

如果之前使用了完整配置，迁移到简化配置：

1. **删除冗余的全局参数**
   - 删除 `default_buy_offset_value`（已有 `default_buy_offset_percentage`）
   - 删除 `order_retry_attempts`（已有 `max_retry_attempts`）
   - 删除 `websocket_reconnect_delay_seconds`（暂不使用）

2. **删除 users 部分**（现在由策略管理）

3. **简化策略配置**
   - 删除与全局默认值相同的参数
   - 只保留必需参数和需要覆盖的参数

4. **清空 user_overrides**（除非真的需要用户级覆盖）

5. **测试配置**
   ```bash
   uv run python scripts/run_trading_strategy.py --status
   ```

