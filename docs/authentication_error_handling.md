# 认证失败处理机制

## 📋 概述

系统现在能够优雅地处理用户认证失败错误。当出现 "补充认证失败" 等错误时，系统会：
1. ✅ 停止当前用户的交易
2. ✅ 记录详细的错误日志
3. ✅ 提示更新凭证的命令
4. ✅ 不影响其他用户的交易

## 🔧 实现细节

### 1. 自定义异常

```python
class AuthenticationError(Exception):
    """认证失败异常"""
    pass
```

### 2. 认证错误检测

系统会自动检测以下错误消息：
- "补充认证失败"
- "您必须完成此认证才能进入下一步"
- "authentication failed"
- "unauthorized"
- "invalid credentials"
- "token expired"
- "session expired"

### 3. 错误处理流程

```
下单失败
  ↓
检测错误消息
  ↓
如果是认证失败 → 抛出 AuthenticationError
  ↓
上层捕获异常
  ↓
记录错误日志 + 提示更新凭证
  ↓
优雅退出当前用户交易
  ↓
清理 WebSocket 连接
  ↓
策略继续（如有其他用户）
```

## 🎯 使用示例

### 场景 1：单用户认证失败

```yaml
strategies:
  - strategy_id: "test_strategy"
    user_ids: [1]  # 用户 1 凭证过期
```

**执行结果：**
```
🚨 用户认证失败，停止交易
   user_id: 1
   error: "用户 1 认证失败，需要更新凭证"

⚠️  请运行以下命令更新凭证：
   command: uv run python scripts/update_user_credentials_quick.py

✅ 用户策略完成（user_id: 1）
✅ 策略执行完成
```

### 场景 2：多用户部分失败

```yaml
strategies:
  - strategy_id: "multi_user_strategy"
    user_ids: [1, 2, 3]  # 用户 1 凭证过期
```

**执行结果：**
```
🚨 用户 1 认证失败，停止交易
✅ 用户 2 交易正常
✅ 用户 3 交易正常
```

## 📝 更新凭证步骤

当看到认证失败提示后：

### 1. 运行更新工具
```bash
uv run python scripts/update_user_credentials_quick.py
```

### 2. 从移动端抓包获取新凭证
- 使用抓包工具（Charles、Proxyman等）
- 捕获币安 App 的请求
- 提取 headers（JSON格式）和 cookies

### 3. 输入新凭证
```
请输入 headers (JSON 格式，一行):
> {"csrftoken": "xxx", ...}

请输入 cookies:
> lang=zh-CN; sessionid=xxx; ...
```

### 4. 确认更新
```
确认更新用户 1 的凭证？(y/n): y

✅ 用户 1 凭证更新成功！
```

### 5. 重新运行策略
```bash
uv run python scripts/run_trading_strategy.py --strategy test_strategy
```

## 🔍 日志示例

### 认证失败日志

```json
{
  "event": "认证失败：用户凭证已过期",
  "level": "error",
  "user_id": 1,
  "strategy_id": "test_strategy",
  "message": "补充认证失败，您必须完成此认证才能进入下一步",
  "action": "停止当前用户交易，请更新凭证"
}

{
  "event": "🚨 用户认证失败，停止交易",
  "level": "error",
  "user_id": 1,
  "strategy_id": "test_strategy",
  "error": "用户 1 认证失败，需要更新凭证"
}

{
  "event": "⚠️  请运行以下命令更新凭证：",
  "level": "error",
  "command": "uv run python scripts/update_user_credentials_quick.py"
}
```

## ✅ 优势

1. **不中断整体流程** - 单个用户失败不影响其他用户
2. **明确的提示** - 清楚地告诉用户如何解决问题
3. **优雅退出** - 正确清理资源（WebSocket等）
4. **便于调试** - 详细的日志记录
5. **可重试** - 更新凭证后可以立即重新运行

## 🚨 注意事项

1. **定期检查凭证** - 建议每周检查一次凭证是否有效
2. **及时更新** - 看到认证失败提示后应立即更新
3. **保存凭证** - 建议保存一份最新的凭证备份（注意安全）
4. **测试验证** - 更新凭证后先小量测试，确认有效再大规模运行

