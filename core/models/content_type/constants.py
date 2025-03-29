"""内容类型配置模块

定义内容类型常量及其配置，作为整个应用的统一来源。
包括不同内容类型的研究配置和写作配置，以及与平台分类的映射关系。
"""

# 内容类型常量
CONTENT_TYPE_FLASH_NEWS = "快讯"
CONTENT_TYPE_SOCIAL_MEDIA = "社交媒体"
CONTENT_TYPE_NEWS = "新闻"
CONTENT_TYPE_BLOG = "博客"
CONTENT_TYPE_TUTORIAL = "教程"
CONTENT_TYPE_REVIEW = "评测"
CONTENT_TYPE_STORY = "故事"
CONTENT_TYPE_PAPER = "论文"
CONTENT_TYPE_RESEARCH_REPORT = "研究报告"
CONTENT_TYPE_ANALYSIS = "分析"
CONTENT_TYPE_TECH = "技术"
CONTENT_TYPE_QA = "问答"
CONTENT_TYPE_ENTERTAINMENT = "娱乐"
CONTENT_TYPE_LIFE = "生活"
CONTENT_TYPE_SCIENCE = "科普"


# 研究深度级别常量
RESEARCH_DEPTH_LIGHT = "轻量"
RESEARCH_DEPTH_MEDIUM = "中等"
RESEARCH_DEPTH_DEEP = "深度"

# 平台分类与内容类型的映射关系
CATEGORY_TO_CONTENT_TYPE = {
    # 平台属性映射
    "社交": CONTENT_TYPE_SOCIAL_MEDIA,
    "技术": CONTENT_TYPE_TECH,
    "新闻": CONTENT_TYPE_NEWS,
    "知识": CONTENT_TYPE_QA,
    "游戏": CONTENT_TYPE_ENTERTAINMENT,
    "娱乐": CONTENT_TYPE_ENTERTAINMENT,
    "购物": CONTENT_TYPE_LIFE,
    "数码": CONTENT_TYPE_REVIEW,
    "阅读": CONTENT_TYPE_BLOG,

    # 内容属性映射
    "热点": CONTENT_TYPE_FLASH_NEWS,
    "时事": CONTENT_TYPE_NEWS,
    "开发": CONTENT_TYPE_TECH,
    "编程": CONTENT_TYPE_TECH,
    "互联网": CONTENT_TYPE_TECH,
    "科技": CONTENT_TYPE_TECH,
    "创业": CONTENT_TYPE_ANALYSIS,
    "商业": CONTENT_TYPE_ANALYSIS,
    "问答": CONTENT_TYPE_QA,
    "科普": CONTENT_TYPE_SCIENCE,
    "二次元": CONTENT_TYPE_ENTERTAINMENT,
    "电竞": CONTENT_TYPE_ENTERTAINMENT,
    "优惠": CONTENT_TYPE_REVIEW,
    "效率": CONTENT_TYPE_TUTORIAL,
    "安全": CONTENT_TYPE_TECH,
    "创新": CONTENT_TYPE_BLOG,
    "开源": CONTENT_TYPE_TECH,

    # 内容形式映射
    "短视频": CONTENT_TYPE_SOCIAL_MEDIA,
    "讨论": CONTENT_TYPE_SOCIAL_MEDIA,
    "综合": CONTENT_TYPE_NEWS,
    "深度": CONTENT_TYPE_ANALYSIS,
    "视频": CONTENT_TYPE_ENTERTAINMENT,
    "评论": CONTENT_TYPE_REVIEW,
    "博客": CONTENT_TYPE_BLOG,
    "资讯": CONTENT_TYPE_NEWS,

    # 平台特色映射
    "Linux": CONTENT_TYPE_TECH,
    "主机": CONTENT_TYPE_TECH,
    "米哈游": CONTENT_TYPE_ENTERTAINMENT,
    "英雄联盟": CONTENT_TYPE_ENTERTAINMENT,
    "应用": CONTENT_TYPE_REVIEW,
    "安卓": CONTENT_TYPE_TECH,
    "摄影": CONTENT_TYPE_TUTORIAL,
    "设计": CONTENT_TYPE_TUTORIAL,

    # 其他属性映射
    "学习": CONTENT_TYPE_TUTORIAL,
    "国际": CONTENT_TYPE_NEWS,
    "消费": CONTENT_TYPE_REVIEW,
    "生活": CONTENT_TYPE_LIFE,
    "监测": CONTENT_TYPE_FLASH_NEWS,
    "预警": CONTENT_TYPE_FLASH_NEWS
}

