# 🧪 测试指南

本文档介绍 Python 多项目平台的测试策略、工具配置和最佳实践。

## 📋 测试策略

### 测试金字塔

```
    /\
   /  \     E2E 测试 (少量)
  /____\    
 /      \   集成测试 (适量)
/________\  单元测试 (大量)
```

### 测试类型

- **单元测试**: 测试单个函数/类
- **集成测试**: 测试模块间交互
- **端到端测试**: 测试完整业务流程
- **性能测试**: 测试系统性能指标
- **安全测试**: 测试安全漏洞

## 🛠️ 测试工具

### 核心测试框架

- **pytest**: 主要测试框架
- **pytest-asyncio**: 异步测试支持
- **pytest-cov**: 测试覆盖率
- **pytest-mock**: Mock 对象支持

### 测试数据管理

- **factory-boy**: 测试数据工厂
- **faker**: 假数据生成
- **pytest-datadir**: 测试数据文件管理

### 测试报告

- **pytest-html**: HTML 测试报告
- **pytest-xdist**: 并行测试执行
- **pytest-benchmark**: 性能基准测试

## 🚀 快速开始

### 安装测试依赖

```bash
# 安装测试工具
uv pip install pytest pytest-asyncio pytest-cov pytest-mock

# 安装测试数据工具
uv pip install factory-boy faker pytest-datadir

# 安装测试报告工具
uv pip install pytest-html pytest-xdist pytest-benchmark
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_http_client.py

# 运行特定测试函数
uv run pytest tests/test_http_client.py::test_http_client_init

# 运行标记的测试
uv run pytest -m "slow"
```

## 📝 测试编写

### 基本测试结构

```python
import pytest
from common.network.http_client import HTTPClient


class TestHTTPClient:
    """HTTP 客户端测试类"""
    
    @pytest.fixture
    def http_client(self):
        """创建 HTTP 客户端实例"""
        return HTTPClient()
    
    def test_init(self, http_client):
        """测试初始化"""
        assert http_client.base_url == ""
        assert http_client.timeout == 30
    
    @pytest.mark.asyncio
    async def test_get_request(self, http_client):
        """测试 GET 请求"""
        # 测试代码
        pass
```

### 异步测试

```python
import pytest
import aiohttp
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_async_http_request():
    """测试异步 HTTP 请求"""
    with patch('aiohttp.ClientSession') as mock_session:
        # 设置 mock
        mock_session.return_value.__aenter__.return_value = AsyncMock()
        mock_session.return_value.__aexit__.return_value = None
        
        # 测试代码
        pass
```

### 测试数据管理

```python
import pytest
from faker import Faker


@pytest.fixture
def fake():
    """Faker 实例"""
    return Faker()


@pytest.fixture
def sample_user_data(fake):
    """示例用户数据"""
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password()
    }


def test_user_creation(sample_user_data):
    """测试用户创建"""
    assert "username" in sample_user_data
    assert "email" in sample_user_data
    assert "password" in sample_user_data
```

### Mock 和 Stub

```python
import pytest
from unittest.mock import Mock, patch, MagicMock


def test_with_mock():
    """使用 Mock 测试"""
    # 创建 mock 对象
    mock_service = Mock()
    mock_service.get_data.return_value = {"key": "value"}
    
    # 使用 mock
    result = mock_service.get_data()
    assert result == {"key": "value"}
    mock_service.get_data.assert_called_once()


@patch('common.storage.redis_client.Redis')
def test_with_patch(mock_redis):
    """使用 patch 装饰器测试"""
    # mock_redis 会自动注入
    mock_redis.return_value.get.return_value = "cached_value"
    
    # 测试代码
    pass
```

## 🔧 测试配置

### pytest 配置

在 `pyproject.toml` 中配置：

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=common",
    "--cov-report=html",
    "--cov-report=term-missing"
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests"
]
asyncio_mode = "auto"
```

### 测试标记

```python
import pytest


@pytest.mark.slow
def test_slow_operation():
    """慢速操作测试"""
    pass


@pytest.mark.integration
def test_database_integration():
    """数据库集成测试"""
    pass


@pytest.mark.unit
def test_unit_function():
    """单元函数测试"""
    pass
```

## 📊 测试覆盖率

### 覆盖率配置

```toml
[tool.coverage.run]
source = ["common"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/migrations/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod"
]
```

### 生成覆盖率报告

```bash
# 生成 HTML 报告
uv run pytest --cov=common --cov-report=html

# 生成 XML 报告 (CI/CD 使用)
uv run pytest --cov=common --cov-report=xml

# 生成终端报告
uv run pytest --cov=common --cov-report=term-missing
```

## 🚨 测试最佳实践

### 测试命名

```python
# 好的命名
def test_user_creation_with_valid_data():
    """测试使用有效数据创建用户"""
    pass

def test_user_creation_fails_with_invalid_email():
    """测试使用无效邮箱创建用户失败"""
    pass

# 避免的命名
def test_1():
    """测试 1"""
    pass

def test_something():
    """测试某些东西"""
    pass
```

### 测试结构

```python
def test_function_behavior():
    """测试函数行为"""
    # Arrange (准备)
    input_data = "test"
    expected = "TEST"
    
    # Act (执行)
    result = function_to_test(input_data)
    
    # Assert (断言)
    assert result == expected
```

### 测试隔离

```python
import pytest


@pytest.fixture(autouse=True)
def setup_database():
    """每个测试前设置数据库"""
    # 设置测试数据库
    setup_test_db()
    yield
    # 测试后清理
    cleanup_test_db()


@pytest.fixture(autouse=True)
def mock_external_service():
    """每个测试前 mock 外部服务"""
    with patch('external.service.call'):
        yield
```

## 🔍 测试调试

### 调试选项

```bash
# 详细输出
uv run pytest -v

# 显示本地变量
uv run pytest -l

# 在失败时停止
uv run pytest -x

# 显示最慢的测试
uv run pytest --durations=10

# 并行执行
uv run pytest -n auto
```

### 调试特定测试

```python
import pytest


def test_debug_example():
    """调试示例"""
    # 设置断点
    breakpoint()
    
    # 或者使用 pdb
    import pdb; pdb.set_trace()
    
    # 测试代码
    pass
```

## 📈 持续集成

### GitHub Actions 配置

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      run: uv pip install -e ".[dev]"
    
    - name: Run tests
      run: uv run pytest --cov=common --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## 🎯 测试目标

### 覆盖率目标

- **单元测试**: 90%+
- **集成测试**: 80%+
- **端到端测试**: 60%+

### 性能目标

- **测试执行时间**: < 30 秒
- **内存使用**: < 500MB
- **CPU 使用**: < 80%

## 📚 下一步

- 查看 [代码质量工具](code-quality.md)
- 了解 [开发环境设置](setup.md)
- 阅读 [API 参考](../api/common.md)

## 🤝 获取帮助

如果遇到测试问题：

1. 查看 [pytest 官方文档](https://docs.pytest.org/)
2. 检查测试配置
3. 查看测试日志
4. 联系项目维护者
