"""
Pytest 测试配置文件

包含测试夹具、自定义标记和pytest钩子。
该文件为所有测试提供全局配置。
"""
import os
import sys
import pytest
import logging
import asyncio
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock
from pytest_asyncio.plugin import Mode

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 添加各个测试子目录到路径
test_dir = Path(__file__).parent
for subdir in ['models', 'crewai', 'fastapi']:
    subdir_path = str(test_dir / subdir)
    if subdir_path not in sys.path:
        sys.path.insert(0, subdir_path)

# 导入测试工具
try:
    from tests.test_utils import mock_module, mock_modules, mock_submodules
except ImportError:
    # 如果测试工具模块不可用，提供简单的替代实现
    def mock_module(module_name, attrs=None):
        mock = MagicMock()
        if attrs:
            for key, value in attrs.items():
                setattr(mock, key, value)
        sys.modules[module_name] = mock
        return mock

    def mock_modules(module_names):
        return {name: mock_module(name) for name in module_names}

    def mock_submodules(base_module, submodules):
        result = {base_module: mock_module(base_module)}
        for sub in submodules:
            full_name = f"{base_module}.{sub}"
            result[full_name] = mock_module(full_name)
        return result

# === 全局模块模拟 ===
# 为了避免导入错误，这里模拟所有可能需要的模块

# 1. 核心依赖模块
core_deps = [
    'config_service',
    'db_adapter',
    'redis',
    'enums',
    'json_loader',
    'langsmith',
    'langchain',
    'crewai'
]
mock_modules(core_deps)

# 2. 核心模块及其子模块
core_modules = mock_submodules('core', [
    'models', 'tools', 'agents', 'config', 'controllers'
])

# 3. 更深层次的子模块
submodules_map = {
    'core.models': ['infra', 'platform', 'topic', 'style', 'article'],
    'core.tools': ['content_collectors', 'style_tools', 'research_tools', 'topic_tools'],
    'core.agents': ['research_crew'],
    'langchain': ['agents', 'tools'],
    'crewai': ['agent', 'crew', 'task', 'tools']
}

for parent, subs in submodules_map.items():
    mock_submodules(parent, subs)

# 4. 特定的深层嵌套模块
deep_modules = [
    'core.models.infra.enums',
    'core.models.infra.db_adapter',
    'core.models.platform.platform',
    'core.tools.style_tools.adapter',
    'core.tools.content_collectors',
    'core.agents.research_crew.research_tools',
    'core.agents.research_crew.research_agents',
    'core.agents.research_crew.research_crew'
]

for module_name in deep_modules:
    mock_module(module_name)

# 5. 模拟特定的类
class_modules = {
    'core.models.platform.platform.Platform': MagicMock(),
    'core.tools.style_tools.adapter.StyleAdapter': MagicMock(),
    'core.tools.content_collectors.ContentCollector': MagicMock(),
    'core.agents.research_crew.research_tools.ResearchTools': MagicMock(),
    'core.agents.research_crew.research_agents.ResearchAgents': MagicMock()
}

for class_path, mock_obj in class_modules.items():
    parts = class_path.split('.')
    module_path = '.'.join(parts[:-1])
    class_name = parts[-1]

    # 确保模块存在
    if module_path not in sys.modules:
        sys.modules[module_path] = MagicMock()

    # 设置类对象
    setattr(sys.modules[module_path], class_name, mock_obj)

# 配置pytest-asyncio
pytest_plugins = ["pytest_asyncio"]
pytest_asyncio_mode = Mode.AUTO
pytestmark = pytest.mark.asyncio

# 配置日志
def pytest_configure(config):
    """配置pytest日志"""
    # 确保logs目录存在
    logs_dir = os.path.join(test_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, 'test.log')),
            logging.StreamHandler()
        ]
    )

    # 设置pytest-asyncio模式
    config.option.asyncio_mode = "auto"

@pytest.fixture(scope="session")
def event_loop():
    """创建一个事件循环，供所有测试使用"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_logging(caplog):
    """设置日志捕获"""
    caplog.set_level(logging.INFO)

# 添加pytest异步标记
def pytest_collection_modifyitems(items):
    """自动添加异步标记，并对测试项进行排序"""
    # 1. 先添加异步标记
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)

    # 2. 对测试按以下优先级排序：
    # - 独立测试优先（standalone）
    # - 模型测试其次
    # - crewai和fastapi测试最后
    standalone_tests = []
    model_tests = []
    other_tests = []

    for item in items:
        if 'standalone' in item.nodeid:
            standalone_tests.append(item)
        elif '/models/' in item.nodeid:
            model_tests.append(item)
        else:
            other_tests.append(item)

    items[:] = standalone_tests + model_tests + other_tests

def pytest_ignore_collect(collection_path: Path):
    """配置忽略收集的路径"""
    # 忽略非测试文件和特定目录
    str_path = str(collection_path)
    if "__pycache__" in str_path:
        return True
    if ".DS_Store" in str_path:
        return True
    return False
