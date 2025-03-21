from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from ..models import Article, User
from ..extensions import db
import os
import base64
import uuid
from datetime import datetime

editor_api_bp = Blueprint('editor_api', __name__, url_prefix='/editor')

def save_base64_image(base64_str, folder='uploads'):
    """保存 base64 格式的图片"""
    try:
        # 确保上传目录存在
        upload_dir = os.path.join(current_app.static_folder, folder)
        os.makedirs(upload_dir, exist_ok=True)
        
        # 解码并保存图片
        img_data = base64.b64decode(base64_str.split(',')[1])
        filename = f"{uuid.uuid4()}.png"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(img_data)
            
        return f'/static/{folder}/{filename}'
    except Exception as e:
        current_app.logger.error(f"保存图片失败: {str(e)}")
        return None

@editor_api_bp.route('/draft', methods=['POST'])
@jwt_required()
def save_draft():
    """保存文章草稿"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # 验证必要字段
        required_fields = ['title', 'content']
        if not all(field in data for field in required_fields):
            return jsonify({'error': '缺少必要字段'}), 400
            
        # 处理封面图片
        cover_image_url = None
        if 'cover_image' in data and data['cover_image']:
            cover_image_url = save_base64_image(data['cover_image'], 'covers')
            if not cover_image_url:
                return jsonify({'error': '封面图片保存失败'}), 500
        
        # 创建或更新文章
        article_id = data.get('id')
        if article_id:
            article = Article.query.get(article_id)
            if not article or str(article.author_id) != str(user_id):
                return jsonify({'error': '无权限编辑此文章'}), 403
        else:
            article = Article(author_id=user_id)
            
        # 更新文章信息
        article.title = data['title']
        article.content = data['content']
        article.summary = data.get('summary', '')
        article.tags = data.get('tags', [])
        if cover_image_url:
            article.cover_image = cover_image_url
        article.status = 'draft'
        article.updated_at = datetime.utcnow()
        
        db.session.add(article)
        db.session.commit()
        
        return jsonify({
            'message': '草稿保存成功',
            'article_id': article.id
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"保存草稿失败: {str(e)}")
        return jsonify({'error': '保存草稿失败'}), 500

@editor_api_bp.route('/publish', methods=['POST'])
@jwt_required()
def publish_article():
    """发布文章"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # 验证必要字段
        required_fields = ['title', 'content']
        if not all(field in data for field in required_fields):
            return jsonify({'error': '缺少必要字段'}), 400
            
        # 处理封面图片
        cover_image_url = None
        if 'cover_image' in data and data['cover_image']:
            cover_image_url = save_base64_image(data['cover_image'], 'covers')
            if not cover_image_url:
                return jsonify({'error': '封面图片保存失败'}), 500
        
        # 创建或更新文章
        article_id = data.get('id')
        if article_id:
            article = Article.query.get(article_id)
            if not article or str(article.author_id) != str(user_id):
                return jsonify({'error': '无权限编辑此文章'}), 403
        else:
            article = Article(author_id=user_id)
            
        # 更新文章信息
        article.title = data['title']
        article.content = data['content']
        article.summary = data.get('summary', '')
        article.tags = data.get('tags', [])
        if cover_image_url:
            article.cover_image = cover_image_url
        article.status = 'published'
        article.published_at = datetime.utcnow()
        article.updated_at = datetime.utcnow()
        
        db.session.add(article)
        db.session.commit()
        
        return jsonify({
            'message': '文章发布成功',
            'article_id': article.id
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"发布文章失败: {str(e)}")
        return jsonify({'error': '发布文章失败'}), 500

@editor_api_bp.route('/upload-image', methods=['POST'])
@jwt_required()
def upload_image():
    """上传图片"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
            
        file = request.files['image']
        if not file.filename:
            return jsonify({'error': '文件名为空'}), 400
            
        # 验证文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not '.' in file.filename or \
           file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'error': '不支持的文件类型'}), 400
            
        # 保存文件
        filename = secure_filename(f"{uuid.uuid4()}.{file.filename.rsplit('.', 1)[1]}")
        upload_dir = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        return jsonify({
            'url': f'/static/uploads/{filename}',
            'message': '图片上传成功'
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"上传图片失败: {str(e)}")
        return jsonify({'error': '上传图片失败'}), 500

# AI 相关功能
@editor_api_bp.route('/ai/assist', methods=['POST'])
@jwt_required()
def ai_assist():
    """AI 辅助写作"""
    try:
        data = request.get_json()
        if not data.get('prompt'):
            return jsonify({'error': '缺少提示信息'}), 400
            
        # TODO: 调用 AI 服务
        # 这里需要实现实际的 AI 处理逻辑
        
        return jsonify({
            'content': '生成的内容',
            'message': 'AI 辅助生成成功'
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"AI 辅助失败: {str(e)}")
        return jsonify({'error': 'AI 辅助失败'}), 500

@editor_api_bp.route('/ai/optimize', methods=['POST'])
@jwt_required()
def ai_optimize():
    """AI 优化内容"""
    try:
        data = request.get_json()
        if not data.get('content'):
            return jsonify({'error': '缺少需要优化的内容'}), 400
            
        # TODO: 调用 AI 服务
        # 这里需要实现实际的 AI 处理逻辑
        
        return jsonify({
            'content': '优化后的内容',
            'message': '内容优化成功'
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"内容优化失败: {str(e)}")
        return jsonify({'error': '内容优化失败'}), 500

@editor_api_bp.route('/ai/summarize', methods=['POST'])
@jwt_required()
def ai_summarize():
    """AI 生成摘要"""
    try:
        data = request.get_json()
        if not data.get('content'):
            return jsonify({'error': '缺少文章内容'}), 400
            
        # TODO: 调用 AI 服务
        # 这里需要实现实际的 AI 处理逻辑
        
        return jsonify({
            'summary': '生成的摘要',
            'message': '摘要生成成功'
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"生成摘要失败: {str(e)}")
        return jsonify({'error': '生成摘要失败'}), 500

@editor_api_bp.route('/ai/tags', methods=['POST'])
@jwt_required()
def ai_generate_tags():
    """AI 生成标签"""
    try:
        data = request.get_json()
        if not data.get('content'):
            return jsonify({'error': '缺少文章内容'}), 400
            
        # TODO: 调用 AI 服务
        # 这里需要实现实际的 AI 处理逻辑
        
        return jsonify({
            'tags': ['标签1', '标签2', '标签3'],
            'message': '标签生成成功'
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"生成标签失败: {str(e)}")
        return jsonify({'error': '生成标签失败'}), 500 