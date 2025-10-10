# 批次执行逻辑说明

## 概述

优化后的交易策略执行逻辑采用**批次循环**方式，先查询用户当前交易量，计算剩余交易量和所需循环次数，执行完一批后重新查询，确保达标为止。

---

## 新执行流程

### 1. 整体流程图

```
启动策略
    ↓
并行检查所有用户交易量
    ↓
筛选未达标用户
    ↓
【每个未达标用户独立执行】
    ↓
    ┌─────────────────────────────────────┐
    │  1. 查询当前交易量                    │
    │     GET /user-volume                 │
    │     找到目标代币的 volume             │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │  2. 检查是否达标                      │
    │     current >= target ?              │
    └──────┬──────────────────┬───────────┘
      达标  │                  │ 未达标
       ↓   │                  ↓
   【完成】 │     ┌─────────────────────────┐
           │     │  3. 计算剩余交易量和循环次数│
           │     │     remaining = target - current│
           │     │     loops = ceil(remaining / single_real_volume)│
           │     │     single_real_volume = amount / mulPoint│
           │     └──────────┬──────────────┘
           │                ↓
           │     ┌─────────────────────────┐
           │     │  4. 建立 WebSocket 连接  │
           │     │     获取 ListenKey       │
           │     │     订阅订单推送          │
           │     └──────────┬──────────────┘
           │                ↓
           │     ┌─────────────────────────┐
           │     │  5. 执行 N 次批次交易     │
           │     │     for i in range(loops):│
           │     │       - 下 OTO 订单      │
           │     │       - 等待买单成交      │
           │     │       - 等待卖单成交      │
           │     │       - 等待交易间隔      │
           │     └──────────┬──────────────┘
           │                ↓
           │     ┌─────────────────────────┐
           │     │  6. 批次完成，重新查询    │
           │     │     回到步骤 1            │
           │     └──────────┬──────────────┘
           │                ↓
           └────────────【循环直至达标】
```

---

## 关键改进

### 改进 1: 先并行检查所有用户

**旧逻辑**：
```python
# 直接启动所有用户策略，内部自己统计交易量
for user_id in strategy.user_ids:
    asyncio.create_task(_run_user_strategy(user_id, strategy))
```

**新逻辑**：
```python
# 先查询所有用户的当前交易量
tasks = []
for user_id in strategy.user_ids:
    tasks.append(_query_user_current_volume(user_id, token, headers, cookies))

volumes = await asyncio.gather(*tasks)

# 筛选未达标用户
for user_id, volume in zip(user_ids, volumes):
    if volume < target_volume:
        # 只对未达标用户执行策略
        asyncio.create_task(_run_user_strategy(user_id, strategy))
```

**优点**：
- ✅ 避免已达标用户重复交易
- ✅ 提高执行效率

---

### 改进 2: 根据剩余交易量计算循环次数

**示例计算**（AOP, mulPoint=4）:

```python
# 当前状态
target_volume = 10000  # 目标 10,000 USDT
current_volume = 8500  # 已完成 8,500 USDT
remaining_volume = 10000 - 8500 = 1500  # 剩余 1,500 USDT

# 代币信息
mulPoint = 4  # AOP 是 4 倍交易量代币

# 单次交易真实交易量
single_trade_amount = 30  # 单次下单 30 USDT
single_real_volume = 30 / 4 = 7.5  # 真实计入 7.5 USDT

# 计算循环次数
loop_count = ceil(1500 / 7.5) = ceil(200) = 200 次

# 预计完成总交易量
expected = 8500 + (200 × 7.5) = 8500 + 1500 = 10000 ✅
```

---

### 改进 3: 批次完成后重新查询

**原因**：
- 币安 API 返回的交易量可能有延迟
- 其他系统/手动交易可能也会计入交易量
- 网络波动可能导致部分订单未成交

**新逻辑**：
```python
while True:
    # 查询最新交易量
    current_volume = await query_user_current_volume()
    
    if current_volume >= target_volume:
        break  # 达标，退出
    
    # 计算剩余并执行
    remaining = target_volume - current_volume
    loops = calculate_loop_count(remaining)
    
    await execute_batch_trades(loops)
    
    # 重新查询（回到循环开头）
```

**优点**：
- ✅ 确保不遗漏任何交易量
- ✅ 避免过度交易
- ✅ 适应币安 API 延迟

---

## 核心方法说明

### 方法 1: `_query_user_current_volume()`

**功能**: 查询用户当前代币交易量

```python
async def _query_user_current_volume(
    user_id: int,
    token_symbol: str,
    headers: Dict[str, str],
    cookies: str,
) -> Decimal:
    # 调用币安 API
    volume_data = await client.get_user_volume()
    
    # 从 tradeVolumeInfoList 中查找目标代币
    for token_vol in volume_data["tradeVolumeInfoList"]:
        if token_vol["tokenName"] == token_symbol:
            return Decimal(token_vol["volume"])
    
    # 未找到，返回 0
    return Decimal("0")
```

