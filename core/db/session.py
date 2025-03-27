"""数据库会话管理

提供SQLite数据库连接和会话管理功能，支持本地存储。
"""

from typing import Generator, Optional, Dict, Any
import os
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool
import json
from loguru import logger

from core.config import Config

# 创建基类
Base = declarative_base()

# 获取配置
config = Config()

# 数据库目录
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# 数据库文件路径
DB_FILE = os.path.join(DB_DIR, "genflow.db")

# 创建数据库引擎
engine = create_engine(
    f"sqlite:///{DB_FILE}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# 注册SQLite外部函数 - 支持JSON操作
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """设置SQLite连接参数"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """获取数据库会话的上下文管理器

    使用方法:
    ```python
    with get_db() as db:
        result = db.query(Model).all()
    ```

    Returns:
        Session: 数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """初始化数据库，创建所有表"""
    logger.info("正在初始化数据库...")
    Base.metadata.create_all(bind=engine)
    logger.info(f"数据库初始化完成，数据存储在: {DB_FILE}")

def get_or_create(db: Session, model, **kwargs) -> tuple[Any, bool]:
    """获取或创建数据库对象

    如果对象已存在，返回现有对象，否则创建新对象

    Args:
        db: 数据库会话
        model: 模型类
        **kwargs: 过滤条件

    Returns:
        tuple: (对象, 是否新创建)
    """
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance, True

def export_to_json(export_path: Optional[str] = None) -> Dict[str, Any]:
    """将数据库导出为JSON格式

    Args:
        export_path: 可选的导出文件路径

    Returns:
        Dict[str, Any]: 导出的数据字典
    """
    from core.db.models import ContentType, ArticleStyle, Platform

    result = {}

    with get_db() as db:
        # 导出内容类型
        content_types = db.query(ContentType).all()
        result["content_types"] = [ct.to_dict() for ct in content_types]

        # 导出文章风格
        styles = db.query(ArticleStyle).all()
        result["article_styles"] = [style.to_dict() for style in styles]

        # 导出平台
        platforms = db.query(Platform).all()
        result["platforms"] = [platform.to_dict() for platform in platforms]

    # 如果指定了导出路径，将结果写入文件
    if export_path:
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    return result

def import_from_json(import_path: str) -> bool:
    """从JSON文件导入数据

    Args:
        import_path: 导入文件路径

    Returns:
        bool: 是否成功导入
    """
    from core.db.models import ContentType, ArticleStyle, Platform

    if not os.path.exists(import_path):
        logger.error(f"导入文件不存在: {import_path}")
        return False

    try:
        with open(import_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        with get_db() as db:
            # 导入内容类型
            for ct_data in data.get("content_types", []):
                ct, created = get_or_create(db, ContentType, id=ct_data["id"])
                if created or ct_data.get("update_if_exists", True):
                    for key, value in ct_data.items():
                        if key != "id" and hasattr(ct, key):
                            setattr(ct, key, value)

            # 导入文章风格
            for style_data in data.get("article_styles", []):
                style, created = get_or_create(db, ArticleStyle, id=style_data["id"])
                if created or style_data.get("update_if_exists", True):
                    for key, value in style_data.items():
                        if key != "id" and hasattr(style, key):
                            setattr(style, key, value)

            # 导入平台
            for platform_data in data.get("platforms", []):
                platform, created = get_or_create(db, Platform, id=platform_data["id"])
                if created or platform_data.get("update_if_exists", True):
                    for key, value in platform_data.items():
                        if key != "id" and hasattr(platform, key):
                            setattr(platform, key, value)

            db.commit()

        logger.info(f"已从 {import_path} 成功导入数据")
        return True

    except Exception as e:
        logger.error(f"导入数据失败: {str(e)}")
        return False
