"""平台模型

该模块定义了平台的数据结构和与平台相关的基本操作。
每个平台定义了内容的发布约束、审核规则及技术要求。
"""

from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field, field_validator, computed_field
import os
import json
from loguru import logger

from core.models.infra import JsonModelLoader

# 全局平台配置字典
PLATFORM_CONFIGS = {}


class PlatformConstraints(BaseModel):
    """平台硬约束规则"""
    min_length: int = Field(default=0, description="最小字数限制")
    max_length: int = Field(default=100000, description="最大字数限制")
    max_title_length: int = Field(default=100, description="标题最大长度")
    max_image_count: int = Field(default=20, description="最大图片数量")
    max_video_count: int = Field(default=0, description="最大视频数量")
    forbidden_words: List[str] = Field(default_factory=list, description="禁用词列表")
    required_elements: List[str] = Field(default_factory=list, description="必需元素")
    allowed_formats: List[str] = Field(default_factory=lambda: ["text"], description="允许的内容格式")
    allowed_media_types: List[str] = Field(default_factory=list, description="允许的媒体类型")
    code_block_support: bool = Field(default=True, description="是否支持代码块")
    math_formula_support: bool = Field(default=False, description="是否支持数学公式")
    table_support: bool = Field(default=True, description="是否支持表格")
    emoji_support: bool = Field(default=True, description="是否支持表情符号")

    @computed_field
    @property
    def is_code_friendly(self) -> bool:
        """是否适合代码内容"""
        return self.code_block_support and "code" in self.allowed_formats

    @computed_field
    @property
    def is_media_rich(self) -> bool:
        """是否支持丰富媒体内容"""
        return len(self.allowed_media_types) > 2 or self.max_image_count > 5 or self.max_video_count > 0


class TechnicalRequirements(BaseModel):
    """技术要求"""
    api_version: str = Field(default="v1", description="API版本")
    rate_limits: Dict[str, int] = Field(default_factory=dict, description="API速率限制")
    max_request_size: int = Field(default=5242880, description="最大请求大小(字节)")
    supported_file_types: List[str] = Field(default_factory=list, description="支持的文件类型")
    auth_required: bool = Field(default=True, description="是否需要认证")
    https_required: bool = Field(default=True, description="是否要求HTTPS")