**API 响应示例**:
```json
{
  "totalVolume": 8532.45,
  "tradeVolumeInfoList": [
    {
      "tokenName": "AOP",
      "volume": 8500.00
    },
    {
      "tokenName": "KOGE",
      "volume": 32.45
    }
  ]
}
```

**返回**:
- `8500.00`（找到 AOP）
- `0`（未找到指定代币）

---

### 方法 2: `_calculate_loop_count()`

**功能**: 计算所需循环次数

```python
async def _calculate_loop_count(
    user_id: int,
    strategy: StrategyConfig,
    remaining_volume: Decimal,
    headers: Dict[str, str],
    cookies: str,
) -> int:
    # 获取 mulPoint
    token_info = await client.get_token_info()
    mul_point = await self._get_mul_point(token_info, strategy.target_token)
    
    # 单次交易真实交易量
    single_real_volume = strategy.single_trade_amount_usdt / Decimal(str(mul_point))
    
    # 计算循环次数（向上取整）
    loop_count = math.ceil(float(remaining_volume / single_real_volume))
    
    return max(1, loop_count)  # 至少 1 次
```

**计算示例**:

| 代币 | mulPoint | 剩余量 | 单次金额 | 真实单次 | 循环次数 |
|------|----------|--------|---------|---------|---------|
| KOGE | 1 | 1000 | 30 | 30 | 34 |
| AOP | 4 | 1000 | 30 | 7.5 | 134 |

---

### 方法 3: `_execute_batch_trades()`

**功能**: 执行批次交易

```python
async def _execute_batch_trades(
    user_id: int,
    strategy: StrategyConfig,
    loop_count: int,
    headers: Dict[str, str],
    cookies: str,
) -> None:
    for i in range(loop_count):
        # 检查停止标志
        if self._stop_flags.get(strategy.strategy_id):
            break
        
        # 执行一次交易
        success, trade_volume = await self._execute_single_trade(...)
        
        if success:
            logger.info(f"批次交易成功 {i+1}/{loop_count}")
        else:
            logger.warning(f"批次交易失败 {i+1}/{loop_count}")
            # 等待重试
        
        # 等待交易间隔
        await interruptible_sleep(strategy.trade_interval_seconds)
```

---

## 完整执行示例

### 场景

- **用户**: user_id=1
- **代币**: AOP (mulPoint=4)
- **目标交易量**: 10,000 USDT
- **单次金额**: 30 USDT
- **当前已完成**: 8,500 USDT

### 执行过程

```
时间 00:00 - 启动策略
    策略ID: aop_volume_boost
    目标交易量: 10,000 USDT

时间 00:01 - 并行查询所有用户交易量
    用户1: 8,500 USDT (未达标)
    用户2: 10,200 USDT (已达标) ❌ 跳过

时间 00:02 - 筛选未达标用户
    需要执行: [用户1]

时间 00:03 - 用户1：查询当前交易量
    当前: 8,500 USDT
    目标: 10,000 USDT
    剩余: 1,500 USDT

时间 00:04 - 用户1：计算循环次数
    mulPoint: 4
    单次真实交易量: 30 / 4 = 7.5 USDT
    循环次数: ceil(1500 / 7.5) = 200 次

时间 00:05 - 用户1：建立 WebSocket 连接
    ListenKey: pqia91ma19a5s61cv6a81va65sdf19v7
    连接状态: ✅ 已连接

时间 00:06 - 用户1：开始批次交易 (1/200)
    下单: 30 USDT
    买单成交: ✅
    卖单成交: ✅
    真实交易量: 7.5 USDT

时间 00:10 - 用户1：批次交易 (2/200)
    ...

时间 08:30 - 用户1：批次交易 (200/200)
    下单: 30 USDT
    买单成交: ✅
    卖单成交: ✅
    真实交易量: 7.5 USDT

时间 08:31 - 用户1：批次完成，重新查询
    当前交易量: 9,950 USDT（有10次订单未成交）
    剩余: 50 USDT

时间 08:32 - 用户1：计算新循环次数
    循环次数: ceil(50 / 7.5) = 7 次

时间 08:33 - 用户1：开始新批次交易 (1/7)
    ...

时间 08:40 - 用户1：批次交易 (7/7)
    下单: 30 USDT
    买单成交: ✅
    卖单成交: ✅

时间 08:41 - 用户1：批次完成，重新查询
    当前交易量: 10,002.5 USDT ✅ 达标

时间 08:42 - 用户1：策略完成
    清理 WebSocket 连接
    最终交易量: 10,002.5 USDT
```

---

## 日志输出示例

