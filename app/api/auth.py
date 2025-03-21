from flask import jsonify, request, Blueprint
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt_identity, 
    set_access_cookies,
    get_jwt,
    unset_jwt_cookies
)
from ..models.user import User
from ..utils.validators import validate_registration_data, validate_login_data
from ..extensions import db
from datetime import datetime, timedelta
from flask import current_app

# 定义认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    # 验证数据
    is_valid, error_msg = validate_registration_data(data)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '该邮箱已被注册'}), 400
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': '注册成功'}), 201

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify(user.to_dict())

@auth_bp.route('/login', methods=['POST'])
def login():
    """普通用户登录"""
    data = request.get_json()
    
    # 验证数据
    is_valid, error_msg = validate_login_data(data)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # 验证用户
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '邮箱或密码错误'}), 401
    
    # 生成访问令牌
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict(),
        'role': user.role
    }), 200

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    try:
        data = request.get_json()
        
        # 验证数据
        is_valid, error_msg = validate_login_data(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 验证用户
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({'error': '邮箱或密码错误'}), 401
        
        # 验证管理员角色
        if user.role != 'admin':
            return jsonify({'error': '无管理员权限'}), 403
        
        # 生成访问令牌
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role},
            expires_delta=timedelta(hours=24)
        )
        
        # 创建响应
        response = jsonify({
            'message': '登录成功',
            'access_token': access_token,
            'user': user.to_dict()
        })
        
        # 设置 JWT cookie
        set_access_cookies(response, access_token)
        
        return response, 200
            
    except Exception as e:
        print(f"登录错误: {str(e)}")
        return jsonify({
            'error': '登录处理失败',
            'detail': str(e)
        }), 500

@auth_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表（仅管理员可用）"""
    try:
        # 获取当前用户
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # 验证管理员权限
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '无权访问此资源'}), 403
        
        # 获取所有用户
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        print(f"获取用户列表错误: {str(e)}")
        return jsonify({
            'error': '获取用户列表失败',
            'detail': str(e)
        }), 500

@auth_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户（仅管理员可用）"""
    try:
        # 获取当前用户
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # 验证管理员权限
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '无权执行此操作'}), 403
        
        # 不允许删除自己
        if str(user_id) == current_user_id:
            return jsonify({'error': '不能删除当前登录的管理员账号'}), 400
            
        # 查找并删除用户
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
            
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': f'用户 {user.username} 已成功删除'
        }), 200
        
    except Exception as e:
        print(f"删除用户错误: {str(e)}")
        return jsonify({
            'error': '删除用户失败',
            'detail': str(e)
        }), 500

@auth_bp.route('/admin/verify', methods=['GET'])
@jwt_required()
def verify_admin():
    """验证管理员认证状态"""
    try:
        # 获取当前用户
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # 验证管理员权限
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '无管理员权限'}), 403
        
        return jsonify({
            'verified': True,
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"验证管理员权限错误: {str(e)}")
        return jsonify({
            'error': '验证失败',
            'detail': str(e)
        }), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    response = jsonify({'message': '登出成功'})
    unset_jwt_cookies(response)
    return response, 200
