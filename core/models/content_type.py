"""内容类型模型

该模块定义了内容类型的数据模型，用于对内容进行分类和规范化处理。
与 core/models/content_types/*.json 中的配置相对应。
"""

from typing import List, Dict, Optional, Any, Set
from enum import auto
from pydantic import BaseModel, Field, computed_field
import os
import json
from .util import JsonModelLoader
from .enums import ContentCategory

class StructureTemplate(BaseModel):
    """结构模板"""
    name: str = Field(..., description="模板名称")
    description: str = Field(default="", description="模板描述")
    sections: List[str] = Field(default_factory=list, description="章节列表")
    outline_template: Dict[str, Any] = Field(default_factory=dict, description="大纲模板")
    examples: List[str] = Field(default_factory=list, description="示例")

class FormatGuidelines(BaseModel):
    """格式指南"""
    min_length: int = Field(default=0, description="最小长度")
    max_length: int = Field(default=10000, description="最大长度")
    min_section_count: int = Field(default=3, description="最小章节数")
    max_section_count: int = Field(default=12, description="最大章节数")
    recommended_section_length: int = Field(default=500, description="推荐章节长度")
    title_guidelines: Dict[str, Any] = Field(default_factory=dict, description="标题指南")
    requires_images: bool = Field(default=False, description="是否需要图片")
    requires_code: bool = Field(default=False, description="是否需要代码")

    @computed_field
    @property
    def is_long_form(self) -> bool:
        """是否长篇内容"""
        return self.max_length > 5000

    @computed_field
    @property
    def is_short_form(self) -> bool:
        """是否短篇内容"""
        return self.max_length <= 2000

class ContentCharacteristics(BaseModel):
    """内容特性"""
    is_technical: bool = Field(default=False, description="是否技术性内容")
    is_creative: bool = Field(default=False, description="是否创意性内容")
    is_formal: bool = Field(default=False, description="是否正式内容")
    is_timely: bool = Field(default=False, description="是否时效性内容")
    is_narrative: bool = Field(default=False, description="是否叙事性内容")
    is_instructional: bool = Field(default=False, description="是否教学性内容")
    audience_level: str = Field(default="general", description="受众水平")
    multimedia_focus: bool = Field(default=False, description="是否多媒体为主")
    research_intensity: int = Field(default=2, description="研究密集度 1-5")

# 默认内容类型配置
DEFAULT_CONTENT_TYPE = {
    "id": "article",
    "name": "普通文章",
    "category": "ARTICLE",
    "description": "标准文章格式，适合各类主题",
    "format": "long-form",
    "primary_purpose": "inform",
    "structure_templates": [
        {
            "name": "标准文章",
            "description": "常规文章结构",
            "sections": ["引言", "主体", "结论"],
            "outline_template": {
                "intro": "引入主题和背景",
                "main_body": "分析和讨论主题",
                "conclusion": "总结和展望"
            },
            "examples": ["一般性解说文章", "主题研究文章"]
        }
    ],
    "format_guidelines": {
        "min_length": 1000,
        "max_length": 5000,
        "min_section_count": 3,
        "max_section_count": 10,
        "recommended_section_length": 500,
        "title_guidelines": {
            "min_length": 10,
            "max_length": 100,
            "format": "descriptive"
        },
        "requires_images": False,
        "requires_code": False
    },
    "characteristics": {
        "is_technical": False,
        "is_creative": False,
        "is_formal": True,
        "is_timely": False,
        "is_narrative": False,
        "is_instructional": False,
        "audience_level": "general",
        "multimedia_focus": False,
        "research_intensity": 3
    },
    "compatible_styles": ["formal", "informative", "analytical"],
    "example_topics": ["行业分析", "产品评测", "科学研究"],
    "metadata": {
        "version": 1,
        "last_updated": "2023-01-01"
    }
}

