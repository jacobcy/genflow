from datetime import datetime
from ..extensions import db

class PlatformAccount(db.Model):
    """平台账号模型"""
    __tablename__ = 'platform_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    platform_name = db.Column(db.String(50), nullable=False)
    access_token = db.Column(db.String(500), nullable=False)
    refresh_token = db.Column(db.String(500))
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'platform_name': self.platform_name,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat()
        }

class Publication(db.Model):
    """文章发布记录"""
    __tablename__ = 'publications'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform_accounts.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, published, failed
    url = db.Column(db.String(500))  # 发布后的文章链接
    error = db.Column(db.Text)  # 发布失败原因
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'article_id': self.article_id,
            'platform_id': self.platform_id,
            'status': self.status,
            'url': self.url,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
