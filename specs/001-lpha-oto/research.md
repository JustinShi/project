# Phase 0: Technical Research & Decisions
# 币安多用户Alpha代币OTO订单自动交易系统

**Branch**: `001-lpha-oto` | **Date**: 2025-10-09  
**Purpose**: 解决技术选型和架构设计中的未决问题

---

## 研究概述

本文档记录所有技术选型的研究过程、决策依据和替代方案评估。每个决策都包含：
- 最终选择及版本
- 选择理由
- 考虑的替代方案
- 潜在风险和缓解措施

---

## 1. WebSocket客户端库选择

### 决策: `websockets` 库 (v12.0+)

**选择理由**:
- ✅ Python原生asyncio支持，与FastAPI完美集成
- ✅ 简洁的API设计，易于使用和测试
- ✅ 内置自动重连和心跳机制
- ✅ 活跃维护，社区支持良好
- ✅ 低层级控制，适合币安WebSocket协议

**替代方案考虑**:

| 方案 | 优点 | 缺点 | 为何未选择 |
|------|------|------|----------|
| python-socketio | Socket.IO协议支持 | 过度设计，币安不使用Socket.IO | 协议不匹配 |
| aiohttp.ClientSession.ws_connect | 集成HTTP客户端 | WebSocket功能较弱，缺少重连 | 功能不足 |
| websocket-client | 同步API简单 | 同步阻塞，不适合高并发 | 性能限制 |

**实施要点**:
```python
# 连接管理模式
async with websockets.connect(uri, extra_headers=headers) as ws:
    async for message in ws:
        # 处理消息
        
# 重连策略
while True:
    try:
        await connect_and_listen()
    except websockets.ConnectionClosed:
        await asyncio.sleep(exponential_backoff())
```

**潜在风险**:
- 网络不稳定时频繁重连 → **缓解**: 指数退避重连策略，最大重试次数限制
- 内存泄漏（长连接） → **缓解**: 定期监控连接状态，异常时主动关闭重建

---

## 2. 订单状态机实现方案

### 决策: `python-statemachine` 库 (v2.1+)

**选择理由**:
- ✅ 声明式状态定义，代码可读性高
- ✅ 类型安全（支持type hints）
- ✅ 内置状态转换验证，防止非法状态跳转
- ✅ 支持状态图可视化导出（方便文档化）
- ✅ 事件驱动模型，易于与WebSocket集成

**替代方案考虑**:

| 方案 | 优点 | 缺点 | 为何未选择 |
|------|------|------|----------|
| transitions | 功能丰富，嵌套状态支持 | API较复杂，学习曲线陡 | 功能过度 |
| 自定义枚举+字典 | 简单直接，无外部依赖 | 缺少状态转换验证，易出错 | 安全性不足 |
| pytransitions | 轻量级 | 缺少类型安全，维护不活跃 | 类型安全缺失 |

**状态机设计**（基于FR-011, 订单状态机实体）:
```python
from statemachine import StateMachine, State

class OrderStateMachine(StateMachine):
    # 状态定义
    idle = State('空闲', initial=True)
    placing = State('下单中')
    pending = State('等待成交')
    partially_filled = State('部分成交')
    filled = State('完全成交', final=True)
    cancelling = State('取消中')
    cancelled = State('已取消')
    timeout = State('超时处理')
    
    # 状态转换
    place_order = idle.to(placing)
    order_placed = placing.to(pending)
    partial_fill = pending.to(partially_filled) | partially_filled.to.itself()
    complete_fill = (pending.to(filled) | 
                     partially_filled.to(filled))
    timeout_check = (pending.to(timeout) | 
                     partially_filled.to(timeout))
    cancel = (pending.to(cancelling) | 
              partially_filled.to(cancelling) |
              timeout.to(cancelling))
    cancel_complete = cancelling.to(cancelled)
    retry = (cancelled.to(idle) | 
             timeout.to(idle))
    
    # 防止重复下单的守卫
    def before_place_order(self):
        if self.current_state != self.idle:
            raise ValueError("只能在空闲状态下单")
```

**潜在风险**:
- 状态不一致（WebSocket延迟） → **缓解**: 所有状态变更带时间戳，冲突时以最新为准
- 并发状态修改 → **缓解**: 使用数据库乐观锁（version字段）

---

## 3. 认证信息加密方案

### 决策: `cryptography` 库的 Fernet (对称加密)

**选择理由**:
- ✅ NIST推荐的AES-128-CBC算法
- ✅ 内置消息完整性验证（HMAC）
- ✅ 简单易用，自动处理IV和padding
- ✅ 符合NFR-006要求（加密存储）
- ✅ Python标准加密库，广泛使用

