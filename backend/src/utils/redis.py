from typing import Optional
import logging

import redis.asyncio as redis
from redis.asyncio import Redis

from core.config import settings

logger = logging.getLogger(__name__)
_redis_client: Optional[Redis] = None


async def get_redis_client() -> Redis:
    """获取 Redis 客户端实例"""
    global _redis_client

    if _redis_client is None:
        try:
            logger.info(f"正在连接Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            _redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,  # 设置连接超时
                socket_timeout=5,          # 设置操作超时
            )
            # 测试连接
            await _redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            # 返回一个空的Redis客户端，以便应用可以继续运行
            # 在生产环境中可能需要更强的错误处理
            _redis_client = redis.Redis.from_pool(redis.ConnectionPool())

    return _redis_client


async def close_redis_connection() -> None:
    """关闭 Redis 连接"""
    global _redis_client

    if _redis_client is not None:
        try:
            await _redis_client.close()
            logger.info("Redis连接已关闭")
        except Exception as e:
            logger.error(f"关闭Redis连接时出错: {e}")
        finally:
            _redis_client = None
