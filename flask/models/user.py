from datetime import datetime
from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False, default='user')  # 确保非空且有默认值
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    platforms = db.relationship('PlatformAccount', backref='user', lazy='dynamic')
    
    @classmethod
    def create_user(cls, username, email, password, role='user'):
        """创建新用户，处理唯一性约束冲突"""
        try:
            user = cls(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user, None
        except IntegrityError as e:
            db.session.rollback()
            if 'users_username_key' in str(e):
                return None, "用户名已存在"
            elif 'users_email_key' in str(e):
                return None, "邮箱已被注册"
            return None, str(e)
    
    @classmethod
    def update_user(cls, user_id, **kwargs):
        """更新用户信息，处理唯一性约束冲突"""
        try:
            user = cls.query.get(user_id)
            if not user:
                return None, "用户不存在"
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    if key == 'password':
                        user.set_password(value)
                    else:
                        setattr(user, key, value)
            
            db.session.commit()
            return user, None
        except IntegrityError as e:
            db.session.rollback()
            if 'users_username_key' in str(e):
                return None, "用户名已存在"
            elif 'users_email_key' in str(e):
                return None, "邮箱已被注册"
            return None, str(e)
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }