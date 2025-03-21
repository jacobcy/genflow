from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, set_access_cookies
from ..models import User, Article
import logging

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    """首页和用户登录"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.role == 'admin':
                # 管理员应该使用管理员登录页面
                flash('请使用管理员登录页面', 'error')
                return redirect(url_for('admin.login'))
            
            access_token = create_access_token(identity=str(user.id))
            response = redirect(url_for('main.user_dashboard'))
            set_access_cookies(response, access_token)
            return response
        
        flash('邮箱或密码错误', 'error')
    
    return render_template('index.html')

@main_bp.route('/user/dashboard')
@jwt_required()
def user_dashboard():
    """用户仪表盘"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return redirect(url_for('main.index'))
    
    if user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    articles = Article.query.filter_by(user_id=current_user_id).all()
    return render_template('user/dashboard.html', user=user, articles=articles)

@main_bp.route('/user/edit')
@main_bp.route('/user/edit/<int:article_id>')
@jwt_required()
def user_edit(article_id=None):
    """用户编辑界面"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return redirect(url_for('main.index'))
    
    article = None
    if article_id:
        article = Article.query.get_or_404(article_id)
        # 确保只能编辑自己的文章
        if str(article.user_id) != current_user_id:
            flash('您没有权限编辑这篇文章', 'error')
            return redirect(url_for('main.user_dashboard'))
    
    return render_template('user/edit.html', user=user, article=article)

@main_bp.route('/user/page/<int:article_id>')
def user_page(article_id):
    """用户文章页面"""
    article = Article.query.get_or_404(article_id)
    return render_template('user/page.html', article=article)

@main_bp.route('/test-sentry')
def test_sentry():
    """测试 Sentry 错误捕获"""
    try:
        # 故意触发一个除零错误
        1 / 0
    except Exception as e:
        logging.exception("测试 Sentry 错误捕获")
        raise  # 重新抛出异常，让 Sentry 捕获

@main_bp.route('/test-sentry-auth')
@jwt_required()
def test_sentry_auth():
    """测试 Sentry 认证相关错误捕获"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        raise ValueError("用户不存在")
        
    # 故意访问不存在的属性
    return jsonify({"username": user.non_existent_field})

@main_bp.route('/profile')
@jwt_required()
def profile():
    """用户个人资料"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return redirect(url_for('main.index'))
    
    return render_template('profile.html', user=user)