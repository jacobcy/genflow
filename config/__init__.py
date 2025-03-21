import os
import secrets

class Config:
    """基础配置类"""
    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if JWT_SECRET_KEY:
        JWT_SECRET_KEY_SET_BY_ENV = True
    else:
        JWT_SECRET_KEY = secrets.token_urlsafe(32)
        JWT_SECRET_KEY_SET_BY_ENV = False
    
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 3600  # 24小时
    
    # Dify配置
    DIFY_API_KEY = os.environ.get('DIFY_API_KEY')
    DIFY_ENDPOINT = os.environ.get('DIFY_ENDPOINT', 'https://api.dify.ai/v1')
    
    # Celery配置
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# 从环境变量加载配置类
from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}