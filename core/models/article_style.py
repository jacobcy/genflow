"""文章风格模型

该模块定义了文章风格的数据模型，用于规范化文章的风格配置。
与 core/models/styles/*.json 中的风格配置相对应。
"""

from typing import List, Dict, Optional, Any, Set
from pydantic import BaseModel, Field, computed_field
import os
import json
from .util import JsonModelLoader

class ContentRules(BaseModel):
    """内容规则"""
    min_length: int = Field(default=0, description="最小字数")
    max_length: int = Field(default=10000, description="最大字数")
    allowed_formats: List[str] = Field(default_factory=list, description="允许的格式")
    forbidden_words: List[str] = Field(default_factory=list, description="禁用词列表")
    required_sections: List[str] = Field(default_factory=list, description="必需章节")

class StyleRules(BaseModel):
    """风格规则"""
    tone: str = Field(default="neutral", description="语气风格")
    formality: int = Field(default=3, description="正式程度 1-5")
    emotion: bool = Field(default=False, description="是否使用情感表达")
    code_block: bool = Field(default=True, description="是否支持代码块")
    emoji: bool = Field(default=False, description="是否使用表情")
    image_text_ratio: float = Field(default=0.1, description="图文比例 (0-1)")
    max_image_count: int = Field(default=10, description="最大图片数量")
    min_paragraph_length: int = Field(default=50, description="最小段落长度")
    max_paragraph_length: int = Field(default=400, description="最大段落长度")
    paragraph_count_range: List[int] = Field(default_factory=lambda: [8, 40], description="段落数量范围")
    section_count_range: List[int] = Field(default_factory=lambda: [4, 15], description="章节数量范围")
    title_length_range: List[int] = Field(default_factory=lambda: [20, 80], description="标题长度范围")
    keyword_density: float = Field(default=0.01, description="关键词密度")
    heading_required: bool = Field(default=True, description="是否需要小标题")
    tag_count_range: List[int] = Field(default_factory=lambda: [3, 8], description="标签数量范围")

    @computed_field
    @property
    def is_formal(self) -> bool:
        """是否为正式风格"""
        return self.formality >= 4

    @computed_field
    @property
    def is_casual(self) -> bool:
        """是否为轻松风格"""
        return self.formality <= 2

class StyleGuide(BaseModel):
    """风格指南"""
    tone: str = Field(default="neutral", description="语气(专业/轻松/正式等)")
    format: str = Field(default="text", description="格式(图文/视频等)")
    target_audience: str = Field(default="general", description="目标受众")
    writing_style: str = Field(default="standard", description="写作风格")
    language_level: str = Field(default="normal", description="语言难度")
    content_approach: str = Field(default="standard", description="内容方法")
    recommended_patterns: List[str] = Field(default_factory=list, description="推荐模式")
    examples: List[str] = Field(default_factory=list, description="示例")


class PublishSettings(BaseModel):
    """发布设置"""
    auto_publish: bool = Field(default=False, description="是否自动发布")
    review_required: bool = Field(default=True, description="是否需要审核")
    publish_time: str = Field(default="immediate", description="发布时间")

# 默认风格配置
DEFAULT_STYLE = {
    "id": "default",
    "name": "默认风格",
    "type": "general",
    "description": "通用的文章风格，适合大多数场景",
    "target_audience": "通用受众",
    "content_types": ["article", "blog"],
    "primary_language": "zh-CN",
    "tone": "neutral",
    "formality": 3,
    "emotion": False,
    "content_rules": {
        "min_length": 800,
        "max_length": 8000,
        "allowed_formats": [
            "text",
            "image",
            "code"
        ],
        "forbidden_words": [],
        "required_sections": [
            "引言",
            "正文",
            "总结"
        ]
    },
    "style_rules": {
        "code_block": True,
        "emoji": False,
        "image_text_ratio": 0.2,
        "max_image_count": 10,
        "min_paragraph_length": 50,
        "max_paragraph_length": 300,
        "paragraph_count_range": [5, 30],
        "section_count_range": [3, 10],
        "title_length_range": [20, 60],
        "keyword_density": 0.02,
        "heading_required": True,
        "tag_count_range": [3, 8]
    },
    "style_guide": {
        "format": "article",
        "writing_style": "standard",
        "language_level": "normal",
        "content_approach": "balanced",
        "recommended_patterns": [
            "清晰的结构",
            "逻辑性强",
            "易于理解",
            "重点突出"
        ],
        "examples": [
            "标准文章结构示例",
            "通用写作风格指南"
        ]
    },
    "publish_settings": {
        "auto_publish": False,
        "review_required": True,
        "publish_time": "immediate"
    }
}

