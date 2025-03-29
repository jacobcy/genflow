"""文章风格模型

该模块定义了文章风格的核心数据模型，用于规范化文章的风格配置。
与 core/models/styles/*.json 中的风格配置对应，精简版本。
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

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


class StyleModel(BaseModel):
    """精简的风格模型"""
    # 核心风格属性
    style: str = Field(default="formal", description="风格类型")
    tone: str = Field(default="neutral", description="语气风格")
    formality: int = Field(default=3, description="正式程度 1-5")
    emotion: bool = Field(default=False, description="是否使用情感表达")
    emoji: bool = Field(default=False, description="是否使用表情")


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
    """获取默认风格实例

    Returns:
        ArticleStyle: 默认风格对象
    """
    return ArticleStyle(**DEFAULT_STYLE)


def load_article_styles() -> Dict[str, ArticleStyle]:
    """从StyleManager加载所有文章风格

    避免直接使用，应该通过StyleManager获取风格
    这里主要是为了解决循环导入问题

    Returns:
        Dict[str, ArticleStyle]: 风格名称->风格对象的映射
    """
    # 避免循环导入
    from .style_manager import StyleManager

    StyleManager.ensure_initialized()
    styles = {}

    for style in StyleManager.get_all_styles():
        styles[style.name] = style

    return styles
