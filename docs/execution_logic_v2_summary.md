# 交易策略执行逻辑 V2.2 总结

## 🎯 核心改进

### V2.1 → V2.2 重大更新

#### 旧逻辑（V2.1）
```
启动策略
  ↓
为每个用户创建任务
  ↓
【每个用户独立执行】
  ├─ 初始化交易量统计 = 0
  ├─ 建立 WebSocket
  ├─ 循环执行交易
  │   ├─ 下单 → 等待成交
  │   ├─ 累计本地交易量
  │   └─ 检查本地交易量是否达标
  └─ 达标后退出
```

**问题**:
- ❌ 本地统计可能不准确
- ❌ 已达标用户仍会执行
- ❌ 订单失败导致交易量统计错误
- ❌ 无法应对 API 延迟

#### 新逻辑（V2.2）
```
启动策略
  ↓
【并行查询所有用户当前交易量】
  ↓
筛选未达标用户
  ↓
【每个未达标用户独立执行】
  ├─ 建立 WebSocket
  ├─ while True:
  │   ├─ 查询最新交易量
  │   ├─ 检查是否达标 → 是：退出
  │   ├─ 计算剩余交易量和循环次数
  │   ├─ 执行 N 次批次交易
  │   └─ 批次完成，回到循环开头
  └─ 达标后清理 WebSocket
```

**优势**:
- ✅ **真实交易量**：直接查询币安 API
- ✅ **高效执行**：跳过已达标用户
- ✅ **批次可预测**：预先计算循环次数
- ✅ **容错机制**：批次后重查，自动补足
- ✅ **适应延迟**：多次查询确保准确

---

## 📊 执行流程详解

### 阶段 1: 初始检查

```python
# 并行查询所有用户的当前交易量
async def start_strategy(strategy):
    # 1. 获取所有用户凭证
    for user_id in strategy.user_ids:
        credentials = await get_user_credentials(user_id)
        ...
    
    # 2. 并行查询交易量
    tasks = [
        query_user_current_volume(user_id, token, headers, cookies)
        for user_id in strategy.user_ids
    ]
    volumes = await asyncio.gather(*tasks)
    
    # 3. 筛选未达标用户
    for user_id, volume in zip(user_ids, volumes):
        if volume < target_volume:
            # 启动该用户的策略
            asyncio.create_task(run_user_strategy(user_id, strategy))
        else:
            logger.info(f"用户{user_id}已达标，跳过")
```

**示例**:
```
策略: aop_volume_boost
目标: 10,000 USDT
用户列表: [1, 2, 3]

查询结果:
  用户1: 8,500 USDT → 未达标 ✅ 执行
  用户2: 10,200 USDT → 已达标 ❌ 跳过
  用户3: 0 USDT → 未达标 ✅ 执行

实际执行用户: [1, 3]
```

---

### 阶段 2: 用户批次循环

```python
async def run_user_strategy(user_id, strategy):
    # 建立 WebSocket 连接
    await ensure_websocket_connection(user_id, headers, cookies)
    
    try:
        # 批次循环，直至达标
        while True:
            # 查询当前交易量
            current_volume = await query_user_current_volume(
                user_id, strategy.target_token, headers, cookies
            )
            
            # 检查是否达标
            if current_volume >= strategy.target_volume:
                logger.info("用户已达成目标交易量")
                break
            
            # 计算剩余交易量和循环次数
            remaining = strategy.target_volume - current_volume
            loop_count = await calculate_loop_count(
                user_id, strategy, remaining, headers, cookies
            )
            
            # 执行 N 次批次交易
            await execute_batch_trades(
                user_id, strategy, loop_count, headers, cookies
            )
            
            # 批次完成，回到循环开头（重新查询）
            
    finally:
        # 清理 WebSocket
        await cleanup_websocket_connection(user_id)
```

---

### 阶段 3: 循环次数计算

```python
async def calculate_loop_count(user_id, strategy, remaining_volume, headers, cookies):
    # 1. 获取代币的 mulPoint
    token_info = await client.get_token_info()
    mul_point = await self._get_mul_point(token_info, strategy.target_token)
    
    # 2. 计算单次交易的真实交易量
    single_real_volume = strategy.single_trade_amount_usdt / Decimal(str(mul_point))
    
    # 3. 计算循环次数（向上取整）
    loop_count = math.ceil(float(remaining_volume / single_real_volume))
    
    return max(1, loop_count)
```

**计算示例**:

