# 币安Alpha代币自动交易工具

基于DDD（领域驱动设计）架构的币安Alpha代币自动交易工具，提供完整的交易功能、风险控制和多种接口。

## 🏗️ 架构设计

本项目采用DDD架构，分为以下层次：

```
src/BinanceTools/
├── domain/                    # 领域层 (核心业务逻辑)
│   ├── entities/             # 实体
│   ├── value_objects/        # 值对象
│   ├── aggregates/           # 聚合根
│   ├── repositories/         # 仓储接口
│   ├── services/            # 领域服务
│   └── events/              # 领域事件
├── application/              # 应用层 (用例和应用服务)
│   ├── use_cases/           # 用例
│   ├── services/            # 应用服务
│   ├── dto/                 # 数据传输对象
│   └── interfaces/          # 应用接口
├── infrastructure/           # 基础设施层 (外部依赖)
│   ├── repositories/        # 仓储实现
│   ├── external_services/   # 外部服务
│   ├── config/              # 配置
│   └── adapters/            # 适配器
├── interfaces/               # 接口层 (用户接口)
│   ├── cli/                 # 命令行接口
│   ├── api/                 # REST API接口
│   └── sdk/                 # SDK接口
└── shared/                   # 共享层
    ├── exceptions/          # 异常
    ├── utils/               # 工具函数
    └── constants/           # 常量
```

## 🚀 功能特性

### 核心功能
- **钱包管理**: 查询余额、资产信息
- **订单管理**: 下单、取消、查询订单状态
- **交易历史**: 查询交易记录和统计
- **投资组合**: 持仓分析、盈亏计算
- **风险控制**: 仓位控制、风险监控

### 接口支持
- **CLI接口**: 命令行交互
- **REST API**: HTTP API服务
- **Python SDK**: 编程接口

### 技术特性
- **DDD架构**: 清晰的领域模型和业务逻辑
- **异步支持**: 基于asyncio的高性能异步处理
- **配置管理**: 灵活的配置系统
- **错误处理**: 完善的异常处理机制
- **日志记录**: 详细的日志记录
- **类型提示**: 完整的类型注解

## 📦 安装依赖

```bash
# 安装Python依赖
uv add aiohttp fastapi uvicorn click websockets pydantic

# 或者使用pip
pip install aiohttp fastapi uvicorn click websockets pydantic
```

## ⚙️ 配置

### 1. 用户配置

创建 `configs/binance/users.json` 文件：

```json
{
  "users": [
    {
      "id": "1",
      "name": "用户1",
      "enabled": true,
      "headers": {
        "authority": "www.binance.com",
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      },
      "cookies": {
        "bnc-uuid": "your-uuid-here",
        "logined": "y"
      }
    }
  ],
  "default_user": "1"
}
```

### 2. API配置

创建 `configs/binance/api_config.json` 文件：

```json
{
  "base_url": "https://www.binance.com",
  "timeout": 30,
  "retry_count": 3,
  "rate_limit": {
    "requests_per_minute": 1200,
    "requests_per_second": 20
  }
}
```

### 3. 代理配置（可选）

创建 `configs/proxy.json` 文件：

```json
{
  "enabled": false,
  "type": "http",
  "host": "",
  "port": 0,
  "username": "",
  "password": ""
}
```

## 🎯 使用方法

### 1. CLI模式

```bash
# 启动CLI
python -m BinanceTools.main cli

# 获取钱包余额
python -m BinanceTools.main cli wallet balance --user-id 1

# 下单
python -m BinanceTools.main cli order place --user-id 1 --symbol ALPHA_373USDT --side BUY --quantity 100 --price 0.23

# 取消订单
python -m BinanceTools.main cli order cancel --user-id 1 --order-id 12345

# 获取订单列表
python -m BinanceTools.main cli order list --user-id 1 --limit 10

# 获取交易历史
python -m BinanceTools.main cli trade history --user-id 1 --limit 10

# 获取投资组合摘要
python -m BinanceTools.main cli portfolio summary --user-id 1
```

### 2. API模式

```bash
# 启动API服务器
python -m BinanceTools.main api --host 0.0.0.0 --port 8000

# 访问API文档
# http://localhost:8000/docs
```

### 3. SDK模式

```python
import asyncio
from BinanceTools.interfaces.sdk.sdk_client import SdkClient
from BinanceTools.interfaces.sdk.sdk_config import SdkConfig

async def main():
    config = SdkConfig()
    async with SdkClient(config) as client:
        # 获取钱包余额
        wallet = await client.get_wallet_balance("1")
        print(f"总估值: {wallet.total_valuation} USDT")
        
        # 下单
        order = await client.place_buy_order("1", "ALPHA_373USDT", 100, 0.23)
        print(f"订单ID: {order.order_id}")

asyncio.run(main())
```

## 📚 示例代码

### SDK示例

```python
# 运行SDK示例
python src/BinanceTools/examples/sdk_example.py
```

### API示例

```python
# 运行API示例
python src/BinanceTools/examples/api_example.py
```

## 🔧 开发指南

### 项目结构

- **领域层**: 包含核心业务逻辑，不依赖外部框架
- **应用层**: 协调领域对象完成业务功能
- **基础设施层**: 实现外部依赖，如数据库、API客户端
- **接口层**: 提供用户接口，如CLI、API、SDK
- **共享层**: 提供共享组件，如异常、工具函数

### 添加新功能

1. **领域层**: 在 `domain/` 中添加实体、值对象、领域服务
2. **应用层**: 在 `application/` 中添加用例和应用服务
3. **基础设施层**: 在 `infrastructure/` 中实现外部依赖
4. **接口层**: 在 `interfaces/` 中添加用户接口

### 测试

```bash
# 运行测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_trading.py
```

## 🛡️ 风险控制

### 内置风险控制

- **仓位控制**: 限制单个代币的最大仓位比例
- **日亏损限制**: 限制每日最大亏损
- **交易量限制**: 限制每日最大交易量
- **流动性检查**: 检查市场流动性
- **集中度控制**: 控制资产集中度

### 风险配置

```python
# 在RiskService中配置风险参数
risk_service = RiskService(
    max_position_size=Decimal('0.1'),    # 最大仓位比例 10%
    max_daily_loss=Decimal('0.05'),      # 最大日亏损 5%
    max_daily_volume=Decimal('10000'),   # 最大日交易量
    min_liquidity=Decimal('100000')      # 最小流动性
)
```

## 📝 日志记录

### 日志级别

- **DEBUG**: 调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 日志配置

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('binance_tools.log'),
        logging.StreamHandler()
    ]
)
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目链接: [https://github.com/your-username/binance-tools](https://github.com/your-username/binance-tools)
- 问题反馈: [https://github.com/your-username/binance-tools/issues](https://github.com/your-username/binance-tools/issues)

## 🙏 致谢

- 感谢币安提供的API服务
- 感谢所有贡献者的支持
- 感谢DDD架构的指导

---

**⚠️ 风险提示**: 数字货币交易存在风险，请谨慎投资，本工具仅供学习和研究使用。
