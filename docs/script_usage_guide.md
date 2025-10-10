# 脚本使用指南

## 问题说明

### ❌ 常见误解

**问题**: 修改了 `config/trading_config.yaml`，但配置没有生效

**原因**: 使用了错误的脚本！

---

## 📂 脚本对比

### 脚本 1: `quick_start_strategy.py` ⚠️

**用途**: 快速测试，**不读取配置文件**

**特点**:
- ❌ **忽略** `config/trading_config.yaml`
- ✅ 使用**命令行参数**生成临时配置
- ✅ 适合快速测试

**使用方法**:
```bash
uv run python scripts/quick_start_strategy.py \
  --token AOP \
  --chain BSC \
  --volume 200 \
  --amount 40 \
  --user 1 \
  --interval 3
```

**配置来源**:
```python
# 完全由命令行参数控制
--token AOP      → target_token: AOP
--volume 200     → target_volume: 200
--amount 40      → single_trade_amount_usdt: 40
--interval 3     → trade_interval_seconds: 3
```

**默认值**:
```python
--amount 默认: 10.0 USDT
--interval 默认: 1 秒
--buy-offset 默认: 0.5%
--sell-profit 默认: 1.0%
```

---

### 脚本 2: `run_trading_strategy.py` ✅

**用途**: 生产环境，**读取配置文件**

**特点**:
- ✅ **读取** `config/trading_config.yaml`
- ✅ 遵守 `enabled: true/false`
- ✅ 使用配置文件中的所有参数

**使用方法**:

#### 方式 1: 运行所有启用的策略
```bash
uv run python scripts/run_trading_strategy.py
```

**行为**:
- 读取 `config/trading_config.yaml`
- 只运行 `enabled: true` 的策略
- 跳过 `enabled: false` 的策略

#### 方式 2: 运行指定策略
```bash
uv run python scripts/run_trading_strategy.py --strategy aop_test
```

**行为**:
- 只运行 `aop_test` 策略
- 使用配置文件中的所有参数

#### 方式 3: 查看状态
```bash
uv run python scripts/run_trading_strategy.py --status
```

---

## 🔧 您的问题解答

### 问题 1: KOGE `enabled: false` 仍在交易

**您的配置**:
```yaml
# config/trading_config.yaml
strategies:
  - strategy_id: "koge_volume_boost"
    enabled: false  # ← 已关闭
    target_token: KOGE
```

**您运行的命令**:
```bash
uv run python scripts/quick_start_strategy.py --token KOGE ...
```

**为什么还在交易 KOGE**:
- `quick_start_strategy.py` **不读取配置文件**
- 它根据命令行参数 `--token KOGE` 创建临时策略
- 完全忽略 `config/trading_config.yaml`

**解决方案**:
```bash
# 方式 1: 使用配置文件脚本（推荐）
uv run python scripts/run_trading_strategy.py
# 这会跳过 KOGE（因为 enabled: false）

# 方式 2: 如果要测试，不要指定 KOGE
uv run python scripts/quick_start_strategy.py --token AOP ...
```

---

### 问题 2: AOP 单次交易额是 10 USDT 而不是 200 USDT

**您的配置**:
```yaml
# config/trading_config.yaml
global_settings:
  default_single_trade_amount_usdt: 200  # ← 200 USDT

strategies:
  - strategy_id: "aop_test"
    enabled: true
    target_token: AOP
    target_volume: 5000
    #single_trade_amount_usdt: 10  # ← 注释了
```

**您运行的命令**:
```bash
# 情况 1: 没有指定 --amount
uv run python scripts/quick_start_strategy.py --token AOP --chain BSC --volume 200 --user 1

# 情况 2: 指定了 --amount 40
uv run python scripts/quick_start_strategy.py --token AOP --volume 200 --amount 40 --user 1
```

**为什么是 10 USDT**:
- `quick_start_strategy.py` **不读取配置文件**
- 如果没有 `--amount` 参数，默认值是 **10.0 USDT**（第39行）
- 配置文件中的 200 USDT 被忽略

**解决方案**:

