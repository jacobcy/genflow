from . import Config

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # 使用内存数据库
    JWT_SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
