# 订单 WebSocket 推送测试

## 快速开始

已为您创建完整的订单 WebSocket 推送测试系统。

### 运行测试

```bash
# 测试订单 WebSocket 推送（30秒）
uv run python scripts/test_order_ws_final.py --user 1 --duration 30
```

### 同时触发订单（在另一个终端）

```bash
# 触发交易策略，生成订单
uv run python scripts/quick_start_strategy.py --token KOGE --chain BSC --volume 20 --amount 10 --user 1 --interval 5
```

## 测试脚本

### 主要测试脚本

| 脚本 | 功能 | 用途 |
|-----|------|-----|
| `test_order_ws_final.py` | 完整测试 | 获取凭证 + ListenKey + WebSocket 连接 + 订单监听 |
| `test_order_ws_simple.py` | 简化测试 | 仅测试凭证获取和 ListenKey |
| `test_listen_key_quick.py` | 快速测试 | 快速验证 ListenKey 获取功能 |

### 其他相关脚本

| 脚本 | 功能 |
|-----|------|
| `test_order_websocket.py` | 早期版本（较复杂） |
| `test_order_ws_direct.py` | 使用环境变量凭证 |

## 功能特性

✅ **已实现的功能**:

1. **ListenKey 管理**
   - 自动获取 ListenKey
   - 自动续期（每30分钟）
   - 过期检测和刷新

2. **WebSocket 连接**
   - 建立到币安的 WebSocket 连接
   - 订阅订单推送频道: `alpha@{listenKey}`
   - 自动重连（指数退避策略）
   - 连接状态监控

3. **订单推送处理**
   - 实时接收订单状态更新
   - 解析 `executionReport` 事件
   - 显示订单详细信息
   - 统计订单状态分布

4. **优雅停止**
   - 支持 Ctrl+C 中断
   - 自动清理资源
   - 显示测试统计信息

## 测试输出示例

### 成功连接

```
================================================================================
🚀 测试订单 WebSocket 推送
================================================================================
用户ID: 1
测试时长: 30 秒

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

⏳ 等待订单更新（30 秒）...
```

### 接收到订单推送

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

### 测试统计

```
================================================================================
📊 测试统计
================================================================================
总订单更新数: 4
连接事件数: 2

订单状态分布:
   FILLED: 2
   NEW: 2
================================================================================

✅ 测试完成
```

## WebSocket 消息类型

### 订单状态

- `NEW` - 新订单已接受
- `PARTIALLY_FILLED` - 部分成交
- `FILLED` - 完全成交
- `CANCELED` - 已取消
- `REJECTED` - 已拒绝
- `EXPIRED` - 已过期

### 消息字段

| 字段 | 说明 |
|-----|------|
| `i` | 订单ID（交易所） |
| `c` | 客户端订单ID |
| `s` | 交易对符号 |
| `S` | 订单方向 (BUY/SELL) |
| `X` | 订单状态 |
| `p` | 订单价格 |
| `q` | 订单数量 |
| `z` | 累计成交数量 |

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      测试脚本                                 │
│            test_order_ws_final.py                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
          ┌─────────────┴────────────┐
          │                          │
┌─────────▼──────────┐    ┌─────────▼──────────┐
│  ListenKeyManager  │    │ OrderWebSocket     │
│                    │    │    Connector       │
│  - 获取 ListenKey  │    │ - 建立 WS 连接     │
│  - 自动续期        │    │ - 订阅推送         │
│  - 过期检测        │    │ - 自动重连         │
└─────────┬──────────┘    └─────────┬──────────┘
          │                         │
          │ ListenKey               │ WebSocket
          │                         │ Messages
          ▼                         ▼
    ┌──────────────────────────────────────┐
    │         币安 API / WebSocket         │
    │  - userDataStream (ListenKey)       │
    │  - wss://nbstream.binance.com       │
    └──────────────────────────────────────┘
```

## 核心组件

### 1. ListenKeyManager

**文件**: `src/binance/infrastructure/binance_client/listen_key_manager.py`

**职责**:
- 调用币安 API 获取 ListenKey
- 每30分钟自动续期
- 检测过期并自动刷新

### 2. OrderWebSocketConnector

**文件**: `src/binance/infrastructure/binance_client/order_websocket.py`

**职责**:
- 建立 WebSocket 连接
- 订阅 `alpha@{listenKey}` 频道
- 接收和解析订单消息
- 断线自动重连

### 3. BinanceWebSocketClient

**文件**: `src/binance/infrastructure/binance_client/websocket_client.py`

**职责**:
- 底层 WebSocket 通信
- 心跳检测
- 重连逻辑

## 故障排查

### 问题 1: ListenKey 获取失败

**症状**: `❌ 获取 ListenKey 失败`

**原因**:
- 用户凭证无效或过期
- 网络连接问题
- 需要补充认证

**解决**:
1. 检查数据库中的用户凭证
2. 更新 headers 中的认证 token
3. 完成币安平台的补充认证

### 问题 2: WebSocket 连接失败

**症状**: `⚠️  WebSocket 连接未建立`

**原因**:
- ListenKey 无效
- 网络问题
- 币安 WebSocket 服务故障

**解决**:
1. 重新获取 ListenKey
2. 检查网络连接
3. 查看日志文件获取详细错误

### 问题 3: 没有接收到订单推送

**症状**: 连接成功但没有消息

**原因**:
- 没有实际订单触发
- WebSocket 订阅未成功

**解决**:
1. 使用 `quick_start_strategy.py` 触发订单
2. 检查 WebSocket 连接状态
3. 查看日志中的订阅确认消息

## 相关文档

- 📖 [详细测试指南](docs/order_websocket_test_guide.md)
- 📖 [WebSocket 消息格式](specs/001-lpha-oto/contracts/websocket-messages.yaml)
- 📖 [币安 API 文档](docs/binance/api.md)

## 版本信息

- **创建日期**: 2025-10-10
- **版本**: 1.0.0
- **状态**: ✅ 已测试

## 下一步

1. ✅ 运行 `test_order_ws_final.py` 验证 WebSocket 连接
2. ✅ 使用 `quick_start_strategy.py` 触发订单
3. ✅ 观察订单推送消息
4. ✅ 检查统计信息是否正确

---

**提示**: 如果遇到问题，请查看日志文件或参考详细测试指南。