#### 选项 1: 使用配置文件脚本（推荐）
```bash
uv run python scripts/run_trading_strategy.py --strategy aop_test
```

**读取的配置**:
```yaml
target_volume: 5000
single_trade_amount_usdt: 200  # ← 使用全局默认值
```

#### 选项 2: 命令行指定 --amount
```bash
uv run python scripts/quick_start_strategy.py \
  --token AOP \
  --volume 200 \
  --amount 200 \  # ← 明确指定
  --user 1
```

---

## 📊 决策树

```
需要运行策略？
    │
    ├─ 快速测试（不在乎配置文件）
    │   └─> 使用 quick_start_strategy.py
    │       • 所有参数通过命令行传递
    │       • --amount 不指定就是 10 USDT
    │
    └─ 正式执行（使用配置文件）
        └─> 使用 run_trading_strategy.py
            • 读取 config/trading_config.yaml
            • 遵守 enabled: true/false
            • 使用配置文件中的所有参数
```

---

## 🔍 配置文件优先级

### `run_trading_strategy.py`（读取配置文件）

**优先级**:
```
用户覆盖 > 策略配置 > 全局默认
```

**示例**:
```yaml
# 全局默认: 200 USDT
global_settings:
  default_single_trade_amount_usdt: 200

# 策略配置: 未指定，继承全局 200 USDT
strategies:
  - strategy_id: "aop_test"
    target_token: AOP
    # single_trade_amount_usdt: (未指定)

# 用户覆盖: 用户1 使用 50 USDT
user_overrides:
  - user_id: 1
    strategies:
      aop_test:
        single_trade_amount_usdt: 50

# 最终结果: 用户1 使用 50 USDT（用户覆盖）
```

### `quick_start_strategy.py`（忽略配置文件）

**优先级**:
```
命令行参数 > 脚本硬编码默认值
```

**示例**:
```bash
# 硬编码默认值: 10 USDT
# 命令行参数: 40 USDT
uv run python scripts/quick_start_strategy.py --amount 40 ...

# 最终结果: 40 USDT（命令行参数）
```

---

## ✅ 正确使用方式

### 场景 1: 使用配置文件运行 AOP 策略

**配置文件**:
```yaml
# config/trading_config.yaml
global_settings:
  default_single_trade_amount_usdt: 200

strategies:
  - strategy_id: "koge_volume_boost"
    enabled: false  # 关闭 KOGE
    
  - strategy_id: "aop_test"
    enabled: true   # 启用 AOP
    target_volume: 5000
    # 使用全局默认 200 USDT
```

**运行**:
```bash
# 只运行 AOP（KOGE 被跳过）
uv run python scripts/run_trading_strategy.py
```

**效果**:
- ✅ KOGE 不会执行（enabled: false）
- ✅ AOP 使用 200 USDT 单次交易

---

### 场景 2: 快速测试 AOP（不在乎配置文件）

**运行**:
```bash
uv run python scripts/quick_start_strategy.py \
  --token AOP \
  --chain BSC \
  --volume 100 \
  --amount 50 \
  --user 1 \
  --interval 2
```

**效果**:
- ✅ 忽略配置文件
- ✅ 单次交易 50 USDT
- ✅ 交易间隔 2 秒

---

## 📝 总结

| 需求 | 使用脚本 | 配置来源 |
|------|---------|---------|
| **正式运行，使用配置文件** | `run_trading_strategy.py` | `config/trading_config.yaml` |
| **快速测试，命令行配置** | `quick_start_strategy.py` | 命令行参数 |

### 记住

- ⚠️ `quick_start_strategy.py` = 快速测试，**不读配置文件**
- ✅ `run_trading_strategy.py` = 正式运行，**读配置文件**

### 您当前的问题

如果想使用 `config/trading_config.yaml` 中的配置：

```bash
# ❌ 错误（不读配置文件）
uv run python scripts/quick_start_strategy.py --token AOP ...

# ✅ 正确（读配置文件）
uv run python scripts/run_trading_strategy.py
# 或
uv run python scripts/run_trading_strategy.py --strategy aop_test
```

