"""
Pytest 测试配置文件

包含测试夹具、自定义标记和pytest钩子。
"""
import os
import sys
import pytest
import logging
import asyncio

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 配置pytest-asyncio
pytest_plugins = ["pytest_asyncio"]
pytestmark = pytest.mark.asyncio

# 配置日志
def pytest_configure(config):
    """配置pytest日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
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
    """自动添加异步标记"""
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio) 