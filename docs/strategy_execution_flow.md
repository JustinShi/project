# 交易策略执行流程详解

## 概述

当前交易策略执行器 (`StrategyExecutor`) 采用**完全成交等待机制** + **WebSocket 实时监听** + **MulPoint 交易量处理**，确保每次 OTO 订单完全成交后才继续下一单。

---

## 完整执行流程

### 1. 策略启动阶段

```
用户启动策略
    ↓
读取配置文件 (config/trading_config.yaml)
    ↓
加载策略配置
    ↓
为每个用户创建并发任务
```

**代码位置**: `start_all_strategies()` / `start_strategy()`

---

### 2. 用户策略初始化

```
获取用户凭证（从数据库）
    ↓
建立 WebSocket 连接
    ├─ 获取 ListenKey
    ├─ 连接到 wss://nbstream.binance.com/w3w/stream
    ├─ 订阅: alpha@{listenKey}
    └─ 启动订单状态监听
    ↓
初始化交易量统计 (user_volumes[user_id][strategy_id] = 0)
    ↓
进入交易循环
```

**代码位置**: `_run_user_strategy()`

**关键点**:
- ✅ WebSocket 连接失败会终止策略
- ✅ 连接成功后才开始交易

---

### 3. 交易循环（核心逻辑）

```
while 未达到目标交易量 AND 未收到停止信号:
    ↓
    【步骤 1】获取代币信息
    ├─ 获取当前价格
    ├─ 获取 mulPoint（交易量倍数）
    └─ 获取符号映射
    ↓
    【步骤 2】计算订单参数
    ├─ 买入价格 = 市场价格 × (1 + buy_offset_percentage / 100)
    ├─ 卖出价格 = 买入价格 × (1 - sell_profit_percentage / 100)
    └─ 计算数量 = single_trade_amount_usdt / buy_price
    ↓
    【步骤 3】下 OTO 订单
    ├─ 调用币安 API 下单
    ├─ 获取 working_order_id (买单ID)
    └─ 获取 pending_order_id (卖单ID)
    ↓
    【步骤 4】等待买单成交 ⏱️
    ├─ 监听 WebSocket 推送
    ├─ 收到 executionReport: status=NEW
    ├─ 收到 executionReport: status=FILLED ✅
    └─ 或者超时（默认 300 秒）
    ↓
    买单成交？
    ├─ 否 → 跳过此次交易，等待重试
    └─ 是 → 继续
    ↓
    【步骤 5】等待卖单成交 ⏱️
    ├─ 监听 WebSocket 推送
    ├─ 收到 executionReport: status=NEW
    ├─ 收到 executionReport: status=FILLED ✅
    └─ 或者超时（默认 300 秒）
    ↓
    卖单成交？
    ├─ 否 → 记录部分成功（买单已成交）
    └─ 是 → 完全成功 ✅
    ↓
    【步骤 6】计算真实交易量
    ├─ real_trade_volume = effective_amount / mulPoint
    ├─ 累计到用户交易量
    └─ 记录日志
    ↓
    【步骤 7】等待交易间隔
    ├─ 可中断的等待（每 0.1 秒检查停止标志）
    └─ 间隔结束，回到步骤 1
```

**代码位置**: `_trade_loop()` + `_execute_single_trade()`

---

## 详细步骤说明

### 步骤 1: 获取代币信息

```python
# 获取当前价格
token_info = await client.get_token_info()
last_price = await self._fetch_last_price(token_info, "KOGE")

# 获取 mulPoint
mul_point = await self._get_mul_point(token_info, "KOGE")
# 返回: 1 (KOGE) 或 4 (AOP)
```

**用途**:
- 价格用于计算订单数量
- mulPoint 用于计算真实交易量

---

### 步骤 2: 计算订单参数

**刷量策略价格计算**（高买低卖）:

```python
# 买入价格（溢价买入）
buy_offset_percentage = 10  # 配置: 10%
buy_price = market_price × (1 + 10/100)
         = market_price × 1.10

# 卖出价格（折价卖出）
sell_profit_percentage = 10  # 配置: 10%
sell_price = buy_price × (1 - 10/100)
          = buy_price × 0.90

# 数量
quantity = single_trade_amount_usdt / buy_price
         = 30 / buy_price
```

**示例**（市场价 = 100 USDT）:
- 买入价格: 100 × 1.10 = **110 USDT**
- 卖出价格: 110 × 0.90 = **99 USDT**
- 数量: 30 / 110 = **0.2727**

---

### 步骤 3: 下 OTO 订单

```python
# OTO 订单包含两个订单
order_info = await oto_client.place_oto_order(
    symbol="KOGEUSDT",
    quantity=0.2727,
    buy_price=110,
    sell_price=99,
)

# 返回
{
    "workingOrderId": "191281455",  # 买单（先执行）
    "pendingOrderId": "191281574"   # 卖单（买单成交后触发）
}
```