# 研究配置项 - 添加新增内容类型的配置
RESEARCH_CONFIG = {
    # 短内容类型 - 轻量级研究
    CONTENT_TYPE_FLASH_NEWS: {
        "depth": RESEARCH_DEPTH_LIGHT,
        "needs_expert": False,
        "needs_data_analysis": False,
        "source_count": "2-5",
        "source_types": ["新闻网站", "官方声明"],

        "focus": "时效性",
        "description": "简短的信息收集，重点在于时效性和准确性"
    },
    CONTENT_TYPE_SOCIAL_MEDIA: {
        "depth": RESEARCH_DEPTH_LIGHT,
        "needs_expert": False,
        "needs_data_analysis": False,
        "source_count": "3-7",
        "source_types": ["社交平台", "热门话题", "新闻"],

        "focus": "话题热度",
        "description": "收集当前热门讨论和观点，关注传播性"
    },

    # 标准内容类型 - 中等深度研究
    CONTENT_TYPE_NEWS: {
        "depth": RESEARCH_DEPTH_MEDIUM,
        "needs_expert": False,
        "needs_data_analysis": True,
        "source_count": "5-10",
        "source_types": ["新闻网站", "官方声明", "专业评论"],

        "focus": "事实准确性",
        "description": "全面收集事实和观点，注重多角度报道"
    },
    CONTENT_TYPE_BLOG: {
        "depth": RESEARCH_DEPTH_MEDIUM,
        "needs_expert": False,
        "needs_data_analysis": False,
        "source_count": "5-8",
        "source_types": ["博客", "专业网站", "案例研究"],

        "focus": "观点和案例",
        "description": "收集独特观点和有价值的案例，注重个性化内容"
    },
    CONTENT_TYPE_TUTORIAL: {
        "depth": RESEARCH_DEPTH_MEDIUM,
        "needs_expert": True,
        "needs_data_analysis": False,
        "source_count": "3-7",
        "source_types": ["官方文档", "教程网站", "实践案例"],

        "focus": "实操性",
        "description": "收集详细操作步骤和最佳实践，注重准确性和实用性"
    },
    CONTENT_TYPE_REVIEW: {
        "depth": RESEARCH_DEPTH_MEDIUM,
        "needs_expert": True,
        "needs_data_analysis": True,
        "source_count": "5-10",
        "source_types": ["产品文档", "专业评测", "用户反馈"],

        "focus": "全面评价",
        "description": "收集多维度评价数据，注重客观性和比较视角"
    },
    CONTENT_TYPE_STORY: {
        "depth": RESEARCH_DEPTH_MEDIUM,
        "needs_expert": False,
        "needs_data_analysis": False,
        "source_count": "5-10",
        "source_types": ["故事素材", "相关背景", "文化资料"],

        "focus": "叙事元素",
        "description": "收集故事元素和背景资料，注重情感共鸣和故事性"
    },
    CONTENT_TYPE_TECH: {
        "depth": RESEARCH_DEPTH_MEDIUM,
        "needs_expert": True,
        "needs_data_analysis": True,
        "source_count": "5-15",
        "source_types": ["技术文档", "代码库", "开发论坛"],

        "focus": "技术准确性",
        "description": "收集技术细节和实现方法，注重实际应用和可靠性"
    },
    CONTENT_TYPE_QA: {
        "depth": RESEARCH_DEPTH_MEDIUM,
        "needs_expert": True,
        "needs_data_analysis": False,
        "source_count": "5-15",
        "source_types": ["问答平台", "专业讨论", "官方资料"],

        "focus": "解决问题",
        "description": "收集问题和解决方案，注重实用性和可操作性"
    },
    CONTENT_TYPE_ENTERTAINMENT: {
        "depth": RESEARCH_DEPTH_LIGHT,
        "needs_expert": False,
        "needs_data_analysis": False,
        "source_count": "3-10",
        "source_types": ["娱乐平台", "粉丝社区", "新闻资讯"],

        "focus": "趣味性",
        "description": "收集有趣内容和背景信息，注重吸引力和传播性"
    },
    CONTENT_TYPE_LIFE: {
        "depth": RESEARCH_DEPTH_MEDIUM,
        "needs_expert": False,
        "needs_data_analysis": False,
        "source_count": "5-10",
        "source_types": ["生活平台", "用户反馈", "专业建议"],

        "focus": "实用性",
        "description": "收集生活实用信息和经验，注重实用性和可操作性"
    },
    CONTENT_TYPE_SCIENCE: {
        "depth": RESEARCH_DEPTH_MEDIUM,
        "needs_expert": True,
        "needs_data_analysis": True,
        "source_count": "5-15",
        "source_types": ["科普网站", "研究简报", "专业资料"],

        "focus": "科学准确性",
        "description": "收集科学知识和研究结果，注重准确性和通俗解释"
    },

    # 深度内容类型 - 深入研究
    CONTENT_TYPE_PAPER: {
        "depth": RESEARCH_DEPTH_DEEP,
        "needs_expert": True,
        "needs_data_analysis": True,
        "source_count": "15-30",
        "source_types": ["学术论文", "研究数据", "专业书籍"],

        "focus": "学术严谨",
        "description": "深入文献研究，建立理论框架，严格的学术标准"
    },
    CONTENT_TYPE_RESEARCH_REPORT: {
        "depth": RESEARCH_DEPTH_DEEP,
        "needs_expert": True,
        "needs_data_analysis": True,
        "source_count": "15-25",
        "source_types": ["行业报告", "数据分析", "专家访谈"],

        "focus": "数据驱动",
        "description": "综合数据分析和行业洞察，注重预测性和指导性"
    },
    CONTENT_TYPE_ANALYSIS: {
        "depth": RESEARCH_DEPTH_DEEP,
        "needs_expert": True,
        "needs_data_analysis": True,
        "source_count": "10-20",
        "source_types": ["数据分析", "案例研究", "专业观点"],

        "focus": "深度洞察",
        "description": "对特定问题进行深入分析，提供独到见解和解决方案"
    }
}

