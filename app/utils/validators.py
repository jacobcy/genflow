from typing import Dict, Tuple, Optional
from werkzeug.exceptions import BadRequest
from email_validator import validate_email, EmailNotValidError

def validate_registration_data(data: Dict) -> Tuple[bool, Optional[str]]:
    """验证注册数据"""
    if not data:
        return False, "请提供注册数据"
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return False, f"缺少必填字段: {field}"
    
    # 验证用户名
    username = data['username']
    if not 3 <= len(username) <= 20:
        return False, "用户名长度必须在3-20个字符之间"
    
    # 验证邮箱
    try:
        validate_email(data['email'])
    except EmailNotValidError:
        return False, "邮箱格式不正确"
    
    # 验证密码
    password = data['password']
    if len(password) < 6:
        return False, "密码长度不能少于6个字符"
    
    return True, None

def validate_login_data(data: Dict) -> Tuple[bool, Optional[str]]:
    """验证登录数据"""
    if not data:
        return False, "请提供登录数据"
    
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return False, f"缺少必填字段: {field}"
    
    # 验证邮箱
    email = data.get('email', '').strip()
    if not email:
        return False, "请输入邮箱"
    
    # 验证密码
    if len(data['password']) < 1:
        return False, "请输入密码"
    
    return True, None

def validate_article_data(data: Dict) -> Tuple[bool, Optional[str]]:
    """验证文章数据"""
    if not data:
        return False, "请提供文章数据"
    
    required_fields = ['title', 'content']
    for field in required_fields:
        if field not in data:
            return False, f"缺少必填字段: {field}"
    
    # 验证标题
    if not 1 <= len(data['title']) <= 200:
        return False, "标题长度必须在1-200个字符之间"
    
    # 验证内容
    if len(data['content']) < 1:
        return False, "文章内容不能为空"
    
    return True, None

def validate_platform_data(data: Dict):
    """验证平台账号数据"""
    if 'access_token' not in data:
        raise BadRequest('缺少访问令牌')
