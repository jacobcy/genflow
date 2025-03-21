import os
import tempfile
import pytest
import logging
import asyncio
import sys
from app import create_app, db

# 添加 src 目录到 Python 路径
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, src_path)

# 配置日志
def pytest_configure(config):
    """配置pytest日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

@pytest.fixture(scope="session")
def event_loop():
    """创建一个事件循环，供所有测试使用"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def app():
    """创建测试应用"""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    
    async with app.app_context():
        await db.create_all()
        yield app
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope="session")
async def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture(scope="session")
async def auth_headers(client):
    """获取认证头"""
    response = await client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

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