# 默认研究配置
DEFAULT_RESEARCH_CONFIG = {
    "depth": RESEARCH_DEPTH_MEDIUM,
    "needs_expert": False,
    "needs_data_analysis": False,
    "source_count": "5-10",
    "source_types": ["专业网站", "新闻", "行业资料"],

    "focus": "综合信息",
    "description": "全面收集相关信息，平衡深度和广度"
}


#################################################
# 写作配置
#################################################

# 写作配置项 - 更新并添加新增内容类型的配置
WRITING_CONFIG = {
    # 短内容类型 - 简洁、直接
    CONTENT_TYPE_FLASH_NEWS: {
        "word_count": "800-1200",
        "style": "简洁直接",
        "structure": "要点式",
        "seo_focus": "时效性关键词",
        "depth": RESEARCH_DEPTH_LIGHT
    },
    CONTENT_TYPE_SOCIAL_MEDIA: {
        "word_count": "300-800",
        "style": "对话式、引人入胜",
        "structure": "段落简短",
        "seo_focus": "热门话题标签",
        "depth": RESEARCH_DEPTH_LIGHT
    },

    # 标准内容类型 - 平衡信息量和可读性
    CONTENT_TYPE_NEWS: {
        "word_count": "1000-1500",
        "style": "客观报道",
        "structure": "倒金字塔",
        "seo_focus": "时效性+主题关键词",
        "depth": RESEARCH_DEPTH_MEDIUM
    },
    CONTENT_TYPE_BLOG: {
        "word_count": "1200-2000",
        "style": "个性化、对话式",
        "structure": "引言-主体-结论",
        "seo_focus": "长尾关键词",
        "depth": RESEARCH_DEPTH_MEDIUM
    },
    CONTENT_TYPE_TUTORIAL: {
        "word_count": "1500-3000",
        "style": "教学式、步骤清晰",
        "structure": "步骤式",
        "seo_focus": "操作类关键词",
        "depth": RESEARCH_DEPTH_MEDIUM
    },
    CONTENT_TYPE_REVIEW: {
        "word_count": "1500-2500",
        "style": "分析性、评价性",
        "structure": "优缺点分析",
        "seo_focus": "产品+评价关键词",
        "depth": RESEARCH_DEPTH_MEDIUM
    },
    CONTENT_TYPE_STORY: {
        "word_count": "1500-3000",
        "style": "叙事性、生动",
        "structure": "起承转合",
        "seo_focus": "情感关键词",
        "depth": RESEARCH_DEPTH_MEDIUM
    },
    CONTENT_TYPE_TECH: {
        "word_count": "1500-3000",
        "style": "技术性、精确",
        "structure": "问题-方案-实现",
        "seo_focus": "技术词汇+实现方法",
        "depth": RESEARCH_DEPTH_MEDIUM
    },
    CONTENT_TYPE_QA: {
        "word_count": "1000-2000",
        "style": "问答式、清晰",
        "structure": "问题-解答-扩展",
        "seo_focus": "问题关键词+解决方案",
        "depth": RESEARCH_DEPTH_MEDIUM
    },
    CONTENT_TYPE_ENTERTAINMENT: {
        "word_count": "800-1500",
        "style": "轻松活泼",
        "structure": "亮点突出",
        "seo_focus": "娱乐热词+人物名称",
        "depth": RESEARCH_DEPTH_LIGHT
    },
    CONTENT_TYPE_LIFE: {
        "word_count": "1200-2000",
        "style": "亲和实用",
        "structure": "场景-解决-建议",
        "seo_focus": "生活场景+解决方案",
        "depth": RESEARCH_DEPTH_MEDIUM
    },
    CONTENT_TYPE_SCIENCE: {
        "word_count": "1500-2500",
        "style": "通俗易懂、准确",
        "structure": "原理-应用-意义",
        "seo_focus": "科学概念+通俗解释",
        "depth": RESEARCH_DEPTH_MEDIUM
    },

    # 深度内容类型 - 详尽、专业
    CONTENT_TYPE_PAPER: {
        "word_count": "3000-8000",
        "style": "学术性、严谨",
        "structure": "引言-方法-结果-讨论",
        "seo_focus": "专业术语",
        "depth": RESEARCH_DEPTH_DEEP
    },
    CONTENT_TYPE_RESEARCH_REPORT: {
        "word_count": "2500-5000",
        "style": "分析性、专业",
        "structure": "摘要-发现-分析-建议",
        "seo_focus": "行业专业词汇",
        "depth": RESEARCH_DEPTH_DEEP
    },
    CONTENT_TYPE_ANALYSIS: {
        "word_count": "2000-4000",
        "style": "深入分析、数据支持",
        "structure": "论点-论据-结论",
        "seo_focus": "专业词汇+分析类词汇",
        "depth": RESEARCH_DEPTH_DEEP
    }
}

# 默认写作配置
DEFAULT_WRITING_CONFIG = {
    "word_count": "1500-2500",
    "style": "专业清晰",
    "structure": "标准文章结构",
    "seo_focus": "主题关键词",
    "depth": RESEARCH_DEPTH_MEDIUM
}
