import logging
import uuid

from backend.src.db.session import engine, async_session_maker
from backend.src.models.base import Base
# 显式导入所有模型，确保它们被包含在 metadata 中
from backend.src.models.user import User
from backend.src.models.article import Article, Tag, article_tag
from backend.src.core.security import get_password_hash
from backend.src.core.config import settings
from sqlalchemy import text, inspect
from sqlalchemy.schema import CreateTable


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database() -> None:
    """初始化数据库，创建所有表"""
    # 导入所有模型确保元数据完整

    async with engine.begin() as conn:
        try:
            # 检查用户表是否存在（作为示例）
            exists = await conn.run_sync(
                lambda sync_conn: sync_conn.dialect.has_table(sync_conn, "user")
            )

            if not exists:
                logger.info("Creating database tables... / 创建数据库表...")
                # 导出创建表的SQL以便调试
                for table in Base.metadata.sorted_tables:
                    create_stmt = CreateTable(table).compile(engine.dialect)
                    logger.debug(f"Creating table {table.name}: {create_stmt} / 创建表 {table.name}: {create_stmt}")

                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created / 数据库表创建完成")
            else:
                logger.info("Database tables already exist / 数据库表已存在")
        except Exception as e:
            logger.error(f"Error checking or creating database tables: {e} / 检查或创建数据库表时出错: {e}")
            # 显示更详细的错误信息
            logger.exception("Detailed error information / 详细错误信息:")
            raise


async def create_first_admin() -> None:
    """创建初始管理员账户"""
    try:
        async with async_session_maker() as session:
            # 检查是否已存在管理员
            admin_exists = False
            try:
                result = await session.scalar(
                    text("SELECT EXISTS(SELECT 1 FROM \"user\" WHERE email = :email)"),
                    {"email": settings.ADMIN_EMAIL}
                )
                admin_exists = result
            except Exception as e:
                logger.error(f"Error checking if admin exists: {e} / 检查管理员是否存在时出错: {e}")
                admin_exists = False

            if not admin_exists:
                logger.info(f"Creating admin user: {settings.ADMIN_EMAIL} / 创建管理员用户: {settings.ADMIN_EMAIL}")
                admin_user = User(
                    id=uuid.uuid4(),  # 为用户生成 UUID
                    email=settings.ADMIN_EMAIL,
                    hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                    is_active=True,  # 使用布尔值，而不是字符串 "True"
                    name="Administrator",
                    role="admin"  # 使用 role 字段标识管理员
                )
                session.add(admin_user)
                await session.commit()
                logger.info("Admin user created successfully / 管理员用户创建成功")
            else:
                logger.info("Admin user already exists / 管理员用户已存在")
    except Exception as e:
        logger.error(f"Error creating admin user: {e} / 创建管理员用户时出错: {e}")
        raise