**替代方案考虑**:

| 方案 | 优点 | 缺点 | 为何未选择 |
|------|------|------|----------|
| PyNaCl (NaCl/libsodium) | 现代密码学库，性能好 | 学习曲线高，过度强调匿名性 | 使用复杂 |
| PyCrypto/PyCryptodome | 功能全面 | 需手动处理IV、padding | 易出错 |
| 数据库内置加密 | 透明加密 | 依赖数据库特性，不可移植 | 灵活性差 |

**实施模式**:
```python
from cryptography.fernet import Fernet

class CryptoService:
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """加密认证信息"""
        return self.fernet.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """解密认证信息"""
        return self.fernet.decrypt(ciphertext.encode()).decode()

# 密钥管理: 从环境变量读取，不在代码中硬编码
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # 32字节base64编码
```

**密钥管理策略**:
- 密钥存储: 环境变量或Secret管理服务（如Kubernetes Secrets）
- 密钥轮换: 定期更新（建议每6个月）
- 旧密钥保留: 支持双密钥解密（过渡期）

**潜在风险**:
- 密钥泄露 → **缓解**: 严格访问控制，定期轮换，审计日志
- 性能开销 → **评估**: Fernet加密/解密约10-20μs，可接受

---

## 4. Redis缓存策略

### 决策: Redis 7.0+ 作为缓存层

**缓存用途**:
1. 代币符号映射 (Token Symbol Mapping) - FR-022
2. 代币精度信息 (Token Precision Cache) - FR-023, FR-024
3. 价格历史数据（1分钟滑动窗口） - FR-020

**缓存键命名规范**:
```
token:mapping:{symbol_short}     # 代币符号映射，如 token:mapping:KOGE
token:precision:{symbol_short}   # 代币精度，如 token:precision:KOGE
price:history:{symbol}           # 价格历史，如 price:history:ALPHA_123
```

**TTL策略**:

| 缓存类型 | TTL | 理由 |
|---------|-----|------|
| 代币符号映射 | 7天 | 映射关系稳定，很少变化 |
| 代币精度信息 | 24小时 | 符合Assumption 12，交易所精度配置稳定 |
| 价格历史 | 5分钟 | 仅保留最近1分钟窗口数据 |

**缓存失效处理**（FR-024）:
```python
async def get_token_precision(symbol: str) -> TokenPrecision:
    # 1. 尝试从缓存读取
    cached = await redis.get(f"token:precision:{symbol}")
    if cached:
        return TokenPrecision.parse_raw(cached)
    
    # 2. 缓存未命中，调用API
    precision = await binance_client.get_precision_info(symbol)
    
    # 3. 更新缓存
    await redis.setex(
        f"token:precision:{symbol}",
        86400,  # 24小时
        precision.json()
    )
    return precision
```

**Redis客户端**: `redis-py[hiredis]` (异步支持)
- 连接池配置: max_connections=50
- 超时设置: socket_timeout=5s

**潜在风险**:
- Redis不可用 → **缓解**: 降级到数据库查询，记录警告日志
- 缓存数据不一致 → **缓解**: 提供手动刷新缓存的CLI命令

---

## 5. 币安WebSocket API集成模式

### 决策: 双WebSocket连接模式

**连接策略**:
- **连接1**: 价格数据流 (`wss://nbstream.binance.com/w3w/wsa/stream`)
  - 订阅: `{symbol}@aggTrade` - 聚合成交数据
  - 用途: 实时价格更新（FR-006）
  
- **连接2**: 订单状态推送 (`wss://nbstream.binance.com/w3w/stream`)
  - 订阅: `alpha@{listenKey}` - 用户订单推送
  - 用途: 订单状态更新（FR-010, FR-011）

**ListenKey管理**:
```python
# 获取ListenKey（有效期60分钟）
listen_key = await api_client.post("/bapi/defi/v1/private/alpha-trade/get-listen-key")

# 定时续期（每30分钟）
async def keep_alive_listen_key():
    while True:
        await asyncio.sleep(1800)  # 30分钟
        await api_client.put(f"/bapi/defi/v1/private/alpha-trade/keep-alive?listenKey={listen_key}")
```

**心跳机制**:
- WebSocket Ping/Pong: 每30秒
- 检测超时: 60秒无响应视为断连

**重连策略** (指数退避):
```python
backoff_seconds = [1, 2, 4, 8, 16, 32, 60]  # 最大60秒
for delay in itertools.cycle(backoff_seconds):
    try:
        await connect_websocket()
        break  # 连接成功
    except Exception as e:
        logger.error(f"WebSocket连接失败: {e}, {delay}秒后重试")
        await asyncio.sleep(delay)
```

