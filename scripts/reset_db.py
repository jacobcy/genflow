#!/usr/bin/env python3
"""
增强版数据库重置脚本
支持 PostgreSQL 和 SQLite

数据库重置脚本功能：
1. 根据配置重置 PostgreSQL 或 SQLite 数据库
2. 自动处理 PostgreSQL 的活跃连接
3. 重建数据库迁移记录
4. 初始化管理员账号 (定义在 app/__init__.py)
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from urllib.parse import urlparse

def reset_database():
    load_dotenv()  # 加载环境变量
    db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    
    # 添加调试输出
    print(f"\n=== 数据库连接信息 ===")
    print(f"SQLALCHEMY_DATABASE_URI: {db_uri}")
    
    if not db_uri:
        print("警告: SQLALCHEMY_DATABASE_URI 环境变量未设置，尝试使用 DATABASE_URL")
        db_uri = os.getenv('DATABASE_URL')
        print(f"DATABASE_URL: {db_uri}")
        
        if not db_uri:
            raise ValueError("数据库连接字符串未设置")
    
    if db_uri.startswith('postgresql://'):
        # 从URI中提取信息
        parsed = urlparse(db_uri)
        
        # 验证所有必要参数
        if not all([parsed.username, parsed.password, parsed.hostname, parsed.path]):
            raise ValueError("数据库URI配置不完整")
        
        db_user = parsed.username
        db_password = parsed.password
        db_host = parsed.hostname
        db_port = parsed.port or 5432
        db_name = parsed.path[1:]  # 去掉路径前的斜杠
        
        # 构建管理员连接URI
        admin_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
        
        try:
            engine = create_engine(admin_uri)
            conn = engine.connect()
            conn.execute("COMMIT")
            
            # 终止连接使用新参数
            conn.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid();
            """)
            
            # 创建数据库时使用动态用户名
            conn.execute(f"DROP DATABASE IF EXISTS {db_name}")
            conn.execute(f"""
                CREATE DATABASE {db_name} 
                WITH OWNER = {db_user}
                ENCODING 'UTF8'
                LC_COLLATE 'en_US.UTF-8'
                LC_CTYPE 'en_US.UTF-8'
                TEMPLATE template0;
            """)
            print(f"✅ PostgreSQL数据库 {db_name} 已重置")
            conn.close()
        except OperationalError as e:
            print(f"❌ 数据库重置失败: {str(e)}")
            sys.exit(1)
    else:
        # 处理SQLite
        db_path = Path('instance/flaskr.sqlite')
        if db_path.exists():
            db_path.unlink()
            print(f"✅ SQLite数据库文件已删除: {db_path}")
        else:
            print(f"ℹ️ SQLite数据库文件不存在: {db_path}")

def main():
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # 重置数据库
    reset_database()
    
    # 清理迁移记录
    migrations_dir = Path('migrations')
    if migrations_dir.exists():
        import shutil
        shutil.rmtree(migrations_dir)
        print(f"✅ 迁移目录已删除: {migrations_dir}")
    
    # 重新初始化
    print("\n正在初始化数据库迁移...")
    os.system('flask db init')
    os.system('flask db migrate -m "Initial migration"')
    os.system('flask db upgrade')
    
    print("\n✅ 数据库重置完成！")

if __name__ == '__main__':
    if input("⚠️  确认要重置数据库吗？所有数据将丢失！(y/N) ").lower() == 'y':
        main()
    else:
        print("操作已取消") 