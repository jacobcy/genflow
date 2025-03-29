"""平台分类数据模型

该模块提供了平台分类的数据模型，用于规范化处理平台分类信息。
主要包含以下功能：
1. 平台分类的数据结构定义
2. 分类标签的验证和管理
3. 平台与分类的关联关系处理
4. 分类查询和过滤功能
"""

from typing import List, Dict, Set, Optional
from pydantic import BaseModel, Field, field_validator
from ..tools.trending_tools.platform_categories import PLATFORM_CATEGORIES, CATEGORY_TAGS
from .infra.enums import CategoryType

class Category(BaseModel):
    """分类模型，使用name作为唯一标识"""
    name: str = Field(..., description="分类名称，作为唯一标识")
    type: CategoryType = Field(..., description="分类类型")
    platforms: List[str] = Field(default_factory=list, description="包含该分类的平台列表")
    description: str = Field(default="", description="分类描述")
    parent: Optional[str] = Field(default=None, description="父分类名称")
    children: List[str] = Field(default_factory=list, description="子分类名称列表")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """验证分类名称是否在预定义集合中"""
        if v not in CATEGORY_TAGS:
            raise ValueError(f"Invalid category name: {v}")
        return v

    @field_validator("parent")
    @classmethod
    def validate_parent(cls, v):
        """验证父分类是否有效"""
        if v and v not in CATEGORY_TAGS:
            raise ValueError(f"Invalid parent category: {v}")
        return v

    @field_validator("children")
    @classmethod
    def validate_children(cls, v):
        """验证子分类列表"""
        invalid_categories = set(v) - CATEGORY_TAGS
        if invalid_categories:
            raise ValueError(f"Invalid child categories: {invalid_categories}")
        return v

    @classmethod
    def get_all_categories(cls) -> List["Category"]:
        """获取所有分类"""
        categories = []
        for category in CATEGORY_TAGS:
            # 确定分类类型
            category_type = CategoryType.OTHER
            if category in {"社交", "技术", "新闻", "知识", "游戏", "娱乐", "购物", "数码", "阅读"}:
                category_type = CategoryType.PLATFORM
            elif category in {"热点", "时事", "开发", "编程", "互联网", "科技", "创业", "商业", "问答",
                            "科普", "二次元", "电竞", "优惠", "效率", "安全", "创新", "开源"}:
                category_type = CategoryType.CONTENT
            elif category in {"短视频", "讨论", "综合", "深度", "视频", "评论", "博客", "资讯"}:
                category_type = CategoryType.FORMAT
            elif category in {"Linux", "主机", "米哈游", "英雄联盟", "应用", "安卓", "摄影", "设计"}:
                category_type = CategoryType.FEATURE

            # 获取包含该分类的平台列表
            platforms = [
                platform for platform, cats in PLATFORM_CATEGORIES.items()
                if category in cats
            ]

            categories.append(cls(
                name=category,
                type=category_type,
                platforms=platforms,
                description=f"{category}相关内容"
            ))
        return categories

    @classmethod
    def get_platform_categories(cls, platform: str) -> List[str]:
        """获取平台的所有分类"""
        return PLATFORM_CATEGORIES.get(platform, [])

    @classmethod
    def get_platforms_by_category(cls, category: str) -> List[str]:
        """获取指定分类下的所有平台"""
        return [
            platform for platform, categories
            in PLATFORM_CATEGORIES.items()
            if category in categories
        ]

    @classmethod
    def get_category_by_name(cls, name: str) -> Optional["Category"]:
        """根据名称获取分类"""
        if name not in CATEGORY_TAGS:
            return None
        return next(
            (cat for cat in cls.get_all_categories() if cat.name == name),
            None
        )

    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": {
                "name": "技术",
                "type": "平台属性",
                "platforms": ["github", "v2ex", "juejin", "csdn"],
                "description": "技术相关内容",
                "parent": None,
                "children": ["开发", "编程", "互联网"]
            }
        }
