from redis import Redis
from fastapi import Depends, Cookie
from typing import Optional

from core.config import settings
from db.session import get_db


def get_redis_url() -> str:
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"


def get_redis_client() -> Redis:
    redis = Redis.from_url(
        get_redis_url(),
        max_connections=10,
        encoding="utf8",
        decode_responses=True,
    )
    return redis


def get_refresh_token_from_cookie(refresh_token: Optional[str] = Cookie(None, alias="refresh_token")) -> Optional[str]:
    """从Cookie中获取refresh_token"""
    return refresh_token