**符号格式转换**（FR-022, FR-026）:
```python
# 配置输入: KOGE (代币简称)
# 订单API: ALPHA_123 (通过映射表查询)
# WebSocket订阅: alpha_123usdt@aggTrade (小写格式)

def get_websocket_symbol(short_name: str) -> str:
    mapping = get_token_mapping(short_name)  # 从缓存/数据库获取
    return f"{mapping.alpha_id.lower()}usdt@aggTrade"
```

**潜在风险**:
- ListenKey过期 → **缓解**: 定时续期 + 过期检测自动刷新
- 消息丢失 → **缓解**: 连接断开时暂停交易（FR-016），不自动恢复

---

## 6. 多用户并发处理方案

### 决策: Asyncio协程 + FastAPI BackgroundTasks

**架构模式**:
```
用户A: [Trading Coroutine] → [Order State Machine] → [WebSocket Listeners]
用户B: [Trading Coroutine] → [Order State Machine] → [WebSocket Listeners]
...
用户N: [Trading Coroutine] → [Order State Machine] → [WebSocket Listeners]

共享资源:
- WebSocket连接池（按用户认证信息分组）
- Redis缓存（全局共享）
- 数据库连接池（SQLAlchemy异步引擎）
```

**并发隔离**:
- 每个用户独立的交易协程
- 用户级锁防止并发修改配置
- 数据库隔离：`WHERE user_id = ?`

**启动/停止控制**:
```python
# 用户交易任务管理
class TradingManager:
    def __init__(self):
        self.tasks: Dict[int, asyncio.Task] = {}
    
    async def start_trading(self, user_id: int):
        if user_id in self.tasks:
            raise ValueError("该用户交易已在运行")
        
        task = asyncio.create_task(trading_loop(user_id))
        self.tasks[user_id] = task
    
    async def stop_trading(self, user_id: int):
        task = self.tasks.pop(user_id, None)
        if task:
            task.cancel()
            await task  # 等待任务清理资源
```

**性能目标验证**（SC-004）:
- 10个并发用户 × 2个WebSocket连接 = 20个连接
- Python asyncio可轻松支持数千协程
- 预期CPU使用率: <30% (10用户)

**替代方案对比**:

| 方案 | 优点 | 缺点 | 选择原因 |
|------|------|------|----------|
| Asyncio协程（选择） | 轻量、共享内存、易调试 | 单进程CPU限制 | 10用户场景足够，简单高效 |
| Celery任务队列 | 分布式、可扩展 | 架构复杂，引入消息队列 | 过度设计 |
| 多进程 | CPU并行 | 内存开销大，数据共享难 | 初期无需 |

**潜在风险**:
- 单进程CPU瓶颈 → **缓解**: 初期10用户足够，未来可水平扩展多实例
- 全局异常导致所有用户停止 → **缓解**: 异常隔离，单用户异常不影响其他

---

## 7. 数据库设计和迁移

### 决策: PostgreSQL 14+ + Alembic迁移

**选择PostgreSQL理由**:
- ✅ 成熟的ACID事务支持（订单数据准确性）
- ✅ JSON类型支持（灵活存储headers/cookies）
- ✅ 丰富的索引类型（查询性能优化）
- ✅ SQLAlchemy ORM良好支持

**Alembic迁移工具**:
- 版本化数据库schema
- 自动生成迁移脚本
- 支持数据库回滚

**关键表设计预览**（详见data-model.md）:

```sql
-- 用户账户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 认证信息表（加密存储）
CREATE TABLE auth_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    headers_encrypted TEXT NOT NULL,  -- 加密后的headers JSON
    cookies_encrypted TEXT NOT NULL,  -- 加密后的cookies
    last_verified TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 代币符号映射表
CREATE TABLE token_mappings (
    id SERIAL PRIMARY KEY,
    symbol_short VARCHAR(20) UNIQUE NOT NULL,  -- KOGE
    order_api_symbol VARCHAR(50) NOT NULL,     -- ALPHA_123
    websocket_symbol VARCHAR(50) NOT NULL,     -- alpha_123usdt
    token_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 其他表见data-model.md
```

**索引策略**:
- 主键自动索引
- 用户ID外键索引
- 订单状态+用户ID复合索引（查询优化）
- 代币简称唯一索引

**潜在风险**:
- 数据库连接池耗尽 → **缓解**: 合理配置pool_size（初期20）
- 迁移失败回滚 → **缓解**: 迁移前备份，测试环境验证

---

## 8. 价格波动监控实现

### 决策: 滑动窗口算法 + Redis时序数据

