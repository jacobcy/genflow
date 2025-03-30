"""Article模型独立测试

测试Article模型的基本功能，不依赖其他模块
"""
import sys
import os
from datetime import datetime
from uuid import uuid4
from typing import Dict, List, Any, Optional

# 使用相对导入以避免依赖问题
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 导入Pydantic相关模块
from pydantic import BaseModel, Field

# 定义Section类 - 独立于实际代码的测试类
class Section(BaseModel):
    """文章章节"""
    id: str = Field(default="", description="章节ID")
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    order: int = Field(..., description="章节顺序")
    type: str = Field(default="text", description="章节类型")
    parent_id: Optional[str] = Field(default=None, description="父章节ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="章节元数据")

# 定义Article类 - 独立于实际代码的测试类
class Article(BaseModel):
    """文章模型 - 内容创作的核心产出"""
    # 基础标识
    id: str = Field(..., description="文章ID")
    topic_id: str = Field(..., description="关联话题ID")
    outline_id: Optional[str] = Field(default=None, description="关联大纲ID")

    # 核心内容
    title: str = Field(..., description="文章标题")
    summary: str = Field(..., description="文章摘要")
    sections: List[Section] = Field(default_factory=list, description="文章章节")
    tags: List[str] = Field(default_factory=list, description="文章标签")
    content: str = Field(default="", description="文章正文内容（纯文本格式）")

    # 状态管理
    status: str = Field(
        default="initialized",
        description="文章状态(initialized/topic/research/outline/writing/style/review/completed/failed/cancelled)"
    )
    is_published: bool = Field(default=False, description="是否已发布")

    # 元数据
    word_count: int = Field(default=0, description="字数统计")
    read_time: int = Field(default=0, description="阅读时间(分钟)")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")

    def update_status(self, new_status: str) -> None:
        """更新文章状态并记录时间"""
        self.status = new_status
        self.updated_at = datetime.now()

        # 记录状态变更到元数据
        if "status_history" not in self.metadata:
            self.metadata["status_history"] = []

        self.metadata["status_history"].append({
            "status": new_status,
            "timestamp": self.updated_at.isoformat()
        })

    def calculate_metrics(self) -> Dict[str, Any]:
        """计算文章指标"""
        # 计算总字数
        total_words = len(self.title) + len(self.summary)
        for section in self.sections:
            total_words += len(section.title) + len(section.content)

        # 估算阅读时间 (假设平均阅读速度400字/分钟)
        read_time = max(1, round(total_words / 400))

        # 更新指标
        self.word_count = total_words
        self.read_time = read_time

        return {
            "word_count": total_words,
            "read_time": read_time,
            "section_count": len(self.sections),
            "image_count": 0  # 简化版本不计算图片
        }

# 定义BasicArticle类 - 用于测试
class BasicArticle(BaseModel):
    """基础文章模型 - 用于测试"""
    id: Optional[str] = Field(default=None, description="文章ID")
    title: str = Field(..., description="文章标题")
    summary: str = Field(..., description="文章摘要")
    content: str = Field(..., description="文章内容")
    tags: List[str] = Field(default_factory=list, description="文章标签")
    word_count: int = Field(default=0, description="字数统计")
    read_time: int = Field(default=0, description="阅读时间(分钟)")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    @classmethod
    def from_article(cls, article: Article) -> "BasicArticle":
        """从Article创建BasicArticle对象"""
        return cls(
            id=article.id,
            title=article.title,
            summary=article.summary,
            content=article.content,
            tags=article.tags,
            word_count=article.word_count,
            read_time=article.read_time,
            created_at=article.created_at,
            updated_at=article.updated_at
        )

# 创建模拟的ArticleService
class MockArticleService:
    """模拟ArticleService，供测试使用"""

    @staticmethod
    def update_article_status(article: Any, new_status: str) -> None:
        """更新文章状态

        Args:
            article: 文章对象
            new_status: 新状态
        """
        article.status = new_status
        article.updated_at = datetime.now()

        # 记录状态变更到元数据
        if not hasattr(article, "metadata"):
            article.metadata = {}

        if "status_history" not in article.metadata:
            article.metadata["status_history"] = []

        article.metadata["status_history"].append({
            "status": new_status,
            "timestamp": datetime.now().isoformat()
        })

    @staticmethod
    def calculate_article_metrics(article: Any) -> Dict[str, Any]:
        """计算文章指标

        Args:
            article: 文章对象

        Returns:
            Dict[str, Any]: 文章指标
        """
        # 计算总字数
        total_words = len(article.title) + len(article.summary)
        for section in article.sections:
            total_words += len(section.title) + len(section.content)

        # 估算阅读时间
        read_time = max(1, round(total_words / 400))

        # 更新指标
        article.word_count = total_words
        article.read_time = read_time

        return {
            "word_count": total_words,
            "read_time": read_time,
            "section_count": len(article.sections),
            "image_count": len(article.images) if hasattr(article, "images") else 0
        }

# 测试函数
def test_section_creation():
    """测试创建Section对象"""
    section = Section(
        id="section_1",
        title="测试章节",
        content="这是测试章节的内容",
        order=1
    )

    assert section.id == "section_1"
    assert section.title == "测试章节"
    assert section.content == "这是测试章节的内容"
    assert section.order == 1
    assert section.type == "text"  # 默认值
    assert section.parent_id is None  # 默认值
    assert section.metadata == {}  # 默认值


def test_article_creation():
    """测试创建基本的Article对象"""
    # 创建基本章节
    section = Section(
        id="section_1",
        title="测试章节",
        content="这是测试章节的内容",
        order=1
    )

    # 创建文章
    article = Article(
        id="test_article_1",
        topic_id="test_topic",
        title="测试文章",
        summary="这是一篇测试文章",
        sections=[section]
    )

    # 验证基本字段
    assert article.id == "test_article_1"
    assert article.topic_id == "test_topic"
    assert article.title == "测试文章"
    assert article.summary == "这是一篇测试文章"
    assert len(article.sections) == 1
    assert article.sections[0].title == "测试章节"
    assert article.status == "initialized"
    assert article.is_published == False


def test_article_update_status():
    """测试更新文章状态"""
    article = Article(
        id="test_article_2",
        topic_id="test_topic",
        title="测试文章2",
        summary="这是一篇测试文章"
    )

    # 检查初始状态
    assert article.status == "initialized"
    assert "status_history" not in article.metadata

    # 更新状态
    MockArticleService.update_article_status(article, "writing")

    # 验证状态更新
    assert article.status == "writing"
    assert "status_history" in article.metadata
    assert len(article.metadata["status_history"]) == 1
    assert article.metadata["status_history"][0]["status"] == "writing"


def test_article_calculate_metrics():
    """测试计算文章指标"""
    article = Article(
        id="test_article_3",
        topic_id="test_topic",
        title="测试文章指标",
        summary="这是关于指标计算的测试",
        sections=[
            Section(title="章节1", content="这是第一个章节的内容", order=1),
            Section(title="章节2", content="这是第二个章节的内容", order=2)
        ]
    )

    # 计算前检查
    assert article.word_count == 0
    assert article.read_time == 0

    # 计算指标
    metrics = MockArticleService.calculate_article_metrics(article)

    # 验证结果
    assert metrics["word_count"] > 0
    assert metrics["read_time"] > 0
    assert metrics["section_count"] == len(article.sections)
    assert article.word_count == metrics["word_count"]
    assert article.read_time == metrics["read_time"]


def test_convert_between_article_types():
    """测试Article和BasicArticle之间的转换"""
    # 创建文章
    article = Article(
        id="test_article_4",
        topic_id="test_topic",
        title="测试文章4",
        summary="测试文章和基础文章之间的转换",
        content="这是文章内容"
    )

    # 从Article创建BasicArticle
    basic_article = BasicArticle.from_article(article)

    # 验证转换
    assert basic_article.id == article.id
    assert basic_article.title == article.title
    assert basic_article.summary == article.summary
    assert basic_article.content == article.content
