# MulPoint（交易量倍数）处理说明

## 概述

币安 Alpha 平台对某些代币采用了**交易量放大显示**机制，通过 `mulPoint` 字段标识放大倍数。

## 问题说明

### 示例：AOP 代币

- **mulPoint**: 4
- **显示交易量**: 40,000 USDT
- **真实交易量**: 10,000 USDT（40,000 ÷ 4）

### 为什么需要处理？

我们的交易策略配置中的**目标交易量是对标真实交易量**的，因此需要：

1. 获取代币的 `mulPoint` 值
2. 将每次交易的名义金额除以 `mulPoint` 得到真实交易量
3. 累计真实交易量与目标交易量比较

## 代币信息示例

```json
{
  "AOP": {
    "data": {
      "symbol": "AOP",
      "price": "0.08158153381312587918",
      "volume24h": "7409062153.078521775670234390659",  // 这是放大后的交易量
      "mulPoint": 4,  // 表示交易量放大了4倍
      ...
    }
  }
}
```

## 实现逻辑

### 1. 获取 mulPoint

**方法**: `_get_mul_point()`

```python
async def _get_mul_point(
    self, 
    token_list: List[Dict[str, Any]], 
    symbol_short: str
) -> int:
    """获取代币的交易量倍数"""
    for entry in token_list:
        if str(entry.get("symbol", "")).upper() == symbol_short.upper():
            mul_point = entry.get("mulPoint", 1)
            return int(mul_point) if mul_point else 1
    
    # 未找到，默认返回 1（不放大）
    return 1
```

### 2. 计算真实交易量

**在 OTO 订单完全成交后**:

```python
# 名义交易金额（下单金额）
effective_amount = quantity * buy_price  # 例如: 10 USDT

# 真实交易量（考虑 mulPoint）
real_trade_volume = effective_amount / Decimal(str(mul_point))
# mulPoint=4: real_trade_volume = 10 / 4 = 2.5 USDT

return True, real_trade_volume
```

### 3. 交易量累计

```python
if success:
    # 累计的是真实交易量，不是名义金额
    self._user_volumes[user_id][strategy_id] += trade_volume
```

## 配置示例

### 对于 AOP（mulPoint=4）

```yaml
strategies:
  - strategy_id: "aop_volume_boost"
    target_token: AOP
    target_chain: BSC
    target_volume: 10000  # 目标真实交易量 10,000 USDT
    single_trade_amount_usdt: 40  # 单次下单 40 USDT
```

**执行情况**:
- 每次下单：40 USDT（名义金额）
- 计入交易量：10 USDT（40 ÷ 4）
- 需要交易次数：1000 次（10,000 ÷ 10）
- 总下单金额：40,000 USDT（40 × 1000）

### 对于 KOGE（mulPoint=1，默认）

```yaml
strategies:
  - strategy_id: "koge_volume_boost"
    target_token: KOGE
    target_chain: BSC
    target_volume: 10000  # 目标交易量 10,000 USDT
    single_trade_amount_usdt: 40  # 单次下单 40 USDT
```

**执行情况**:
- 每次下单：40 USDT
- 计入交易量：40 USDT（40 ÷ 1）
- 需要交易次数：250 次（10,000 ÷ 40）
- 总下单金额：10,000 USDT（40 × 250）

## MulPoint 值说明

根据 `data/cache/token_info.json`:

| mulPoint | 说明 | 示例代币 |
|----------|------|---------|
| 1 | 不放大（默认） | KOGE, 大部分代币 |
| 2 | 2倍放大 | 某些代币 |
| 4 | 4倍放大 | AOP |

## 日志输出

### 启用 mulPoint 处理后

```
2025-10-10 17:00:00 | INFO | 代币交易量倍数, token=AOP, mul_point=4
2025-10-10 17:00:05 | INFO | OTO订单完全成交, 
    working_order_id=123456, 
    pending_order_id=123457, 
    amount=40.0,  // 名义金额
    mul_point=4, 
    real_trade_volume=10.0  // 真实交易量
2025-10-10 17:00:05 | INFO | 交易成功, 
    trade_volume=10.0,  // 计入的真实交易量
    current_volume=10.0, 
    progress=0.10%  // 10.0 / 10000 * 100
```

## 注意事项

### 1. 目标交易量的含义

配置文件中的 `target_volume` 是**真实交易量目标**，不需要考虑 mulPoint。

### 2. 单次交易金额

`single_trade_amount_usdt` 是**每次下单的金额**（名义金额），系统会自动除以 mulPoint 计算真实交易量。

### 3. 进度计算

```python
progress = current_volume / target_volume * 100
# current_volume 是累计的真实交易量
# target_volume 是配置的目标真实交易量
```

### 4. 兼容性

- 如果代币没有 `mulPoint` 字段，默认使用 1（不放大）
- 向后兼容，不会影响已有的交易策略

## 测试验证

### 测试 AOP（mulPoint=4）

```bash
uv run python scripts/quick_start_strategy.py \
  --token AOP \
  --chain BSC \
  --volume 100 \  # 目标真实交易量 100 USDT
  --amount 40 \   # 单次下单 40 USDT
  --user 1 \
  --interval 3

# 预期:
# - 下单3次（40 × 3 = 120 USDT 名义金额）
# - 真实交易量: 30 USDT（120 ÷ 4）
# - 或者下单4次完成 100 USDT 真实交易量
```

### 测试 KOGE（mulPoint=1）

```bash
uv run python scripts/quick_start_strategy.py \
  --token KOGE \
  --chain BSC \
  --volume 100 \  # 目标交易量 100 USDT
  --amount 40 \   # 单次下单 40 USDT
  --user 1 \
  --interval 3

# 预期:
# - 下单3次（40 × 3 = 120 USDT）
# - 真实交易量: 120 USDT（120 ÷ 1）
```

## 修改文件

- **`src/binance/application/services/strategy_executor.py`**
  - 新增 `_get_mul_point()` 方法
  - 修改 `_execute_single_trade()` 返回真实交易量

## 版本历史

- **v2.1.0** (2025-10-10)
  - ✅ 支持 mulPoint 交易量倍数处理
  - ✅ 真实交易量计算
  - ✅ 日志输出优化

## 相关文档

- [交易策略优化总结](./strategy_optimization_summary.md)
- [交易策略配置指南](./trading_strategy_guide.md)

