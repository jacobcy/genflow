"""文章风格模型

该模块定义了文章风格的核心数据模型，用于规范化文章的风格配置。
与 core/models/styles/*.json 中的风格配置对应，精简版本。
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import os
from .util import JsonModelLoader


class StyleModel(BaseModel):
    """精简的风格模型"""
    # 核心风格属性
    style: str = Field(default="formal", description="风格类型")
    tone: str = Field(default="neutral", description="语气风格")
    formality: int = Field(default=3, description="正式程度 1-5")
    emotion: bool = Field(default=False, description="是否使用情感表达")
    emoji: bool = Field(default=False, description="是否使用表情")


# 默认风格配置
DEFAULT_STYLE = {
    "name": "默认风格",
    "type": "general",
    "description": "通用的文章风格，适合大多数场景",
    "target_audience": "通用受众",
    "content_types": ["article", "blog"],
    "primary_language": "zh-CN",
    "tone": "neutral",
    "formality": 3,
    "emotion": False,
    "emoji": False,
    "recommended_patterns": ["清晰的结构", "逻辑性强", "易于理解", "重点突出"],
    "examples": ["标准文章结构示例", "通用写作风格指南"]
}


class ArticleStyle(StyleModel):
    """文章风格定义，精简版本，专注于StyleCrew所需属性"""
    # 基本信息
    name: str = Field(..., description="风格名称")
    type: str = Field(default="general", description="风格类型")
    description: str = Field(default="", description="风格描述")
    target_audience: str = Field(default="", description="目标受众")
    content_types: List[str] = Field(default_factory=list, description="内容类型")

    # 内容长度限制
    min_length: int = Field(default=800, description="最小字数")
    max_length: int = Field(default=8000, description="最大字数")

    # 段落指南
    min_paragraph_length: int = Field(default=50, description="最小段落长度")
    max_paragraph_length: int = Field(default=300, description="最大段落长度")
    paragraph_count_range: List[int] = Field(default_factory=lambda: [5, 30], description="段落数量范围")

    # 代码和媒体支持
    code_block: bool = Field(default=True, description="是否支持代码块")
    allowed_formats: List[str] = Field(default_factory=lambda: ["text", "image", "code"], description="允许的格式")

    # 风格规范和示例
    writing_style: str = Field(default="standard", description="写作风格")
    language_level: str = Field(default="normal", description="语言难度")
    recommended_patterns: List[str] = Field(default_factory=list, description="推荐模式")
    examples: List[str] = Field(default_factory=list, description="风格示例")

    def to_style_config(self) -> Dict[str, Any]:
        """转换为StyleCrew需要的风格配置字典

        Returns:
            Dict[str, Any]: 风格配置字典
        """
        return {
            "style_name": self.name,
            "style": self.type,
            "tone": self.tone,
            "formality": self.formality,
            "emotion": self.emotion,
            "emoji": self.emoji,
            "description": self.description,
            "target_audience": self.target_audience,
            "writing_style": self.writing_style,
            "language_level": self.language_level,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "min_paragraph_length": self.min_paragraph_length,
            "max_paragraph_length": self.max_paragraph_length,
            "paragraph_count_min": self.paragraph_count_range[0] if self.paragraph_count_range else 5,
            "paragraph_count_max": self.paragraph_count_range[1] if self.paragraph_count_range else 30,
            "code_block": self.code_block,
            "allowed_formats": self.allowed_formats,
            "recommended_patterns": self.recommended_patterns,
            "examples": self.examples
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


def get_default_style() -> ArticleStyle:
    """获取默认的文章风格配置

    Returns:
        ArticleStyle: 默认的文章风格配置
    """
    return ArticleStyle(**DEFAULT_STYLE)


def get_style_by_name(style_name: str) -> Optional[ArticleStyle]:
    """根据名称获取文章风格配置

    Args:
        style_name: 风格名称

    Returns:
        Optional[ArticleStyle]: 文章风格配置，如果不存在则返回默认风格
    """
    styles = load_article_styles()
    return styles.get(style_name, get_default_style())


def load_article_styles() -> Dict[str, ArticleStyle]:
    """加载所有文章风格配置

    Returns:
        Dict[str, ArticleStyle]: 文章风格字典，键为风格名称
    """
    base_dir = JsonModelLoader.get_base_directory()
    styles_dir = os.path.join(base_dir, 'styles')

    # 从目录加载风格文件
    raw_styles = JsonModelLoader.load_models_from_directory(styles_dir, ArticleStyle)

    # 将字典键从id改为name
    name_based_styles = {}
    for style in raw_styles.values():
        name_based_styles[style.name] = style

    return name_based_styles


def get_platform_style(platform: str) -> Optional[ArticleStyle]:
    """根据平台名称获取对应的风格配置

    Args:
        platform: 平台名称

    Returns:
        Optional[ArticleStyle]: 平台风格配置，如果不存在则返回None
    """
    styles = load_article_styles()

    # 尝试直接匹配平台名称和风格名称
    if platform in styles:
        return styles[platform]

    # 尝试模糊匹配名称
    platform_lower = platform.lower()
    for style_name, style in styles.items():
        if platform_lower in style_name.lower():
            return style

    return None


def get_or_create_style(text: str, options: Optional[Dict[str, Any]] = None) -> ArticleStyle:
    """通过文本获取或创建风格

    首先尝试匹配现有风格(精确或模糊匹配)，如果匹配不到，则创建一个临时风格。
    该方法仅在内存中创建风格对象，不会保存到数据库。

    Args:
        text: 风格名称或描述文本
        options: 其他选项和风格属性

    Returns:
        ArticleStyle: 匹配到的或新创建的风格对象
    """
    # 调用StyleFactory中的实现
    from .util import StyleFactory
    return StyleFactory.create_style_from_description(text, options)


def create_style_from_description(description: str, options: Optional[Dict[str, Any]] = None) -> ArticleStyle:
    """根据文本描述创建风格对象

    Args:
        description: 风格的文本描述
        options: 其他选项和风格属性

    Returns:
        ArticleStyle: 创建的风格对象
    """
    # 调用StyleFactory中的实现
    from .util import StyleFactory
    return StyleFactory.create_style_from_description(description, options)


# 保持向后兼容
def get_style_by_id(style_id: str) -> Optional[ArticleStyle]:
    """根据ID获取文章风格配置 (兼容性函数)

    Args:
        style_id: 旧版风格ID，现在被视为风格名称

    Returns:
        Optional[ArticleStyle]: 文章风格配置，如果不存在则返回默认风格
    """
    return get_style_by_name(style_id)
