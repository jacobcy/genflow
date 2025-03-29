"""数据仓库模式实现

为各种模型提供数据访问层，隔离数据库操作与业务逻辑。
"""

from typing import List, Optional, Dict, Any, Type, TypeVar, Generic
from sqlalchemy.orm import Session
import json
from datetime import datetime
import logging

from core.models.db.session import get_db, get_or_create
from core.models.db import  ContentType, ArticleStyle, Platform, Article, Topic

# 创建logger
logger = logging.getLogger(__name__)

# 定义泛型类型变量
T = TypeVar('T')
ModelType = TypeVar('ModelType')

class BaseRepository(Generic[ModelType]):
    """基础数据仓库，提供通用CRUD操作"""

    def __init__(self, model: Type[ModelType], db: Optional[Session] = None):
        """初始化

        Args:
            model: 模型类
            db: 数据库会话，如果为None则自动创建
        """
        self.model = model
        self.db = db or get_db()

    def get(self, id: str) -> Optional[ModelType]:
        """根据ID获取记录

        Args:
            id: 记录ID

        Returns:
            Optional[ModelType]: 记录对象
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> List[ModelType]:
        """获取所有记录

        Returns:
            List[ModelType]: 记录列表
        """
        return self.db.query(self.model).all()

    def get_enabled(self) -> List[ModelType]:
        """获取所有启用的记录

        Returns:
            List[ModelType]: 记录列表
        """
        return self.db.query(self.model).filter(self.model.is_enabled == True).all()

    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """创建新记录

        Args:
            obj_in: 输入数据

        Returns:
            ModelType: 创建的记录
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: str, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """更新记录

        Args:
            id: 记录ID
            obj_in: 更新数据

        Returns:
            Optional[ModelType]: 更新后的记录
        """
        db_obj = self.db.query(self.model).filter(self.model.id == id).first()
        if db_obj is None:
            return None

        for key, value in obj_in.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: str) -> bool:
        """删除记录

        Args:
            id: 记录ID

        Returns:
            bool: 是否成功删除
        """
        db_obj = self.db.query(self.model).filter(self.model.id == id).first()
        if db_obj is None:
            return False

        self.db.delete(db_obj)
        self.db.commit()
        return True

    def get_or_create(self, **kwargs) -> tuple[ModelType, bool]:
        """获取或创建记录

        Args:
            **kwargs: 过滤条件

        Returns:
            tuple: (对象, 是否新创建)
        """
        return get_or_create(self.db, self.model, **kwargs)

class ContentTypeRepository(BaseRepository[ContentType]):
    """内容类型数据仓库"""

    def __init__(self):
        super().__init__(ContentType)

    def get_compatible_with_style(self, style_id: str) -> List[ContentType]:
        """获取与指定风格兼容的内容类型

        Args:
            style_id: 风格ID

        Returns:
            List[ContentType]: 内容类型列表
        """
        style = self.db.query(ArticleStyle).filter(ArticleStyle.id == style_id).first()
        if not style:
            return []
        return style.compatible_content_types

    def add_compatible_style(self, content_type_id: str, style_id: str) -> bool:
        """添加兼容风格

        Args:
            content_type_id: 内容类型ID
            style_id: 风格ID

        Returns:
            bool: 是否成功
        """
        content_type = self.db.query(ContentType).filter(ContentType.id == content_type_id).first()
        style = self.db.query(ArticleStyle).filter(ArticleStyle.id == style_id).first()

        if not content_type or not style:
            return False

        # 检查是否已经存在关联
        if style in content_type.compatible_styles:
            return True

        content_type.compatible_styles.append(style)
        self.db.commit()
        return True

    def remove_compatible_style(self, content_type_id: str, style_id: str) -> bool:
        """移除兼容风格

        Args:
            content_type_id: 内容类型ID
            style_id: 风格ID

        Returns:
            bool: 是否成功
        """
        content_type = self.db.query(ContentType).filter(ContentType.id == content_type_id).first()
        style = self.db.query(ArticleStyle).filter(ArticleStyle.id == style_id).first()

        if not content_type or not style:
            return False

        # 检查是否存在关联
        if style not in content_type.compatible_styles:
            return True

        content_type.compatible_styles.remove(style)
        self.db.commit()
        return True