---

### 步骤 4: 等待买单成交

**WebSocket 监听流程**:

```
时间 0s: 下单成功
    ↓
时间 1s: WebSocket 推送
    {
        "order_id": "191281455",
        "status": "NEW",  # 订单已创建
        "executed_quantity": "0"
    }
    ↓
时间 3s: WebSocket 推送
    {
        "order_id": "191281455",
        "status": "FILLED",  # 完全成交 ✅
        "executed_quantity": "0.2727"
    }
    ↓
买单成交确认，继续等待卖单
```

**等待机制**:

```python
# 使用 asyncio.Event 实现异步等待
buy_filled = await self._wait_for_order_filled(
    working_order_id,
    timeout=300  # 5分钟超时
)
```

**超时处理**:
- 如果 300 秒内未成交 → 返回失败，跳过此次交易

---

### 步骤 5: 等待卖单成交

类似买单流程，等待卖单完全成交。

**特殊情况**:
- 买单成交但卖单超时 → **仍计入交易量**（部分成功）
- 避免重复买入导致资金占用

---

### 步骤 6: 计算真实交易量

**考虑 mulPoint 倍数**:

```python
# 名义交易金额
effective_amount = 30 USDT  # 单次下单金额

# 真实交易量
real_trade_volume = effective_amount / mul_point

# 示例 1: KOGE (mulPoint=1)
real_trade_volume = 30 / 1 = 30 USDT

# 示例 2: AOP (mulPoint=4)
real_trade_volume = 30 / 4 = 7.5 USDT
```

**累计交易量**:

```python
self._user_volumes[user_id][strategy_id] += real_trade_volume
```

---

### 步骤 7: 等待交易间隔

**可中断的等待**:

```python
# trade_interval_seconds = 3
for _ in range(3 * 10):  # 30 次循环
    if self._stop_flags.get(strategy_id):
        break  # 收到停止信号，立即退出
    await asyncio.sleep(0.1)  # 每次等待 0.1 秒
```

**优点**:
- 支持 Ctrl+C 立即停止
- 响应时间 < 100ms

---

## WebSocket 订单监听机制

### 连接建立

```
1. 获取 ListenKey
   POST /bapi/defi/v1/private/alpha-trade/get-listen-key
   ↓
2. 连接 WebSocket
   wss://nbstream.binance.com/w3w/stream
   ↓
3. 发送订阅消息
   {
     "method": "SUBSCRIBE",
     "params": ["alpha@{listenKey}"],
     "id": 1
   }
   ↓
4. 接收订阅确认
   {"result": null, "id": 1}
```

### 消息处理

```python
# WebSocket 回调
async def _handle_order_update(order_data):
    order_id = order_data["order_id"]
    status = order_data["status"]
    
    # 更新订单状态
    self._order_status[order_id] = order_data
    
    # 如果订单完成，触发事件
    if status in ["FILLED", "CANCELED", "REJECTED"]:
        self._order_events[order_id].set()  # 唤醒等待的协程
```

### 消息格式

```json
{
  "stream": "alpha@{listenKey}",
  "data": {
    "e": "executionReport",
    "s": "ALPHA_22USDT",
    "i": "191281455",  // 订单ID
    "X": "FILLED",     // 订单状态
    "S": "BUY",        // 方向
    "p": "110",        // 价格
    "q": "0.2727",     // 数量
    "z": "0.2727",     // 已成交数量
    ...
  }
}
```

---

## 关键数据结构

### 1. 订单状态追踪

```python
self._order_status = {
    "191281455": {
        "order_id": "191281455",
        "status": "FILLED",
        "side": "BUY",
        "executed_quantity": "0.2727",
        ...
    }
}
```

### 2. 订单事件

```python
self._order_events = {
    "191281455": asyncio.Event()  # 用于等待订单完成
}
```

### 3. 用户交易量

```python
self._user_volumes = {
    1: {  # user_id
        "koge_volume_boost": Decimal("150.5"),  # strategy_id: volume
        "aop_test": Decimal("25.0")
    }
}
```

### 4. WebSocket 连接

```python
self._ws_connectors = {
    1: OrderWebSocketConnector(...)  # user_id: connector
}
```

---

## 配置参数说明

### 全局配置

```yaml
global_settings:
  default_buy_offset_percentage: 10      # 买入溢价 10%
  default_sell_profit_percentage: 10     # 卖出折扣 10%
  default_trade_interval_seconds: 1      # 交易间隔 1 秒
  default_single_trade_amount_usdt: 30   # 单次交易 30 USDT
  order_timeout_seconds: 300             # 订单超时 5 分钟
```

### 策略配置

