# GenFlow 测试指南

本目录包含GenFlow项目的测试用例和工具。以下是运行测试的指南。

## 测试环境准备

1. 确保已安装所有依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 确保已设置Python路径，使其能够找到项目根目录：
   ```bash
   export PYTHONPATH=$PYTHONPATH:/path/to/GenFlow
   ```

## 运行测试

### 运行所有测试

使用pytest运行所有测试：
```bash
cd /path/to/GenFlow
python -m pytest tests
```

### 运行特定测试

可以运行特定测试文件：
```bash
python -m pytest tests/test_tools.py
```

也可以运行特定的测试类或测试方法：
```bash
python -m pytest tests/test_tools.py::TestContentTools
python -m pytest tests/test_tools.py::TestContentTools::test_content_collector
```


## CrewAI 版本兼容性

本项目测试已更新为支持最新版 CrewAI。使用新版 CrewAI 时，需要注意以下测试配置变更：

### 工具实现变更

1. **工具类型**：所有工具必须是 `BaseTool` 的实例
2. **方法命名**：工具必须实现 `_run` 方法（不再使用 `execute`）
3. **断言检查**：使用 `isinstance(tool, BaseTool)` 和 `hasattr(tool, "_run")` 进行验证

### Mock 配置

测试中 mock 外部服务时，需遵循以下模式：

```python
# 正确的 mock 声明
patch("core.tools.writing_tools.article_writer.ArticleWriter.generate_article",
      return_value=MagicMock(success=True, data="模拟结果"))

# 避免实例化的 mock（适用于有复杂依赖的类）
patch("core.agents.writing_crew.writing_tools.ArticleWriter",
      return_value=MagicMock(
          generate_article=MagicMock(return_value=MagicMock(success=True, data="模拟结果"))
      ))
```

### Platform 类实例化

如果测试需要使用 `Platform` 类，请按照最新的 dataclass 格式初始化：

```python
# 正确的 Platform 初始化
platform = Platform(name="测试平台", url="https://test.com")

# 不要使用不存在的参数
# 错误示例: platform = Platform(id="test", name="测试平台", url="https://test.com")
```

## 常见问题排查

1. **AttributeError**：检查工具类是否正确实现了 `_run` 方法而不是 `execute`
2. **TypeError**：检查类初始化时参数是否匹配最新定义
3. **断言失败**：确保工具实例是 `BaseTool` 的实例，并包含 `_run` 方法

## 测试验证

成功配置后，运行特定测试模块进行验证：

```bash
# 验证写作工具测试
python -m tests.test_writing_tools

# 验证 CrewAI 工具集成测试
python -m tests.test_crewai_tools
```

如需进一步协助，请参考 `test_writing_tools.py` 和 `test_crewai_tools.py` 作为最新版 CrewAI 测试的参考实现。

## 使用模拟模块

如果在测试过程中遇到依赖问题，我们提供了模拟模块（`tests/mock_tools.py`），可以替代实际的工具模块。这个模块提供了所有必要工具类的模拟版本。

## 常见问题

1. **导入错误**：如果遇到模块导入错误，请确保已正确设置PYTHONPATH
2. **依赖错误**：如果缺少依赖，请安装requirements.txt中的包
3. **网络相关错误**：默认情况下，测试使用模拟依赖，不应该有网络相关错误
