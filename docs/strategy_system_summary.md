# 交易策略系统总结

## 🎯 系统概述

已成功创建一个**多用户并发 OTO 订单交易策略系统**，支持灵活的配置管理和用户自定义功能。

## 📁 创建的文件

### 1. 配置文件
- `config/trading_config.yaml` - 统一配置文件（包含策略、用户、全局设置）

### 2. 核心模块
- `src/binance/infrastructure/config/strategy_config_manager.py` - 策略配置管理器
- `src/binance/application/services/strategy_executor.py` - 策略执行器

### 3. 脚本
- `scripts/run_trading_strategy.py` - 策略运行脚本
- `scripts/quick_start_strategy.py` - 快速启动脚本

### 4. 文档
- `docs/trading_strategy_guide.md` - 使用指南
- `docs/strategy_system_summary.md` - 本文档

## ✨ 核心功能

### 1. 多策略支持
```yaml
strategies:
  - strategy_id: "koge_volume_boost"
    # KOGE 刷量策略
  - strategy_id: "aop_test"  
    # AOP 测试策略
```

### 2. 多用户并发
```yaml
strategies:
  - strategy_id: "koge_volume_boost"
    user_ids: [1, 2, 3]  # 3 个用户同时执行
```

### 3. 用户自定义配置（优先级最高）
```yaml
user_overrides:
  - user_id: 1
    strategies:
      koge_volume_boost:
        single_trade_amount_usdt: 50  # 用户 1 覆盖为 50 USDT
```

### 4. 配置层级
```
全局设置 (global_settings)
  ↓ 应用到
策略配置 (strategies)
  ↓ 被覆盖
用户覆盖 (user_overrides) ← 优先级最高
```

## 🚀 使用方法

### 方法 1: 使用配置文件运行

1. **编辑配置文件** `config/trading_config.yaml`:
```yaml
strategies:
  - strategy_id: "koge_volume_boost"
    strategy_name: "KOGE 刷量策略"
    enabled: true
    target_token: KOGE
    target_chain: BSC
    target_volume: 16384          # 目标交易量
    single_trade_amount_usdt: 30  # 单次金额
    trade_interval_seconds: 1     # 间隔 1 秒
    user_ids: [1]                 # 用户 ID
```

2. **运行策略**:
```bash
# 运行所有启用的策略
uv run python scripts/run_trading_strategy.py

# 运行指定策略
uv run python scripts/run_trading_strategy.py --strategy koge_volume_boost

# 查看状态
uv run python scripts/run_trading_strategy.py --status
```

### 方法 2: 快速启动（测试用）

```bash
# 快速测试：KOGE 代币，目标 100 USDT，每次 10 USDT
uv run python scripts/quick_start_strategy.py \
  --token KOGE \
  --chain BSC \
  --volume 100 \
  --amount 10 \
  --user 1 \
  --interval 1
```

## 📊 示例配置

### 示例 1: KOGE 单用户刷量
```yaml
strategies:
  - strategy_id: "koge_volume_boost"
    enabled: true
    target_token: KOGE
    target_chain: BSC
    target_volume: 16384
    single_trade_amount_usdt: 30
    trade_interval_seconds: 1
    buy_offset_percentage: 0.5
    sell_profit_percentage: 1.0
    user_ids: [1]
```

**执行效果**:
- 用户 1 每秒执行一次交易
- 每次交易 30 USDT
- 总交易量达到 16384 USDT 后停止
- 预计用时: 16384 / 30 ≈ 546 秒 ≈ 9 分钟

### 示例 2: KOGE 多用户并发
```yaml
strategies:
  - strategy_id: "koge_volume_boost"
    target_volume: 16384
    single_trade_amount_usdt: 30
    trade_interval_seconds: 1
    user_ids: [1, 2, 3]  # 3 个用户

user_overrides:
  - user_id: 1
    strategies:
      koge_volume_boost:
        single_trade_amount_usdt: 50  # 用户 1: 50 USDT
  - user_id: 2
    strategies:
      koge_volume_boost:
        single_trade_amount_usdt: 30  # 用户 2: 30 USDT  
  - user_id: 3
    strategies:
      koge_volume_boost:
        single_trade_amount_usdt: 20  # 用户 3: 20 USDT
```

**执行效果**:
- 3 个用户同时执行
- 每秒总交易: 50 + 30 + 20 = 100 USDT
- 预计用时: 16384 / 100 ≈ 164 秒 ≈ 2.7 分钟

## 🔧 配置参数说明

