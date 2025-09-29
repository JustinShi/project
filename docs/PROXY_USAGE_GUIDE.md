# BinanceTools 代理功能使用指南

## 📋 概述

BinanceTools 现在完全支持代理功能，包括 HTTP、HTTPS 和 SOCKS 代理。代理配置可以通过多种方式设置，包括环境变量、配置文件和代码配置。

## 🔧 代理配置方式

### 1. 环境变量配置（推荐）

设置以下环境变量来启用代理：

```bash
# HTTP/HTTPS 代理
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=https://proxy.example.com:8080

# 或者使用小写
export http_proxy=http://proxy.example.com:8080
export https_proxy=https://proxy.example.com:8080

# 通用代理（适用于所有协议）
export ALL_PROXY=http://proxy.example.com:8080

# SOCKS 代理
export SOCKS_PROXY=socks5://socks.example.com:1080

# 代理认证（可选）
export PROXY_USER=your_username
export PROXY_PASS=your_password
```

### 2. 配置文件设置

在 `configs/binance/api_config.json` 中添加代理配置：

```json
{
  "api_config": {
    "base_url": "https://www.binance.com",
    "timeout": 30,
    "retry_times": 3,
    "endpoints": {
      "user_volume": "/bapi/defi/v1/private/wallet-direct/buw/wallet/today/user-volume",
      "wallet_balance": "/bapi/defi/v1/private/wallet-direct/cloud-wallet/alpha",
      "place_oto_order": "/bapi/defi/v1/private/alpha-trade/oto-order/place",
      "get_listen_key": "/bapi/defi/v1/private/alpha-trade/stream/get-listen-key"
    }
  },
  "websocket_config": {
    "stream_url": "wss://nbstream.binance.com/w3w/wsa/stream",
    "order_stream_url": "wss://nbstream.binance.com/w3w/stream",
    "ping_interval": 30,
    "reconnect_interval": 5,
    "max_reconnect_attempts": 10
  },
  "proxy_config": {
    "enabled": true,
    "http": "http://proxy.example.com:8080",
    "https": "https://proxy.example.com:8080",
    "socks4": null,
    "socks5": "socks5://socks.example.com:1080",
    "username": "your_username",
    "password": "your_password"
  }
}
```

### 3. 代码配置

```python
from BinanceTools import BinanceService, UserConfigManager, ProxyConfig

# 创建代理配置
proxy_config = ProxyConfig(
    http="http://proxy.example.com:8080",
    https="https://proxy.example.com:8080",
    socks5="socks5://socks.example.com:1080",
    username="your_username",
    password="your_password",
    enabled=True
)

# 获取其他配置
config_manager = UserConfigManager()
user_config = config_manager.get_user()
api_config = config_manager.get_api_config()

# 创建服务（使用代理配置）
service = BinanceService(user_config, api_config, proxy_config=proxy_config)

# 初始化并使用
await service.initialize()
balance = await service.get_wallet_balance()
await service.disconnect()
```

## 🌐 支持的代理类型

### HTTP/HTTPS 代理
- 支持基本的 HTTP 和 HTTPS 代理
- 自动根据目标 URL 选择对应的代理
- 支持代理认证

### SOCKS 代理
- 支持 SOCKS4 和 SOCKS5 代理
- 需要安装 `aiohttp-socks` 包：
  ```bash
  pip install aiohttp-socks
  ```

## 📖 使用示例

### 基础代理使用

```python
import asyncio
from BinanceTools import BinanceService, UserConfigManager

async def main():
    # 获取配置
    config_manager = UserConfigManager()
    user_config = config_manager.get_user()
    api_config = config_manager.get_api_config()
    
    # 创建服务（会自动检测环境变量中的代理设置）
    service = BinanceService(user_config, api_config)
    
    try:
        # 初始化服务
        await service.initialize()
        
        # 获取钱包余额（通过代理）
        balance = await service.get_wallet_balance()
        print(f"钱包余额: {balance}")
        
    finally:
        await service.disconnect()

# 运行
asyncio.run(main())
```

### 多用户代理使用