**实现方案**（FR-020）:
```python
from datetime import datetime, timedelta

class PriceVolatilityMonitor:
    def __init__(self, redis_client, threshold_percent: float = 2.0):
        self.redis = redis_client
        self.threshold = threshold_percent
        self.window_size = 60  # 1分钟窗口
    
    async def check_volatility(self, symbol: str, new_price: float) -> bool:
        """检查价格波动，返回True表示超过阈值需要暂停"""
        key = f"price:history:{symbol}"
        now = datetime.utcnow().timestamp()
        
        # 添加新价格到sorted set（按时间戳排序）
        await self.redis.zadd(key, {new_price: now})
        
        # 移除1分钟之前的数据
        cutoff = now - self.window_size
        await self.redis.zremrangebyscore(key, '-inf', cutoff)
        
        # 获取1分钟内的价格范围
        prices = await self.redis.zrange(key, 0, -1)
        if len(prices) < 2:
            return False  # 数据不足，不触发
        
        prices_float = [float(p) for p in prices]
        min_price = min(prices_float)
        max_price = max(prices_float)
        
        # 计算波动百分比
        volatility = ((max_price - min_price) / min_price) * 100
        
        return volatility > self.threshold
```

**触发流程**:
1. 每次接收到新价格 → 加入滑动窗口
2. 计算窗口内最大波动
3. 超过阈值 → 触发暂停交易 + 通知用户

**性能优化**:
- Redis Sorted Set O(log N)复杂度
- 每分钟最多60个价格点
- TTL自动清理过期数据

---

## 9. 日志和可观测性

### 决策: Python `structlog` + 文件日志轮转

**结构化日志格式**:
```python
import structlog

logger = structlog.get_logger()

# 示例日志
logger.info(
    "order_placed",
    user_id=123,
    order_id="OTO_456",
    symbol="KOGE",
    side="BUY",
    price=1.23,
    quantity=100,
    timestamp=datetime.utcnow().isoformat()
)
```

**日志级别策略**:
- ERROR: 异常、错误（需要人工介入）
- WARNING: 异常暂停、认证失效、余额不足
- INFO: 订单提交、状态变更、交易完成
- DEBUG: WebSocket消息、API调用详情

**日志输出**:
- 开发环境: 控制台（彩色格式）
- 生产环境: 文件（JSON格式） + 可选的日志收集（如ELK）

**审计日志要求**（NFR-005）:
- 所有订单操作
- 配置变更
- 认证信息更新
- 异常暂停事件

---

## 10. HTTP客户端选择

### 决策: `httpx` 异步HTTP客户端

**选择理由**:
- ✅ 完整的async/await支持
- ✅ HTTP/2支持（性能提升）
- ✅ 与`requests`兼容的API
- ✅ 内置连接池和超时管理

**币安API集成**:
```python
import httpx

class BinanceHTTPClient:
    def __init__(self, headers: dict, cookies: dict):
        self.client = httpx.AsyncClient(
            base_url="https://www.binance.com",
            headers=headers,
            cookies=cookies,
            timeout=10.0,  # 10秒超时
            limits=httpx.Limits(max_connections=100)
        )
    
    async def get_user_volume(self) -> dict:
        response = await self.client.get(
            "/bapi/defi/v1/private/wallet-direct/buw/wallet/today/user-volume"
        )
        response.raise_for_status()
        return response.json()
```

**限流控制**（NFR-004）:
- 使用`aiolimiter`库
- 限制: 10 requests/second per user（初始值，根据测试调整）

---

## 研究总结

### 核心技术栈确认

| 组件 | 技术选择 | 版本 |
|------|---------|------|
| 语言 | Python | 3.11+ |
| Web框架 | FastAPI | 0.104+ |
| 数据库 | PostgreSQL | 14+ |
| ORM | SQLAlchemy | 2.0+ (async) |
| 缓存 | Redis | 7.0+ |
| WebSocket客户端 | websockets | 12.0+ |
| HTTP客户端 | httpx | 0.25+ |
| 状态机 | python-statemachine | 2.1+ |
| 加密 | cryptography (Fernet) | 41.0+ |
| 日志 | structlog | 23.2+ |
| 测试 | pytest + pytest-asyncio | 7.4+ |
| 数据库迁移 | Alembic | 1.12+ |
| 数据验证 | Pydantic | 2.5+ |

### 所有技术决策已解决

✅ 所有Phase 0研究问题已完成  
✅ 无遗留NEEDS CLARIFICATION项  
✅ 准备进入Phase 1设计阶段

---

## Phase 1预览

接下来将生成：
1. **data-model.md**: 详细数据库模型设计
2. **contracts/**: API合约定义（OpenAPI规范）
3. **quickstart.md**: 开发环境快速搭建指南

**Phase 0完成标记**: ✅ 2025-10-09

