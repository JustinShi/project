# 统一交易脚本使用指南

## 📌 现在只有一个脚本

**`scripts/run_trading_strategy.py`** - 统一的交易策略执行脚本

支持两种模式：
1. **配置文件模式** - 读取 `config/trading_config.yaml`
2. **快速测试模式** - 使用命令行参数

---

## 🎯 使用方式

### 模式 1: 配置文件模式（推荐）

#### 1.1 运行所有启用的策略
```bash
uv run python scripts/run_trading_strategy.py
```

**行为**:
- 读取 `config/trading_config.yaml`
- 只运行 `enabled: true` 的策略
- 自动跳过 `enabled: false` 的策略

**示例**:
```yaml
# config/trading_config.yaml
strategies:
  - strategy_id: "koge_volume_boost"
    enabled: false  # ← 会被跳过
    
  - strategy_id: "aop_test"
    enabled: true   # ← 会执行
```

---

#### 1.2 运行指定策略
```bash
uv run python scripts/run_trading_strategy.py --strategy aop_test
```

**行为**:
- 只运行 `aop_test` 策略
- 使用配置文件中的所有参数

---

#### 1.3 查看策略状态
```bash
uv run python scripts/run_trading_strategy.py --status
```

**输出示例**:
```
策略信息:
  strategy_id: aop_test
  strategy_name: AOP 测试策略
  enabled: True
  is_running: False
  target_volume: 5000
  total_volume: 0
  progress: 0.00%
  user_count: 1
```

---

### 模式 2: 快速测试模式

用于临时测试，**不使用配置文件**。

#### 2.1 基本用法
```bash
uv run python scripts/run_trading_strategy.py \
  --token AOP \
  --chain BSC \
  --volume 200 \
  --amount 40 \
  --user 1
```

**参数说明**:
- `--token AOP` - 代币符号
- `--chain BSC` - 链名称（默认 BSC）
- `--volume 200` - 目标交易量 200 USDT
- `--amount 40` - 单次交易 40 USDT
- `--user 1` - 用户 ID

---

#### 2.2 完整参数
```bash
uv run python scripts/run_trading_strategy.py \
  --token KOGE \
  --chain BSC \
  --volume 1000 \
  --amount 50 \
  --user 1 \
  --interval 2 \
  --buy-offset 5.0 \
  --sell-profit 5.0
```

**可选参数**:
- `--interval 2` - 交易间隔 2 秒（默认 1）
- `--buy-offset 5.0` - 买入溢价 5%（默认 10.0）
- `--sell-profit 5.0` - 卖出折扣 5%（默认 10.0）

---

## 📊 模式对比

| 特性 | 配置文件模式 | 快速测试模式 |
|------|------------|------------|
| **配置来源** | `config/trading_config.yaml` | 命令行参数 |
| **遵守 enabled** | ✅ 是 | ❌ 否 |
| **适用场景** | 正式运行 | 临时测试 |
| **参数管理** | 集中管理 | 命令行指定 |
| **多策略** | ✅ 支持 | ❌ 单策略 |

---

## ✅ 常见使用场景

### 场景 1: 正式运行 AOP 策略

**第一步：配置文件**
```yaml
# config/trading_config.yaml
global_settings:
  default_single_trade_amount_usdt: 200

strategies:
  - strategy_id: "aop_test"
    enabled: true
    target_token: AOP
    target_chain: BSC
    target_volume: 5000
    user_ids: [1]
    # 其他参数使用全局默认值
```

**第二步：运行**
```bash
uv run python scripts/run_trading_strategy.py
```

**效果**:
- ✅ 使用 200 USDT 单次交易（全局默认）
- ✅ 目标交易量 5000 USDT
- ✅ 只运行 AOP（其他策略被跳过）

---

### 场景 2: 快速测试 KOGE

**直接运行**（不需要配置文件）:
```bash
uv run python scripts/run_trading_strategy.py \
  --token KOGE \
  --volume 100 \
  --amount 20 \
  --user 1
```

