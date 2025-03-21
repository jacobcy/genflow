from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request, jsonify, make_response
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt, create_access_token, set_access_cookies
from functools import wraps
import platform
import os
from datetime import datetime
from ..models import User
from ..extensions import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # 如果是登录页面，直接通过
            if request.endpoint == 'admin.login':
                return fn(*args, **kwargs)
                
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                current_user_id = get_jwt_identity()
                
                # 检查 JWT claims 中的角色
                if claims.get('role') != 'admin':
                    flash('需要管理员权限访问此页面', 'error')
                    return redirect(url_for('admin.login'))
                    
                user = User.query.get(current_user_id)
                if not user:
                    flash('用户不存在', 'error')
                    return redirect(url_for('admin.login'))
                    
                return fn(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"认证错误: {str(e)}")
                return redirect(url_for('admin.login'))
        return decorator
    return wrapper

@admin_bp.route('/')
@admin_required()
def index():
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 清除可能存在的无效 token
    response = None
    
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            data = request.form
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            if request.is_json:
                return jsonify({'message': '请提供邮箱和密码'}), 400
            flash('请提供邮箱和密码', 'error')
            response = redirect(url_for('admin.login'))
            response.delete_cookie('access_token_cookie')
            return response
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.role != 'admin':
                if request.is_json:
                    return jsonify({'message': '非管理员用户'}), 403
                flash('非管理员用户', 'error')
                response = redirect(url_for('admin.login'))
                response.delete_cookie('access_token_cookie')
                return response
            
            # 创建包含角色信息的 token
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={'role': 'admin'}
            )
            
            if request.is_json:
                return jsonify({
                    'access_token': access_token,
                    'message': '登录成功'
                })
            
            response = redirect(url_for('admin.dashboard'))
            set_access_cookies(response, access_token)
            return response
        
        if request.is_json:
            return jsonify({'message': '邮箱或密码错误'}), 401
        flash('邮箱或密码错误', 'error')
        response = redirect(url_for('admin.login'))
        response.delete_cookie('access_token_cookie')
        return response
    
    # GET 请求处理
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
    except Exception:
        response = make_response(render_template('admin/login.html'))
        response.delete_cookie('access_token_cookie')
        return response
    
    response = make_response(render_template('admin/login.html'))
    response.delete_cookie('access_token_cookie')
    return response

@admin_bp.route('/dashboard')
@admin_required()
def dashboard():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return redirect(url_for('admin.login'))
            
        # 获取系统概览数据
        user_count = User.query.count()
        article_count = 0  # 如果有 Article 模型，可以使用 Article.query.count()
        
        # 计算运行时间
        start_time = current_app.config.get('START_TIME', datetime.now())
        uptime = datetime.now() - start_time
        uptime_days = uptime.days
        
        # 获取所有用户列表
        users = User.query.all()
        
        return render_template('admin/dashboard.html', 
                             current_user=user,
                             user_count=user_count,
                             article_count=article_count,
                             uptime=f"{uptime_days}天",
                             users=users)
    except Exception as e:
        current_app.logger.error(f"访问仪表盘错误: {str(e)}")
        return redirect(url_for('admin.login'))

@admin_bp.route('/settings')
@admin_required()
def settings():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    config = current_app.config
    
    # 获取数据库路径
    db_uri = config.get('SQLALCHEMY_DATABASE_URI', '')
    try:
        if '///' in db_uri:
            db_path = db_uri.split('///')[1]
            db_name = os.path.basename(db_path)
        else:
            db_path = db_uri
            db_name = db_uri
    except Exception:
        db_path = db_uri
        db_name = db_uri
    
    # 获取系统信息
    system_info = {
        'username': user.username,
        'env': config.get('ENV', 'production'),
        'debug_mode': config.get('DEBUG', False),
        'python_version': platform.python_version(),
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        
        # 数据库信息
        'db_type': 'SQLite',  # 根据实际配置调整
        'db_host': db_path,
        'db_name': db_name,
        
        # 缓存信息
        'cache_type': 'Redis',  # 根据实际配置调整
        'cache_host': config.get('REDIS_URL', 'localhost:6379'),
        
        # 日志信息
        'log_level': config.get('LOG_LEVEL', 'INFO'),
        'log_path': config.get('LOG_PATH', './logs'),
        'log_retention': config.get('LOG_RETENTION_DAYS', 30)
    }
    
    return render_template('admin/settings.html', **system_info)

@admin_bp.route('/logout', methods=['POST'])
def logout():
    response = redirect(url_for('admin.login'))
    response.delete_cookie('access_token_cookie')
    flash('已成功退出登录', 'success')
    return response

# 用户管理相关路由
@admin_bp.route('/users', methods=['POST'])
@admin_required()
def create_user():
    """创建新用户"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'缺少必填字段: {field}'}), 400
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': '该邮箱已被注册'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': '该用户名已被使用'}), 400
        
        # 创建新用户
        new_user = User(
            username=data['username'],
            email=data['email'],
            role=data['role']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': '用户创建成功'}), 201
        
    except Exception as e:
        current_app.logger.error(f"创建用户错误: {str(e)}")
        db.session.rollback()
        return jsonify({'message': '创建用户失败'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    """删除用户"""
    try:
        current_user_id = get_jwt_identity()
        if str(user_id) == current_user_id:
            return jsonify({'message': '不能删除当前登录的用户'}), 400
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': '用户删除成功'}), 200
        
    except Exception as e:
        current_app.logger.error(f"删除用户错误: {str(e)}")
        db.session.rollback()
        return jsonify({'message': '删除用户失败'}), 500