class ArticleStyleRepository(BaseRepository[ArticleStyle]):
    """文章风格数据仓库"""

    def __init__(self):
        super().__init__(ArticleStyle)

    def get_compatible_with_content_type(self, content_type_id: str) -> List[ArticleStyle]:
        """获取与指定内容类型兼容的风格

        Args:
            content_type_id: 内容类型ID

        Returns:
            List[ArticleStyle]: 风格列表
        """
        content_type = self.db.query(ContentType).filter(ContentType.id == content_type_id).first()
        if not content_type:
            return []
        return content_type.compatible_styles

class PlatformRepository(BaseRepository[Platform]):
    """平台数据仓库"""

    def __init__(self):
        super().__init__(Platform)

    def get_by_type(self, platform_type: str) -> List[Platform]:
        """根据平台类型获取平台

        Args:
            platform_type: 平台类型

        Returns:
            List[Platform]: 平台列表
        """
        return self.db.query(Platform).filter(Platform.platform_type == platform_type).all()

    def search_by_name(self, name: str) -> List[Platform]:
        """根据名称搜索平台

        Args:
            name: 平台名称关键词

        Returns:
            List[Platform]: 平台列表
        """
        return self.db.query(Platform).filter(Platform.name.ilike(f"%{name}%")).all()

class ArticleRepository(BaseRepository[Article]):
    """文章数据仓库，提供基础的CRUD操作"""

    def __init__(self, db: Optional[Session] = None):
        """初始化仓库

        Args:
            db: 数据库会话，如果为None则自动创建
        """
        super().__init__(Article, db)

    def get_by_topic_id(self, topic_id: str) -> List[Article]:
        """获取指定话题的所有文章

        Args:
            topic_id: 话题ID

        Returns:
            List[Article]: 文章列表
        """
        return self.db.query(self.model).filter(self.model.topic_id == topic_id).all()

    def query_by_time_range(self, start_time: int, end_time: int) -> List[Article]:
        """通过时间范围查询文章

        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳

        Returns:
            List[Article]: 文章列表
        """
        return self.db.query(self.model).filter(
            self.model.created_at >= start_time,
            self.model.created_at <= end_time
        ).all()

    def get_latest(self, limit: int = 10) -> List[Article]:
        """获取最新文章列表

        Args:
            limit: 返回数量限制

        Returns:
            List[Article]: 文章列表
        """
        return self.db.query(self.model).order_by(self.model.created_at.desc()).limit(limit).all()

class TopicRepository(BaseRepository[Topic]):
    """话题数据仓库，提供基础的CRUD操作"""

    def __init__(self, db: Optional[Session] = None):
        """初始化仓库

        Args:
            db: 数据库会话，如果为None则自动创建
        """
        super().__init__(Topic, db)

    def get_by_platform(self, platform: str) -> List[Topic]:
        """获取指定平台的所有话题

        Args:
            platform: 平台标识

        Returns:
            List[Topic]: 话题列表
        """
        return self.db.query(self.model).filter(self.model.platform == platform).all()

    def query_by_time_range(self, start_time: int, end_time: int) -> List[Topic]:
        """通过时间范围查询话题

        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳

        Returns:
            List[Topic]: 话题列表
        """
        return self.db.query(self.model).filter(
            self.model.source_time >= start_time,
            self.model.source_time <= end_time
        ).all()

    def get_latest(self, limit: int = 10) -> List[Topic]:
        """获取最新话题列表，按照source_time降序排序

        Args:
            limit: 返回数量限制

        Returns:
            List[Topic]: 话题列表
        """
        return self.db.query(self.model).order_by(self.model.source_time.desc()).limit(limit).all()

# 创建仓库实例
content_type_repo = ContentTypeRepository()
article_style_repo = ArticleStyleRepository()
platform_repo = PlatformRepository()
article_repo = ArticleRepository()
topic_repo = TopicRepository()
