# 订单 WebSocket 推送测试指南

## 概述

本文档介绍如何测试币安 Alpha 交易系统的订单 WebSocket 推送功能。

## 测试架构

```
用户凭证(数据库)
     ↓
ListenKey 获取 (API)
     ↓
WebSocket 连接 (wss://nbstream.binance.com/w3w/stream)
     ↓
订阅: alpha@{listenKey}
     ↓
接收订单推送 (executionReport)
```

## 测试脚本

### 1. 完整测试脚本

**文件**: `scripts/test_order_ws_final.py`

**功能**:
- 从数据库获取用户凭证
- 获取 ListenKey
- 建立 WebSocket 连接
- 监听订单推送
- 实时显示订单更新
- 统计订单状态

**用法**:

```bash
# 测试用户1，持续60秒（默认）
uv run python scripts/test_order_ws_final.py

# 测试用户1，持续30秒
uv run python scripts/test_order_ws_final.py --user 1 --duration 30

# 测试用户2，持续120秒
uv run python scripts/test_order_ws_final.py --user 2 --duration 120
```

**参数**:
- `--user`: 用户ID（默认: 1）
- `--duration`: 测试时长，单位秒（默认: 60）

### 2. ListenKey 快速测试

**文件**: `scripts/test_listen_key_quick.py`

**功能**:
- 快速测试 ListenKey 获取
- 显示 WebSocket 连接信息

**用法**:

```bash
uv run python scripts/test_listen_key_quick.py
```

### 3. 简化测试（数据库版）

**文件**: `scripts/test_order_ws_simple.py`

**功能**:
- 从数据库获取凭证
- 测试 ListenKey 获取
- 不建立实际 WebSocket 连接

## 测试步骤

### 步骤 1: 准备用户凭证

确保数据库中有用户凭证配置：

```sql
SELECT id, name, headers IS NOT NULL as has_headers, 
       cookies IS NOT NULL as has_cookies 
FROM users 
WHERE id = 1;
```

如果没有凭证，请更新：

```sql
UPDATE users 
SET headers = '{"x-passthrough-token":"...","csrftoken":"..."}',
    cookies = 'cookie1=value1; cookie2=value2'
WHERE id = 1;
```

### 步骤 2: 启动 WebSocket 测试

在一个终端窗口中运行：

```bash
uv run python scripts/test_order_ws_final.py --user 1 --duration 60
```

预期输出：

```
================================================================================
🚀 测试订单 WebSocket 推送
================================================================================
用户ID: 1
测试时长: 60 秒

✅ 用户凭证获取成功
✅ ListenKey 获取成功
   ListenKey: pqIA6YaQJw...
✅ WebSocket 连接器创建成功
✅ WebSocket 连接已建立

📊 连接信息:
   用户ID: 1
   已连接: True
   重连尝试: 0/10

💡 提示:
   - 请使用 quick_start_strategy.py 脚本触发订单
   - 或在币安 Alpha 平台手动下单
   - 按 Ctrl+C 停止测试

⏳ 等待订单更新（60 秒）...
```

### 步骤 3: 触发订单（可选）

在另一个终端窗口中运行交易策略：

```bash
uv run python scripts/quick_start_strategy.py --token KOGE --chain BSC --volume 20 --amount 10 --user 1 --interval 5
```

### 步骤 4: 观察 WebSocket 推送

当订单被创建或更新时，测试脚本会实时显示：

```
================================================================================
📦 订单更新 #1
--------------------------------------------------------------------------------
订单信息:
   用户ID: 1
   订单ID: 51481849
   客户端订单ID: web_164e079573c1491795e1ee245d5ed293
   交易对: ALPHA_373USDT
   方向: BUY
   类型: LIMIT
   状态: NEW
   价格: 0.23000000
   数量: 869.56000000
   已执行: 0
================================================================================
```

## WebSocket 消息格式

### 订单执行报告 (executionReport)

**字段说明**:

