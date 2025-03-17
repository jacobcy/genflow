import pytest
from app.models import User, PlatformAccount, Article  # 新增导入
from app.extensions import db
from app.models.article import Article

def test_register(client):
    """测试用户注册"""
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert b'success' in response.data

def test_login(client):
    """测试用户登录"""
    # 先创建测试用户
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    # 测试登录
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    # 需要先登录获取新token（新增）
    login_res = client.post('/api/auth/login', json={
        'email': 'pub@example.com',
        'password': 'password123'
    })
    new_auth_headers = {
        'Authorization': f'Bearer {login_res.json["access_token"]}'
    }
    assert 'access_token' in response.json

def test_invalid_login(client):
    """测试无效登录"""
    response = client.post('/api/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    })
    assert response.status_code == 401

def test_create_article(client, auth_headers):
    """测试创建文章"""
    with client.application.app_context():  # 新增应用上下文
        response = client.post('/api/articles', 
            json={'title': 'Test Article', 'content': 'ValidContent' * 10},
            headers=auth_headers
        )
    assert response.status_code == 201
    assert response.json['title'] == 'Test Article'
    assert 'id' in response.json  # 添加关键字段验证
    assert Article.query.count() == 1  # 验证数据库记录

def test_publish_article(client, auth_headers, app):
    """测试发布文章"""
    # 先注册测试用户（原缺失的步骤）
    client.post('/api/auth/register', json={
        'username': 'publisher',
        'email': 'pub@example.com',
        'password': 'password123'
    })
    
    with app.app_context():
        user = User.query.filter_by(email='pub@example.com').first()
        # 添加平台账户前清理旧数据（新增）
        PlatformAccount.query.delete()
        db.session.add_all([
            PlatformAccount(user=user, platform='baidu', access_token='test1'),
            PlatformAccount(user=user, platform='sohu', access_token='test2')
        ])
        db.session.commit()
    # 先创建文章
    # 创建文章部分需要携带认证头（原缺失）
    response = client.post('/api/articles',
        json={'title': 'Test Article', 'content': 'ValidContent' * 10},
        headers=auth_headers  # 添加认证头
    )
    article_id = response.json['id']
    
    # 需要先登录获取新token（新增）
    login_res = client.post('/api/auth/login', json={
        'email': 'pub@example.com',
        'password': 'password123'
    })
    new_auth_headers = {
        'Authorization': f'Bearer {login_res.json["access_token"]}'
    }
    
    # 测试发布
    response = client.post(f'/api/articles/{article_id}/publish',
        json={'platforms': ['baidu', 'sohu']},
        headers=new_auth_headers  # 使用新token
    )
    assert response.status_code == 200
    assert 'task_id' in response.json
