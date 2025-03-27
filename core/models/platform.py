"""平台数据模型，专注于平台硬约束"""
import os
import json
from typing import List, Dict, Optional, Any, Set
from pydantic import BaseModel, Field, field_validator, computed_field
from .util import JsonModelLoader
from loguru import logger

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
        """平台是否适合技术内容"""
        return self.code_block_support and "code" in self.allowed_formats

    @computed_field
    @property
    def is_media_rich(self) -> bool:
        """平台是否支持丰富媒体"""
        return self.max_image_count > 5 and "image" in self.allowed_formats

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
    id: str = Field(..., description="平台ID")
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

    # 验证器 - 确保顶层字段与嵌套字段保持一致
    @field_validator('constraints')
    def sync_constraints(cls, v, info):
        """同步顶层约束到constraints结构"""
        # 从values中获取顶层字段
        values = info.data
        if 'min_length' in values:
            v.min_length = values['min_length']
        if 'max_length' in values:
            v.max_length = values['max_length']
        if 'max_title_length' in values:
            v.max_title_length = values['max_title_length']
        if 'max_image_count' in values:
            v.max_image_count = values['max_image_count']
        if 'forbidden_words' in values:
            v.forbidden_words = values['forbidden_words']
        return v

    def model_post_init(self, __context):
        """初始化后同步constraints到顶层字段"""
        self.min_length = self.constraints.min_length
        self.max_length = self.constraints.max_length
        self.max_title_length = self.constraints.max_title_length
        self.max_image_count = self.constraints.max_image_count
        self.forbidden_words = self.constraints.forbidden_words

    @computed_field
    @property
    def supports_code(self) -> bool:
        """平台是否支持代码块"""
        return self.constraints.code_block_support

    @computed_field
    @property
    def supports_math(self) -> bool:
        """平台是否支持数学公式"""
        return self.constraints.math_formula_support

    @computed_field
    @property
    def allowed_formats(self) -> List[str]:
        """平台支持的内容格式"""
        return self.constraints.allowed_formats

    def validate_content(self, title_length: int, content_length: int, image_count: int = 0,
                        video_count: int = 0, formats: List[str] = None) -> Dict[str, bool]:
        """验证内容是否符合平台硬约束

        Args:
            title_length: 标题长度
            content_length: 内容长度
            image_count: 图片数量
            video_count: 视频数量
            formats: 使用的内容格式列表

        Returns:
            Dict[str, bool]: 各项验证结果
        """
        results = {
            "title_length_valid": title_length <= self.max_title_length,
            "content_length_valid": (self.min_length <= content_length <= self.max_length),
            "image_count_valid": image_count <= self.max_image_count,
            "video_count_valid": video_count <= self.constraints.max_video_count,
        }

        # 验证格式支持
        if formats:
            results["formats_valid"] = all(fmt in self.constraints.allowed_formats for fmt in formats)

        return results

    def has_forbidden_words(self, text: str) -> List[str]:
        """检查文本中是否包含禁用词

        Args:
            text: 要检查的文本

        Returns:
            List[str]: 找到的禁用词列表，空列表表示没有禁用词
        """
        found = []
        for word in self.forbidden_words:
            if word in text:
                found.append(word)
        return found

    def get_platform_constraints(self) -> Dict[str, Any]:
        """获取平台硬约束的详细信息，用于发布前检查

        Returns:
            Dict: 平台约束详情
        """
        return {
            "content_constraints": {
                "min_length": self.min_length,
                "max_length": self.max_length,
                "max_title_length": self.max_title_length,
                "max_image_count": self.max_image_count,
                "max_video_count": self.constraints.max_video_count,
                "allowed_formats": self.constraints.allowed_formats,
                "forbidden_words": self.forbidden_words,
                "required_elements": self.constraints.required_elements,
                "supports_code": self.supports_code,
                "supports_math": self.supports_math
            },
            "technical_requirements": {
                "supported_file_types": self.technical.supported_file_types,
                "max_request_size": self.technical.max_request_size,
                "api_version": self.technical.api_version,
            },
            "review_info": {
                "review_required": self.review_required,
                "auto_review_enabled": self.auto_review_enabled,
            }
        }

    def get_all_supported_formats(self) -> Set[str]:
        """获取平台支持的所有内容格式

        Returns:
            Set[str]: 支持的格式集合
        """
        formats = set(self.constraints.allowed_formats)
        if self.supports_code:
            formats.add("code")
        if self.supports_math:
            formats.add("math")
        return formats

    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": {
                "id": "zhihu",
                "name": "知乎",
                "url": "https://www.zhihu.com",
                "description": "中文互联网高质量问答社区和创作者聚集平台",
                "category": "knowledge_sharing",
                "primary_language": "zh-CN",
                "min_length": 100,
                "max_length": 60000,
                "max_title_length": 100,
                "max_image_count": 50,
                "forbidden_words": ["广告", "推广", "违禁词"],
                "constraints": {
                    "allowed_formats": ["text", "image", "video", "code", "math"],
                    "code_block_support": True,
                    "math_formula_support": True
                },
                "review_required": True
            }
        }

