# .env 文件代理配置使用指南

## 📋 概述

现在 BinanceTools 支持通过 `.env` 文件来管理代理配置，这样更加方便和持久化。

## 🔧 配置方法

### 1. 创建 .env 文件

项目已经包含了 `env.example` 文件作为模板，你可以：

```bash
# 复制模板文件
copy env.example .env
```

### 2. 编辑 .env 文件

在 `.env` 文件中添加代理配置：

```bash
# 代理配置
# HTTP代理设置
HTTP_PROXY=http://127.0.0.1:10808
HTTPS_PROXY=http://127.0.0.1:10808

# 可选：其他代理设置
# http_proxy=http://127.0.0.1:10808
# https_proxy=http://127.0.0.1:10808
# ALL_PROXY=http://127.0.0.1:10808
# SOCKS_PROXY=socks5://127.0.0.1:10808

# 代理认证（如果需要）
# PROXY_USERNAME=your_proxy_username
# PROXY_PASSWORD=your_proxy_password
```

### 3. 加载环境变量

在运行 Python 脚本之前，先加载 `.env` 文件：

```python
from load_env import load_env_file

# 加载 .env 文件中的环境变量
load_env_file()
```

## 🚀 使用方法

### 方法1：在脚本开头加载

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# 加载 .env 文件
from load_env import load_env_file
load_env_file()

# 现在可以正常使用 BinanceTools
from BinanceTools import BinanceService, UserConfigManager

async def main():
    config_manager = UserConfigManager()
    user_config = config_manager.get_user()
    api_config = config_manager.get_api_config()
    
    service = BinanceService(user_config, api_config)
    await service.initialize()
    
    # 代理会自动从 .env 文件加载
    print(f"代理配置: {service.proxy_config}")
    
    await service.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 方法2：手动设置环境变量

```python
import os

# 手动设置代理环境变量
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10808'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10808'

# 然后正常使用 BinanceTools
```

## 🔍 支持的代理类型

### HTTP/HTTPS 代理
```bash
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=https://proxy.example.com:8080
```

### SOCKS 代理
```bash
SOCKS_PROXY=socks5://proxy.example.com:1080
# 或者
ALL_PROXY=socks5://proxy.example.com:1080
```

### 带认证的代理
```bash
HTTP_PROXY=http://username:password@proxy.example.com:8080
HTTPS_PROXY=https://username:password@proxy.example.com:8080
```

## 📊 测试验证

运行测试脚本来验证配置：

```bash
# 测试环境变量加载
uv run python load_env.py

# 测试代理功能
uv run python test_env_proxy.py
```

## 🎯 优势

1. **持久化配置**: 代理设置在 `.env` 文件中，不会因为重启而丢失
2. **版本控制友好**: `.env` 文件通常被 `.gitignore` 忽略，不会提交敏感信息
3. **环境隔离**: 不同环境可以使用不同的 `.env` 文件
4. **易于管理**: 集中管理所有环境变量配置

## ⚠️ 注意事项

1. **文件安全**: 确保 `.env` 文件不被提交到版本控制系统
2. **代理服务器**: 确保代理服务器地址和端口正确
3. **网络环境**: 在需要翻墙的环境中，代理配置特别有用
4. **性能影响**: 使用代理可能会增加请求延迟

## 🔧 故障排除

### 问题1：代理不生效
```bash
# 检查环境变量是否正确加载
uv run python load_env.py
```

### 问题2：连接超时
- 检查代理服务器是否运行
- 检查代理地址和端口是否正确
- 检查网络连接

### 问题3：认证失败
- 检查代理用户名和密码是否正确
- 确认代理服务器支持认证

## 📝 总结

通过 `.env` 文件管理代理配置是一个很好的实践，它提供了：

- ✅ 集中化的配置管理
- ✅ 环境变量的持久化
- ✅ 更好的安全性
- ✅ 易于维护和部署

现在你可以通过修改 `.env` 文件来轻松管理代理设置了！