class ContentType(BaseModel):
    """内容类型定义，与 content_types/*.json 格式完全对应"""
    # 基本信息
    id: str = Field(..., description="内容类型ID")
    name: str = Field(..., description="内容类型名称")
    category: str = Field(..., description="内容类别", examples=["ARTICLE", "BLOG", "TUTORIAL"])
    description: str = Field(default="", description="内容类型描述")
    format: str = Field(default="standard", description="格式(长文/短文等)")
    primary_purpose: str = Field(default="inform", description="主要目的")
    url: str = Field(default="", description="相关URL")

    # 顶层常用属性 - 便于快速访问
    min_length: int = Field(default=0, description="最小长度")
    max_length: int = Field(default=10000, description="最大长度")
    is_technical: bool = Field(default=False, description="是否技术性内容")
    is_creative: bool = Field(default=False, description="是否创意性内容")
    requires_images: bool = Field(default=False, description="是否需要图片")
    requires_code: bool = Field(default=False, description="是否需要代码")

    # 细节配置
    structure_templates: List[StructureTemplate] = Field(default_factory=list, description="结构模板")
    format_guidelines: FormatGuidelines = Field(default_factory=FormatGuidelines, description="格式指南")
    characteristics: ContentCharacteristics = Field(default_factory=ContentCharacteristics, description="内容特性")
    compatible_styles: List[str] = Field(default_factory=list, description="兼容的风格")
    example_topics: List[str] = Field(default_factory=list, description="示例主题")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    def model_post_init(self, __context):
        """初始化后同步数据"""
        # 同步顶层属性与嵌套结构
        self.min_length = self.format_guidelines.min_length
        self.max_length = self.format_guidelines.max_length
        self.is_technical = self.characteristics.is_technical
        self.is_creative = self.characteristics.is_creative
        self.requires_images = self.format_guidelines.requires_images
        self.requires_code = self.format_guidelines.requires_code

    @computed_field
    @property
    def is_longform(self) -> bool:
        """是否为长篇内容"""
        return self.max_length > 5000

    @computed_field
    @property
    def is_shortform(self) -> bool:
        """是否为短篇内容"""
        return self.max_length <= 2000

    @computed_field
    @property
    def is_formal(self) -> bool:
        """是否为正式内容"""
        return self.characteristics.is_formal

    @computed_field
    @property
    def research_level(self) -> int:
        """研究强度等级"""
        return self.characteristics.research_intensity

    @computed_field
    @property
    def is_educational(self) -> bool:
        """是否教育性内容"""
        return self.characteristics.is_instructional

    @classmethod
    def get_all_content_types(cls) -> Dict[str, 'ContentType']:
        """获取所有内容类型配置

        Returns:
            Dict[str, ContentType]: 内容类型字典，键为内容类型ID
        """
        return load_content_types()

    @classmethod
    def from_id(cls, content_type_id: str) -> Optional['ContentType']:
        """根据ID获取内容类型

        Args:
            content_type_id: 内容类型ID

        Returns:
            Optional[ContentType]: 内容类型配置，如果不存在则返回None
        """
        return get_content_type_by_id(content_type_id)

    def get_recommended_structure(self) -> Optional[StructureTemplate]:
        """获取推荐的内容结构模板

        Returns:
            Optional[StructureTemplate]: 推荐的结构模板，如果没有则返回None
        """
        if not self.structure_templates:
            return None
        return self.structure_templates[0]

    def get_section_guidelines(self) -> Dict[str, Any]:
        """获取章节相关指南

        Returns:
            Dict: 章节格式指南
        """
        return {
            "min_count": self.format_guidelines.min_section_count,
            "max_count": self.format_guidelines.max_section_count,
            "recommended_length": self.format_guidelines.recommended_section_length,
            "sections": [t.sections for t in self.structure_templates] if self.structure_templates else []
        }

    def get_title_guidelines(self) -> Dict[str, Any]:
        """获取标题相关指南

        Returns:
            Dict: 标题指南
        """
        return self.format_guidelines.title_guidelines or {}

    def is_compatible_with_style(self, style_id: str) -> bool:
        """检查内容类型是否与指定风格兼容

        Args:
            style_id: 风格ID

        Returns:
            bool: 是否兼容
        """
        if not hasattr(self, "compatible_styles") or not self.compatible_styles:
            # 没有指定兼容风格，默认兼容所有
            return True

        # 当前是否包含该风格
        if style_id in self.compatible_styles:
            return True

        # 尝试模糊匹配
        for compatible_style in self.compatible_styles:
            if (compatible_style in style_id) or (style_id in compatible_style):
                return True

        return False

    def get_type_summary(self) -> Dict[str, Any]:
        """获取内容类型摘要信息

        Returns:
            Dict: 内容类型摘要
        """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "primary_purpose": self.primary_purpose,
            "length_range": [self.min_length, self.max_length],
            "is_technical": self.is_technical,
            "is_creative": self.is_creative,
            "requires_images": self.requires_images,
            "requires_code": self.requires_code,
            "research_level": self.research_level,
            "is_formal": self.is_formal,
            "is_educational": self.is_educational,
            "section_guidelines": self.get_section_guidelines()
        }

    @classmethod
    def get_default(cls) -> 'ContentType':
        """获取默认的内容类型配置

        Returns:
            ContentType: 默认的内容类型配置
        """
        return get_default_content_type()

    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": DEFAULT_CONTENT_TYPE
        }