def get_default_platform() -> Platform:
    """返回默认平台配置

    提供一个通用的基础平台配置，适用于大多数内容发布场景

    Returns:
        Platform: 默认平台配置对象
    """
    return Platform(
        id="default",
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

# 预定义平台配置字典
PLATFORM_CONFIGS: Dict[str, Platform] = {}

def load_platform_config(platform_id: str) -> Platform:
    """从 JSON 文件加载平台配置

    Args:
        platform_id: 平台ID（如 'zhihu', 'wechat' 等）

    Returns:
        Platform: 平台配置对象

    Raises:
        FileNotFoundError: 如果配置文件不存在
        ValueError: 如果配置文件格式不正确
    """
    # 优先从 models/platforms 目录加载
    base_dir = JsonModelLoader.get_base_directory()
    platforms_dir = os.path.join(base_dir, 'platforms')
    config_path = os.path.join(platforms_dir, f'{platform_id}.json')

    try:
        # 尝试使用 JsonModelLoader 加载
        platform = JsonModelLoader.load_model(config_path, Platform)
        if platform:
            return platform

        # 如果加载失败，尝试从旧目录加载
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        legacy_config_path = os.path.join(current_dir, 'core', 'constants', 'platforms', f'{platform_id}.json')

        if os.path.exists(legacy_config_path):
            logger.warning(f"从旧目录加载平台配置: {legacy_config_path}")
            with open(legacy_config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                return Platform(**config_data)

        if platform_id == 'default':
            return get_default_platform()

        raise FileNotFoundError(f"平台配置文件未找到: {config_path}")
    except FileNotFoundError:
        if platform_id == 'default':
            return get_default_platform()
        raise FileNotFoundError(f"平台配置文件未找到: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"平台配置JSON格式错误: {e}")
    except Exception as e:
        raise ValueError(f"加载平台配置出错: {e}")

def init_platform_configs():
    """初始化平台配置字典"""
    # 首先加载默认配置
    PLATFORM_CONFIGS['default'] = get_default_platform()

    # 获取当前配置文件目录
    base_dir = JsonModelLoader.get_base_directory()
    platforms_dir = os.path.join(base_dir, 'platforms')

    # 尝试创建目录（如果不存在）
    if not os.path.exists(platforms_dir):
        try:
            os.makedirs(platforms_dir)
            logger.info(f"已创建平台配置目录: {platforms_dir}")
        except Exception as e:
            logger.error(f"创建平台配置目录失败: {e}")

    # 使用 JsonModelLoader 加载所有平台配置
    platforms = JsonModelLoader.load_models_from_directory(platforms_dir, Platform)
    PLATFORM_CONFIGS.update(platforms)
    logger.info(f"已从 {platforms_dir} 加载 {len(platforms)} 个平台配置")

    # 尝试从旧目录加载，用于兼容
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        legacy_config_dir = os.path.join(current_dir, 'core', 'constants', 'platforms')

        if os.path.exists(legacy_config_dir):
            # 遍历所有 JSON 文件
            for filename in os.listdir(legacy_config_dir):
                if filename.endswith('.json'):
                    platform_id = filename[:-5]  # 移除 .json 后缀
                    # 如果平台还未加载，则从旧目录加载
                    if platform_id not in PLATFORM_CONFIGS:
                        try:
                            PLATFORM_CONFIGS[platform_id] = load_platform_config(platform_id)
                            logger.info(f"从旧目录加载平台配置: {platform_id}")
                        except Exception as e:
                            logger.warning(f"从旧目录加载平台配置 {platform_id} 失败: {e}")
    except Exception as e:
        logger.error(f"尝试从旧目录加载平台配置时出错: {e}")

# 初始化平台配置
init_platform_configs()

def get_platform(platform_id: str) -> Optional[Platform]:
    """根据ID获取平台配置

    Args:
        platform_id: 平台ID

    Returns:
        Optional[Platform]: 平台配置，如不存在则返回None

    Raises:
        ValueError: 平台ID为空时
    """
    if not platform_id:
        raise ValueError("平台ID不能为空")

    # 尝试从缓存获取
    if platform_id in PLATFORM_CONFIGS:
        return PLATFORM_CONFIGS[platform_id]

    # 尝试从文件加载
    try:
        platform = load_platform_config(platform_id)
        # 缓存平台配置
        if platform:
            PLATFORM_CONFIGS[platform_id] = platform
        return platform
    except (FileNotFoundError, ValueError) as e:
        logger.warning(f"获取平台配置失败: {e}")

    # 平台不存在，返回None
    return None

def get_all_platforms() -> Dict[str, Platform]:
    """获取所有平台配置

    Returns:
        Dict[str, Platform]: 平台配置字典，键为平台ID
    """
    # 返回当前已加载的所有平台配置
    return PLATFORM_CONFIGS.copy()
