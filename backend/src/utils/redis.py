from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from src.core.config import settings


_redis_client: Optional[Redis] = None


async def get_redis_client() -> Redis:
    """获取 Redis 客户端实例"""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
    
    return _redis_client


async def close_redis_connection() -> None:
    """关闭 Redis 连接"""
    global _redis_client
    
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None 