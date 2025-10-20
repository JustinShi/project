# 如何运行交易策略

## 📌 唯一脚本

**`scripts/run_trading_strategy.py`** - 使用配置文件运行策略

---

## 🎯 使用方式

### 1. 运行所有启用的策略（最常用）

```bash
uv run python scripts/run_trading_strategy.py
```

**行为**:
- 读取 `config/trading_config.yaml`
- 运行所有 `enabled: true` 的策略
- 自动跳过 `enabled: false` 的策略

**示例配置**:
```yaml
# config/trading_config.yaml
strategies:
  - strategy_id: "koge_volume_boost"
    enabled: false  # ← 不会运行
    
  - strategy_id: "aop_test"
    enabled: true   # ← 会运行
```

**运行结果**:
- ✅ 只运行 AOP 策略
- ✅ KOGE 策略被跳过

---

### 2. 运行指定策略

```bash
uv run python scripts/run_trading_strategy.py --strategy aop_test
```

**行为**:
- 只运行 `aop_test` 策略
- 使用配置文件中的所有参数

---

### 3. 查看策略状态

```bash
uv run python scripts/run_trading_strategy.py --status
```

**输出示例**:
```
================================================================================
交易策略状态
================================================================================
策略信息:
  strategy_id: koge_volume_boost
  strategy_name: KOGE 刷量策略
  enabled: False
  is_running: False
  target_volume: 16384
  total_volume: 0
  progress: 0.00%
  user_count: 1
--------------------------------------------------------------------------------
策略信息:
  strategy_id: aop_test
  strategy_name: AOP 测试策略
  enabled: True
  is_running: False
  target_volume: 5000
  total_volume: 0
  progress: 0.00%
  user_count: 1
--------------------------------------------------------------------------------
================================================================================
```

---

### 4. 使用自定义配置文件

```bash
uv run python scripts/run_trading_strategy.py --config path/to/custom_config.yaml
```

---

## 📋 配置文件说明

### 配置文件位置

**默认**: `config/trading_config.yaml`

### 配置文件结构

```yaml
# 全局设置（所有策略的默认值）
global_settings:
  default_buy_offset_percentage: 10
  default_sell_profit_percentage: 10
  default_trade_interval_seconds: 1
  default_single_trade_amount_usdt: 200
  max_concurrent_users: 10
  order_timeout_seconds: 300

# 策略配置
strategies:
  - strategy_id: "aop_test"
    strategy_name: "AOP 测试策略"
    enabled: true              # ← 控制是否运行
    target_token: AOP
    target_chain: BSC
    target_volume: 5000        # ← 目标交易量
    user_ids: [1]              # ← 参与用户
    
    # 可选：覆盖全局设置
    # single_trade_amount_usdt: 100
    # trade_interval_seconds: 2

```

---

## 🔧 参数优先级

```
策略配置 > 全局默认
```

### 示例

```yaml
# 全局默认: 200 USDT
global_settings:
  default_single_trade_amount_usdt: 200

# 策略配置: 使用全局默认（未覆盖）
strategies:
  - strategy_id: "aop_test"
    target_token: AOP
    # single_trade_amount_usdt: (未指定，继承全局 200)

# 最终结果: 使用 200 USDT
```

---

## ✅ 常见使用场景

### 场景 1: 运行 AOP 策略，关闭 KOGE

**第一步：配置文件**
```yaml
# config/trading_config.yaml
global_settings:
  default_single_trade_amount_usdt: 200

strategies:
  - strategy_id: "koge_volume_boost"
    enabled: false  # ← 关闭
    
  - strategy_id: "aop_test"
    enabled: true   # ← 启用
    target_token: AOP
    target_volume: 5000
    user_ids: [1]
```

**第二步：运行**
```bash
uv run python scripts/run_trading_strategy.py
```

**结果**:
- ✅ 只运行 AOP 策略
- ✅ KOGE 被跳过
- ✅ 使用 200 USDT 单次交易（全局默认）

---

### 场景 2: 多用户多策略