```
2025-10-10 00:00:00 | INFO | 策略开始执行, strategy_id=aop_volume_boost

# 并行查询
2025-10-10 00:01:00 | INFO | 查询到用户代币交易量, user_id=1, token=AOP, volume=8500.00
2025-10-10 00:01:00 | INFO | 查询到用户代币交易量, user_id=2, token=AOP, volume=10200.00

# 筛选未达标用户
2025-10-10 00:02:00 | INFO | 用户策略开始, user_id=1, target_volume=10000, current_volume=8500

# 计算循环次数
2025-10-10 00:04:00 | INFO | 计算循环次数, 
    user_id=1, 
    remaining_volume=1500.00, 
    single_trade_amount=30, 
    mul_point=4, 
    single_real_volume=7.5, 
    loop_count=200

# 批次交易
2025-10-10 00:05:00 | INFO | 开始批次交易, 
    user_id=1, 
    current_volume=8500.00, 
    remaining_volume=1500.00, 
    planned_loops=200

2025-10-10 00:06:00 | INFO | 执行批次交易, user_id=1, current_loop=1, total_loops=200
2025-10-10 00:06:05 | INFO | 批次交易成功, user_id=1, loop=1/200, trade_volume=7.5

...

2025-10-10 08:30:00 | INFO | 执行批次交易, user_id=1, current_loop=200, total_loops=200
2025-10-10 08:30:05 | INFO | 批次交易成功, user_id=1, loop=200/200, trade_volume=7.5

# 批次完成，重新查询
2025-10-10 08:31:00 | INFO | 批次交易完成，重新查询交易量, user_id=1
2025-10-10 08:31:01 | INFO | 查询到用户代币交易量, user_id=1, token=AOP, volume=9950.00

# 计算新循环次数
2025-10-10 08:32:00 | INFO | 计算循环次数, 
    user_id=1, 
    remaining_volume=50.00, 
    loop_count=7

...

# 达标
2025-10-10 08:41:01 | INFO | 查询到用户代币交易量, user_id=1, token=AOP, volume=10002.5
2025-10-10 08:41:02 | INFO | 用户已达成目标交易量, 
    user_id=1, 
    current_volume=10002.5, 
    target_volume=10000

2025-10-10 08:42:00 | INFO | 用户策略完成, user_id=1
```

---

## 优势对比

### 旧逻辑 vs 新逻辑

| 特性 | 旧逻辑 | 新逻辑 |
|------|--------|--------|
| **交易量查询** | 程序内部统计 | 查询币安 API（真实） |
| **达标检测** | 程序统计可能不准 | API 查询，绝对准确 |
| **已达标用户** | 继续执行浪费资源 | 跳过，不执行 |
| **循环次数** | 逐笔执行，不可预测 | 预先计算，可预测 |
| **容错性** | 订单失败不重查 | 批次后重查，自动补足 |
| **执行效率** | 低（逐笔） | 高（批次） |
| **API 延迟处理** | 无 | 有（重查机制） |

---

## 配置示例

### 多用户策略

```yaml
strategies:
  - strategy_id: "aop_volume_boost"
    target_token: AOP
    target_chain: BSC
    target_volume: 10000  # 目标真实交易量
    
    user_ids:
      - 1  # 用户1：当前8500，需补1500
      - 2  # 用户2：当前10200，已达标 ✅ 跳过
      - 3  # 用户3：当前0，需补10000
    
    single_trade_amount_usdt: 30
    trade_interval_seconds: 1
```

**执行情况**:
- **用户1**: 计算 200 次循环 → 执行 → 重查 → 补7次 → 达标
- **用户2**: 跳过（已达标）
- **用户3**: 计算 1334 次循环 → 执行 → 重查 → 继续

---

## 注意事项

### 1. mulPoint 处理

确保 `_get_mul_point()` 正确获取代币的交易量倍数：

```python
mul_point = await self._get_mul_point(token_info, "AOP")
# 返回: 4 (对于 AOP)
# 返回: 1 (对于 KOGE)
```

### 2. API 调用频率

- 批次开始前查询 1 次
- 批次结束后查询 1 次
- 不会频繁调用 API

### 3. WebSocket 连接复用

- 每个用户只建立 1 个 WebSocket 连接
- 在整个策略执行期间保持连接
- 策略完成后才清理连接

---

## 相关文档

- [MulPoint 处理说明](./mulpoint_handling.md)
- [策略执行流程](./strategy_execution_flow.md)
- [订单 WebSocket 测试指南](./order_websocket_test_guide.md)

---

## 版本

- **v2.2.0** (2025-10-10)
  - ✅ 批次循环执行逻辑
  - ✅ 先查询再计算循环次数
  - ✅ 批次后重新查询确保达标
  - ✅ 筛选未达标用户执行

