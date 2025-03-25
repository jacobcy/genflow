#!/usr/bin/env python3
"""
简单的数据库重置脚本
使用直接的SQL命令删除并重建数据库
"""
import os
import sys
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/genflow_dev")
DB_NAME = "genflow_dev"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"

def main():
    """主函数：重置数据库"""
    print("正在重置数据库...")

    # 连接到postgres数据库
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    conn.autocommit = True  # 自动提交，用于创建和删除数据库

    try:
        with conn.cursor() as cursor:
            # 检查是否有活动连接
            print("正在断开现有连接...")
            cursor.execute(
                sql.SQL("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = %s
                AND pid <> pg_backend_pid()
                """),
                [DB_NAME]
            )

            # 删除数据库（如果存在）
            print(f"正在删除数据库 {DB_NAME}...")
            cursor.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(
                    sql.Identifier(DB_NAME)
                )
            )

            # 创建数据库
            print(f"正在创建数据库 {DB_NAME}...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {} WITH OWNER = {}").format(
                    sql.Identifier(DB_NAME),
                    sql.Identifier(DB_USER)
                )
            )

            print("数据库重置成功")
    except Exception as e:
        print(f"数据库重置失败: {e}")
        sys.exit(1)
    finally:
        conn.close()

    # 返回成功
    return 0

if __name__ == "__main__":
    sys.exit(main())
