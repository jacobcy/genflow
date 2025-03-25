from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_bp
from ..models.platform import PlatformAccount
from ..utils.validators import validate_platform_data
from ..extensions import db

@api_bp.route('/platforms', methods=['POST'])
@jwt_required()
def add_platform():
    """添加平台账号"""
    data = request.get_json()
    validate_platform_data(data)
    
    platform = PlatformAccount(
        user_id=get_jwt_identity(),
        platform_name=data['platform'],
        access_token=data['access_token']
    )
    
    db.session.add(platform)
    db.session.commit()
    
    return jsonify(platform.to_dict()), 201

@api_bp.route('/platforms', methods=['GET'])
@jwt_required()
def get_platforms():
    """获取用户的平台账号列表"""
    user_id = get_jwt_identity()
    platforms = PlatformAccount.query.filter_by(user_id=user_id).all()
    return jsonify([p.to_dict() for p in platforms]), 200
