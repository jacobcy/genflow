import pytest
from app.models.user import User
from app.models.article import Article
from app.models.platform import PlatformAccount, Publication
from app.extensions import db

def test_user_model(app):
    """测试用户模型"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        
        assert user.username == 'testuser'
        assert user.check_password('password123')
        assert not user.check_password('wrong')

def test_article_model(app):
    """测试文章模型"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        db.session.add(user)
        db.session.commit()
        
        article = Article(
            title='Test Article',
            content='Test content',
            author=user
        )
        db.session.add(article)
        db.session.commit()
        
        assert article.title == 'Test Article'
        assert article.author == user
        assert article.status == 'draft'

def test_platform_model(app):
    """测试平台模型"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        db.session.add(user)  # 确保用户被保存
        platform = PlatformAccount(
            user=user,
            user=user,
            platform='baidu',
            access_token='test_token'
        )
        
        db.session.add(platform)
        db.session.commit()  # 新增提交操作
        
        assert platform.platform == 'baidu'
        assert platform.user == user
