import os
from datetime import timedelta
import getpass

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 构建数据库 URI
    DB_USER = os.getenv('DB_USER', getpass.getuser())  # 使用当前系统用户作为默认值
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')  # 默认密码为空
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'genflow_dev')
    
    # 如果设置了完整的 DATABASE_URL，则使用它，否则使用组件构建
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    TEMPLATES_AUTO_RELOAD = True

class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
    TEMPLATES_AUTO_RELOAD = False