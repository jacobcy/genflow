from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Article, PlatformAccount
from ..extensions import db
from . import api_bp

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """获取管理后台统计数据"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    stats = {
        'total_articles': Article.query.count(),
        'total_users': User.query.count(),
        'total_platforms': PlatformAccount.query.count()
    }
    return jsonify(stats)

@admin_bp.route('/articles', methods=['GET'])
@jwt_required()
def get_admin_articles():
    """获取所有文章"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return jsonify([{
        'id': article.id,
        'title': article.title,
        'status': article.status,
        'created_at': article.created_at.isoformat(),
        'user_id': article.user_id
    } for article in articles])

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """获取所有用户"""
    current_user = User.query.get(get_jwt_identity())
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]) 