| 场景 | 剩余量 | 代币 | mulPoint | 单次金额 | 真实单次 | 循环次数 |
|------|--------|------|----------|---------|---------|---------|
| 场景1 | 1500 | AOP | 4 | 30 | 7.5 | 200 |
| 场景2 | 50 | AOP | 4 | 30 | 7.5 | 7 |
| 场景3 | 1000 | KOGE | 1 | 30 | 30 | 34 |
| 场景4 | 100 | KOGE | 1 | 30 | 30 | 4 |

---

### 阶段 4: 批次交易执行

```python
async def execute_batch_trades(user_id, strategy, loop_count, headers, cookies):
    for i in range(loop_count):
        # 检查停止标志
        if stop_flag:
            break
        
        logger.info(f"执行批次交易 {i+1}/{loop_count}")
        
        # 执行单次交易
        success, trade_volume = await execute_single_trade(
            user_id, strategy, headers, cookies
        )
        
        if success:
            logger.info(f"批次交易成功 {i+1}/{loop_count}, volume={trade_volume}")
        else:
            logger.warning(f"批次交易失败 {i+1}/{loop_count}")
            await interruptible_sleep(retry_delay)
            continue
        
        # 等待交易间隔
        await interruptible_sleep(strategy.trade_interval_seconds)
```

---

### 阶段 5: 重新查询验证

```python
# 批次完成后，回到 while 循环开头
while True:
    # 重新查询最新交易量
    current_volume = await query_user_current_volume(...)
    
    # 再次检查是否达标
    if current_volume >= target_volume:
        break  # 达标，退出
    
    # 未达标，继续计算并执行
    ...
```

**示例**:
```
第1批次:
  计划: 200 次
  执行: 200 次
  查询: 9,950 USDT (10次订单未成交)
  剩余: 50 USDT
  继续: 计算第2批次

第2批次:
  计划: 7 次
  执行: 7 次
  查询: 10,002.5 USDT
  达标: ✅ 退出
```

---

## 🔧 关键方法

### 1. `_query_user_current_volume()`

**功能**: 查询用户指定代币的当前交易量

**API**: `GET /bapi/defi/v1/private/wallet-direct/buw/wallet/today/user-volume`

**返回示例**:
```json
{
  "totalVolume": 8532.45,
  "tradeVolumeInfoList": [
    {
      "tokenName": "AOP",
      "volume": 8500.00
    }
  ]
}
```

**代码**:
```python
volume_data = await client.get_user_volume()
for token_vol in volume_data["tradeVolumeInfoList"]:
    if token_vol["tokenName"] == token_symbol:
        return Decimal(token_vol["volume"])
return Decimal("0")
```

---

### 2. `_calculate_loop_count()`

**功能**: 根据剩余交易量和 mulPoint 计算循环次数

**公式**:
```
single_real_volume = single_trade_amount / mulPoint
loop_count = ceil(remaining_volume / single_real_volume)
```

**代码**:
```python
mul_point = await self._get_mul_point(token_info, strategy.target_token)
single_real_volume = strategy.single_trade_amount_usdt / Decimal(str(mul_point))
loop_count = math.ceil(float(remaining_volume / single_real_volume))
return max(1, loop_count)
```

---

### 3. `_execute_batch_trades()`

**功能**: 执行 N 次批次交易

**流程**:
```
for i in range(loop_count):
    1. 检查停止标志
    2. 执行单次交易
    3. 等待交易间隔
```

**特点**:
- 可中断（Ctrl+C）
- 失败重试
- 进度日志

---

## 📈 完整执行示例

### 场景设置

```yaml
# config/trading_config.yaml
strategies:
  - strategy_id: "aop_volume_boost"
    target_token: AOP
    target_chain: BSC
    target_volume: 10000  # 目标 10,000 USDT
    
    user_ids: [1, 2, 3]
    
    single_trade_amount_usdt: 30
    trade_interval_seconds: 1
```

### 执行时间线

