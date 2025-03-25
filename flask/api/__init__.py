from flask import Blueprint
from .auth import auth_bp

# 创建API主蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

def register_blueprints():
    """注册所有API蓝图"""
    # 导入子蓝图
    from .user_management import user_management_bp
    from .articles import articles_bp
    from .editor_api import editor_api_bp
    from .ai_api import ai_api_bp
    from .config import config_bp
    
    # 注册子蓝图
    api_bp.register_blueprint(auth_bp)  # auth_bp 已经有 /api/auth 前缀
    api_bp.register_blueprint(user_management_bp)
    api_bp.register_blueprint(articles_bp)
    api_bp.register_blueprint(editor_api_bp)
    api_bp.register_blueprint(ai_api_bp)
    api_bp.register_blueprint(config_bp)

# 在应用初始化时调用此函数
