import pytest
from app.models import User
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
    assert response.status_code == 200
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
    response = client.post('/api/articles', 
        json={
            'title': 'Test Article',
            'content': 'This is a test article content. ' * 10
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json['title'] == 'Test Article'

def test_publish_article(client, auth_headers, app):
    """测试发布文章"""
    # 先创建文章
    response = client.post('/api/articles',
        json={
            'title': 'Test Article',
            'content': 'This is a test article content. ' * 10
        },
        headers=auth_headers
    )
    article_id = response.json['id']
    
    # 测试发布
    response = client.post(f'/api/articles/{article_id}/publish',
        json={
            'platforms': ['baidu', 'sohu']
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert 'task_id' in response.json