**配置文件**:
```yaml
strategies:
  - strategy_id: "aop_test"
    enabled: true
    target_token: AOP
    target_volume: 5000
    user_ids: [1, 2]  # ← 两个用户同时交易 AOP
    
  - strategy_id: "koge_volume_boost"
    enabled: true
    target_token: KOGE
    target_volume: 10000
    user_ids: [3]     # ← 用户3 交易 KOGE
```

**运行**:
```bash
uv run python scripts/run_trading_strategy.py
```

**结果**:
- ✅ 用户1、2 同时交易 AOP（目标各 5000 USDT）
- ✅ 用户3 交易 KOGE（目标 10000 USDT）
- ✅ 并行执行，互不影响

---

### 场景 3: 不同用户使用不同金额

**配置文件**:
```yaml
global_settings:
  default_single_trade_amount_usdt: 200

strategies:
  - strategy_id: "aop_test"
    enabled: true
    target_token: AOP
    target_volume: 5000
    user_ids: [1, 2]

```

**运行**:
```bash
uv run python scripts/run_trading_strategy.py
```

**结果**:
- ✅ 用户1：单次 100 USDT
- ✅ 用户2：单次 50 USDT

---

## 🛑 停止策略

### 方法 1: Ctrl+C（优雅停止）

```bash
# 运行中按 Ctrl+C
^C
```

**行为**:
- ✅ 等待当前交易完成
- ✅ 清理 WebSocket 连接
- ✅ 显示最终统计
- ✅ 正常退出

### 方法 2: 修改配置文件

```yaml
strategies:
  - strategy_id: "aop_test"
    enabled: false  # ← 改为 false 并重启
```

---

## 📊 查看执行日志

### 日志文件位置

```
logs/app.log
```

### 查看最新日志

```bash
# Windows
Get-Content logs\app.log -Tail 50

# Linux/Mac
tail -f logs/app.log
```

---

## ⚠️ 注意事项

### 1. 配置文件语法

- 使用 YAML 格式
- 注意缩进（使用空格，不要用 Tab）
- 注释使用 `#`

### 2. enabled 字段

```yaml
enabled: true   # ← 运行
enabled: false  # ← 跳过
```

- 只有 `enabled: true` 的策略会运行
- `enabled: false` 的策略会被跳过

### 3. user_ids 列表

```yaml
user_ids: [1]        # ← 单个用户
user_ids: [1, 2, 3]  # ← 多个用户
```

- 必须是列表格式
- 用户ID必须在数据库中存在

---

## 🔍 故障排查

### 问题 1: 策略没有运行

**检查**:
```yaml
strategies:
  - strategy_id: "aop_test"
    enabled: true  # ← 确保是 true
```

### 问题 2: 单次交易金额不对

**检查优先级**:
```
1. strategies 中是否有指定？
2. 使用 global_settings 默认值
```

### 问题 3: 用户凭证无效

**检查数据库**:
- 用户是否存在？
- headers 和 cookies 是否过期？

---

## 📝 快速参考

### 命令速查

```bash
# 运行所有启用的策略
uv run python scripts/run_trading_strategy.py

# 运行指定策略
uv run python scripts/run_trading_strategy.py --strategy aop_test

# 查看状态
uv run python scripts/run_trading_strategy.py --status

# 使用自定义配置
uv run python scripts/run_trading_strategy.py --config my_config.yaml

# 查看帮助
uv run python scripts/run_trading_strategy.py --help
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--config` | 配置文件路径 | `config/trading_config.yaml` |
| `--strategy` | 运行指定策略ID | 运行所有启用的策略 |
| `--status` | 显示策略状态 | - |

---

## 🎉 总结

### 唯一需要记住的命令

```bash
uv run python scripts/run_trading_strategy.py
```

### 所有配置都在这里

```
config/trading_config.yaml
```

### 三个简单步骤

1. **编辑配置文件** - 设置策略参数
2. **运行脚本** - 执行策略
3. **Ctrl+C 停止** - 优雅退出

就这么简单！🚀

