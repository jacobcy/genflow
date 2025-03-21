from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.article import Article
from ..utils.validators import validate_article_data
from ..extensions import db
from ..services.article_service import ArticleService

# 创建文章蓝图
articles_bp = Blueprint('articles', __name__, url_prefix='/articles')

article_service = ArticleService()

@articles_bp.route('', methods=['POST'])
@jwt_required()
def create_article():
    """创建文章"""
    data = request.get_json()
    
    # 验证数据
    is_valid, error_msg = validate_article_data(data)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # 创建文章
    article = Article(
        title=data['title'],
        content=data['content'],
        user_id=get_jwt_identity()
    )
    
    db.session.add(article)
    db.session.commit()
    
    return jsonify(article.to_dict()), 201

@articles_bp.route('/draft', methods=['POST'])
@jwt_required()
def save_draft():
    """保存文章草稿"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    # 检查必要字段
    if not data.get('content'):
        return jsonify({'error': '文章内容不能为空'}), 400
    
    # 设置标题 - 如果未提供则使用内容的第一行
    title = data.get('title', '未命名文章')
    if not title or title == '未命名文章':
        # 从内容提取第一行作为标题
        first_line = data['content'].split('\n')[0].strip()
        if first_line:
            title = first_line[:100]  # 限制标题长度
    
    # 查找用户最新的草稿
    draft = Article.query.filter_by(
        user_id=user_id, 
        status='draft'
    ).order_by(Article.updated_at.desc()).first()
    
    if draft:
        # 更新现有草稿
        draft.title = title
        draft.content = data['content']
        draft.updated_at = db.func.now()
    else:
        # 创建新草稿
        draft = Article(
            title=title,
            content=data['content'],
            status='draft',
            user_id=user_id
        )
        db.session.add(draft)
    
    db.session.commit()
    
    return jsonify({
        'message': '草稿保存成功',
        'article': draft.to_dict()
    }), 200

@articles_bp.route('/last-draft', methods=['GET'])
@jwt_required()
def get_last_draft():
    """获取用户最新的草稿"""
    user_id = get_jwt_identity()
    
    # 查找用户最新的草稿
    draft = Article.query.filter_by(
        user_id=user_id, 
        status='draft'
    ).order_by(Article.updated_at.desc()).first()
    
    if not draft:
        return jsonify({'message': '未找到草稿'}), 404
    
    return jsonify({
        'message': '获取成功',
        'article': draft.to_dict()
    }), 200

@articles_bp.route('', methods=['GET'])
@jwt_required()
def get_articles():
    """获取用户的文章列表"""
    user_id = get_jwt_identity()
    articles = Article.query.filter_by(user_id=user_id).all()
    return jsonify([article.to_dict() for article in articles]), 200

@articles_bp.route('/<int:article_id>', methods=['GET'])
@jwt_required()
def get_article(article_id):
    """获取文章详情"""
    article = Article.query.get_or_404(article_id)
    return jsonify(article.to_dict())

@articles_bp.route('/<int:article_id>/publish', methods=['POST'])
@jwt_required()
def publish_article(article_id):
    """发布文章到指定平台"""
    data = request.get_json()
    platforms = data.get('platforms', [])
    
    task = article_service.publish_article(article_id, platforms)
    return jsonify({'task_id': task.id})
