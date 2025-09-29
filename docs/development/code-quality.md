# 🛠️ 代码质量工具

本指南介绍项目中使用的代码质量工具及其配置方法。

## 🎯 工具概览

| 工具 | 用途 | 配置文件 | 命令 |
|------|------|----------|------|
| **Black** | 代码格式化 | `pyproject.toml` | `make format` |
| **isort** | 导入排序 | `pyproject.toml` | `make format` |
| **flake8** | 代码风格检查 | `.flake8` | `make check-style` |
| **bandit** | 安全漏洞检查 | `pyproject.toml` | `make check-security` |
| **mypy** | 类型检查 | `pyproject.toml` | `make check-types` |
| **pre-commit** | Git 钩子 | `.pre-commit-config.yaml` | `make pre-commit-run` |

## 🚀 快速使用

### **一键运行所有检查**
```bash
# 运行完整的代码质量检查流程
make quality

# 或分步运行
make format      # 格式化代码
make lint        # 代码质量检查
make test        # 运行测试
```

### **检查代码格式（不修改）**
```bash
# 检查所有格式问题
make check-format

# 检查语法错误
make check-syntax

# 检查代码风格
make check-style

# 检查安全漏洞
make check-security

# 检查类型注解
make check-types

# 运行所有检查
make check-all
```

## 🔧 工具详细配置

### **1. Black - 代码格式化**

#### **配置 (pyproject.toml)**
```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

#### **使用示例**
```bash
# 格式化所有 Python 文件
uv run black .

# 格式化特定文件
uv run black common/network/http_client.py

# 检查格式（不修改）
uv run black --check --diff .
```

### **2. isort - 导入排序**

#### **配置 (pyproject.toml)**
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["common", "projects"]
known_third_party = ["aiohttp", "redis", "sqlalchemy"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
```

#### **使用示例**
```bash
# 排序所有导入
uv run isort .

# 排序特定文件
uv run isort common/network/http_client.py

# 检查排序（不修改）
uv run isort --check-only --diff .
```

### **3. flake8 - 代码风格检查**

#### **配置 (.flake8)**
```ini
[flake8]
max-line-length = 88
extend-ignore = 
    E203,  # whitespace before ':'
    W503,  # line break before binary operator
    E501,  # line too long (handled by black)
    F401,  # imported but unused
    F403,  # wildcard import
    F405   # name may be undefined, or defined from star imports
exclude = 
    .git,
    __pycache__,
    .venv,
    .mypy_cache,
    build,
    dist,
    *.egg-info
per-file-ignores =
    __init__.py:F401
    tests/*:F401,F403,F405
```

#### **使用示例**
```bash
# 检查代码风格
uv run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

# 检查语法错误
uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

### **4. bandit - 安全漏洞检查**

#### **配置 (pyproject.toml)**
```toml
[tool.bandit]
exclude_dirs = ["tests", ".venv", "build", "dist"]
skips = ["B101", "B601"]
```

#### **使用示例**
```bash
# 检查安全漏洞
uv run bandit -r . -f json -o bandit-report.json

# 检查特定目录
uv run bandit -r common/ -f json -o common-security-report.json

# 跳过特定检查
uv run bandit -r . -s B101,B601
```

### **5. mypy - 类型检查**

#### **配置 (pyproject.toml)**
```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "redis.*",
    "sqlalchemy.*",
    "aiohttp.*"
]
ignore_missing_imports = true
```

#### **使用示例**
```bash
# 类型检查
uv run mypy . --ignore-missing-imports --no-strict-optional

# 检查特定模块
uv run mypy common/network/ --ignore-missing-imports

# 生成类型报告
uv run mypy . --html-report mypy-report
```

## 🔄 自动化集成

### **1. pre-commit 钩子**

#### **安装钩子**
```bash
# 安装 pre-commit 钩子
make pre-commit-install

# 手动运行所有钩子
make pre-commit-run
```

#### **配置 (.pre-commit-config.yaml)**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, .]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### **2. CI/CD 集成**

#### **GitHub Actions 示例**
```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run code quality checks
        run: |
          make check-all
          make test
```

## 📊 质量报告

### **生成报告**
```bash
# 生成安全报告
make check-security

# 生成类型检查报告
uv run mypy . --html-report mypy-report

# 生成覆盖率报告
uv run pytest --cov=common --cov-report=html
```

### **查看报告**
```bash
# 查看安全报告
cat bandit-report.json | uv run python -m json.tool

# 打开 HTML 报告
start mypy-report/index.html  # Windows
open mypy-report/index.html   # macOS
xdg-open mypy-report/index.html  # Linux
```

## 🚨 常见问题

### **问题 1: Black 和 isort 冲突**
```bash
# 解决方案：先运行 isort，再运行 black
uv run isort .
uv run black .
```

### **问题 2: flake8 误报**
```bash
# 在代码中添加忽略注释
# flake8: noqa: E501
```

### **问题 3: mypy 类型错误**
```bash
# 添加类型注解
def greet(name: str) -> str:
    return f"Hello, {name}!"

# 或使用类型忽略
def legacy_function():  # type: ignore
    pass
```

### **问题 4: pre-commit 钩子失败**
```bash
# 跳过钩子（不推荐）
git commit --no-verify

# 修复问题后重新运行
make pre-commit-run
```

## 📚 最佳实践

### **1. 开发流程**
1. **编写代码** → 遵循编码规范
2. **本地检查** → `make check-all`
3. **提交代码** → pre-commit 自动检查
4. **持续集成** → CI/CD 自动检查

### **2. 代码规范**
- 使用 Black 格式化代码
- 使用 isort 排序导入
- 添加类型注解
- 编写单元测试
- 遵循 PEP 8 规范

### **3. 定期维护**
- 更新工具版本
- 检查配置文件
- 运行完整检查
- 修复发现的问题

## 🔗 相关链接

- [Black 官方文档](https://black.readthedocs.io/)
- [isort 官方文档](https://pycqa.github.io/isort/)
- [flake8 官方文档](https://flake8.pycqa.org/)
- [bandit 官方文档](https://bandit.readthedocs.io/)
- [mypy 官方文档](https://mypy.readthedocs.io/)
- [pre-commit 官方文档](https://pre-commit.com/)

---

🛠️ **开始使用** → 运行 `make help` 查看所有可用命令
