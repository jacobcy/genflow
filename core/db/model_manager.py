"""数据库模型定义

定义内容类型、文章风格和平台等数据模型，用于本地存储和管理。
"""

from typing import Dict, List, Optional, Any, Set
import json
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList
import time

from core.db.session import Base
from core.db.utils import JSONEncodedDict

# 创建内容类型和文章风格的多对多关系表
content_type_style = Table(
    "content_type_style",
    Base.metadata,
    Column("content_type_id", String(50), ForeignKey("content_type.id", ondelete="CASCADE"), primary_key=True),
    Column("style_id", String(50), ForeignKey("article_style.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True  # 允许重新定义已存在的表
)

from core.db.platform import Platform
from core.db.topic import Topic
from core.db.article import Article
from core.db.article_style import ArticleStyle
from core.db.content_type import ContentType


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
