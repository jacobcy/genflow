"""平台模型

该模块定义了平台配置的数据结构。
只包含数据结构，不包含逻辑代码。
"""

from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field, ConfigDict

class PlatformConstraints(BaseModel):
    """平台内容的硬约束规则"""
    min_length: int = Field(default=0, description="最小字数限制")
    max_length: int = Field(default=100000, description="最大字数限制")
    max_title_length: int = Field(default=100, description="标题最大长度")
    max_image_count: int = Field(default=20, description="最大图片数量")
    max_video_count: int = Field(default=0, description="最大视频数量")
    forbidden_words: List[str] = Field(default_factory=list, description="禁用词列表")
    required_elements: List[str] = Field(default_factory=list, description="必需元素 (例如特定格式的脚注)")
    allowed_formats: List[str] = Field(default_factory=lambda: ["text"], description="允许的内容格式 (例如 text, markdown, html)")
    allowed_media_types: List[str] = Field(default_factory=lambda: ["image/png", "image/jpeg"], description="允许的媒体类型 (MIME types)")
    code_block_support: bool = Field(default=True, description="是否支持代码块")
    math_formula_support: bool = Field(default=False, description="是否支持数学公式")
    table_support: bool = Field(default=True, description="是否支持表格")
    emoji_support: bool = Field(default=True, description="是否支持表情符号")

class TechnicalRequirements(BaseModel):
    """平台的技术对接要求"""
    api_endpoint: Optional[str] = Field(default=None, description="API基础URL")
    api_version: Optional[str] = Field(default=None, description="API版本")
    max_request_size_kb: int = Field(default=5120, description="最大请求大小(KB)")
    supported_media_upload_formats: List[str] = Field(default_factory=lambda: ["image/png", "image/jpeg"], description="支持上传的媒体文件类型")
    auth_method: Optional[str] = Field(default=None, description="认证方式 (e.g., OAuth2, APIKey)")
    https_required: bool = Field(default=True, description="是否要求HTTPS")

class Platform(BaseModel):
    """平台配置模型，定义一个平台的属性、约束和技术要求"""
    id: str = Field(..., description="平台的唯一标识符 (例如 'wechat_mp', 'zhihu')")
    name: str = Field(..., description="平台的可读名称 (例如 '微信公众号', '知乎')")
    url: Optional[str] = Field(default=None, description="平台主页或发布入口 URL")
    description: str = Field(default="", description="平台描述")
    category: str = Field(default="general", description="平台分类 (例如 'blogging', 'social', 'news')")
    primary_language: str = Field(default="zh-CN", description="平台主要语言")
    supported_languages: List[str] = Field(default_factory=lambda: ["zh-CN"], description="支持的语言列表")

    # 内容约束
    constraints: PlatformConstraints = Field(default_factory=PlatformConstraints, description="内容发布约束")

    # 技术要求
    technical: TechnicalRequirements = Field(default_factory=TechnicalRequirements, description="技术对接要求")

    # 审核相关 (简化)
    manual_review_likely: bool = Field(default=True, description="是否可能需要人工审核")

    # 使用 ConfigDict
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "medium",
                "name": "Medium",
                "url": "https://medium.com",
                "description": "Medium是一个开放的内容平台，任何人都可以阅读、写作和分享想法。",
                "category": "blogging",
                "primary_language": "en-US",
                "supported_languages": ["en-US", "es"],
                "constraints": {
                    "min_length": 100,
                    "max_length": 20000,
                    "max_title_length": 100,
                    "max_image_count": 50,
                    "forbidden_words": ["advertisement"],
                    "allowed_formats": ["markdown", "text"],
                    "code_block_support": True,
                },
                "technical": {
                    "auth_method": "OAuth2",
                    "https_required": True
                },
                "manual_review_likely": True
            }
        }
    )