| 字段 | 说明 |
|-----|-----|
| `e` | 事件类型 (executionReport) |
| `s` | 交易对符号 |
| `c` | 客户端订单ID |
| `S` | 订单方向 (BUY/SELL) |
| `o` | 订单类型 (LIMIT/MARKET) |
| `X` | 订单状态 (NEW/FILLED/CANCELED等) |
| `i` | 订单ID（交易所） |
| `p` | 订单价格 |
| `q` | 订单数量 |
| `z` | 累计成交数量 |
| `L` | 最后成交价格 |
| `n` | 手续费 |
| `N` | 手续费资产 |

### 订单状态枚举

| 状态 | 说明 |
|-----|-----|
| NEW | 新订单已接受 |
| PARTIALLY_FILLED | 部分成交 |
| FILLED | 完全成交 |
| CANCELED | 已取消 |
| PENDING_CANCEL | 取消中 |
| REJECTED | 已拒绝 |
| EXPIRED | 已过期 |

## 测试统计

测试结束后会显示统计信息：

```
================================================================================
📊 测试统计
================================================================================
总订单更新数: 5
连接事件数: 2

订单状态分布:
   FILLED: 2
   NEW: 3
================================================================================

✅ 测试完成
```

## 常见问题

### 1. ListenKey 获取失败

**错误**: `❌ 获取 ListenKey 失败: HTTP错误: 401`

**解决**:
- 检查用户凭证是否有效
- 确认 headers 中包含正确的认证 token
- 检查是否需要完成补充认证

### 2. WebSocket 连接未建立

**错误**: `⚠️  WebSocket 连接未建立（可能正在连接中）`

**解决**:
- 等待几秒，连接可能需要时间
- 检查网络连接
- 查看日志文件中的详细错误信息

### 3. 没有接收到订单推送

**原因**:
- 没有实际订单触发
- WebSocket 订阅未成功
- ListenKey 过期

**解决**:
- 使用 `quick_start_strategy.py` 触发订单
- 检查 WebSocket 连接状态
- 查看日志中是否有订阅确认消息

### 4. 用户凭证为空

**错误**: `❌ 用户 1 没有配置凭证`

**解决**:

```sql
-- 更新用户凭证
UPDATE users 
SET headers = '{"x-passthrough-token":"your_token","csrftoken":"your_csrf"}',
    cookies = 'your_cookies_string'
WHERE id = 1;
```

## 实现细节

### ListenKey 管理

**代码位置**: `src/binance/infrastructure/binance_client/listen_key_manager.py`

**功能**:
- 获取 ListenKey (有效期60分钟)
- 自动保活 (每30分钟续期)
- 过期检测和自动刷新

### WebSocket 连接器

**代码位置**: `src/binance/infrastructure/binance_client/order_websocket.py`

**功能**:
- 建立 WebSocket 连接
- 订阅订单推送频道
- 解析订单消息
- 自动重连（指数退避）
- 连接状态监控

### 订单推送处理

**流程**:

```
WebSocket 接收消息
     ↓
解析 JSON
     ↓
检查事件类型 (executionReport)
     ↓
提取订单信息
     ↓
调用回调函数
     ↓
更新本地订单状态
```

## 测试清单

- [ ] ListenKey 获取成功
- [ ] WebSocket 连接建立成功
- [ ] 接收到订单创建推送 (NEW)
- [ ] 接收到订单成交推送 (FILLED)
- [ ] 接收到订单取消推送 (CANCELED)
- [ ] WebSocket 自动重连正常
- [ ] ListenKey 自动续期正常
- [ ] 统计信息准确
- [ ] Ctrl+C 可以正常停止测试

## 参考文档

- [WebSocket 消息格式](../specs/001-lpha-oto/contracts/websocket-messages.yaml)
- [币安 API 文档](./binance/api.md)
- [订单执行服务](../src/binance/application/services/order_execution_service.py)

## 版本历史

- **v1.0.0** (2025-10-10)
  - 初始版本
  - 支持基本的订单 WebSocket 推送测试
  - 包含完整的测试脚本和文档

