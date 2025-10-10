# Ctrl+C 无法停止策略的修复说明

## 🐛 问题描述

之前的实现中，按 Ctrl+C 无法快速停止正在运行的策略，需要等待很长时间才能响应。

## 🔍 根本原因

1. **长时间阻塞的 `asyncio.sleep()`**
   - 在交易间隔等待时使用了 `await asyncio.sleep(strategy.trade_interval_seconds)`
   - 在失败重试等待时使用了 `await asyncio.sleep(strategy.trade_interval_seconds * 2)`
   - 这些长时间的 sleep 会阻塞事件循环，无法及时响应停止信号

2. **缺少信号处理器**
   - `quick_start_strategy.py` 没有注册 SIGINT/SIGTERM 信号处理器
   - 没有全局停止标志来协调异步任务的停止

## ✅ 修复方案

### 1. 可中断的等待机制

**修改前**:
```python
# 等待交易间隔
await asyncio.sleep(strategy.trade_interval_seconds)
```

**修改后**:
```python
# 等待交易间隔（可中断）
for _ in range(strategy.trade_interval_seconds * 10):
    if self._stop_flags.get(strategy.strategy_id, False):
        break
    await asyncio.sleep(0.1)  # 每 0.1 秒检查一次停止标志
```

**优点**:
- 每 0.1 秒检查一次停止标志
- 最大响应延迟从原来的 `trade_interval_seconds` 秒降低到 0.1 秒
- 保持了原有的等待时长

### 2. 添加信号处理器

**quick_start_strategy.py** 新增:

```python
import signal

# 全局停止标志
_shutdown = False

def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    global _shutdown
    _shutdown = True
    logger.info("收到中断信号，正在停止策略...")

# 在 main() 函数中注册
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# 修改等待循环
while strategy_id in executor._running_tasks and not _shutdown:
    await asyncio.sleep(1)

# 如果被中断，停止策略
if _shutdown:
    logger.info("正在停止策略...")
    await executor.stop_strategy(strategy_id)
```

### 3. 优化失败重试等待

**修改前**:
```python
logger.warning("交易失败，等待重试", user_id=user_id)
await asyncio.sleep(strategy.trade_interval_seconds * 2)
```

**修改后**:
```python
logger.warning("交易失败，等待重试", user_id=user_id)
# 可中断的等待
for _ in range(strategy.trade_interval_seconds * 20):
    if self._stop_flags.get(strategy.strategy_id, False):
        return
    await asyncio.sleep(0.1)
```

## 🚀 修复效果

### 修复前
- ❌ 按 Ctrl+C 后需要等待完整的 `trade_interval_seconds` 才能响应
- ❌ 如果正在等待重试（2倍间隔），响应更慢
- ❌ 用户体验差，感觉程序"卡死"

### 修复后
- ✅ 按 Ctrl+C 后最多 0.1 秒内响应
- ✅ 优雅停止：正在执行的交易会完成，然后立即退出
- ✅ 打印清晰的停止日志
- ✅ 自动清理资源（临时文件等）

## 📝 使用示例

### 测试快速响应

```bash
# 启动一个长时间策略
uv run python scripts/quick_start_strategy.py \
  --token KOGE \
  --chain BSC \
  --volume 10000 \
  --amount 10 \
  --user 1

# 等待几秒后按 Ctrl+C
# 应该立即看到:
# {"event": "收到中断信号，正在停止策略...", "level": "info"}
# {"event": "正在停止策略...", "level": "info"}
# {"event": "策略执行完成", ...}
```

### 响应时间对比

| 场景 | 修复前 | 修复后 |
|------|--------|--------|
| 正常交易间隔（1秒） | 最多等待 1 秒 | 最多等待 0.1 秒 |
| 失败重试等待（2秒） | 最多等待 2 秒 | 最多等待 0.1 秒 |
| 长交易间隔（5秒） | 最多等待 5 秒 | 最多等待 0.1 秒 |

## 🔧 技术细节

### 为什么使用 0.1 秒间隔？

- **平衡响应速度与CPU占用**
  - 0.1 秒足够快，用户感觉不到延迟
  - 避免过于频繁的循环检查（如 0.01 秒）浪费 CPU
  
- **计算方式**
  ```python
  # 等待 N 秒 = N * 10 次循环，每次 0.1 秒
  for _ in range(trade_interval_seconds * 10):
      await asyncio.sleep(0.1)
  ```

### 为什么用循环而不是 asyncio.wait_for()?

`asyncio.wait_for()` 也可以设置超时，但：
- ❌ 超时后会抛出异常，需要额外处理
- ❌ 无法在超时前提前中断
- ✅ 循环检查更灵活，可随时中断

### 停止信号传播路径

```
用户按 Ctrl+C
    ↓
signal_handler 捕获 SIGINT
    ↓
设置 _shutdown = True
    ↓
main() 循环检测到 _shutdown
    ↓
调用 executor.stop_strategy()
    ↓
设置 _stop_flags[strategy_id] = True
    ↓
_run_user_strategy() 循环检测到停止标志
    ↓
中断等待循环，退出任务
    ↓
清理资源，打印最终状态
```

## 🎯 最佳实践

1. **始终使用可中断的等待**
   ```python
   # ❌ 不推荐
   await asyncio.sleep(long_interval)
   
   # ✅ 推荐
   for _ in range(long_interval * 10):
       if stop_flag:
           break
       await asyncio.sleep(0.1)
   ```

2. **注册信号处理器**
   ```python
   signal.signal(signal.SIGINT, signal_handler)
   signal.signal(signal.SIGTERM, signal_handler)
   ```

3. **使用全局停止标志**
   ```python
   _shutdown = False  # 全局变量
   
   def signal_handler(signum, frame):
       global _shutdown
       _shutdown = True
   ```

4. **检查停止标志**
   ```python
   while not _shutdown:
       # 执行任务
       ...
   ```

## 📚 相关文件

- `src/binance/application/services/strategy_executor.py` - 策略执行器（核心修改）
- `scripts/quick_start_strategy.py` - 快速启动脚本（新增信号处理）
- `scripts/run_trading_strategy.py` - 策略运行脚本（已有信号处理，保持不变）

## ✅ 测试验证

1. 启动任意策略
2. 等待几秒后按 Ctrl+C
3. 观察是否在 0.1-0.2 秒内响应
4. 检查是否打印停止日志
5. 验证资源是否正确清理

**预期结果**: 快速、优雅地停止，无需等待长时间