```python
import asyncio
from BinanceTools import MultiUserBinanceService, ProxyConfig

async def main():
    # 创建代理配置
    proxy_config = ProxyConfig(
        http="http://proxy.example.com:8080",
        enabled=True
    )
    
    # 创建多用户服务
    multi_service = MultiUserBinanceService()
    
    try:
        # 初始化服务
        await multi_service.initialize()
        
        # 为所有用户服务设置代理
        for user_id, service in multi_service._user_services.items():
            service.proxy_config = proxy_config
        
        # 获取所有用户的钱包余额（通过代理）
        balance_results = await multi_service.get_all_wallet_balances()
        
        for result in balance_results:
            if result.success:
                print(f"用户 {result.user_id}: 余额查询成功")
            else:
                print(f"用户 {result.user_id}: 余额查询失败 - {result.error}")
        
    finally:
        await multi_service.disconnect_all()

# 运行
asyncio.run(main())
```

## 🔍 代理检测和调试

### 检查代理配置

```python
from BinanceTools import UserConfigManager

# 获取配置管理器
config_manager = UserConfigManager()

# 检查代理配置
proxy_config = config_manager.get_proxy_config()
if proxy_config and proxy_config.enabled:
    print(f"代理已启用:")
    print(f"  HTTP: {proxy_config.http}")
    print(f"  HTTPS: {proxy_config.https}")
    print(f"  SOCKS4: {proxy_config.socks4}")
    print(f"  SOCKS5: {proxy_config.socks5}")
else:
    print("未配置代理")
```

### 环境变量检测

```python
import os
from BinanceTools.infrastructure.http_client import BinanceHttpClient
from BinanceTools.config import UserConfig, ApiConfig

# 创建测试配置
user_config = UserConfig(
    id="test",
    name="测试用户",
    enabled=True,
    headers={"User-Agent": "Test"},
    cookies={"test": "cookie"}
)

api_config = ApiConfig(
    base_url="https://httpbin.org",
    timeout=10,
    retry_times=1
)

# 创建HTTP客户端（会自动检测环境变量中的代理）
client = BinanceHttpClient(user_config, api_config)

if client.proxy_config and client.proxy_config.enabled:
    print("检测到代理配置:")
    print(f"  HTTP: {client.proxy_config.http}")
    print(f"  HTTPS: {client.proxy_config.https}")
    print(f"  SOCKS4: {client.proxy_config.socks4}")
    print(f"  SOCKS5: {client.proxy_config.socks5}")
else:
    print("未检测到代理配置")
```

## ⚠️ 注意事项

### 1. 代理优先级
代理配置的优先级从高到低：
1. 代码中直接传入的 `ProxyConfig`
2. 配置文件中的 `proxy_config`
3. 环境变量中的代理设置

### 2. SOCKS 代理依赖
使用 SOCKS 代理需要安装额外的依赖：
```bash
pip install aiohttp-socks
```

### 3. 代理认证
如果代理需要认证，可以通过以下方式设置：
- 环境变量：`PROXY_USER` 和 `PROXY_PASS`
- 配置文件：`username` 和 `password` 字段
- 代码配置：`ProxyConfig` 的 `username` 和 `password` 参数

### 4. 代理URL格式
- HTTP: `http://proxy.example.com:8080`
- HTTPS: `https://proxy.example.com:8080`
- SOCKS4: `socks4://socks.example.com:1080`
- SOCKS5: `socks5://socks.example.com:1080`
- 带认证: `http://username:password@proxy.example.com:8080`

## 🚀 最佳实践

1. **使用环境变量**：推荐使用环境变量设置代理，这样可以在不同环境中灵活切换
2. **测试连接**：在正式使用前，先用简单的测试验证代理连接是否正常
3. **错误处理**：代理连接失败时，库会自动重试，但建议添加适当的错误处理
4. **日志监控**：启用日志记录来监控代理连接状态

## 🔧 故障排除

### 常见问题

1. **代理连接失败**
   - 检查代理服务器地址和端口是否正确
   - 确认代理服务器是否支持目标协议
   - 检查网络连接和防火墙设置

2. **SOCKS 代理不可用**
   - 确认已安装 `aiohttp-socks` 包
   - 检查 SOCKS 代理服务器是否正常运行

3. **认证失败**
   - 验证用户名和密码是否正确
   - 检查代理服务器是否支持认证

### 调试技巧

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

# 查看代理配置
from BinanceTools import UserConfigManager
config_manager = UserConfigManager()
proxy_config = config_manager.get_proxy_config()
print(f"代理配置: {proxy_config}")
```

通过以上配置和使用方法，您可以在任何网络环境中使用 BinanceTools，包括需要通过代理访问 Binance API 的情况。
