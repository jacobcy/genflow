from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.ai_service import AIService
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
ai_api_bp = Blueprint('ai_api', __name__, url_prefix='/ai')

# 创建服务实例
ai_service = AIService()

@ai_api_bp.route('/check', methods=['GET'])
def check_ai_service():
    """检查AI服务是否可用"""
    return jsonify({
        'status': 'available' if ai_service.is_available else 'unavailable'
    })

@ai_api_bp.route('/title-suggestions', methods=['POST'])
@jwt_required()
def get_title_suggestions():
    """获取文章标题建议"""
    data = request.get_json()
    content = data.get('content', '')
    
    if not content:
        return jsonify({'error': '文章内容不能为空'}), 400
    
    # 获取标题建议
    result = ai_service.get_title_suggestions(content)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 500
    
    return jsonify(result)

@ai_api_bp.route('/content-improvement', methods=['POST'])
@jwt_required()
def get_content_improvement():
    """获取文章内容改进建议"""
    data = request.get_json()
    title = data.get('title', '')
    content = data.get('content', '')
    
    if not content:
        return jsonify({'error': '文章内容不能为空'}), 400
    
    # 获取内容改进建议
    result = ai_service.get_content_improvement(title, content)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 500
    
    return jsonify(result)

@ai_api_bp.route('/seo-suggestions', methods=['POST'])
@jwt_required()
def get_seo_suggestions():
    """获取SEO优化建议"""
    data = request.get_json()
    title = data.get('title', '')
    content = data.get('content', '')
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    # 获取SEO建议
    result = ai_service.get_seo_suggestions(title, content)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 500
    
    return jsonify(result)

@ai_api_bp.route('/generate-image', methods=['POST'])
@jwt_required()
def generate_image():
    """生成文章配图"""
    data = request.get_json()
    title = data.get('title', '')
    content = data.get('content', '')
    style = data.get('style', 'realistic')
    
    if not title and not content:
        return jsonify({'error': '标题和内容不能同时为空'}), 400
    
    # 生成图片
    result = ai_service.generate_article_image(title, content, style)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 500
    
    return jsonify(result)

@ai_api_bp.route('/publish', methods=['POST'])
@jwt_required()
def publish_article():
    """发布文章到平台"""
    data = request.get_json()
    
    required_fields = ['title', 'content', 'platform']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要字段: {field}'}), 400
    
    # 获取用户ID
    user_id = get_jwt_identity()
    
    # 添加用户ID到数据中
    data['user_id'] = user_id
    
    # 发布文章
    result = ai_service.publish_to_platform(data)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 500
    
    return jsonify(result) 