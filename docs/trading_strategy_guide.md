# 交易策略系统使用指南

## 📋 概述

交易策略系统支持多用户并发执行 OTO 订单交易，具有灵活的配置管理和用户自定义功能。

## 🎯 核心特性

1. **多策略支持** - 可配置多个不同的交易策略
2. **多用户并发** - 支持多个用户同时执行同一策略
3. **用户自定义配置** - 用户可覆盖策略的任何参数
4. **实时监控** - 查看策略执行状态和进度
5. **灵活控制** - 可启动/停止单个或所有策略

## 📁 配置文件结构

### 配置文件位置
`config/trading_config.yaml` (统一配置文件)

### 配置层级
```
全局设置 (global_settings)
  ↓
策略配置 (strategies)
  ↓
用户覆盖 (user_overrides) ← 优先级最高
```

## 🔧 配置示例

### 1. 全局设置

```yaml
global_settings:
  default_buy_offset_percentage: 0.5      # 默认买入溢价 0.5%
  default_sell_profit_percentage: 1.0     # 默认卖出利润 1.0%
  default_trade_interval_seconds: 1       # 默认交易间隔 1 秒
  default_single_trade_amount_usdt: 30    # 默认单次交易金额 30 USDT
  max_concurrent_users: 10                # 最大并发用户数
  max_price_volatility_percentage: 5.0    # 最大价格波动 5%
```

### 2. 策略配置

```yaml
strategies:
  - strategy_id: "koge_volume_boost"
    strategy_name: "KOGE 刷量策略"
    enabled: true
    
    # 目标配置
    target_token: KOGE                    # 目标代币符号
    target_chain: BSC                     # 目标链
    target_volume: 16384                  # 目标交易量
    
    # 交易参数
    single_trade_amount_usdt: 30          # 单次交易金额
    trade_interval_seconds: 1             # 交易间隔（秒）
    buy_offset_percentage: 0.5            # 买入溢价 0.5%
    sell_profit_percentage: 1.0           # 卖出利润 1.0%
    
    # 用户分配
    user_ids:
      - 1                                 # 参与此策略的用户 ID 列表
      - 2
      - 3
```

### 3. 用户自定义配置

```yaml
user_overrides:
  - user_id: 1
    strategies:
      koge_volume_boost:
        enabled: true
        single_trade_amount_usdt: 50      # 用户 1 使用 50 USDT
        trade_interval_seconds: 2         # 用户 1 每 2 秒交易一次
```

## 💻 使用方法

### 1. 运行所有启用的策略

```bash
uv run python scripts/run_trading_strategy.py
```

### 2. 运行指定策略

```bash
uv run python scripts/run_trading_strategy.py --strategy koge_volume_boost
```

### 3. 查看策略状态

```bash
uv run python scripts/run_trading_strategy.py --status
```

### 4. 使用自定义配置文件

```bash
uv run python scripts/run_trading_strategy.py --config config/my_config.yaml
```

## 📊 策略执行流程

```
1. 加载配置文件
   ↓
2. 为每个启用的策略创建执行任务
   ↓
3. 为策略中的每个用户创建并发交易任务
   ↓
4. 用户任务循环执行：
   - 检查是否达到目标交易量
   - 获取当前价格
   - 计算买入/卖出价格
   - 下 OTO 订单
   - 更新交易量
   - 等待交易间隔
   ↓
5. 达成目标或手动停止
```

## 🎛️ 价格计算逻辑

### 当前实现
```
当前价格 = 从 Binance API 获取
买入价格 = 当前价格 × (1 + buy_offset_percentage / 100)
卖出价格 = 买入价格 × (1 + sell_profit_percentage / 100)

示例（buy_offset=0.5%, sell_profit=1.0%）:
- 当前价: 100 USDT
- 买入价: 100 × 1.005 = 100.5 USDT
- 卖出价: 100.5 × 1.01 = 101.505 USDT
- 利润: 1.505 USDT (1.5%)
```

## 📈 监控和日志

### 日志输出
所有操作都会输出结构化 JSON 日志：

```json
{
  "user_id": 1,
  "strategy_id": "koge_volume_boost",
  "current_volume": "300.5",
  "target_volume": "16384",
  "progress": "1.83%",
  "event": "交易成功",
  "level": "info",
  "timestamp": "2025-10-10T14:30:00.000000Z"
}
```

### 状态查询
```bash
$ uv run python scripts/run_trading_strategy.py --status

策略信息:
  strategy_id: koge_volume_boost
  strategy_name: KOGE 刷量策略
  enabled: true
  is_running: true
  target_volume: 16384
  total_volume: 1234.56
  progress: 7.53%
  user_count: 3
  user_volumes:
    1: "456.78"
    2: "389.12"
    3: "388.66"
```

## ⚠️ 注意事项

1. **认证有效性**
   - 确保用户凭证在数据库中有效
   - 如遇 "补充认证失败"，需重新更新凭证

2. **交易量计算**
   - `target_volume` 是所有参与用户的总目标
   - 系统会自动累计每个用户的交易量

3. **交易间隔**
   - `trade_interval_seconds` 控制单个用户的交易频率
   - 多用户并发时，总交易频率 = 用户数 × (1 / 间隔)

4. **错误处理**
   - 交易失败时会自动重试
   - 价格异常时会记录日志并等待下次尝试

5. **优雅停止**
   - 使用 `Ctrl+C` 可优雅停止所有策略
   - 当前进度会保存在内存中

## 🚀 最佳实践

1. **分阶段测试**
   ```yaml
   # 先用小金额测试
   single_trade_amount_usdt: 1
   target_volume: 10
   ```

2. **合理设置间隔**
   ```yaml
   # 避免触发 API 限流
   trade_interval_seconds: 1  # 最少 1 秒
   ```

3. **使用用户覆盖**
   ```yaml
   # 为不同用户设置不同参数
   user_overrides:
     - user_id: 1
       strategies:
         koge_volume_boost:
           single_trade_amount_usdt: 50  # VIP 用户
     - user_id: 2
       strategies:
         koge_volume_boost:
           single_trade_amount_usdt: 10  # 普通用户
   ```

4. **监控进度**
   ```bash
   # 定期查看状态
   watch -n 5 "uv run python scripts/run_trading_strategy.py --status"
   ```

## 📝 配置模板

### KOGE 刷量策略模板
```yaml
strategies:
  - strategy_id: "koge_volume_boost"
    strategy_name: "KOGE 刷量策略"
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

### 多代币策略模板
```yaml
strategies:
  - strategy_id: "koge_boost"
    target_token: KOGE
    target_chain: BSC
    target_volume: 16384
    user_ids: [1, 2]
    
  - strategy_id: "aop_boost"
    target_token: AOP
    target_chain: BSC
    target_volume: 10000
    user_ids: [3, 4]
```

## 🔍 故障排查

### 问题：策略不执行
**检查**:
1. `enabled: true` 是否设置
2. `user_ids` 是否包含有效用户
3. 用户凭证是否有效

### 问题：交易失败
**检查**:
1. 用户余额是否充足
2. 代币符号是否正确
3. 链配置是否匹配

### 问题：进度不更新
**检查**:
1. 查看日志是否有错误
2. 检查网络连接
3. 验证 API 访问权限

## 📚 相关文档

- [Binance Alpha API 文档](../docs/binance/api.md)
- [统一配置文件](../config/trading_config.yaml)
- [符号映射说明](../src/binance/infrastructure/config/symbol_mapper.py)


