"""数据仓库模式实现

为各种模型提供数据访问层，隔离数据库操作与业务逻辑。
"""

from typing import List, Optional, Dict, Any, Type, TypeVar, Generic
from sqlalchemy.orm import Session
import json
from datetime import datetime
import logging

from core.db.session import get_db, get_or_create
from core.db.models import ContentType, ArticleStyle, Platform, Article, Topic

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
    """文章数据仓库"""

    def __init__(self, db: Optional[Session] = None):
        """初始化仓库

        Args:
            db: 数据库会话，如果为None则自动创建
        """
        super().__init__(Article, db)

    def get_by_status(self, status: str) -> List[Dict[str, Any]]:
        """获取指定状态的所有文章

        Args:
            status: 文章状态

        Returns:
            List[Dict]: 文章列表
        """
        articles = self.db.query(self.model).filter(self.model.status == status).all()
        return [article.to_dict() for article in articles]

    def get_by_topic_id(self, topic_id: str) -> List[Dict[str, Any]]:
        """获取指定话题的所有文章

        Args:
            topic_id: 话题ID

        Returns:
            List[Dict]: 文章列表
        """
        articles = self.db.query(self.model).filter(self.model.topic_id == topic_id).all()
        return [article.to_dict() for article in articles]

    def update_status(self, id: str, status: str) -> Optional[Dict[str, Any]]:
        """更新文章状态

        Args:
            id: 文章ID
            status: 新状态

        Returns:
            Optional[Dict]: 更新后的文章数据，如果文章不存在则返回None
        """
        article = self.get(id)
        if not article:
            return None

        # 更新状态和时间
        now = datetime.now()
        db_article = self.db.query(self.model).filter(self.model.id == id).first()

        # 获取现有元数据并更新状态历史
        try:
            metadata = json.loads(db_article.metadata) if db_article.metadata else {}
        except:
            metadata = {}

        if "status_history" not in metadata:
            metadata["status_history"] = []

        metadata["status_history"].append({
            "status": status,
            "timestamp": now.isoformat()
        })

        # 更新数据库记录
        db_article.status = status
        db_article.updated_at = now
        db_article.metadata = json.dumps(metadata)

        try:
            self.db.commit()
            self.db.refresh(db_article)
            return db_article.to_dict()
        except:
            self.db.rollback()
            return None

    def create_or_update(self, article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建或更新文章

        Args:
            article_data: 文章数据

        Returns:
            Optional[Dict]: 创建或更新后的文章数据，失败则返回None
        """
        article_id = article_data.get("id")
        if not article_id:
            return None

        existing = self.get(article_id)

        try:
            if existing:
                # 更新现有文章
                db_article = self.db.query(self.model).filter(self.model.id == article_id).first()

                # 更新所有字段
                for key, value in article_data.items():
                    if key in ["sections", "tags", "keywords", "images", "categories", "review", "metadata"]:
                        # JSON字段需要序列化
                        setattr(db_article, key, json.dumps(value))
                    elif key not in ["created_at"]:  # 创建时间不更新
                        setattr(db_article, key, value)

                # 确保更新时间
                db_article.updated_at = datetime.now()

                self.db.commit()
                self.db.refresh(db_article)
                return db_article.to_dict()
            else:
                # 创建新文章
                db_article = Article.from_dict(article_data)
                self.db.add(db_article)
                self.db.commit()
                self.db.refresh(db_article)
                return db_article.to_dict()
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建或更新文章失败: {str(e)}")
            return None

class TopicRepository(BaseRepository[Topic]):
    """话题数据仓库"""

    def __init__(self, db: Optional[Session] = None):
        """初始化仓库

        Args:
            db: 数据库会话，如果为None则自动创建
        """
        super().__init__(Topic, db)

    def get_by_platform(self, platform: str) -> List[Dict[str, Any]]:
        """获取指定平台的所有话题

        Args:
            platform: 平台标识

        Returns:
            List[Dict]: 话题列表
        """
        topics = self.db.query(self.model).filter(self.model.platform == platform).all()
        return [topic.to_dict() for topic in topics]

    def get_by_status(self, status: str) -> List[Dict[str, Any]]:
        """获取指定状态的所有话题

        Args:
            status: 话题状态

        Returns:
            List[Dict]: 话题列表
        """
        topics = self.db.query(self.model).filter(self.model.status == status).all()
        return [topic.to_dict() for topic in topics]

    def update_status(self, id: str, status: str) -> Optional[Dict[str, Any]]:
        """更新话题状态

        Args:
            id: 话题ID
            status: 新状态

        Returns:
            Optional[Dict]: 更新后的话题数据，如果话题不存在则返回None
        """
        topic = self.get(id)
        if not topic:
            return None

        # 更新状态和时间
        topic.status = status
        topic.updated_at = datetime.now()

        try:
            self.db.commit()
            self.db.refresh(topic)
            return topic.to_dict()
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新话题状态失败: {str(e)}")
            return None

    def sync_from_redis(self, topics_data: List[Dict[str, Any]]) -> List[str]:
        """从Redis同步话题数据到数据库

        Args:
            topics_data: 话题数据列表

        Returns:
            List[str]: 成功同步的话题ID列表
        """
        synced_ids = []

        for topic_data in topics_data:
            topic_id = topic_data.get("id")
            if not topic_id:
                continue

            try:
                # 检查是否存在
                existing = self.get(topic_id)

                if existing:
                    # 更新现有话题
                    for key, value in topic_data.items():
                        if key in ["categories", "tags"]:
                            # 序列化JSON字段
                            setattr(existing, key, json.dumps(value))
                        elif key != "created_at":  # 创建时间不更新
                            setattr(existing, key, value)

                    # 确保更新时间
                    existing.updated_at = datetime.now()
                    self.db.commit()
                    self.db.refresh(existing)
                else:
                    # 创建新话题
                    new_topic = Topic.from_dict(topic_data)
                    self.db.add(new_topic)
                    self.db.commit()

                synced_ids.append(topic_id)
            except Exception as e:
                self.db.rollback()
                logger.error(f"同步话题数据失败 {topic_id}: {str(e)}")

        return synced_ids

    def get_latest_topics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最新的话题列表

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict]: 话题列表
        """
        topics = self.db.query(self.model).order_by(self.model.fetch_time.desc()).limit(limit).all()
        return [topic.to_dict() for topic in topics]

    def get_trending_topics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取热门话题列表

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict]: 话题列表
        """
        topics = self.db.query(self.model).order_by(self.model.trend_score.desc()).limit(limit).all()
        return [topic.to_dict() for topic in topics]

# 创建仓库实例
content_type_repo = ContentTypeRepository()
article_style_repo = ArticleStyleRepository()
platform_repo = PlatformRepository()
article_repo = ArticleRepository()
topic_repo = TopicRepository()