### 全局设置参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `default_buy_offset_percentage` | 买入溢价百分比 | 0.5 |
| `default_sell_profit_percentage` | 卖出利润百分比 | 1.0 |
| `default_trade_interval_seconds` | 交易间隔（秒） | 1 |
| `default_single_trade_amount_usdt` | 单次交易金额 | 30 |
| `max_concurrent_users` | 最大并发用户数 | 10 |
| `max_price_volatility_percentage` | 最大价格波动 | 5.0 |

### 策略参数
| 参数 | 说明 | 必填 |
|------|------|------|
| `strategy_id` | 策略唯一标识 | ✅ |
| `strategy_name` | 策略名称 | ✅ |
| `enabled` | 是否启用 | ✅ |
| `target_token` | 目标代币符号 | ✅ |
| `target_chain` | 目标链 | ✅ |
| `target_volume` | 目标交易量 | ✅ |
| `single_trade_amount_usdt` | 单次交易金额 | ✅ |
| `trade_interval_seconds` | 交易间隔 | ✅ |
| `buy_offset_percentage` | 买入溢价 | ✅ |
| `sell_profit_percentage` | 卖出利润 | ✅ |
| `user_ids` | 参与用户列表 | ✅ |

## 📈 价格计算逻辑

```python
当前价格 = 从 Binance API 实时获取

买入价格 = 当前价格 × (1 + buy_offset_percentage / 100)
卖出价格 = 买入价格 × (1 + sell_profit_percentage / 100)

# 示例计算（buy_offset=0.5%, sell_profit=1.0%）
当前价: 100 USDT
买入价: 100 × 1.005 = 100.5 USDT
卖出价: 100.5 × 1.01 = 101.505 USDT
利润: 1.505 USDT (1.5%)
```

## 🔄 执行流程

```
1. 加载配置
   ├─ 全局设置
   ├─ 策略配置
   └─ 用户覆盖

2. 启动策略
   ├─ 为每个用户创建并发任务
   └─ 并行执行

3. 用户任务循环
   ├─ 检查目标交易量
   ├─ 获取实时价格
   ├─ 计算买卖价格
   ├─ 下 OTO 订单
   ├─ 更新交易量统计
   ├─ 等待交易间隔
   └─ 重复直到达成目标

4. 完成或停止
   └─ 输出最终统计
```

## 🎛️ 实时监控

### 查看状态
```bash
uv run python scripts/run_trading_strategy.py --status
```

### 输出示例
```json
{
  "strategy_id": "koge_volume_boost",
  "strategy_name": "KOGE 刷量策略",
  "is_running": true,
  "target_volume": "16384",
  "total_volume": "1234.56",
  "progress": "7.53%",
  "user_volumes": {
    "1": "456.78",
    "2": "389.12",
    "3": "388.66"
  }
}
```

## ⚙️ 高级功能

### 1. 动态配置重载
```python
executor = StrategyExecutor("config/trading_strategy.yaml")
executor.config_manager.reload()  # 重新加载配置
```

### 2. 单独控制策略
```python
# 启动单个策略
await executor.start_strategy("koge_volume_boost")

# 停止单个策略
await executor.stop_strategy("koge_volume_boost")
```

### 3. 获取实时状态
```python
status = executor.get_strategy_status("koge_volume_boost")
all_status = executor.get_all_strategy_status()
```

## ⚠️ 注意事项

1. **用户凭证** - 确保用户在数据库中有有效凭证
2. **余额充足** - 用户钱包需有足够 USDT
3. **交易间隔** - 建议最少 1 秒，避免触发限流
4. **目标交易量** - 是所有用户的总和
5. **优雅停止** - 使用 Ctrl+C 可安全停止

## 🔍 故障排查

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| 策略不执行 | `enabled: false` | 设置为 `true` |
| 交易失败 | 凭证过期 | 更新数据库凭证 |
| 价格异常 | 代币符号错误 | 检查 `target_token` |
| 进度不更新 | 网络问题 | 检查网络连接 |

## 📚 相关文档

- [使用指南](./trading_strategy_guide.md)
- [API 文档](./binance/api.md)
- [统一配置文件](../config/trading_config.yaml)

## 🎉 完成清单

- ✅ 创建策略配置管理器
- ✅ 实现多用户并发执行
- ✅ 支持用户自定义配置
- ✅ 实现配置优先级系统
- ✅ 创建策略执行器
- ✅ 实现实时状态监控
- ✅ 创建命令行工具
- ✅ 编写完整文档

---

**系统已就绪，可以开始执行交易策略！** 🚀


