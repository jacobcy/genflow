"""风格模块简化测试

测试风格模块的核心功能，包括风格创建、匹配和转换。
这是一个独立的简化测试，避免数据库和外部依赖。
"""

import sys
import os
import pytest
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# 导入模块
from core.models.style.article_style import ArticleStyle, StyleModel, DEFAULT_STYLE, get_default_style
from core.models.style.style_service import StyleFactory


def test_article_style_creation():
    """测试文章风格模型创建"""
    # 创建基本风格
    style = ArticleStyle(
        name="测试风格",
        type="technical",
        description="技术类文章风格",
        tone="professional",
        formality=4,
        emotion=False,
        emoji=False,
        target_audience="开发者",
        content_types=["article", "tutorial"],
        writing_style="technical"
    )

    # 验证基本属性
    assert style.name == "测试风格"
    assert style.type == "technical"
    assert style.tone == "professional"
    assert style.formality == 4
    assert style.emotion is False
    assert style.target_audience == "开发者"
    assert "article" in style.content_types
    assert "tutorial" in style.content_types

    # 验证默认值
    assert style.emoji is False
    assert style.min_length == 800
    assert style.max_length == 8000
    assert style.code_block is True


def test_default_style():
    """测试默认风格"""
    # 获取默认风格
    default_style = get_default_style()

    # 验证默认值
    assert default_style.name == DEFAULT_STYLE["name"]
    assert default_style.type == DEFAULT_STYLE["type"]
    assert default_style.description == DEFAULT_STYLE["description"]
    assert default_style.formality == DEFAULT_STYLE["formality"]
    assert default_style.tone == DEFAULT_STYLE["tone"]

    # 验证风格配置转换
    config = default_style.to_style_config()
    assert config["style_name"] == default_style.name
    assert config["style"] == default_style.type
    assert config["tone"] == default_style.tone
    assert config["formality"] == default_style.formality


def test_style_factory():
    """测试风格工厂"""
    # 通过描述创建风格
    tech_style = StyleFactory._create_temp_style("技术类教程，专业严谨的风格",
                                                {"style_name": "技术教程风格"})

    # 验证属性推断
    assert tech_style.name == "技术教程风格"
    assert tech_style.type == "technical"
    assert tech_style.tone == "informative"
    assert tech_style.formality == 4
    assert tech_style.target_audience == "专业人士"

    # 创建休闲风格
    casual_style = StyleFactory._create_temp_style("轻松活泼的博客风格，适合初学者",
                                                  {"style_name": "休闲博客风格"})

    # 验证属性推断
    assert casual_style.name == "休闲博客风格"
    assert casual_style.type == "casual"
    assert casual_style.tone == "friendly"
    assert casual_style.formality == 2
    assert casual_style.target_audience == "初学者"
    assert "blog" in casual_style.content_types


def test_style_content_type_compatibility():
    """测试风格与内容类型兼容性"""
    # 创建有限定内容类型的风格
    style = ArticleStyle(
        name="博客风格",
        content_types=["blog", "social"]
    )

    # 测试兼容性
    assert style.is_compatible_with_content_type("blog") is True
    assert style.is_compatible_with_content_type("social") is True
    assert style.is_compatible_with_content_type("blog_post") is True  # 模糊匹配
    assert style.is_compatible_with_content_type("tutorial") is False

    # 测试通用风格
    generic_style = ArticleStyle(
        name="通用风格",
        content_types=[]  # 空列表表示通用
    )

    assert generic_style.is_compatible_with_content_type("blog") is True
    assert generic_style.is_compatible_with_content_type("article") is True
    assert generic_style.is_compatible_with_content_type("tutorial") is True


if __name__ == "__main__":
    # 运行所有测试
    test_article_style_creation()
    test_default_style()
    test_style_factory()
    test_style_content_type_compatibility()
    print("所有测试通过!")
