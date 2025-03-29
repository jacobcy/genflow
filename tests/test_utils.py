"""测试工具模块

提供用于测试的辅助函数和类
"""
import sys
import pytest
from typing import Dict, Any, Optional, List, Union, Callable
from unittest.mock import MagicMock


def mock_module(module_name: str, attrs: Optional[Dict[str, Any]] = None) -> MagicMock:
    """
    创建并注册一个模拟模块

    Args:
        module_name: 模块名称，如 'core.models'
        attrs: 模块属性字典，可选

    Returns:
        模拟模块对象
    """
    mock = MagicMock()

    # 如果提供了属性，设置到模拟对象上
    if attrs:
        for key, value in attrs.items():
            setattr(mock, key, value)

    # 注册模拟模块
    sys.modules[module_name] = mock
    return mock


def mock_modules(module_names: List[str]) -> Dict[str, MagicMock]:
    """
    批量创建并注册多个模拟模块

    Args:
        module_names: 模块名称列表

    Returns:
        模块名称到模拟对象的映射字典
    """
    return {name: mock_module(name) for name in module_names}


def mock_submodules(base_module: str, submodules: List[str]) -> Dict[str, MagicMock]:
    """
    批量创建并注册一个基础模块及其子模块

    Args:
        base_module: 基础模块名称，如 'core'
        submodules: 子模块名称列表，如 ['models', 'tools']

    Returns:
        模块名称到模拟对象的映射字典
    """
    result = {base_module: mock_module(base_module)}

    for sub in submodules:
        full_name = f"{base_module}.{sub}"
        result[full_name] = mock_module(full_name)

    return result


def patch_import(target: str,
                return_value: Any = None,
                side_effect: Optional[Union[Callable, Exception]] = None) -> MagicMock:
    """
    创建一个导入补丁，用于测试中替换导入

    Args:
        target: 目标导入路径，例如 'module.Class'
        return_value: 返回值，可选
        side_effect: 副作用，可选

    Returns:
        模拟对象
    """
    mock = MagicMock()

    if return_value is not None:
        mock.return_value = return_value

    if side_effect is not None:
        mock.side_effect = side_effect

    # 处理嵌套路径
    parts = target.split('.')

    # 创建并注册模块路径
    current = ''

    for i, part in enumerate(parts[:-1]):
        current = current + part if i == 0 else current + '.' + part
        if current not in sys.modules:
            sys.modules[current] = MagicMock()

    # 设置最终属性
    parent_module = sys.modules['.'.join(parts[:-1])]
    setattr(parent_module, parts[-1], mock)

    return mock
