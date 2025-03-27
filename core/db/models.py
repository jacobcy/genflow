"""数据库模型定义

定义内容类型、文章风格和平台等数据模型，用于本地存储和管理。
"""

from typing import Dict, List, Optional, Any, Set
import json
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.types import TypeDecorator, TEXT

from core.db.session import Base

class JSONEncodedDict(TypeDecorator):
    """存储和检索JSON格式的字典"""
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value, ensure_ascii=False)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

# 创建内容类型和文章风格的多对多关系表
content_type_style = Table(
    "content_type_style",
    Base.metadata,
    Column("content_type_id", String(50), ForeignKey("content_type.id", ondelete="CASCADE"), primary_key=True),
    Column("style_id", String(50), ForeignKey("article_style.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True  # 允许重新定义已存在的表
)

class Topic(Base):
    """话题数据模型"""
    __tablename__ = "topic"
    __table_args__ = {'extend_existing': True}  # 允许重新定义已存在的表

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    platform = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True, default="")
    url = Column(String(500), nullable=True, default="")
    mobile_url = Column(String(500), nullable=True, default="")
    cover = Column(String(500), nullable=True, default="")
    hot = Column(Integer, nullable=False, default=0)
    trend_score = Column(Float, nullable=False, default=0.0)

    # 时间信息
    timestamp = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))
    fetch_time = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))
    expire_time = Column(Integer, nullable=False, default=lambda: int((datetime.now() + datetime.timedelta(days=7)).timestamp()))

    # 分类信息
    categories = Column(Text, nullable=True, default="[]")  # JSON格式存储分类列表
    tags = Column(Text, nullable=True, default="[]")  # JSON格式存储标签
    content_type = Column(String(50), nullable=True)

    # 状态管理
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, selected, rejected

    # 元数据
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # 自定义元数据字段
    meta_json = Column(Text, nullable=True, default="{}")  # 改名避免与SQLAlchemy的metadata属性冲突

    def __repr__(self):
        return f"<Topic {self.id}:{self.title}>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示

        Returns:
            Dict: 话题数据字典
        """
        # 反序列化JSON字段
        try:
            categories = json.loads(self.categories) if self.categories else []
        except:
            categories = []

        try:
            tags = json.loads(self.tags) if self.tags else []
        except:
            tags = []

        try:
            meta_data = json.loads(self.meta_json) if self.meta_json else {}
        except:
            meta_data = {}

        return {
            "id": self.id,
            "title": self.title,
            "platform": self.platform,
            "description": self.description,
            "url": self.url,
            "mobile_url": self.mobile_url,
            "cover": self.cover,
            "hot": self.hot,
            "trend_score": self.trend_score,
            "timestamp": self.timestamp,
            "fetch_time": self.fetch_time,
            "expire_time": self.expire_time,
            "categories": categories,
            "tags": tags,
            "content_type": self.content_type,
            "status": self.status,
            "metadata": meta_data,  # 返回时使用原名metadata
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Topic":
        """从字典创建模型实例

        Args:
            data: 话题数据字典

        Returns:
            Topic: 话题模型实例
        """
        # 序列化JSON字段
        categories = json.dumps(data.get("categories", []))
        tags = json.dumps(data.get("tags", []))

        # 处理元数据字段
        meta_data = data.get("metadata", {})
        meta_json = json.dumps(meta_data) if meta_data else "{}"

        return cls(
            id=data.get("id"),
            title=data.get("title"),
            platform=data.get("platform"),
            description=data.get("description", ""),
            url=data.get("url", ""),
            mobile_url=data.get("mobile_url", ""),
            cover=data.get("cover", ""),
            hot=data.get("hot", 0),
            trend_score=data.get("trend_score", 0.0),
            timestamp=data.get("timestamp", int(datetime.now().timestamp())),
            fetch_time=data.get("fetch_time", int(datetime.now().timestamp())),
            expire_time=data.get("expire_time", int((datetime.now() + datetime.timedelta(days=7)).timestamp())),
            categories=categories,
            tags=tags,
            content_type=data.get("content_type"),
            status=data.get("status", "pending"),
            meta_json=meta_json
        )

class ContentType(Base):
    """内容类型模型"""
    __tablename__ = "content_type"
    __table_args__ = {'extend_existing': True}  # 允许重新定义已存在的表

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    default_word_count = Column(String(50), nullable=True)
    is_enabled = Column(Boolean, default=True)

    # 模板配置
    prompt_template = Column(Text, nullable=True)
    output_format = Column(JSONEncodedDict, nullable=True)

    # 所需的文章元素
    required_elements = Column(JSONEncodedDict, nullable=True)
    optional_elements = Column(JSONEncodedDict, nullable=True)

    # 与文章风格的多对多关系
    compatible_styles = relationship("ArticleStyle", secondary=content_type_style,
                                    back_populates="compatible_content_types")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ContentType {self.id}:{self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "default_word_count": self.default_word_count,
            "is_enabled": self.is_enabled,
            "prompt_template": self.prompt_template,
            "output_format": self.output_format,
            "required_elements": self.required_elements,
            "optional_elements": self.optional_elements,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def is_compatible_with_style(self, style_id: str) -> bool:
        """检查是否与指定风格兼容

        Args:
            style_id: 风格ID

        Returns:
            bool: 是否兼容
        """
        for style in self.compatible_styles:
            if style.id == style_id:
                return True
        return False

class ArticleStyle(Base):
    """文章风格模型"""
    __tablename__ = "article_style"
    __table_args__ = {'extend_existing': True}  # 允许重新定义已存在的表

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)

    # 风格特性
    tone = Column(String(100), nullable=True)
    style_characteristics = Column(JSONEncodedDict, nullable=True)
    language_preference = Column(JSONEncodedDict, nullable=True)
    writing_format = Column(JSONEncodedDict, nullable=True)

    # 模板配置
    prompt_template = Column(Text, nullable=True)
    example = Column(Text, nullable=True)

    # 与内容类型的多对多关系
    compatible_content_types = relationship("ContentType", secondary=content_type_style,
                                         back_populates="compatible_styles")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ArticleStyle {self.id}:{self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_enabled": self.is_enabled,
            "tone": self.tone,
            "style_characteristics": self.style_characteristics,
            "language_preference": self.language_preference,
            "writing_format": self.writing_format,
            "prompt_template": self.prompt_template,
            "example": self.example,
            "content_types": [ct.id for ct in self.compatible_content_types],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def is_compatible_with_content_type(self, content_type_id: str) -> bool:
        """检查是否与指定内容类型兼容

        Args:
            content_type_id: 内容类型ID

        Returns:
            bool: 是否兼容
        """
        for ct in self.compatible_content_types:
            if ct.id == content_type_id:
                return True
        return False

class Platform(Base):
    """平台配置模型"""
    __tablename__ = "platform"
    __table_args__ = {'extend_existing': True}  # 允许重新定义已存在的表

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)

    # 平台特性
    platform_type = Column(String(50), nullable=True)
    url = Column(String(255), nullable=True)
    logo_url = Column(String(255), nullable=True)

    # 平台限制
    max_title_length = Column(JSONEncodedDict, nullable=True)
    max_content_length = Column(JSONEncodedDict, nullable=True)
    allowed_media_types = Column(JSONEncodedDict, nullable=True)

    # API配置
    api_config = Column(JSONEncodedDict, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Platform {self.id}:{self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_enabled": self.is_enabled,
            "platform_type": self.platform_type,
            "url": self.url,
            "logo_url": self.logo_url,
            "max_title_length": self.max_title_length,
            "max_content_length": self.max_content_length,
            "allowed_media_types": self.allowed_media_types,
            "api_config": self.api_config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# 创建默认数据加载函数
def get_default_content_type() -> ContentType:
    """获取默认内容类型

    Returns:
        ContentType: 默认内容类型
    """
    return ContentType(
        id="general_article",
        name="通用文章",
        description="适用于大多数场景的通用文章格式",
        default_word_count="1000-2000",
        is_enabled=True,
        prompt_template="请创作一篇关于{topic}的文章，包含以下要点：{points}",
        output_format={
            "title": "文章标题",
            "content": "文章内容"
        },
        required_elements={
            "title": "必须有一个吸引人的标题",
            "introduction": "开篇介绍主题",
            "body": "主体内容",
            "conclusion": "总结观点"
        },
        optional_elements={
            "subheadings": "可以包含小标题",
            "examples": "可以包含示例",
            "quotes": "可以包含引述"
        }
    )

def get_default_article_style() -> ArticleStyle:
    """获取默认文章风格

    Returns:
        ArticleStyle: 默认文章风格
    """
    return ArticleStyle(
        id="standard",
        name="标准风格",
        description="中性的、专业的标准写作风格",
        is_enabled=True,
        tone="专业、中立",
        style_characteristics={
            "formality": "中等",
            "complexity": "中等",
            "audience": "一般读者"
        },
        language_preference={
            "sentence_length": "中等",
            "vocabulary": "中等",
            "emotion": "中性"
        },
        writing_format={
            "paragraph_structure": "标准",
            "headings": "清晰明了",
            "transitions": "自然流畅"
        },
        prompt_template="请使用专业、中立的语气撰写这篇文章，使用中等长度的句子和段落，确保内容清晰易懂。",
        example="这是一个示例文章，展示了标准风格的写作特点。段落结构清晰，句子长度适中，语言表达专业而不失亲和力。"
    )

def get_default_platform() -> Platform:
    """获取默认平台配置

    Returns:
        Platform: 默认平台配置
    """
    return Platform(
        id="website",
        name="网站",
        description="通用网站发布平台",
        is_enabled=True,
        platform_type="website",
        url="",
        logo_url="",
        max_title_length={"min": 10, "max": 100},
        max_content_length={"min": 100, "max": 50000},
        allowed_media_types={"image": ["jpg", "png", "gif"], "video": [], "audio": []},
        api_config={}
    )

class Article(Base):
    """文章数据库模型"""
    __tablename__ = "article"
    __table_args__ = {'extend_existing': True}  # 允许重新定义已存在的表

    id = Column(String(50), primary_key=True, index=True)
    topic_id = Column(String(50), nullable=False, index=True)
    outline_id = Column(String(50), nullable=True)

    # 核心内容
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    sections = Column(Text, nullable=False, default="[]")  # JSON格式存储章节
    tags = Column(Text, nullable=True, default="[]")  # JSON格式存储标签
    keywords = Column(Text, nullable=True, default="[]")  # JSON格式存储关键词

    # 媒体元素
    cover_image = Column(String(500), nullable=True)
    cover_image_alt = Column(String(500), nullable=True)
    images = Column(Text, nullable=True, default="[]")  # JSON格式存储图片

    # 分类与类型
    content_type = Column(String(50), nullable=False, default="default")
    categories = Column(Text, nullable=True, default="[]")  # JSON格式存储分类

    # 元数据
    author = Column(String(100), nullable=False, default="AI")
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    word_count = Column(Integer, nullable=False, default=0)
    read_time = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=1)

    # 状态管理
    status = Column(String(50), nullable=False, default="initialized", index=True)
    is_published = Column(Boolean, nullable=False, default=False)

    # 风格相关
    style_id = Column(String(50), nullable=True)

    # 平台相关
    platform_id = Column(String(50), nullable=True)
    platform_url = Column(String(500), nullable=True)

    # 审核相关
    review = Column(Text, nullable=True, default="{}")  # JSON格式存储审核结果

    # 其他元数据
    meta_json = Column(Text, nullable=True, default="{}")  # JSON格式存储元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示

        Returns:
            Dict: 文章数据字典
        """
        # 反序列化JSON字段
        try:
            sections = json.loads(self.sections) if self.sections else []
        except:
            sections = []

        try:
            tags = json.loads(self.tags) if self.tags else []
        except:
            tags = []

        try:
            keywords = json.loads(self.keywords) if self.keywords else []
        except:
            keywords = []

        try:
            images = json.loads(self.images) if self.images else []
        except:
            images = []

        try:
            categories = json.loads(self.categories) if self.categories else []
        except:
            categories = []

        try:
            review = json.loads(self.review) if self.review else {}
        except:
            review = {}

        try:
            metadata = json.loads(self.meta_json) if self.meta_json else {}
        except:
            metadata = {}

        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "outline_id": self.outline_id,
            "title": self.title,
            "summary": self.summary,
            "sections": sections,
            "tags": tags,
            "keywords": keywords,
            "cover_image": self.cover_image,
            "cover_image_alt": self.cover_image_alt,
            "images": images,
            "content_type": self.content_type,
            "categories": categories,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "word_count": self.word_count,
            "read_time": self.read_time,
            "version": self.version,
            "status": self.status,
            "is_published": self.is_published,
            "style_id": self.style_id,
            "platform_id": self.platform_id,
            "platform_url": self.platform_url,
            "review": review,
            "metadata": metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Article":
        """从字典创建模型实例

        Args:
            data: 文章数据字典

        Returns:
            Article: 文章模型实例
        """
        # 序列化JSON字段
        sections = json.dumps(data.get("sections", []))
        tags = json.dumps(data.get("tags", []))
        keywords = json.dumps(data.get("keywords", []))
        images = json.dumps(data.get("images", []))
        categories = json.dumps(data.get("categories", []))
        review = json.dumps(data.get("review", {}))
        meta_json = json.dumps(data.get("metadata", {}))

        created_at = data.get("created_at", datetime.now())
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except:
                created_at = datetime.now()

        updated_at = data.get("updated_at", datetime.now())
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at)
            except:
                updated_at = datetime.now()

        return cls(
            id=data.get("id"),
            topic_id=data.get("topic_id"),
            outline_id=data.get("outline_id"),
            title=data.get("title"),
            summary=data.get("summary"),
            sections=sections,
            tags=tags,
            keywords=keywords,
            cover_image=data.get("cover_image"),
            cover_image_alt=data.get("cover_image_alt"),
            images=images,
            content_type=data.get("content_type", "default"),
            categories=categories,
            author=data.get("author", "AI"),
            created_at=created_at,
            updated_at=updated_at,
            word_count=data.get("word_count", 0),
            read_time=data.get("read_time", 0),
            version=data.get("version", 1),
            status=data.get("status", "initialized"),
            is_published=data.get("is_published", False),
            style_id=data.get("style_id"),
            platform_id=data.get("platform_id"),
            platform_url=data.get("platform_url"),
            review=review,
            meta_json=meta_json
        )

# 在文件末尾添加获取默认文章方法
def get_default_article() -> Optional[Dict[str, Any]]:
    """获取默认文章

    Returns:
        Optional[Dict]: 默认文章数据，如果不存在则返回None
    """
    from core.db.session import get_db
    db = next(get_db())
    article = db.query(Article).filter(Article.status == "completed").first()
    if article:
        return article.to_dict()
    return None
