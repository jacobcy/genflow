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

### 运行选题工具测试

我们为选题团队工具（`TopicTools`）创建了专门的测试用例和运行脚本：

```bash
# 从项目根目录运行
python tests/run_topic_tools_test.py
```

这将运行选题工具的所有测试，并生成详细的日志输出。

## 测试说明

### 选题工具测试

选题工具测试验证以下功能：

1. **工具初始化**：核心工具实例是否正确初始化
2. **方法绑定**：工具方法是否正确绑定，确保不会出现`self`参数缺失错误
3. **搜索功能**：网络搜索工具是否可以正确调用
4. **趋势分析**：趋势分析工具是否可以正确调用
5. **话题潜力分析**：话题潜力分析工具是否可以正确调用

这些测试使用模拟（mock）技术替代实际依赖项，确保测试在任何环境下都能运行，不依赖网络连接或外部服务。

### 使用模拟模块

如果在测试过程中遇到依赖问题，我们提供了模拟模块（`tests/mock_tools.py`），可以替代实际的工具模块。这个模块提供了所有必要工具类的模拟版本。

## 常见问题

1. **导入错误**：如果遇到模块导入错误，请确保已正确设置PYTHONPATH
2. **依赖错误**：如果缺少依赖，请安装requirements.txt中的包
3. **网络相关错误**：默认情况下，测试使用模拟依赖，不应该有网络相关错误
