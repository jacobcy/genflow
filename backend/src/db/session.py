from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from backend.src.core.config import settings


# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    poolclass=NullPool,
    echo=settings.DEBUG,
)

# 创建同步引擎（用于非异步上下文）
sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 创建同步会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


async def init_db() -> None:
    """初始化数据库"""
    from backend.src.models.base import Base  # 避免循环导入

    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


def get_db() -> Generator[Session, None, None]:
    """获取同步数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
