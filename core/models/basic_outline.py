"""基础大纲模型

该模块定义了基础大纲的数据模型，用于组织独立文本内容，
不依赖于特定话题，可用于扩展现有内容或创建独立文档。
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from .util.enums import ArticleSectionType

class OutlineSection(BaseModel):
    """大纲章节

    文章大纲中的章节，包含标题、内容概要、类型和关键点等信息。
    """
    title: str = Field(..., description="章节标题")
    content: str = Field(default="", description="章节概要内容")
    order: int = Field(default=0, description="章节顺序")
    section_type: ArticleSectionType = Field(
        default=ArticleSectionType.MAIN_POINT,
        description="章节类型"
    )
    subsections: List['OutlineSection'] = Field(
        default_factory=list,
        description="子章节"
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="关键要点"
    )
    references: List[str] = Field(
        default_factory=list,
        description="参考资料"
    )

class BasicOutline(BaseModel):
    """基础大纲模型

    提供通用的内容大纲结构，可用于任何文本内容的组织。
    不依赖于特定话题，适用于扩展现有文本或创建独立内容。
    """
    id: Optional[str] = Field(default=None, description="大纲ID")
    content_type: str = Field(default="default", description="内容类型名称")
    title: str = Field(..., description="文章标题")
    summary: str = Field(..., description="文章摘要")
    sections: List[OutlineSection] = Field(
        default_factory=list,
        description="大纲章节列表"
    )
    tags: List[str] = Field(default_factory=list, description="文章标签")

    # 大纲特有字段
    research_notes: List[str] = Field(
        default_factory=list,
        description="研究笔记"
    )
    key_insights: List[str] = Field(
        default_factory=list,
        description="核心见解"
    )
    target_word_count: int = Field(
        default=0,
        description="目标字数"
    )

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v):
        """验证内容类型"""
        # 此处可添加内容类型验证逻辑
        return v

    def to_article_sections(self) -> List[Dict]:
        """将大纲转换为文章章节列表

        用于从大纲创建文章时，将大纲章节转换为文章章节格式。
        为保持兼容性，该方法重定向到OutlineConverter中的同名方法。

        Returns:
            List[Dict]: 文章章节列表
        """
        from .util.outline_converter import OutlineConverter
        return OutlineConverter.to_article_sections(self)

    def to_full_text(self) -> str:
        """将大纲转换为完整文本

        将大纲的所有部分（包括标题、摘要、章节等）
        转换为结构化的文本内容。
        为保持兼容性，该方法重定向到OutlineConverter中的同名方法。

        Returns:
            str: 完整文本内容
        """
        from .util.outline_converter import OutlineConverter
        return OutlineConverter.to_full_text(self)

    def to_basic_article(self) -> 'BasicArticle':
        """将大纲转换为BasicArticle对象

        此方法生成一个仅包含基本信息的文章对象，
        用于提交给StyleCrew进行风格处理。
        为保持兼容性，该方法重定向到OutlineConverter中的同名方法。

        Returns:
            BasicArticle: 基本文章对象
        """
        from .util.outline_converter import OutlineConverter
        return OutlineConverter.to_basic_article(self)

    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": {
                "id": "outline_001",
                "content_type": "general_article",
                "title": "高效时间管理技巧：让你的生活井然有序",
                "summary": "本文介绍了一系列实用的时间管理技巧，帮助读者更好地规划和利用时间",
                "tags": ["时间管理", "效率", "生活技巧"],
                "sections": [
                    {
                        "title": "引言",
                        "content": "介绍时间管理的重要性和常见挑战",
                        "order": 1,
                        "section_type": "introduction",
                        "key_points": [
                            "时间是不可再生资源",
                            "现代生活中的时间压力"
                        ]
                    },
                    {
                        "title": "建立优先级系统",
                        "content": "如何区分任务重要性和紧急程度",
                        "order": 2,
                        "section_type": "main_point",
                        "key_points": [
                            "重要与紧急矩阵",
                            "任务分类方法",
                            "避免只关注紧急事项"
                        ]
                    }
                ],
                "research_notes": [
                    "增加一些实际案例",
                    "考虑添加时间管理工具比较"
                ],
                "key_insights": [
                    "有效的时间管理是技能而非天赋",
                    "持续的小改进比完美的系统更重要"
                ],
                "target_word_count": 2000,
                "created_at": "2023-09-01T10:00:00"
            }
        }
