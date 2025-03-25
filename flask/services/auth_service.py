from typing import Optional
from werkzeug.exceptions import NotFound, Unauthorized
from app.models.user import User
from app.extensions import db

class AuthService:
    def register_user(self, username: str, email: str, password: str) -> User:
        """注册新用户"""
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            raise ValueError('用户名已存在')
        if User.query.filter_by(email=email).first():
            raise ValueError('邮箱已存在')
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> User:
        """用户认证"""
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            raise Unauthorized('用户名或密码错误')
        
        return user
    
    def get_user(self, user_id: int) -> User:
        """获取用户信息"""
        user = User.query.get(user_id)
        if not user:
            raise NotFound('用户不存在')
        return user
