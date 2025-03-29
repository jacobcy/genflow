"""
FastAPI测试的配置文件

提供FastAPI测试所需的夹具和模拟对象
"""
import sys
import pytest
from unittest.mock import MagicMock, patch

# 模拟依赖模块
sys.modules['config_service'] = MagicMock()
sys.modules['db_adapter'] = MagicMock()
sys.modules['redis'] = MagicMock()

@pytest.fixture
def test_client():
    """提供测试用的FastAPI测试客户端"""
    from fastapi.testclient import TestClient

    # 在这里进行实际导入之前，先使用模拟对象
    # 当实际实现FastAPI应用时，可以替换为真实导入
    app_mock = MagicMock()
    app_mock.get = MagicMock()
    app_mock.post = MagicMock()

    # 返回测试客户端
    with patch('fastapi.FastAPI', return_value=app_mock):
        from fastapi import FastAPI
        app = FastAPI()
        client = TestClient(app)
        return client

@pytest.fixture
def mock_auth_dependency():
    """模拟认证依赖"""
    return MagicMock(return_value={"user_id": "test_user", "role": "test_role"})

@pytest.fixture
def mock_fastapi_app():
    """模拟FastAPI应用"""
    app = MagicMock()
    app.dependency_overrides = {}
    app.route = MagicMock()
    app.include_router = MagicMock()
    return app