```
时间 00:00 - 启动策略
    策略: aop_volume_boost
    目标: 10,000 USDT
    用户: [1, 2, 3]

时间 00:01 - 并行查询所有用户交易量
    用户1: GET /user-volume → 8,500 USDT
    用户2: GET /user-volume → 10,200 USDT
    用户3: GET /user-volume → 0 USDT

时间 00:02 - 筛选未达标用户
    用户1: 8,500 < 10,000 → 未达标 ✅
    用户2: 10,200 >= 10,000 → 已达标 ❌ 跳过
    用户3: 0 < 10,000 → 未达标 ✅

时间 00:03 - 用户1：第1批次开始
    当前: 8,500 USDT
    剩余: 1,500 USDT
    mulPoint: 4
    单次真实交易量: 30 / 4 = 7.5 USDT
    循环次数: ceil(1500 / 7.5) = 200 次

时间 00:04 - 用户1：建立 WebSocket
    ListenKey: xxx
    连接状态: ✅

时间 00:05 - 用户1：执行第1批次交易 (1/200)
    下单 30 USDT → 买单成交 → 卖单成交
    
...

时间 08:30 - 用户1：执行第1批次交易 (200/200)
    下单 30 USDT → 买单成交 → 卖单成交

时间 08:31 - 用户1：第1批次完成，重新查询
    查询: GET /user-volume → 9,950 USDT
    剩余: 50 USDT
    分析: 有10次订单未成交

时间 08:32 - 用户1：第2批次开始
    剩余: 50 USDT
    循环次数: ceil(50 / 7.5) = 7 次

时间 08:33 - 用户1：执行第2批次交易 (1/7)
    ...

时间 08:40 - 用户1：执行第2批次交易 (7/7)
    下单 30 USDT → 买单成交 → 卖单成交

时间 08:41 - 用户1：第2批次完成，重新查询
    查询: GET /user-volume → 10,002.5 USDT
    检查: 10,002.5 >= 10,000 ✅ 达标

时间 08:42 - 用户1：策略完成
    清理 WebSocket
    最终交易量: 10,002.5 USDT

---

时间 00:03 - 用户3：第1批次开始
    当前: 0 USDT
    剩余: 10,000 USDT
    循环次数: ceil(10000 / 7.5) = 1334 次

...

时间 18:00 - 用户3：第1批次完成，重新查询
    查询: GET /user-volume → 9,980 USDT
    剩余: 20 USDT

时间 18:01 - 用户3：第2批次开始
    循环次数: ceil(20 / 7.5) = 3 次

...

时间 18:05 - 用户3：策略完成
    最终交易量: 10,005 USDT
```

---

## ✅ 关键优势

### 1. 真实交易量查询

- **旧逻辑**: 程序内部统计（可能不准）
- **新逻辑**: 直接查询币安 API（绝对准确）

### 2. 智能筛选

- **旧逻辑**: 所有用户都执行
- **新逻辑**: 只执行未达标用户

### 3. 批次可预测

- **旧逻辑**: 逐笔执行，不知道要多久
- **新逻辑**: 预先计算 200 次，可预测

### 4. 自动补足

- **旧逻辑**: 订单失败导致交易量不足
- **新逻辑**: 批次后重查，自动补足剩余

### 5. 适应延迟

- **旧逻辑**: 无法应对 API 延迟
- **新逻辑**: 多次查询确保达标

---

## 📊 性能对比

### 场景: 用户1 从 8,500 → 10,000 USDT

| 指标 | 旧逻辑 | 新逻辑 |
|------|--------|--------|
| **初始查询** | 0 次 | 1 次 |
| **批次查询** | 0 次 | 2 次（每批次后） |
| **循环次数** | 逐笔，不可预测 | 200 + 7 次 |
| **API 调用** | 200+ 次下单 | 3 次查询 + 207 次下单 |
| **容错性** | 无 | 自动补足 |
| **达标准确性** | 可能不准 | 绝对准确 |

---

## 🔧 配置参数

### 全局配置

```yaml
global_settings:
  default_single_trade_amount_usdt: 30  # 单次交易金额
  default_trade_interval_seconds: 1      # 交易间隔
  order_timeout_seconds: 300             # 订单超时
```

### 策略配置

```yaml
strategies:
  - strategy_id: "aop_volume_boost"
    target_token: AOP
    target_volume: 10000  # 目标真实交易量
    
    user_ids: [1, 2, 3]  # 多用户
    
    # 可选覆盖
    single_trade_amount_usdt: 30
    trade_interval_seconds: 1
```

---

## 📝 相关文档

- [批次执行逻辑详解](./batch_execution_logic.md)
- [MulPoint 处理说明](./mulpoint_handling.md)
- [策略执行流程](./strategy_execution_flow.md)

---

## 📌 版本历史

- **V2.2.0** (2025-10-10)
  - ✅ 批次循环执行
  - ✅ 先查询再计算
  - ✅ 批次后重新查询
  - ✅ 筛选未达标用户
  - ✅ 完整容错机制

- **V2.1.0** (2025-10-10)
  - ✅ 完全成交等待
  - ✅ WebSocket 实时监听
  - ✅ MulPoint 处理

- **V2.0.0** (2025-10-09)
  - ✅ 初始版本
  - ✅ 基础 OTO 交易