class ArticleStyle(BaseModel):
    """文章风格定义，与 styles/*.json 格式完全对应"""
    # 基本信息
    id: str = Field(..., description="风格ID")
    name: str = Field(..., description="风格名称")
    type: str = Field(..., description="风格类型")
    url: str = Field(default="", description="相关URL")
    description: str = Field(default="", description="风格描述")
    target_audience: str = Field(default="", description="目标受众")
    content_types: List[str] = Field(default_factory=list, description="内容类型")
    primary_language: str = Field(default="zh-CN", description="主要语言")

    # 顶层风格属性 - 将最常用的风格属性提升到顶层
    tone: str = Field(default="neutral", description="语气风格")
    formality: int = Field(default=3, description="正式程度 1-5")
    emotion: bool = Field(default=False, description="是否使用情感表达")

    # 规则配置
    content_rules: ContentRules = Field(default_factory=ContentRules, description="内容规则")
    style_rules: StyleRules = Field(default_factory=StyleRules, description="风格规则")
    style_guide: StyleGuide = Field(default_factory=StyleGuide, description="风格指南")
    publish_settings: PublishSettings = Field(default_factory=PublishSettings, description="发布设置")

    def model_post_init(self, __context):
        """初始化后同步数据"""
        # 处理从JSON文件读取的数据，确保字段同步
        # 1. 从style_rules同步字段到顶层属性
        if hasattr(self.style_rules, "tone") and not self.tone:
            self.tone = self.style_rules.tone
        if hasattr(self.style_rules, "formality") and self.formality == 3:  # 默认值
            self.formality = self.style_rules.formality
        if hasattr(self.style_rules, "emotion") and not self.emotion:
            self.emotion = self.style_rules.emotion

        # 2. 从顶层属性同步到style_rules
        self.style_rules.tone = self.tone
        self.style_rules.formality = self.formality
        self.style_rules.emotion = self.emotion

        # 3. 从style_guide同步字段
        if hasattr(self.style_guide, "tone") and not self.tone:
            self.tone = self.style_guide.tone

        # 4. 同步到style_guide
        self.style_guide.tone = self.tone

    @computed_field
    @property
    def is_emotional(self) -> bool:
        """风格是否带有情感表达"""
        return self.emotion

    @computed_field
    @property
    def is_formal(self) -> bool:
        """是否为正式风格"""
        return self.formality >= 4

    @computed_field
    @property
    def writing_style(self) -> str:
        """获取写作风格"""
        return self.style_guide.writing_style

    @computed_field
    @property
    def min_content_length(self) -> int:
        """获取最小内容长度"""
        return self.content_rules.min_length

    @computed_field
    @property
    def max_content_length(self) -> int:
        """获取最大内容长度"""
        return self.content_rules.max_length

    def get_paragraph_guidelines(self) -> Dict[str, Any]:
        """获取段落相关指南

        Returns:
            Dict: 段落格式指南
        """
        return {
            "min_length": self.style_rules.min_paragraph_length,
            "max_length": self.style_rules.max_paragraph_length,
            "count_range": self.style_rules.paragraph_count_range,
        }

    def get_section_guidelines(self) -> Dict[str, Any]:
        """获取章节相关指南

        Returns:
            Dict: 章节格式指南
        """
        return {
            "count_range": self.style_rules.section_count_range,
            "required_sections": self.content_rules.required_sections,
            "heading_required": self.style_rules.heading_required
        }

    def get_format_guidelines(self) -> Dict[str, Any]:
        """获取格式相关指南

        Returns:
            Dict: 格式指南
        """
        return {
            "allowed_formats": self.content_rules.allowed_formats,
            "code_block": self.style_rules.code_block,
            "emoji": self.style_rules.emoji,
            "image_text_ratio": self.style_rules.image_text_ratio,
            "max_image_count": self.style_rules.max_image_count,
        }

    def is_compatible_with_content_type(self, content_type: str) -> bool:
        """检查风格是否与内容类型兼容

        Args:
            content_type: 内容类型

        Returns:
            bool: 是否兼容
        """
        if not self.content_types:  # 空列表表示通用风格
            return True

        # 直接匹配
        if content_type in self.content_types:
            return True

        # 尝试模糊匹配
        for supported_type in self.content_types:
            if (supported_type in content_type) or (content_type in supported_type):
                return True

        return False

    def get_style_summary(self) -> Dict[str, Any]:
        """获取风格摘要信息

        Returns:
            Dict: 风格摘要
        """
        return {
            "id": self.id,
            "name": self.name,
            "tone": self.tone,
            "formality": self.formality,
            "emotion": self.emotion,
            "writing_style": self.writing_style,
            "target_audience": self.target_audience,
            "content_length_range": [self.min_content_length, self.max_content_length],
            "paragraph_guidelines": self.get_paragraph_guidelines(),
            "section_guidelines": self.get_section_guidelines(),
            "format_guidelines": self.get_format_guidelines(),
        }

    @classmethod
    def get_default(cls) -> 'ArticleStyle':
        """获取默认的文章风格配置

        Returns:
            ArticleStyle: 默认的文章风格配置
        """
        return get_default_style()

    @classmethod
    def get_all_styles(cls) -> Dict[str, 'ArticleStyle']:
        """获取所有文章风格配置

        Returns:
            Dict[str, ArticleStyle]: 风格字典，键为风格ID
        """
        return load_article_styles()

    @classmethod
    def from_id(cls, style_id: str) -> Optional['ArticleStyle']:
        """根据ID获取文章风格配置

        Args:
            style_id: 风格ID

        Returns:
            Optional[ArticleStyle]: 文章风格配置，如果不存在则返回默认风格
        """
        return get_style_by_id(style_id)

    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": DEFAULT_STYLE
        }

