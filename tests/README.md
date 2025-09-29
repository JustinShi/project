# BinanceTools 测试文档

## 📋 测试概览

本测试套件为BinanceTools提供了全面的单元测试和集成测试，确保代码质量和功能正确性。

## 🏗️ 测试结构

```
tests/
├── __init__.py              # 测试模块初始化
├── conftest.py              # 测试配置和fixtures
├── test_config.py           # 配置管理模块测试
├── test_http_client.py      # HTTP客户端测试
├── test_binance_api.py      # API接口测试
├── test_utils.py            # 工具函数测试
├── test_multi_user_service.py # 多用户服务测试
├── test_example.py          # 测试示例
├── test_runner.py           # 测试运行器
└── README.md                # 测试文档
```

## 🧪 测试类型

### 1. 单元测试 (Unit Tests)
- **配置管理测试**: 测试用户配置和API配置的加载、解析、验证
- **HTTP客户端测试**: 测试HTTP请求、响应处理、错误处理、重试机制
- **API接口测试**: 测试各个API接口的调用、数据解析、错误处理
- **工具函数测试**: 测试格式化函数、安全转换函数、验证函数
- **多用户服务测试**: 测试多用户管理、并发操作、错误处理

### 2. 集成测试 (Integration Tests)
- **端到端测试**: 测试完整的业务流程
- **多用户集成测试**: 测试多用户并发操作
- **WebSocket集成测试**: 测试实时数据推送

## 🚀 运行测试

### 基础测试命令

```bash
# 运行所有测试
make test

# 运行单元测试
make test-unit

# 运行集成测试
make test-integration

# 运行快速测试（跳过慢速测试）
make test-fast

# 运行测试并生成覆盖率报告
make test-coverage

# 运行所有测试和覆盖率检查
make test-all
```

### 详细测试命令

```bash
# 使用pytest直接运行
uv run pytest tests/ -v

# 运行特定测试文件
uv run pytest tests/test_config.py -v

# 运行特定测试类
uv run pytest tests/test_config.py::TestUserConfigManager -v

# 运行特定测试方法
uv run pytest tests/test_config.py::TestUserConfigManager::test_load_config_success -v

# 运行带标记的测试
uv run pytest tests/ -m "unit" -v

# 生成详细报告
uv run pytest tests/ --tb=long -v
```

## 📊 测试覆盖率

运行测试覆盖率检查：

```bash
make test-coverage
```

这将在 `htmlcov/` 目录生成HTML覆盖率报告，在终端显示覆盖率统计。

## 🔧 测试配置

### pytest.ini 配置

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = -v --tb=short --strict-markers --disable-warnings --color=yes
asyncio_mode = auto
```

### 测试标记

- `unit`: 单元测试
- `integration`: 集成测试  
- `slow`: 慢速测试
- `network`: 需要网络的测试

## 📝 编写测试

### 测试文件命名

- 测试文件以 `test_` 开头
- 测试类以 `Test` 开头
- 测试方法以 `test_` 开头

### 测试结构示例

```python
class TestExampleClass:
    """测试类文档"""
    
    def test_basic_functionality(self):
        """测试基本功能"""
        # Arrange (准备)
        input_data = "test"
        
        # Act (执行)
        result = some_function(input_data)
        
        # Assert (断言)
        assert result == "expected"
    
    @pytest.mark.asyncio
    async def test_async_function(self):
        """测试异步函数"""
        result = await async_function()
        assert result is not None
```

### 使用Fixtures

```python
def test_with_fixture(sample_user_config):
    """使用fixture进行测试"""
    assert sample_user_config.id == "test_user_001"
```

## 🐛 调试测试

### 运行单个测试

```bash
# 运行特定测试并进入调试模式
uv run pytest tests/test_config.py::TestUserConfigManager::test_load_config_success -v -s --pdb
```

### 查看详细输出

```bash
# 显示所有输出
uv run pytest tests/ -v -s

# 显示最详细的traceback
uv run pytest tests/ --tb=long -v
```

## 📈 测试最佳实践

### 1. 测试隔离
- 每个测试应该独立运行
- 使用fixtures提供测试数据
- 避免测试之间的依赖

### 2. 测试命名
- 使用描述性的测试名称
- 说明测试的场景和期望结果

### 3. 测试覆盖
- 测试正常流程
- 测试异常情况
- 测试边界条件

### 4. 异步测试
- 使用 `@pytest.mark.asyncio` 标记异步测试
- 使用 `AsyncMock` 模拟异步对象

### 5. 模拟外部依赖
- 使用 `unittest.mock` 模拟外部服务
- 避免真实的网络请求
- 使用fixtures提供测试数据

## 🔍 故障排除

### 常见问题

1. **导入错误**: 确保项目根目录在Python路径中
2. **异步测试失败**: 确保安装了 `pytest-asyncio`
3. **模拟不工作**: 检查模拟对象的路径和方法名

### 调试技巧

1. 使用 `print()` 语句输出调试信息
2. 使用 `pytest.set_trace()` 设置断点
3. 使用 `--pdb` 参数进入调试模式

## 📚 测试资源

- [pytest文档](https://docs.pytest.org/)
- [pytest-asyncio文档](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock文档](https://docs.python.org/3/library/unittest.mock.html)

## 🎯 测试目标

- **覆盖率**: 目标达到90%以上的代码覆盖率
- **质量**: 确保所有核心功能都有测试覆盖
- **性能**: 测试套件应该在合理时间内完成
- **可维护性**: 测试代码应该清晰、易于理解和维护
