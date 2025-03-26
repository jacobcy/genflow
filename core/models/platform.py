"""平台数据模型"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass

class ContentRules(BaseModel):
    """内容规则"""
    min_length: int = Field(default=0, description="最小字数")
    max_length: int = Field(default=10000, description="最大字数")
    allowed_formats: List[str] = Field(default_list=["text"], description="允许的格式")
    forbidden_words: List[str] = Field(default_list=[], description="禁用词列表")
    required_sections: List[str] = Field(default_list=[], description="必需章节")

class StyleGuide(BaseModel):
    """风格指南"""
    tone: str = Field(default="neutral", description="语气(专业/轻松/正式等)")
    format: str = Field(default="text", description="格式(图文/视频等)")
    target_audience: str = Field(default="general", description="目标受众")
    writing_style: str = Field(default="standard", description="写作风格")
    language_level: str = Field(default="normal", description="语言难度")

class SEORequirements(BaseModel):
    """SEO要求"""
    title_length: int = Field(default=100, description="标题长度限制")
    description_length: int = Field(default=200, description="描述长度限制")
    keyword_count: int = Field(default=5, description="关键词数量")
    meta_requirements: Dict = Field(default_factory=dict, description="Meta标签要求")

@dataclass
class StyleRules:
    """平台风格规则"""
    # 语气风格
    tone: str  # 例如: "专业学术", "轻松活泼", "严谨正式"
    formality: int  # 正式程度 1-5
    emotion: bool  # 是否使用情感表达

    # 格式规则
    code_block: bool  # 是否支持代码块
    emoji: bool  # 是否使用表情
    image_text_ratio: float  # 图文比例 (0-1)
    max_image_count: int  # 最大图片数量

    # 结构规则
    min_paragraph_length: int  # 最小段落长度
    max_paragraph_length: int  # 最大段落长度
    paragraph_count_range: tuple  # 段落数量范围
    section_count_range: tuple  # 章节数量范围

    # SEO规则
    title_length_range: tuple  # 标题长度范围
    keyword_density: float  # 关键词密度
    heading_required: bool  # 是否需要小标题
    tag_count_range: tuple  # 标签数量范围

class Platform(BaseModel):
    """平台模型"""
    id: str = Field(..., description="平台ID")
    name: str = Field(..., description="平台名称")
    type: str = Field(..., description="平台类型")
    url: str = Field(..., description="平台URL")

    # 内容规范
    content_rules: ContentRules = Field(default_factory=ContentRules, description="内容规则")
    style_guide: StyleGuide = Field(default_factory=StyleGuide, description="风格指南")
    seo_requirements: SEORequirements = Field(default_factory=SEORequirements, description="SEO要求")

    # API配置
    api_config: Optional[Dict] = Field(default=None, description="API配置信息")

    # 发布设置
    publish_settings: Dict = Field(default_factory=dict, description="发布设置")

    # 风格规则
    style_rules: Optional[StyleRules] = None  # 平台风格规则

    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": {
                "id": "platform_001",
                "name": "知乎",
                "type": "knowledge_sharing",
                "url": "https://www.zhihu.com",
                "content_rules": {
                    "min_length": 1000,
                    "max_length": 20000,
                    "allowed_formats": ["text", "image", "code"],
                    "forbidden_words": ["广告", "推广"],
                    "required_sections": ["引言", "正文", "总结"]
                },
                "style_guide": {
                    "tone": "专业",
                    "format": "图文结合",
                    "target_audience": "技术人员",
                    "writing_style": "深度解析",
                    "language_level": "advanced"
                },
                "seo_requirements": {
                    "title_length": 100,
                    "description_length": 200,
                    "keyword_count": 5,
                    "meta_requirements": {
                        "title_format": "{主题} - {副标题}",
                        "description_format": "关于{主题}的深度解析..."
                    }
                },
                "publish_settings": {
                    "auto_publish": False,
                    "review_required": True,
                    "publish_time": "immediate"
                }
            }
        }

# 预定义平台配置
PLATFORM_CONFIGS = {
    "zhihu": Platform(
        id="zhihu",
        name="知乎",
        type="knowledge_sharing",
        url="https://www.zhihu.com",
        content_rules=ContentRules(
            min_length=1000,
            max_length=20000,
            allowed_formats=["text", "image", "code"],
            forbidden_words=["广告", "推广"],
            required_sections=["引言", "正文", "总结"]
        ),
        style_guide=StyleGuide(
            tone="专业",
            format="图文结合",
            target_audience="技术人员",
            writing_style="深度解析",
            language_level="advanced"
        )
    ),

    "xiaohongshu": Platform(
        id="xiaohongshu",
        name="小红书",
        type="lifestyle",
        url="https://www.xiaohongshu.com",
        content_rules=ContentRules(
            min_length=300,
            max_length=5000,
            allowed_formats=["text", "image"],
            forbidden_words=["广告", "推广", "微信"],
            required_sections=["开篇", "主要内容", "总结"]
        ),
        style_guide=StyleGuide(
            tone="轻松",
            format="图文结合",
            target_audience="年轻群体",
            writing_style="生活化",
            language_level="simple"
        )
    ),

    "juejin": Platform(
        id="juejin",
        name="掘金",
        type="tech_blog",
        url="https://juejin.cn",
        content_rules=ContentRules(
            min_length=1000,
            max_length=30000,
            allowed_formats=["text", "image", "code"],
            forbidden_words=["广告", "推广"],
            required_sections=["背景", "实现", "总结"]
        ),
        style_guide=StyleGuide(
            tone="专业",
            format="技术文章",
            target_audience="开发者",
            writing_style="实战指南",
            language_level="advanced"
        )
    )
}

@dataclass
class Platform:
    """平台配置类"""
    name: str  # 平台名称
    url: str   # 平台网址
    max_title_length: int = 60  # 标题最大长度
    max_content_length: int = 10000  # 内容最大长度
    allowed_media_types: List[str] = None  # 允许的媒体类型
    support_categories: List[str] = None  # 支持的类别
    format_requirements: Dict[str, str] = None  # 格式要求
    content_guidelines: Dict[str, str] = None  # 内容指南

# 平台配置字典
PLATFORM_CONFIGS: Dict[str, Platform] = {
    "zhihu": Platform(
        name="知乎",
        url="https://www.zhihu.com",
        max_title_length=50,
        max_content_length=20000,
        allowed_media_types=["image", "video", "link"],
        support_categories=["科技", "文化", "生活", "教育", "财经", "健康"],
        format_requirements={
            "title": "问题形式优先",
            "content": "支持Markdown格式"
        },
        content_guidelines={
            "style": "专业、知识性强",
            "tone": "客观、理性"
        }
    ),
    "wechat": Platform(
        name="微信公众号",
        url="https://mp.weixin.qq.com",
        max_title_length=64,
        max_content_length=20000,
        allowed_media_types=["image", "link"],
        support_categories=["科技", "文化", "生活", "教育", "财经", "健康", "娱乐"],
        format_requirements={
            "title": "吸引力为主",
            "content": "支持富文本格式"
        },
        content_guidelines={
            "style": "易读性强、有吸引力",
            "tone": "亲和、有趣"
        }
    ),
    "weibo": Platform(
        name="微博",
        url="https://weibo.com",
        max_title_length=20,
        max_content_length=2000,
        allowed_media_types=["image", "video", "link"],
        support_categories=["热点", "娱乐", "生活", "科技"],
        format_requirements={
            "title": "简短、吸引眼球",
            "content": "简洁、话题标签"
        },
        content_guidelines={
            "style": "简短、有话题性",
            "tone": "活泼、互动性强"
        }
    ),
    "toutiao": Platform(
        name="今日头条",
        url="https://www.toutiao.com",
        max_title_length=30,
        max_content_length=10000,
        allowed_media_types=["image", "video"],
        support_categories=["科技", "财经", "体育", "娱乐", "健康", "数码"],
        format_requirements={
            "title": "信息量大、有吸引力",
            "content": "图文并茂"
        },
        content_guidelines={
            "style": "信息密度高",
            "tone": "时效性强"
        }
    ),
    "xiaohongshu": Platform(
        name="小红书",
        url="https://www.xiaohongshu.com",
        max_title_length=30,
        max_content_length=5000,
        allowed_media_types=["image", "video"],
        support_categories=["美食", "旅行", "美妆", "时尚", "生活方式"],
        format_requirements={
            "title": "简短、关键词明确",
            "content": "图文结合、步骤化"
        },
        content_guidelines={
            "style": "分享式、教程化",
            "tone": "真实、亲切"
        }
    )
}

def get_default_platform() -> Platform:
    """返回默认平台配置

    返回:
        Platform: 默认平台配置对象
    """
    # 这里使用通用平台配置，不特定于任何特定平台
    return Platform(
        name="通用平台",
        url="",
        max_title_length=100,
        max_content_length=50000,
        allowed_media_types=["image", "video", "link"],
        support_categories=["科技", "文化", "生活", "教育", "财经", "健康", "娱乐",
                           "体育", "旅游", "美食", "时尚", "政治", "环境", "职场"],
        format_requirements={
            "title": "清晰、准确",
            "content": "结构合理、逻辑清晰"
        },
        content_guidelines={
            "style": "适应性强、灵活多变",
            "tone": "根据内容类型调整"
        }
    )
