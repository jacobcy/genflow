"""
数据库初始化脚本
用于创建数据库表和初始化基础数据
"""
from dotenv import load_dotenv
load_dotenv()  # 确保最早加载环境变量

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app import create_app
from app.extensions import db
from app.models import User, Article
from werkzeug.security import generate_password_hash

def init_database():
    """初始化数据库"""
    # 创建应用上下文
    app = create_app()
    with app.app_context():
        try:
            # 创建所有数据库表
            db.create_all()
            print("[OK] 数据库表创建成功")
            
            # 检查是否已存在管理员用户
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                # 创建管理员用户
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    password_hash=generate_password_hash('admin'),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("[OK] 管理员用户创建成功")
            else:
                print("[INFO] 管理员用户已存在")
                
            return True
            
        except Exception as e:
            print(f"[ERROR] 数据库初始化失败: {str(e)}")
            return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)