```yaml
strategies:
  - strategy_id: "koge_volume_boost"
    target_token: KOGE
    target_chain: BSC
    target_volume: 16384  # 目标真实交易量
    user_ids: [1]
    
    # 可选覆盖全局设置
    single_trade_amount_usdt: 30
    trade_interval_seconds: 1
```

---

## 完整示例：执行一次交易

### 场景

- **代币**: KOGE (mulPoint=1)
- **市场价**: 0.002 USDT
- **配置**:
  - 单次金额: 30 USDT
  - 买入溢价: 10%
  - 卖出折扣: 10%

### 执行过程

```
时间 00:00 - 获取价格
    市场价格: 0.002 USDT
    mulPoint: 1

时间 00:01 - 计算订单
    买入价格: 0.002 × 1.10 = 0.0022 USDT
    卖出价格: 0.0022 × 0.90 = 0.00198 USDT
    数量: 30 / 0.0022 = 13636.36

时间 00:02 - 下 OTO 订单
    买单ID: 191281455
    卖单ID: 191281574
    订单状态: 已提交

时间 00:03 - WebSocket 推送
    [买单 NEW] order_id=191281455, status=NEW

时间 00:05 - WebSocket 推送
    [买单 FILLED] order_id=191281455, status=FILLED ✅

时间 00:06 - WebSocket 推送
    [卖单 NEW] order_id=191281574, status=NEW

时间 00:07 - WebSocket 推送
    [卖单 FILLED] order_id=191281574, status=FILLED ✅

时间 00:08 - 计算交易量
    名义金额: 30 USDT
    真实交易量: 30 / 1 = 30 USDT
    累计交易量: 0 + 30 = 30 USDT

时间 00:09 - 等待间隔（1秒）

时间 00:10 - 开始下一笔交易
```

---

## 异常处理

### 1. WebSocket 连接失败

```
策略启动
    ↓
WebSocket 连接失败
    ↓
记录错误日志
    ↓
策略终止（不执行交易）
```

### 2. 订单超时

```
等待订单成交
    ↓
300 秒超时
    ↓
买单超时: 跳过，等待重试间隔
卖单超时: 计入部分成功（买单已成交）
```

### 3. API 错误

```
下单请求失败
    ↓
记录错误日志
    ↓
等待重试间隔（失败间隔 × 20）
    ↓
继续下一次尝试
```

### 4. 用户中断（Ctrl+C）

```
用户按 Ctrl+C
    ↓
设置停止标志
    ↓
当前交易完成后退出
    ↓
清理 WebSocket 连接
    ↓
显示最终统计
```

---

## 性能指标

### 单次交易耗时

| 阶段 | 时间 |
|-----|------|
| 获取价格 | 1-2秒 |
| 下单 | 1-2秒 |
| 买单成交 | 1-10秒 |
| 卖单成交 | 1-10秒 |
| **总计** | **4-24秒** |

### 资源占用

- **WebSocket 连接**: 每用户 1 个
- **内存**: < 50MB（单用户单策略）
- **CPU**: < 5%（等待状态）

---

## 日志输出示例

```
2025-10-10 17:00:00 | INFO | 策略开始执行, strategy_id=koge_volume_boost
2025-10-10 17:00:01 | INFO | WebSocket连接已建立, user_id=1
2025-10-10 17:00:02 | INFO | 代币交易量倍数, token=KOGE, mul_point=1
2025-10-10 17:00:03 | INFO | OTO订单下单成功, working_order_id=191281455
2025-10-10 17:00:03 | INFO | 等待买单成交, order_id=191281455
2025-10-10 17:00:05 | INFO | 订单状态更新, order_id=191281455, status=FILLED
2025-10-10 17:00:05 | INFO | 买单已成交, order_id=191281455
2025-10-10 17:00:05 | INFO | 等待卖单成交, order_id=191281574
2025-10-10 17:00:07 | INFO | 订单状态更新, order_id=191281574, status=FILLED
2025-10-10 17:00:07 | INFO | 卖单已成交, order_id=191281574
2025-10-10 17:00:07 | INFO | OTO订单完全成交, 
    amount=30.0, mul_point=1, real_trade_volume=30.0
2025-10-10 17:00:07 | INFO | 交易成功, trade_volume=30.0, progress=0.18%
```

---

## 相关文档

- [交易策略优化总结](./strategy_optimization_summary.md)
- [订单 WebSocket 测试指南](./order_websocket_test_guide.md)
- [MulPoint 处理说明](./mulpoint_handling.md)
- [交易策略配置指南](./trading_strategy_guide.md)

---

## 版本

- **v2.1.0** (2025-10-10)
  - ✅ 完全成交等待机制
  - ✅ WebSocket 实时监听
  - ✅ MulPoint 交易量处理
  - ✅ 订单超时保护
  - ✅ 优雅停止支持

