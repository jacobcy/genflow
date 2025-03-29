"""
GenFlow 测试包

本包包含GenFlow项目的测试代码。
测试用例主要针对以下几个方面：
1. 模型测试 - 数据模型和业务逻辑
2. CrewAI测试 - 代理和工具功能
3. FastAPI测试 - API接口和集成测试

框架使用 pytest 作为测试框架。
"""

import os
import sys

# 确保将GenFlow项目根目录添加到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导出测试工具
try:
    from tests.test_utils import (
        mock_module,
        mock_modules,
        mock_submodules,
        patch_import
    )
except ImportError:
    from unittest.mock import MagicMock

    # 如果测试工具不可用，提供替代实现
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

    def patch_import(target, return_value=None, side_effect=None):
        mock = MagicMock()
        if return_value is not None:
            mock.return_value = return_value
        if side_effect is not None:
            mock.side_effect = side_effect
        parts = target.split('.')
        current = ''
        for i, part in enumerate(parts[:-1]):
            current = current + part if i == 0 else current + '.' + part
            if current not in sys.modules:
                sys.modules[current] = MagicMock()
        parent_module = sys.modules['.'.join(parts[:-1])]
        setattr(parent_module, parts[-1], mock)
        return mock

# 不主动导入子模块，改为由pytest自动发现
# 这样可以避免导入路径冲突

__all__ = [
    'mock_module',
    'mock_modules',
    'mock_submodules',
    'patch_import'
]

"""测试包初始化"""
