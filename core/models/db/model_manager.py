"""数据库模型关系定义

定义数据库模型之间的关系，如多对多关联表，以及提供默认实例创建函数。
本模块不包含业务逻辑，只提供基础的数据模型关系和默认实例。
"""

from typing import Dict, List, Optional, Any, Set, TypeVar, Type, cast, Union
import json
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList
from loguru import logger

from core.models.db.session import Base
from core.models.db.utils import JSONEncodedDict

# 类型变量，用于类型注解
T = TypeVar('T')

# 创建内容类型名称和文章风格的多对多关系表
content_type_style = Table(
    "content_type_style",
    Base.metadata,
    Column("content_type_id", String(100), ForeignKey("content_type.id", ondelete="CASCADE"), primary_key=True),
    Column("style_id", String(100), ForeignKey("article_style.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True  # 允许重新定义已存在的表
)

def create_default_content_type() -> Dict[str, Any]:
    """创建默认内容类型字典

    返回包含默认值的内容类型字典，用于初始化或当未指定内容类型时使用。
    注意：这个函数返回字典而非模型对象，避免循环导入。

    Returns:
        Dict[str, Any]: 默认内容类型字典
    """
    try:
        # 返回默认内容类型属性字典
        return {
            "id": "article",
            "name": "文章",
            "description": "通用文章类型，适用于大多数场景",
            "default_word_count": 1500,
            "is_enabled": True,
            "prompt_template": "请生成一篇关于{{topic}}的文章，要求{{style}}",
            "output_format": {
                "title": "标题",
                "content": "正文内容"
            },
            "required_elements": {
                "introduction": "介绍部分",
                "body": "主体内容",
                "conclusion": "结论部分"
            },
            "optional_elements": {
                "references": "参考资料"
            }
        }
    except Exception as e:
        logger.error(f"创建默认内容类型失败: {str(e)}")
        # 返回最小化的默认内容类型
        return {
            "id": "article",
            "name": "文章",
            "description": "基础文章类型",
            "is_enabled": True
        }

def create_default_article_style() -> Dict[str, Any]:
    """创建默认文章风格字典

    返回包含默认值的文章风格字典，用于初始化或当未指定文章风格时使用。
    注意：这个函数返回字典而非模型对象，避免循环导入。

    Returns:
        Dict[str, Any]: 默认文章风格字典
    """
    try:
        # 返回默认文章风格属性字典
        return {
            "id": "formal",
            "name": "正式",
            "description": "正式、专业的写作风格，适用于正式场合",
            "is_enabled": True,
            "tone": "professional",
            "style_characteristics": {
                "formality": "high",
                "technical_level": "medium",
                "emotion": "neutral"
            },
            "language_preference": {
                "sentence_length": "medium to long",
                "vocabulary": "professional",
                "first_person": False
            },
            "writing_format": {
                "paragraph_length": "medium",
                "use_subtitles": True,
                "use_bullet_points": True
            },
            "prompt_template": "请使用正式、专业的语言风格，避免口语化表达，保持客观中立的语气",
            "example": "本研究旨在探讨人工智能对现代社会的影响。研究结果表明，AI技术在提高生产效率的同时，也带来了一系列社会问题..."
        }
    except Exception as e:
        logger.error(f"创建默认文章风格失败: {str(e)}")
        # 返回最小化的默认文章风格
        return {
            "id": "formal",
            "name": "正式",
            "description": "正式文章风格",
            "is_enabled": True
        }

def create_default_platform() -> Dict[str, Any]:
    """创建默认平台字典

    返回包含默认值的平台配置字典，用于初始化或当未指定平台时使用。
    注意：这个函数返回字典而非模型对象，避免循环导入。

    Returns:
        Dict[str, Any]: 默认平台字典
    """
    try:
        # 返回默认平台属性字典
        return {
            "id": "default",
            "name": "默认平台",
            "description": "通用内容发布平台",
            "is_enabled": True,
            "platform_type": "generic",
            "url": "",
            "logo_url": "",
            "max_title_length": 100,
            "max_content_length": 10000,
            "allowed_media_types": ["image", "video"],
            "api_config": {}
        }
    except Exception as e:
        logger.error(f"创建默认平台失败: {str(e)}")
        # 返回最小化的默认平台
        return {
            "id": "default",
            "name": "默认平台",
            "description": "基础平台配置",
            "is_enabled": True
        }
