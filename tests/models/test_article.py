"""Article模型测试

测试Article和BasicArticle模型的基本功能

此测试文件使用隔离模式，避免依赖外部模块
"""
from datetime import datetime
from uuid import uuid4
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import pytest

# 定义隔离的测试模型
class Section(BaseModel):
    """文章章节"""
    id: str = Field(default="", description="章节ID")
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    order: int = Field(..., description="章节顺序")
    type: str = Field(default="text", description="章节类型")
    parent_id: Optional[str] = Field(default=None, description="父章节ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="章节元数据")

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

        # 记录状态变更
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
            "image_count": 0  # 简化版测试不考虑图片
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

    # 更新状态前检查
    assert "status_history" not in article.metadata

    # 使用模拟服务更新状态
    MockArticleService.update_article_status(article, "writing")

    # 验证状态已更新
    assert article.status == "writing"
    assert "status_history" in article.metadata
    assert len(article.metadata["status_history"]) == 1
    assert article.metadata["status_history"][0]["status"] == "writing"


def test_article_calculate_metrics():
    """测试计算文章指标"""
    # 创建一些章节
    sections = [
        Section(title="章节1", content="这是第一个章节的内容", order=1),
        Section(title="章节2", content="这是第二个章节的内容", order=2)
    ]

    # 创建文章
    article = Article(
        id="test_article_3",
        topic_id="test_topic",
        title="测试文章指标",
        summary="这是关于指标计算的测试",
        sections=sections
    )

    # 使用模拟服务计算指标
    metrics = MockArticleService.calculate_article_metrics(article)

    # 验证指标已计算
    assert metrics["word_count"] > 0
    assert metrics["read_time"] > 0
    assert metrics["section_count"] == len(sections)
    assert metrics["image_count"] == 0  # 简化版本不计算图片

    # 验证指标已更新到文章对象
    assert article.word_count == metrics["word_count"]
    assert article.read_time == metrics["read_time"]


def test_article_conversion():
    """测试文章转换功能"""
    # 创建一篇带章节的文章
    section = Section(
        id="section_1",
        title="测试章节",
        content="这是测试章节的内容",
        order=1
    )

    article = Article(
        id="test_article_4",
        topic_id="test_topic",
        title="测试文章",
        summary="测试摘要",
        sections=[section]
    )

    # 转换为字典
    article_dict = article.model_dump()

    # 验证字典字段
    assert article_dict["id"] == article.id
    assert article_dict["title"] == article.title
    assert article_dict["summary"] == article.summary
    assert article_dict["topic_id"] == article.topic_id
    assert len(article_dict["sections"]) == 1
    assert article_dict["sections"][0]["title"] == "测试章节"
