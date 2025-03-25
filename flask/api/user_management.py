from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User
from ..extensions import db
from . import api_bp
from ..utils.validators import validate_registration_data

# 创建API蓝图
user_management_bp = Blueprint('user_management', __name__, url_prefix='/admin')

@user_management_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """获取所有用户"""
    # 验证管理员权限
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized', 'message': '需要管理员权限'}), 403
    
    # 获取所有用户
    users = User.query.all()
    return jsonify({'users': [user.to_dict() for user in users]})

@user_management_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """创建新用户"""
    # 验证管理员权限
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized', 'message': '需要管理员权限'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供用户数据'}), 400
    
    # 验证必要字段
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要字段: {field}'}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '该邮箱已被注册'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '该用户名已被使用'}), 400
    
    # 创建新用户
    new_user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'user')  # 默认为普通用户
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': '用户创建成功',
        'user': new_user.to_dict()
    }), 201

@user_management_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户"""
    # 验证管理员权限
    admin_id = get_jwt_identity()
    admin_user = User.query.get(admin_id)
    if not admin_user or admin_user.role != 'admin':
        return jsonify({'error': 'Unauthorized', 'message': '需要管理员权限'}), 403
    
    # 不能删除自己
    if str(user_id) == admin_id:
        return jsonify({'error': '不能删除当前登录的管理员账号'}), 400
    
    # 查找用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 删除用户
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'message': f'用户 {user.username} 已成功删除',
        'user_id': user_id
    }) 