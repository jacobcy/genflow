#!/usr/bin/env python3
"""
GenFlow 数据库管理工具
功能：
1. 初始化数据库
2. 重置数据库
3. 创建迁移
4. 更新数据库结构
5. 创建初始管理员账号
"""
import asyncio
import os
import sys
import click
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# 设置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv()

# 先导入数据库模块
from backend.src.db.session import engine
from backend.src.models.base import Base
# 导入所有模型以确保它们被注册到元数据
from backend.src.models.user import User
from backend.src.models.article import Article, Tag, article_tag
from backend.src.core.security import get_password_hash
from backend.src.core.config import settings

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import text, select

async def get_db_url() -> str:
    """获取数据库 URL"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        db_url = settings.DATABASE_URL
    if not db_url:
        raise ValueError("未设置 DATABASE_URL 环境变量")

    # 确保异步数据库 URL
    if db_url.startswith('postgresql://'):
        db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)

    return db_url

async def create_database(db_url: str) -> None:
    """创建数据库（如果不存在）"""
    parsed = urlparse(db_url)
    db_name = parsed.path[1:]  # 移除开头的 /

    # 构建管理员连接 URL（连接到默认数据库）
    admin_url = f"{parsed.scheme}://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 5432}/postgres"

    engine = create_async_engine(admin_url)

    async with engine.connect() as conn:
        # 检查数据库是否存在
        result = await conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
        exists = result.scalar() is not None

        if not exists:
            await conn.execute(text("COMMIT"))  # 提交当前事务
            # 创建数据库
            await conn.execute(text(f"""
                CREATE DATABASE {db_name}
                WITH OWNER = {parsed.username}
                ENCODING 'UTF8'
                LC_COLLATE 'en_US.UTF-8'
                LC_CTYPE 'en_US.UTF-8'
                TEMPLATE template0
            """))
            logger.info(f"数据库 {db_name} 创建成功")
        else:
            logger.info(f"数据库 {db_name} 已存在")

async def drop_database(db_url: str) -> None:
    """删除数据库"""
    parsed = urlparse(db_url)
    db_name = parsed.path[1:]

    admin_url = f"{parsed.scheme}://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 5432}/postgres"
    engine = create_async_engine(admin_url)

    async with engine.connect() as conn:
        await conn.execute(text("COMMIT"))
        # 终止数据库连接
        await conn.execute(text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
            AND pid <> pg_backend_pid()
        """))
        # 删除数据库
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        logger.info(f"数据库 {db_name} 已删除")

async def init_tables(db_url: str) -> None:
    """初始化数据库表"""
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表创建成功")

async def create_admin_user(db_url: str, email: str, password: str) -> None:
    """创建管理员用户"""
    engine = create_async_engine(db_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # 检查是否已存在管理员用户
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin:
            admin = User(
                id=uuid.uuid4(),
                email=email,
                hashed_password=get_password_hash(password),
                is_active=True,
                name="Administrator",
                role="admin"
            )
            session.add(admin)
            await session.commit()
            logger.info(f"管理员用户 {email} 创建成功")
        else:
            logger.info(f"管理员用户 {email} 已存在")

@click.group()
def cli():
    """GenFlow 数据库管理工具"""
    pass

@cli.command()
@click.option('--email', default='admin@genflow.dev', help='管理员邮箱')
@click.option('--password', default='admin123', help='管理员密码')
def init(email: str, password: str):
    """初始化数据库和管理员用户"""
    async def _init():
        db_url = await get_db_url()
        await create_database(db_url)
        await init_tables(db_url)
        await create_admin_user(db_url, email, password)

    asyncio.run(_init())
    logger.info("数据库初始化完成")

@cli.command()
@click.confirmation_option(prompt='确认要重置数据库吗？所有数据将丢失！')
def reset():
    """重置数据库（删除并重新创建）"""
    async def _reset():
        db_url = await get_db_url()
        await drop_database(db_url)
        await create_database(db_url)
        await init_tables(db_url)
        await create_admin_user(db_url, 'admin@genflow.dev', 'admin123')

    asyncio.run(_reset())
    logger.info("数据库重置完成")

@cli.command()
def status():
    """检查数据库状态"""
    async def _status():
        try:
            db_url = await get_db_url()
            engine = create_async_engine(db_url)
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("数据库连接正常")

                # 获取数据库大小
                result = await conn.execute(text("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """))
                size = result.scalar()
                logger.info(f"数据库大小: {size}")

                # 获取表信息
                result = await conn.execute(text("""
                    SELECT tablename, pg_size_pretty(pg_total_relation_size(quote_ident(tablename)))
                    FROM pg_tables
                    WHERE schemaname = 'public'
                """))
                tables = result.fetchall()
                logger.info("\n表信息:")
                for table, size in tables:
                    logger.info(f"- {table}: {size}")

        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            sys.exit(1)

    asyncio.run(_status())

if __name__ == '__main__':
    cli()
