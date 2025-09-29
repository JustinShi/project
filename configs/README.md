# 验证码识别服务配置说明

## 📁 目录结构

```
configs/
├── captcha/                          # 默认配置文件
│   └── chaojiying.yaml              # 超级鹰默认配置
├── environments/                     # 环境特定配置
│   ├── development/
│   │   └── captcha/
│   │       └── chaojiying.yaml      # 开发环境配置
│   ├── testing/
│   │   └── captcha/
│   │       └── chaojiying.yaml      # 测试环境配置
│   └── production/
│       └── captcha/
│           └── chaojiying.yaml      # 生产环境配置
└── README.md                        # 本文件
```

## 🔧 配置方式

### 1. 环境变量（私密信息）

```bash
# 超级鹰配置
export CHAOJIYING_USERNAME=your_username
export CHAOJIYING_PASSWORD=your_password
export CHAOJIYING_SOFT_ID=your_soft_id

# 可选：指定配置文件路径
export CHAOJIYING_CONFIG_FILE=/path/to/custom/config.yaml
```

### 2. YAML配置文件（其他配置）

配置文件支持以下配置项：

- `timeout`: 请求超时时间（秒）
- `max_retries`: 最大重试次数
- `upload_url`: 上传识别接口URL
- `report_url`: 错误报告接口URL
- `user_agent`: 请求头User-Agent
- `default_codetype`: 默认验证码类型
- `supported_codetypes`: 支持的验证码类型
- `advanced`: 高级配置选项

## 🚀 使用方式

### 基本使用

```python
from common.captcha import ChaojiyingClient

# 使用默认配置
client = ChaojiyingClient()

# 使用特定环境配置
client = ChaojiyingClient(env="development")

# 使用自定义配置文件
client = ChaojiyingClient(config_file="custom_config.yaml")
```

### 识别验证码

```python
import asyncio

async def recognize_captcha():
    client = ChaojiyingClient(env="development")
    
    # 从文件识别
    result = await client.recognize("captcha.jpg", codetype=1902)
    
    if result:
        print(f"识别结果: {result.result}")
    else:
        print(f"识别失败: {result.error_message}")
        
        # 报告错误
        if result.extra.get("pic_id"):
            await client.report_error(result.extra["pic_id"])

# 运行
asyncio.run(recognize_captcha())
```

### 工厂函数使用

```python
from common.captcha import create_client

# 创建客户端
client = create_client("chaojiying", env="production")

# 查看支持的验证码类型
supported_types = client.get_supported_types()
print(f"支持的验证码类型: {supported_types}")
```

## 🌍 环境配置

### 开发环境 (development)
- 超时时间：10秒
- 最大重试：1次
- 详细日志：开启

### 测试环境 (testing)
- 超时时间：20秒
- 最大重试：2次
- 请求日志：开启

### 生产环境 (production)
- 超时时间：60秒
- 最大重试：5次
- 日志：简化

## 📋 支持的验证码类型

| 类型 | 描述 |
|------|------|
| 1902 | 通用数字英文验证码 |
| 1004 | 4位纯数字验证码 |
| 1005 | 5位纯数字验证码 |
| 1006 | 6位纯数字验证码 |
| 2004 | 4位纯英文验证码 |
| 3004 | 4位英文数字验证码 |
| 3005 | 5位英文数字验证码 |
| 3006 | 6位英文数字验证码 |
| 4004 | 4位纯中文验证码 |
| 5000 | 无类型验证码 |

## 🔒 安全说明

1. **私密信息**：用户名、密码、软件ID通过环境变量管理
2. **配置文件**：不包含敏感信息，可以版本控制
3. **环境隔离**：不同环境使用不同的配置和凭据
4. **权限控制**：生产环境配置文件需要适当的文件权限

## 🛠️ 部署建议

### Docker 部署

```dockerfile
# 复制配置文件
COPY configs/ /app/configs/

# 设置环境变量
ENV CHAOJIYING_USERNAME=prod_username
ENV CHAOJIYING_PASSWORD=prod_password
ENV CHAOJIYING_SOFT_ID=prod_soft_id
ENV CHAOJIYING_CONFIG_FILE=/app/configs/environments/production/captcha/chaojiying.yaml
```

### 系统服务部署

```bash
# 创建配置文件目录
sudo mkdir -p /etc/pyproject/captcha

# 复制配置文件
sudo cp configs/environments/production/captcha/chaojiying.yaml /etc/pyproject/captcha/

# 设置环境变量
export CHAOJIYING_USERNAME=prod_username
export CHAOJIYING_PASSWORD=prod_password
export CHAOJIYING_SOFT_ID=prod_soft_id
```

## 📞 支持

如有问题，请查看：
1. 配置文件格式是否正确
2. 环境变量是否设置
3. 网络连接是否正常
4. 验证码类型是否支持
