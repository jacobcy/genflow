# GenFlow 测试架构

本目录包含 GenFlow 项目的测试代码。测试使用 pytest 框架，按照功能模块组织为三个主要测试包。

## 目录结构

```
tests/
├── conftest.py         # 全局测试配置
├── __init__.py         # 测试包初始化
├── README.md           # 测试说明文档
├── models/             # 数据模型和业务逻辑测试
│   ├── conftest.py     # 模型测试特定配置
│   ├── __init__.py
│   ├── test_article.py # 文章模型测试
│   ├── test_standalone_model.py # 独立模型测试（无外部依赖）
│   └── ...
├── crewai/             # CrewAI 代理和工具测试
│   ├── conftest.py     # CrewAI测试特定配置
│   ├── __init__.py
│   ├── test_research_agents.py
│   └── ...
└── fastapi/            # API 接口测试
    ├── conftest.py     # FastAPI测试特定配置
    ├── __init__.py
    ├── test_fastapi_basic.py # 基本FastAPI测试
    └── ...
```

## 测试分类

1. **模型测试 (models)**: 测试核心数据模型、业务逻辑和数据层
   - 文章、话题、研究等基础模型
   - 内容管理器和数据存储
   - 状态转换和业务规则

2. **CrewAI 测试 (crewai)**: 测试 AI 代理和工具功能
   - 代理创建和执行
   - 工具链功能测试
   - 团队协作流程

3. **FastAPI 测试 (fastapi)**: 测试 API 接口和集成功能
   - API 路由和请求处理
   - 中间件和异常处理
   - 端到端集成测试

## 测试方式

### 两种测试方式

项目支持两种测试方式：

1. **独立测试** - 不依赖外部模块和项目代码，主要用于验证基本功能和测试框架
   - `test_standalone_model.py` - 独立的Pydantic模型测试
   - `test_fastapi_basic.py` - 独立的FastAPI基础测试

2. **集成测试** - 依赖项目代码，但使用模拟对象替代外部服务
   - 依赖模块通过`sys.modules`在`conftest.py`中进行模拟
   - 各个测试子目录的`conftest.py`文件提供特定于该模块的模拟对象

### 依赖项模拟

测试中使用以下方式模拟依赖项：

```python
# 在conftest.py中模拟依赖模块
import sys
from unittest.mock import MagicMock

# 模拟模块
sys.modules['config_service'] = MagicMock()

# 模拟类或函数
mock_class = MagicMock()
sys.modules['module_name.class_name'] = mock_class

# 在测试中使用夹具
@pytest.fixture
def mock_service():
    service = MagicMock()
    service.method.return_value = "mocked_result"
    return service
```

## 运行测试

### 运行全部测试

```bash
pytest
```

### 运行特定测试模块

```bash
# 运行模型测试
pytest tests/models/

# 运行 CrewAI 测试
pytest tests/crewai/

# 运行特定测试文件
pytest tests/models/test_article.py

# 运行独立测试
pytest tests/models/test_standalone_model.py tests/fastapi/test_fastapi_basic.py
```

### 测试标记

可以使用标记选择特定类型的测试：

```bash
# 运行异步测试
pytest -m asyncio

# 运行特定标记的测试
pytest -m "not slow"
```

## 测试配置

全局测试配置在 `conftest.py` 中定义，包括：

1. 路径设置和导入配置
2. 日志配置
3. 全局夹具 (fixtures)
4. 异步支持

每个子模块可以有自己的 `conftest.py` 文件，用于定义特定于该模块的配置和夹具。

## 最佳实践

1. **测试隔离**: 测试应该相互独立，不依赖于其他测试的执行顺序或状态
2. **模拟外部依赖**: 使用 unittest.mock 模拟外部服务和依赖
3. **清晰的测试名称**: 测试函数名称应清晰描述测试内容
4. **覆盖边界情况**: 测试应覆盖正常流程和异常情况
5. **保持测试简单**: 每个测试应专注于单个功能点
6. **编写独立测试**: 尽可能编写不依赖项目代码的独立测试
