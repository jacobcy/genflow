"""文章风格模型

该模块定义了文章风格的核心数据模型，用于规范化文章的风格配置。
与 core/models/styles/*.json 中的风格配置对应，精简版本。
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ArticleStyle(BaseModel):
    """文章风格定义，专注于语言风格和内容特征"""
    # 基本信息
    name: str = Field(..., description="风格名称")
    type: str = Field(default="general", description="风格类型")
    description: str = Field(default="", description="风格描述")
    target_audience: str = Field(default="", description="目标受众")
    content_types: List[str] = Field(default_factory=list, description="兼容的内容类型名称列表")

    # Core Style Attributes (previously potentially inherited or missing)
    tone: str = Field(default="neutral", description="语气风格")
    formality: int = Field(default=3, description="正式程度 1-5")
    emotion: bool = Field(default=False, description="是否使用情感表达")
    emoji: bool = Field(default=False, description="是否使用表情")

    # Style Specification and Examples
    language_level: str = Field(default="normal", description="语言难度")
    recommended_patterns: List[str] = Field(default_factory=list, description="推荐的写作模式或技巧")
    examples: List[str] = Field(default_factory=list, description="风格示例 (文本片段)")

    # Removed Platform-specific fields:
    # min_length, max_length
    # min_paragraph_length, max_paragraph_length, paragraph_count_range
    # code_block, allowed_formats
    # writing_style (moved to platform)

    # Comment out to_style_config as it depends on removed fields
    # def to_style_config(self) -> Dict[str, Any]:
    #     """转换为StyleCrew需要的风格配置字典
    #     Returns:
    #         Dict[str, Any]: 风格配置字典
    #     """
    #     return {
    #         # ... fields were here ...
    #     }

    def is_compatible_with_content_type(self, content_type: str) -> bool:
        """检查风格是否与内容类型兼容

        Args:
            content_type: 内容类型名称

        Returns:
            bool: 是否兼容
        """
        if not self.content_types:  # Empty list means compatible with all
            return True

        # Direct match
        if content_type in self.content_types:
            return True

        # Attempt fuzzy matching (consider if this is still needed or should be exact)
        for supported_type in self.content_types:
            if (supported_type in content_type) or (content_type in supported_type):
                return True

        return False
