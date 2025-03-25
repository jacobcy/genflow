from flask import Flask, render_template, redirect, url_for, jsonify, request, render_template_string
from flask import current_app
from .extensions import db, migrate, jwt, cors, login_manager  # 从扩展模块导入所有需要的实例
from config import config
import logging
from .utils.logger import setup_logger
from .utils.errors import not_found, error_response
import os
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token, set_access_cookies, decode_token, JWTManager
from .models import User, Article
from datetime import datetime, timedelta
from .utils.process_manager import process_manager
from flask_cors import CORS

def create_app(config_name="development"):
    """创建 Flask 应用实例"""
    app = Flask(__name__, 
                static_folder='static',
                static_url_path='/static'
               )
    
    if config_name == "development":
        from .config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    else:
        from .config import ProductionConfig
        app.config.from_object(ProductionConfig)
    
    if app.debug:
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.jinja_env.auto_reload = True
    
    # JWT配置
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
    app.config['JWT_REFRESH_COOKIE_PATH'] = '/'
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'
    app.config['JWT_COOKIE_DOMAIN'] = None
    app.config['JWT_COOKIE_HTTPONLY'] = True
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    # 配置日志
    setup_logger(app)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    
    # 配置 Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    # 初始化CORS
    cors.init_app(app,
        resources={r"/*": {"origins": f"http://localhost:{os.getenv('FRONTEND_PORT', '6060')}"}},
        supports_credentials=True,
        expose_headers=["Authorization"]
    )
    
    # 只在应用启动时执行一次数据库初始化
    if not os.environ.get('GUNICORN_WORKER_INITIALIZED'):
        with app.app_context():
            try:
                db.create_all()
                
                # 初始化管理员账号
                admin_email = os.getenv('ADMIN_EMAIL', 'admin@genflow.dev')
                admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
                
                admin = User.query.filter_by(
                    username='admin',
                    email=admin_email,
                    role='admin'
                ).first()
                
                if not admin:
                    admin = User(
                        username='admin',
                        email=admin_email,
                        role='admin'
                    )
                    admin.set_password(admin_password)
                    db.session.add(admin)
                    db.session.commit()
                    app.logger.info(f"管理员账号创建成功: {admin_email}")
                
            except Exception as e:
                app.logger.error(f"数据库初始化失败: {str(e)}")
                if app.debug:
                    import traceback
                    traceback.print_exc()
            finally:
                db.session.remove()
        
        os.environ['GUNICORN_WORKER_INITIALIZED'] = 'true'
    
    # 注册蓝图
    from .views import main_bp
    from .api import api_bp
    from .admin import admin_bp
    
    # 先初始化 API 蓝图的子蓝图
    from .api import register_blueprints
    register_blueprints()
    
    # 然后注册主蓝图
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    
    # 注册错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        return not_found('Resource not found')
    
    @app.errorhandler(500)
    def internal_error(error):
        return error_response(500, 'Internal server error')
    
    # 请求结束时清理数据库会话
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
    
    # JWT错误处理
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        response = redirect(url_for('admin.login'))
        response.delete_cookie('access_token_cookie')
        return response

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        response = redirect(url_for('admin.login'))
        response.delete_cookie('access_token_cookie')
        return response

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        response = redirect(url_for('admin.login'))
        response.delete_cookie('access_token_cookie')
        return response
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(server='werkzeug')
