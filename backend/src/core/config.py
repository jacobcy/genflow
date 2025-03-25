import logging
from typing import Any, Optional, Union, List
from pathlib import Path

from pydantic import AnyHttpUrl, Field, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[
            Path(__file__).parents[3] / ".env",  # 全局配置
            Path(__file__).parents[2] / ".env",  # 后端配置
        ],
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",  # 允许额外的环境变量
    )

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # SERVER_NAME: Optional[str] = Field(..., env="NGINX_HOST")
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    LOG_LEVEL: Union[int, str] = Field(default=logging.INFO)

    @field_validator("LOG_LEVEL", mode="before")
    def validate_log_level(cls, v):
        if isinstance(v, str):
            # 将字符串日志级别转换为整数
            log_levels = {
                "CRITICAL": logging.CRITICAL,
                "ERROR": logging.ERROR,
                "WARNING": logging.WARNING,
                "INFO": logging.INFO,
                "DEBUG": logging.DEBUG,
                "NOTSET": logging.NOTSET
            }
            return log_levels.get(v.upper(), logging.INFO)
        return v

    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=True)

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "genflow"
    POSTGRES_URL: Union[Optional[PostgresDsn], Optional[str]] = None

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    DB_POOL_SIZE: int = Field(default=83)
    WEB_CONCURRENCY: int = Field(default=9)
    MAX_OVERFLOW: int = Field(default=64)
    POOL_SIZE: Optional[int] = None

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GenFlow Backend"

    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []

    # OpenAI
    OPENAI_API_KEY: str = ""

    # JWT
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 7200  # 2小时
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 604800  # 7天
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"

    # 速率限制
    RATE_LIMIT: int = 100
    RATE_LIMIT_PERIOD: int = 60  # 1分钟

    # Sentry
    SENTRY_DSN: str | None = None

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 4
    RELOAD: bool = True

    # 数据库配置
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_HOST: str | None = None
    DB_NAME: str | None = None
    DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_url(cls, v: str | None, values) -> str:
        if v:
            return v
        return f"postgresql://{values.data['DB_USER']}:{values.data['DB_PASSWORD']}@{values.data['DB_HOST']}/{values.data['DB_NAME']}"

    # 日志配置
    LOG_FORMAT: str = "json"

    # 性能监控配置
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # 缓存配置
    CACHE_EXPIRE_MINUTES: int = 15

    # 文件上传配置
    MAX_UPLOAD_SIZE: Union[int, str] = Field(default=5 * 1024 * 1024)  # 5MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf"]
    UPLOAD_DIR: str = "uploads"

    @field_validator("MAX_UPLOAD_SIZE", mode="before")
    def validate_max_upload_size(cls, v):
        if isinstance(v, str):
            # 尝试提取数字部分
            import re
            num_str = re.match(r'^\d+', v)
            if num_str:
                return int(num_str.group(0))
            return 5 * 1024 * 1024  # 默认 5MB
        return v

    @property
    def SECRET_KEY_BYTES(self) -> bytes:
        return self.SECRET_KEY.encode()

    @field_validator("POOL_SIZE", mode="before")
    @classmethod
    def build_pool(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, int):
            return v

        return max(values.data.get("DB_POOL_SIZE") // values.data.get("WEB_CONCURRENCY"), 5)  # type: ignore

    @field_validator("POSTGRES_URL", mode="before")
    @classmethod
    def build_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str) and len(v) > 0:
            return v

        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        ).unicode_string()

    @property
    def sync_database_url(self) -> str:
        if self.POSTGRES_URL:
            return self.POSTGRES_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[AnyHttpUrl]:
        if isinstance(v, str):
            return [AnyHttpUrl(origin.strip()) for origin in v.split(",")]
        return v


settings = Settings()