def get_default_content_type() -> ContentType:
    """获取默认的内容类型配置

    Returns:
        ContentType: 默认的内容类型配置
    """
    return ContentType(**DEFAULT_CONTENT_TYPE)

def load_content_types() -> Dict[str, ContentType]:
    """加载所有内容类型配置

    Returns:
        Dict[str, ContentType]: 内容类型字典，键为内容类型ID
    """
    base_dir = JsonModelLoader.get_base_directory()
    content_types_dir = os.path.join(base_dir, 'content_types')

    # 排除类别映射文件
    results = {}

    # 确保目录存在
    if not os.path.exists(content_types_dir):
        from loguru import logger
        logger.warning(f"目录 {content_types_dir} 不存在")
        return results

    # 加载目录中的所有 JSON 文件，排除category_mapping.json
    json_files = [f for f in os.listdir(content_types_dir)
                  if f.endswith('.json') and f != 'category_mapping.json']

    for json_file in json_files:
        try:
            json_path = os.path.join(content_types_dir, json_file)
            model_instance = JsonModelLoader.load_model(json_path, ContentType)
            if model_instance:
                content_type_id = model_instance.id
                results[content_type_id] = model_instance
        except Exception as e:
            from loguru import logger
            logger.error(f"处理 {json_file} 时出错: {str(e)}")

    return results

def load_category_mapping() -> Dict[str, Any]:
    """加载类别映射配置

    Returns:
        Dict[str, Any]: 类别映射配置
    """
    base_dir = JsonModelLoader.get_base_directory()
    mapping_file = os.path.join(base_dir, 'content_types', 'category_mapping.json')

    if not os.path.exists(mapping_file):
        return {}

    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        from loguru import logger
        logger.error(f"加载类别映射失败: {str(e)}")
        return {}

def get_content_type_by_id(content_type_id: str) -> Optional[ContentType]:
    """根据ID获取内容类型配置

    Args:
        content_type_id: 内容类型ID

    Returns:
        Optional[ContentType]: 内容类型配置，如果不存在则返回None
    """
    content_types = load_content_types()
    return content_types.get(content_type_id, None)

def get_content_type_by_category(category: str) -> Optional[ContentType]:
    """根据类别名称获取内容类型配置

    Args:
        category: 类别名称

    Returns:
        Optional[ContentType]: 内容类型配置，如果不存在则返回None
    """
    category_mapping = load_category_mapping().get("category_mapping", {})
    content_type_id = category_mapping.get(category, None)

    if not content_type_id:
        return None

    return get_content_type_by_id(content_type_id)
