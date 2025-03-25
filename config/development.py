from . import Config

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/genflow_dev'

    # 日志配置
    LOG_LEVEL = 'DEBUG'

    # 跨域配置
    CORS_ORIGINS = ['http://localhost:6060', 'http://127.0.0.1:6060']

    # 文件上传配置
    UPLOAD_FOLDER = 'uploads/development'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = False
    TESTING = True

    # 使用 SQLite 内存数据库进行测试
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # 禁用 CSRF 保护方便测试
    WTF_CSRF_ENABLED = False
