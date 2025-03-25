from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.core.config import settings


# 创建异步引擎
engine = create_async_engine(
    settings.sync_database_url.replace("postgresql://", "postgresql+asyncpg://"),
    poolclass=NullPool,
    echo=settings.DEBUG,
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """初始化数据库"""
    from src.models.base import Base  # 避免循环导入
    
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