**效果**:
- ✅ 临时测试 KOGE
- ✅ 单次 20 USDT
- ✅ 目标 100 USDT
- ✅ 不影响配置文件

---

### 场景 3: 多策略并行

**配置文件**:
```yaml
strategies:
  - strategy_id: "aop_test"
    enabled: true
    target_token: AOP
    target_volume: 5000
    user_ids: [1, 2]  # 两个用户
    
  - strategy_id: "koge_volume_boost"
    enabled: true
    target_token: KOGE
    target_volume: 10000
    user_ids: [3]     # 另一个用户
```

**运行**:
```bash
uv run python scripts/run_trading_strategy.py
```

**效果**:
- ✅ AOP 和 KOGE 同时运行
- ✅ 3 个用户并行执行
- ✅ 各自独立的交易量目标

---

## 🔧 参数详解

### 配置文件模式参数

```bash
--config PATH         # 配置文件路径（默认: config/trading_config.yaml）
--strategy ID         # 运行指定策略ID
--status              # 查看策略状态
```

### 快速测试模式参数

**必需参数**:
```bash
--token SYMBOL        # 代币符号（如 AOP, KOGE）
--volume AMOUNT       # 目标交易量（USDT）
--amount AMOUNT       # 单次交易金额（USDT）
--user ID             # 用户 ID
```

**可选参数**:
```bash
--chain NAME          # 链名称（默认: BSC）
--interval SECONDS    # 交易间隔（默认: 1 秒）
--buy-offset PERCENT  # 买入溢价（默认: 10.0%）
--sell-profit PERCENT # 卖出折扣（默认: 10.0%）
```

---

## 📝 示例命令大全

### 1. 使用配置文件
```bash
# 运行所有启用的策略
uv run python scripts/run_trading_strategy.py

# 运行 AOP 策略
uv run python scripts/run_trading_strategy.py --strategy aop_test

# 查看状态
uv run python scripts/run_trading_strategy.py --status
```

### 2. 快速测试
```bash
# 测试 AOP（最小参数）
uv run python scripts/run_trading_strategy.py --token AOP --volume 100 --amount 20 --user 1

# 测试 KOGE（完整参数）
uv run python scripts/run_trading_strategy.py \
  --token KOGE \
  --chain BSC \
  --volume 500 \
  --amount 50 \
  --user 1 \
  --interval 3 \
  --buy-offset 5.0 \
  --sell-profit 5.0
```

---

## ⚠️ 注意事项

### 1. 模式识别

**脚本自动识别模式**:
- 有 `--token` → 快速测试模式
- 无 `--token` → 配置文件模式

### 2. 参数冲突

**不要混用两种模式**:
```bash
# ❌ 错误：混用参数
uv run python scripts/run_trading_strategy.py --strategy aop_test --token KOGE

# ✅ 正确：配置文件模式
uv run python scripts/run_trading_strategy.py --strategy aop_test

# ✅ 正确：快速测试模式
uv run python scripts/run_trading_strategy.py --token KOGE --volume 100 --amount 20 --user 1
```

### 3. 配置文件优先级

配置文件模式的参数优先级：
```
用户覆盖 > 策略配置 > 全局默认
```

---

## 🎉 总结

### 现在只需要记住一个脚本

**`scripts/run_trading_strategy.py`**

### 两种用法

1. **配置文件模式**（正式运行）
   ```bash
   uv run python scripts/run_trading_strategy.py
   ```

2. **快速测试模式**（临时测试）
   ```bash
   uv run python scripts/run_trading_strategy.py --token AOP --volume 100 --amount 20 --user 1
   ```

### 选择建议

- ✅ **正式运行** → 使用配置文件模式
- ✅ **临时测试** → 使用快速测试模式
- ✅ **查看状态** → `--status`

---

## 📄 相关文档

- [批次执行逻辑](./batch_execution_logic.md)
- [MulPoint 处理](./mulpoint_handling.md)
- [交易策略配置指南](./trading_strategy_guide.md)

