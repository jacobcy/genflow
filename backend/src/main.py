import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parents[2]  # 项目根目录
BACKEND_SRC = Path(__file__).parent       # backend/src 目录
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BACKEND_SRC))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

print(f"Python路径: {sys.path}")
print(f"当前工作目录: {os.getcwd()}")

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from api.v1 import api_router
from core.config import settings
from core.exceptions import register_exception_handlers
from db.session import init_db
from middleware import RequestHeadersMiddleware
from utils.redis import get_redis_client


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        # 确保所有模型都已导入
        import models.article  # 导入所有模型以确保它们被注册
        import models.user

        # Initialize database
        logger.info("正在初始化数据库...")
        try:
            await init_db()
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            logger.exception("详细错误信息:")
            # 在生产环境中，可能需要重新抛出异常以防止应用启动
            if not settings.DEBUG:
                raise

        # Initialize Redis cache
        try:
            logger.info("正在初始化Redis缓存...")
            redis_client = await get_redis_client()
            FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
            logger.info("Redis缓存初始化成功")
        except Exception as e:
            logger.error(f"Redis缓存初始化失败: {e}")
            logger.warning("应用将在没有缓存的情况下继续运行")

        logger.info("启动完成")
        yield
    except Exception as e:
        logger.error(f"启动失败: {e}")
        logger.exception("详细错误信息:")
        raise
    finally:
        # Cleanup
        logger.info("正在关闭应用...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=f"{settings.PROJECT_NAME} API",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# 注册异常处理器
register_exception_handlers(app)

# 添加请求头中间件
app.add_middleware(RequestHeadersMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info",
    )