class Platform(BaseModel):
    """平台模型，专注于发布限制和技术要求"""
    name: str = Field(..., description="平台名称")
    url: str = Field(..., description="平台URL")
    description: str = Field(default="", description="平台描述")
    category: str = Field(default="general", description="平台分类")

    # 基本属性
    primary_language: str = Field(default="zh-CN", description="主要支持语言")
    supported_languages: List[str] = Field(default_factory=lambda: ["zh-CN"], description="支持的语言列表")

    # 内容硬约束 - 将最常用的约束提升到顶层
    min_length: int = Field(default=0, description="内容最小字数")
    max_length: int = Field(default=100000, description="内容最大字数")
    max_title_length: int = Field(default=100, description="标题最大长度")
    max_image_count: int = Field(default=20, description="最大图片数量")
    forbidden_words: List[str] = Field(default_factory=list, description="禁用词列表")

    # 其他约束保留在嵌套结构中
    constraints: PlatformConstraints = Field(default_factory=PlatformConstraints, description="平台完整硬约束")

    # 技术要求
    technical: TechnicalRequirements = Field(default_factory=TechnicalRequirements, description="技术要求")

    # 审核相关
    review_required: bool = Field(default=True, description="是否需要审核")
    auto_review_enabled: bool = Field(default=False, description="是否支持自动审核")

    # 发布设置
    publish_settings: Dict[str, Any] = Field(default_factory=dict, description="发布相关设置")

    @field_validator('constraints')
    def sync_constraints(cls, v, info):
        """同步约束到顶层字段"""
        data = info.data
        # 如果顶层字段有值且约束中没有对应值，同步顶层到约束
        if 'min_length' in data and data['min_length'] != 0:
            v.min_length = data['min_length']
        if 'max_length' in data and data['max_length'] != 100000:
            v.max_length = data['max_length']
        if 'max_title_length' in data and data['max_title_length'] != 100:
            v.max_title_length = data['max_title_length']
        if 'max_image_count' in data and data['max_image_count'] != 20:
            v.max_image_count = data['max_image_count']
        if 'forbidden_words' in data and data['forbidden_words']:
            v.forbidden_words = data['forbidden_words']
        return v

    def model_post_init(self, __context):
        """模型初始化后处理"""
        # 同步约束到顶层
        self.min_length = self.constraints.min_length
        self.max_length = self.constraints.max_length
        self.max_title_length = self.constraints.max_title_length
        self.max_image_count = self.constraints.max_image_count
        self.forbidden_words = self.constraints.forbidden_words

    @computed_field
    @property
    def supports_code(self) -> bool:
        """是否支持代码块"""
        return self.constraints.code_block_support

    @computed_field
    @property
    def supports_math(self) -> bool:
        """是否支持数学公式"""
        return self.constraints.math_formula_support

    @computed_field
    @property
    def allowed_formats(self) -> List[str]:
        """允许的格式列表"""
        return self.constraints.allowed_formats

    def validate_content(self, title_length: int, content_length: int, image_count: int = 0,
                        video_count: int = 0, formats: Optional[List[str]] = None) -> Dict[str, bool]:
        """验证内容是否符合平台硬约束

        Args:
            title_length: 标题长度
            content_length: 内容长度
            image_count: 图片数量
            video_count: 视频数量
            formats: 内容格式列表

        Returns:
            Dict[str, bool]: 验证结果，键为约束名，值为是否通过
        """
        if formats is None:
            formats = ["text"]

        results = {
            "title_length": title_length <= self.max_title_length,
            "min_length": content_length >= self.min_length,
            "max_length": content_length <= self.max_length,
            "max_image_count": image_count <= self.max_image_count,
            "max_video_count": video_count <= self.constraints.max_video_count,
        }

        # 检查内容格式
        has_unsupported_format = False
        for fmt in formats:
            if fmt not in self.constraints.allowed_formats:
                has_unsupported_format = True
                break
        results["formats"] = not has_unsupported_format

        return results

    def has_forbidden_words(self, text: str) -> List[str]:
        """检查文本是否包含禁用词

        Args:
            text: 要检查的文本

        Returns:
            List[str]: 找到的禁用词列表
        """
        found_words = []
        if not self.forbidden_words:
            return found_words

        lower_text = text.lower()
        for word in self.forbidden_words:
            if word.lower() in lower_text:
                found_words.append(word)

        return found_words

    def get_platform_constraints(self) -> Dict[str, Any]:
        """获取平台约束信息

        返回一个包含所有平台约束的字典，用于指导内容生成。

        Returns:
            Dict[str, Any]: 平台约束信息
        """
        # 合并顶层字段和嵌套字段
        constraints = {
            "min_length": self.min_length,
            "max_length": self.max_length,
            "max_title_length": self.max_title_length,
            "max_image_count": self.max_image_count,
            "max_video_count": self.constraints.max_video_count,
            "forbidden_words": self.forbidden_words,
            "required_elements": self.constraints.required_elements,
            "allowed_formats": self.constraints.allowed_formats,
            "allowed_media_types": self.constraints.allowed_media_types,
            "code_block_support": self.constraints.code_block_support,
            "math_formula_support": self.constraints.math_formula_support,
            "table_support": self.constraints.table_support,
            "emoji_support": self.constraints.emoji_support,
        }

        # 添加技术要求
        constraints["technical"] = {
            "api_version": self.technical.api_version,
            "rate_limits": self.technical.rate_limits,
            "max_request_size": self.technical.max_request_size,
            "supported_file_types": self.technical.supported_file_types,
            "auth_required": self.technical.auth_required,
            "https_required": self.technical.https_required
        }

        return constraints

    def get_all_supported_formats(self) -> Set[str]:
        """获取所有支持的格式

        Returns:
            Set[str]: 支持的格式集合
        """
        formats = set(self.constraints.allowed_formats)

        # 根据特殊支持添加格式
        if self.constraints.code_block_support:
            formats.add("code")
        if self.constraints.math_formula_support:
            formats.add("math")
        if self.constraints.table_support:
            formats.add("table")

        return formats

    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": {
                "name": "medium",
                "url": "https://medium.com",
                "description": "Medium是一个开放的内容平台，任何人都可以阅读、写作和分享想法。",
                "category": "blogging",
                "primary_language": "en-US",
                "supported_languages": ["en-US", "zh-CN", "ja-JP"],
                "min_length": 500,
                "max_length": 20000,
                "max_title_length": 100,
                "forbidden_words": ["侮辱性词汇"],
                "constraints": {
                    "code_block_support": True,
                    "math_formula_support": True,
                    "allowed_formats": ["text", "html", "markdown"]
                },
                "technical": {
                    "api_version": "v1",
                    "rate_limits": {"posts_per_day": 10}
                }
            }
        }

def get_default_platform() -> Platform:
    """返回默认平台配置

    提供一个通用的基础平台配置，适用于大多数内容发布场景

    Returns:
        Platform: 默认平台配置对象
    """
    return Platform(
        name="通用平台",
        url="",
        description="通用内容发布平台",
        category="general",
        primary_language="zh-CN",
        supported_languages=["zh-CN", "en-US"],
        min_length=100,
        max_length=100000,
        max_title_length=100,
        max_image_count=20,
        forbidden_words=[],
        constraints=PlatformConstraints(
            required_elements=[],
            allowed_formats=["text", "image", "video", "code"],
            allowed_media_types=["jpg", "png", "gif", "mp4"],
            max_video_count=5,
            code_block_support=True,
            math_formula_support=True,
            table_support=True,
            emoji_support=True
        ),
        technical=TechnicalRequirements(
            api_version="v1",
            rate_limits={"requests_per_minute": 60},
            max_request_size=10485760,  # 10MB
            supported_file_types=["jpg", "png", "gif", "mp4", "pdf"],
            auth_required=True,
            https_required=True
        ),
        review_required=True,
        auto_review_enabled=True,
        publish_settings={
            "default_publish_time": "immediate",
            "scheduling_supported": True,
            "batch_publish_supported": True
        }
    )
