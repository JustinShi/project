# 📚 项目文档

欢迎使用 Python 多项目平台！本文档提供了完整的项目使用指南和开发参考。

## 🗂️ 文档结构

```
docs/
├── README.md              # 本文档 - 文档导航
├── getting-started/       # 快速开始指南
│   ├── installation.md    # 安装指南
│   ├── quickstart.md      # 快速开始
│   └── configuration.md   # 配置说明
├── development/           # 开发指南
│   ├── setup.md          # 开发环境设置
│   ├── code-quality.md   # 代码质量工具
│   └── testing.md        # 测试指南
├── api/                   # API 参考
│   ├── common.md         # 公共模块 API
│   ├── trading.md        # 交易模块 API
│   └── storage.md        # 存储模块 API
├── deployment/            # 部署指南
│   ├── docker.md         # Docker 部署
│   ├── production.md     # 生产环境部署
│   └── monitoring.md     # 监控和日志
└── examples/              # 使用示例
    ├── http-client.md    # HTTP 客户端使用
    ├── redis-usage.md    # Redis 使用示例
    └── database.md       # 数据库操作示例
```

## 🚀 快速导航

### **新用户**
- [安装指南](getting-started/installation.md) - 完整的安装步骤
- [快速开始](getting-started/quickstart.md) - 5分钟快速上手
- [配置说明](getting-started/configuration.md) - 环境配置详解

### **开发者**
- [开发环境设置](development/setup.md) - 本地开发环境配置
- [代码质量工具](development/code-quality.md) - 代码检查和格式化
- [测试指南](development/testing.md) - 单元测试和集成测试

### **API 参考**
- [公共模块](api/common.md) - 通用功能和工具
- [交易模块](api/trading.md) - 交易相关功能
- [存储模块](api/storage.md) - 数据库和缓存操作

### **部署运维**
- [Docker 部署](deployment/docker.md) - 容器化部署
- [生产环境](deployment/production.md) - 生产环境配置
- [监控日志](deployment/monitoring.md) - 系统监控和日志

### **使用示例**
- [HTTP 客户端](examples/http-client.md) - 异步 HTTP 请求
- [Redis 使用](examples/redis-usage.md) - 缓存和状态管理
- [数据库操作](examples/database.md) - MySQL/PostgreSQL 操作

## 🔧 常用命令

```bash
# 查看帮助
make help

# 安装依赖
make install

# 代码质量检查
make check-all

# 运行测试
make test

# 清理项目
make clean
```

## 📝 文档贡献

如果您发现文档有误或需要补充，请：

1. 创建 Issue 描述问题
2. 提交 Pull Request 修复
3. 联系项目维护者

## 🔗 相关链接

- [项目主页](../README.md)
- [快速开始](../QUICKSTART.md)
- [代码仓库](https://github.com/your-repo)
- [问题反馈](https://github.com/your-repo/issues)

---

📖 **开始使用** → [安装指南](getting-started/installation.md)
