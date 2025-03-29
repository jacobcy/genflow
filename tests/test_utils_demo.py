"""测试工具使用示例

展示如何使用 tests.test_utils 中的测试辅助函数
"""
import pytest
from tests.test_utils import mock_module, mock_modules, mock_submodules, patch_import


# 测试 mock_module 函数
def test_mock_module():
    """测试创建单个模拟模块"""
    # 创建一个模拟模块
    mock = mock_module('demo.module', {'CONSTANT': 42, 'function': lambda: 'result'})

    # 从模拟的模块中导入
    from demo.module import CONSTANT, function

    # 验证模拟是否成功
    assert CONSTANT == 42
    assert function() == 'result'
    assert mock.CONSTANT == 42


# 测试 mock_modules 函数
def test_mock_modules():
    """测试批量创建模拟模块"""
    # 批量创建模拟模块
    mocks = mock_modules(['demo.module1', 'demo.module2'])

    # 设置模拟属性
    mocks['demo.module1'].attr1 = 'value1'
    mocks['demo.module2'].attr2 = 'value2'

    # 验证模拟是否成功
    from demo.module1 import attr1
    from demo.module2 import attr2

    assert attr1 == 'value1'
    assert attr2 == 'value2'


# 测试 mock_submodules 函数
def test_mock_submodules():
    """测试创建基础模块及其子模块"""
    # 创建基础模块及其子模块
    mocks = mock_submodules('app', ['config', 'models', 'controllers'])

    # 设置模拟属性
    mocks['app.config'].DEBUG = True
    mocks['app.models'].User = lambda: None
    mocks['app.controllers'].auth = lambda: 'Authenticated'

    # 验证模拟是否成功
    from app.config import DEBUG
    from app.models import User
    from app.controllers import auth

    assert DEBUG is True
    assert User() is None
    assert auth() == 'Authenticated'


# 测试 patch_import 函数
def test_patch_import():
    """测试导入补丁"""
    # 创建一个导入补丁
    mock_class = patch_import('database.connection.Connection', return_value='Connected')

    # 导入被补丁的模块
    from database.connection import Connection

    # 验证模拟是否成功
    assert Connection() == 'Connected'
    assert mock_class.called


# 实际使用场景：模拟依赖的模块
def test_real_world_example():
    """展示实际使用场景"""
    # 模拟一个复杂的依赖关系
    db_mock = mock_module('database')
    db_mock.connect.return_value = {'status': 'connected', 'version': '1.0'}

    # 模拟异常情况
    requests_mock = mock_module('requests')
    requests_mock.get.side_effect = Exception("Network error")

    # 模拟嵌套模块
    auth_mock = mock_module('auth')
    user_mock = mock_module('auth.User')
    user_mock.authenticate.return_value = {'user_id': 1, 'is_admin': True}

    # 在测试中使用
    from database import connect
    from requests import get
    from auth.User import authenticate

    # 验证模拟是否成功
    assert connect()['status'] == 'connected'
    with pytest.raises(Exception):
        get('https://example.com')
    assert authenticate()['is_admin'] is True


if __name__ == "__main__":
    # 直接运行测试
    pytest.main(['-xvs', __file__])