def get_default_style() -> ArticleStyle:
    """获取默认的文章风格配置

    Returns:
        ArticleStyle: 默认的文章风格配置
    """
    return ArticleStyle(**DEFAULT_STYLE)

def load_article_styles() -> Dict[str, ArticleStyle]:
    """加载所有文章风格配置

    Returns:
        Dict[str, ArticleStyle]: 文章风格字典，键为风格ID
    """
    base_dir = JsonModelLoader.get_base_directory()
    styles_dir = os.path.join(base_dir, 'styles')

    return JsonModelLoader.load_models_from_directory(styles_dir, ArticleStyle)

def get_style_by_id(style_id: str) -> Optional[ArticleStyle]:
    """根据ID获取文章风格配置

    Args:
        style_id: 风格ID

    Returns:
        Optional[ArticleStyle]: 文章风格配置，如果不存在则返回默认风格
    """
    styles = load_article_styles()
    return styles.get(style_id, get_default_style())

def get_platform_style(platform: str) -> Optional[ArticleStyle]:
    """根据平台名称获取对应的风格配置

    Args:
        platform: 平台名称

    Returns:
        Optional[ArticleStyle]: 平台风格配置，如果不存在则返回None
    """
    styles = load_article_styles()

    # 平台名称通常就是风格ID
    if platform in styles:
        return styles[platform]

    # 尝试转为小写
    platform_lower = platform.lower()
    if platform_lower in styles:
        return styles[platform_lower]

    # 尝试查找包含该平台名称的风格
    for style_id, style in styles.items():
        if platform.lower() in style_id.lower() or (
            style.name and platform.lower() in style.name.lower()
        ):
            return style

    return None
