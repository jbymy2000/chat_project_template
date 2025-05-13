# API 单元测试

本目录包含了所有 API 的单元测试，采用 pytest 框架实现。

## 文件结构

-   `test_auth_api.py` - 认证 API 测试
-   `test_topic_api.py` - 话题 API 测试
-   `test_message_api.py` - 消息 API 测试
-   `conftest.py` - pytest 配置和公共 fixture
-   `run_tests.py` - 运行测试的脚本

## 如何运行测试

### 安装依赖

首先，安装测试依赖:

```bash
pip install -r requirements-dev.txt
```

### 运行所有测试

推荐使用提供的脚本运行所有测试:

```bash
python tests/run_tests.py
```

或者直接使用 pytest:

```bash
# 从项目根目录运行
pytest --asyncio-mode=auto --cov=api tests/
```

### 运行特定测试

```bash
# 运行认证API测试
pytest tests/test_auth_api.py

# 运行话题API测试
pytest tests/test_topic_api.py

# 运行消息API测试
pytest tests/test_message_api.py
```

如果直接使用 Python 运行单个测试文件，请从项目根目录运行:

```bash
# 从项目根目录运行
python -m tests.test_auth_api
python -m tests.test_topic_api
python -m tests.test_message_api
```

### 常见问题排查

如果遇到导入错误，确保:

1. 从项目根目录运行测试
2. 使用`pytest`命令而不是直接使用`python`运行测试文件
3. 如果必须直接运行测试文件，请使用`python -m`模块方式

## 测试策略

这些测试采用以下策略:

1. **依赖注入模拟** - 使用`unittest.mock`模拟依赖的服务和组件
2. **隔离测试** - 测试单一的 API 端点，不涉及实际的数据库或外部服务
3. **异常处理测试** - 测试 API 在错误情况下的行为
4. **验证响应格式** - 确保 API 返回的数据符合预期格式

## 测试覆盖率

运行测试后，会生成覆盖率报告，显示代码覆盖率情况。可以通过以下命令查看更详细的覆盖率报告:

```bash
# 生成HTML格式的覆盖率报告
pytest --asyncio-mode=auto --cov=api --cov-report=html tests/

# 报告将生成在htmlcov目录中，可以在浏览器中打开
open htmlcov/index.html
```
