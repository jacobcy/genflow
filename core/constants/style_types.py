"""平台风格类型配置模块

定义平台风格特征及配置，为用户提供可选择的文章风格模板。
包括各个主流平台如知乎、小红书、微博等的特色写作风格。
"""

from typing import Dict, List, Optional, Any
import os
import json
from pathlib import Path

# 风格类型常量
STYLE_TYPE_ZHIHU = "知乎"
STYLE_TYPE_XIAOHONGSHU = "小红书"
STYLE_TYPE_WEIBO = "微博"
STYLE_TYPE_BILIBILI = "哔哩哔哩"
STYLE_TYPE_WECHAT = "微信公众号"
STYLE_TYPE_DOUYIN = "抖音"
STYLE_TYPE_CSDN = "CSDN"
STYLE_TYPE_TOUTIAO = "今日头条"

# 风格分类
ACADEMIC_STYLES = [STYLE_TYPE_ZHIHU]
SOCIAL_STYLES = [STYLE_TYPE_XIAOHONGSHU, STYLE_TYPE_WEIBO, STYLE_TYPE_DOUYIN]
PROFESSIONAL_STYLES = [STYLE_TYPE_WECHAT, STYLE_TYPE_CSDN]
ENTERTAINMENT_STYLES = [STYLE_TYPE_BILIBILI, STYLE_TYPE_TOUTIAO]

# 所有支持的风格类型
ALL_STYLE_TYPES = ACADEMIC_STYLES + SOCIAL_STYLES + PROFESSIONAL_STYLES + ENTERTAINMENT_STYLES

# 风格对应的关键特征
STYLE_FEATURES = {
    STYLE_TYPE_ZHIHU: {
        "tone": "conversational_professional",
        "formality": 3,  # 1-5, 越高越正式
        "characteristics": [
            "专业知识深度解析",
            "通俗易懂的类比和比喻",
            "问答体结构",
            "逻辑性强、有深度",
            "适当展示专业背景"
        ],
        "language_patterns": [
            "从...角度来看",
            "其实这个问题可以这样理解",
            "很多人对...存在误解",
            "简单来说",
            "深入来讲"
        ],
        "emoji_usage": "minimal",
        "paragraph_length": "medium_to_long",
        "structure": [
            "开场提问或引入话题",
            "系统性解析概念",
            "举例说明或分析",
            "解决常见疑问",
            "总结观点"
        ]
    },
    STYLE_TYPE_XIAOHONGSHU: {
        "tone": "enthusiastic",
        "formality": 1,  # 非常口语化
        "characteristics": [
            "大量感叹和修饰词",
            "亲身体验分享",
            "图文结合、分点描述",
            "使用流行语和网络用语",
            "强调个人感受"
        ],
        "language_patterns": [
            "太爱了！",
            "绝绝子",
            "yyds",
            "真的是...了",
            "分享一下我的..."
        ],
        "emoji_usage": "abundant",
        "paragraph_length": "short",
        "structure": [
            "吸引眼球的开场",
            "个人体验分享",
            "步骤或要点列举",
            "推荐总结",
            "互动引导"
        ]
    },
    STYLE_TYPE_WEIBO: {
        "tone": "concise",
        "formality": 1,
        "characteristics": [
            "简短直接",
            "观点鲜明",
            "话题标签",
            "时效性强",
            "互动性强"
        ],
        "language_patterns": [
            "转发扩散",
            "#话题标签#",
            "有没有人懂",
            "求扩散",
            "刚刚发生了..."
        ],
        "emoji_usage": "moderate",
        "paragraph_length": "very_short",
        "structure": [
            "核心观点",
            "简短说明",
            "互动引导"
        ]
    },
    STYLE_TYPE_BILIBILI: {
        "tone": "friendly",
        "formality": 2,
        "characteristics": [
            "二次元表达",
            "结合热门梗",
            "生动活泼",
            "接地气",
            "互动性强"
        ],
        "language_patterns": [
            "这波操作太秀了",
            "前方高能",
            "老铁们",
            "不愧是你",
            "泪目"
        ],
        "emoji_usage": "moderate",
        "paragraph_length": "short_to_medium",
        "structure": [
            "吸引眼球的开场",
            "内容预告",
            "主体内容",
            "互动总结"
        ]
    },
    STYLE_TYPE_WECHAT: {
        "tone": "informative",
        "formality": 4,
        "characteristics": [
            "深度内容",
            "原创观点",
            "逻辑清晰",
            "实用性强",
            "标题党倾向"
        ],
        "language_patterns": [
            "深度解析",
            "独家",
            "深思熟虑后",
            "值得收藏",
            "建议收藏"
        ],
        "emoji_usage": "minimal",
        "paragraph_length": "medium",
        "structure": [
            "引人入胜的标题",
            "开篇引入话题",
            "分段阐述观点",
            "案例支持",
            "总结与延伸"
        ]
    },
    STYLE_TYPE_DOUYIN: {
        "tone": "energetic",
        "formality": 1,
        "characteristics": [
            "极简表达",
            "高能量",
            "流行语",
            "强烈情感",
            "重点突出"
        ],
        "language_patterns": [
            "太绝了",
            "学到了",
            "冲冲冲",
            "一起来看",
            "推荐推荐"
        ],
        "emoji_usage": "abundant",
        "paragraph_length": "very_short",
        "structure": [
            "震撼开场",
            "核心内容",
            "互动引导"
        ]
    },
    STYLE_TYPE_CSDN: {
        "tone": "technical",
        "formality": 4,
        "characteristics": [
            "技术细节",
            "代码示例",
            "步骤清晰",
            "问题解决导向",
            "专业术语"
        ],
        "language_patterns": [
            "实现原理是",
            "代码如下",
            "问题解决方案",
            "技术架构",
            "核心算法"
        ],
        "emoji_usage": "minimal",
        "paragraph_length": "medium_to_long",
        "structure": [
            "问题描述",
            "解决方案",
            "代码实现",
            "运行结果",
            "总结展望"
        ]
    },
    STYLE_TYPE_TOUTIAO: {
        "tone": "informative",
        "formality": 3,
        "characteristics": [
            "时效性强",
            "标题吸引眼球",
            "观点鲜明",
            "易读性强",
            "数据支持"
        ],
        "language_patterns": [
            "重磅",
            "独家",
            "最新消息",
            "突发",
            "解读"
        ],
        "emoji_usage": "minimal",
        "paragraph_length": "short_to_medium",
        "structure": [
            "引人标题",
            "核心信息摘要",
            "详细内容",
            "观点分析",
            "背景补充"
        ]
    }
}

# 平台风格描述，供用户选择参考
STYLE_DESCRIPTIONS = {
    STYLE_TYPE_ZHIHU: "专业学术风格，逻辑清晰、有深度的内容，以知识解析和专业见解为主",
    STYLE_TYPE_XIAOHONGSHU: "种草体验式风格，亲切活泼，大量使用感叹词和流行语，强调个人感受",
    STYLE_TYPE_WEIBO: "简短直接风格，话题性强，适合快速传播和互动",
    STYLE_TYPE_BILIBILI: "二次元风格，活泼有趣，使用B站特色表达和热门梗，互动性强",
    STYLE_TYPE_WECHAT: "公众号风格，深度原创内容，逻辑清晰，标题吸引眼球",
    STYLE_TYPE_DOUYIN: "短视频风格，高能量表达，极简重点突出，流行语丰富",
    STYLE_TYPE_CSDN: "技术博客风格，专业详实，代码示例丰富，问题解决导向",
    STYLE_TYPE_TOUTIAO: "新闻资讯风格，时效性强，标题党，内容易读性强"
}

# 平台配置映射表，关联平台ID与风格类型
PLATFORM_TO_STYLE_MAP = {
    "zhihu": STYLE_TYPE_ZHIHU,
    "xiaohongshu": STYLE_TYPE_XIAOHONGSHU,
    "weibo": STYLE_TYPE_WEIBO,
    "bilibili": STYLE_TYPE_BILIBILI,
    "wechat": STYLE_TYPE_WECHAT,
    "douyin": STYLE_TYPE_DOUYIN,
    "csdn": STYLE_TYPE_CSDN,
    "toutiao": STYLE_TYPE_TOUTIAO
}


class StyleTypeConfig:
    """风格类型配置类，负责平台风格配置的加载和管理"""

    _instance = None
    _platform_configs = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StyleTypeConfig, cls).__new__(cls)
            cls._instance._load_platform_configs()
        return cls._instance

    def _load_platform_configs(self):
        """加载所有平台配置文件"""
        try:
            # 获取平台配置文件目录
            current_file = Path(__file__)
            platforms_dir = current_file.parent / "platforms"

            # 检查目录是否存在
            if not platforms_dir.exists():
                print(f"警告: 平台配置目录不存在 - {platforms_dir}")
                return

            # 加载所有平台配置
            for platform_file in platforms_dir.glob("*.json"):
                try:
                    with open(platform_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        platform_id = config.get("id")
                        if platform_id:
                            self._platform_configs[platform_id] = config
                except Exception as e:
                    print(f"加载平台配置文件失败: {platform_file} - {str(e)}")

        except Exception as e:
            print(f"加载平台配置失败: {str(e)}")

    def get_platform_config(self, platform_id: str) -> Optional[Dict]:
        """获取指定平台的配置

        Args:
            platform_id: 平台ID

        Returns:
            Optional[Dict]: 平台配置字典，如果不存在则返回None
        """
        return self._platform_configs.get(platform_id)

    def get_platform_style_guide(self, platform_id: str) -> Optional[Dict]:
        """获取指定平台的风格指南

        Args:
            platform_id: 平台ID

        Returns:
            Optional[Dict]: 平台风格指南，如果不存在则返回None
        """
        config = self.get_platform_config(platform_id)
        if config and "style_guide" in config:
            return config["style_guide"]
        return None

    def get_platform_style_rules(self, platform_id: str) -> Optional[Dict]:
        """获取指定平台的风格规则

        Args:
            platform_id: 平台ID

        Returns:
            Optional[Dict]: 平台风格规则，如果不存在则返回None
        """
        config = self.get_platform_config(platform_id)
        if config and "style_rules" in config:
            return config["style_rules"]
        return None

    def get_all_platform_ids(self) -> List[str]:
        """获取所有可用平台ID

        Returns:
            List[str]: 平台ID列表
        """
        return list(self._platform_configs.keys())

    @property
    def platform_configs(self) -> Dict:
        """获取所有平台配置"""
        return self._platform_configs


#################################################
# 辅助函数
#################################################

def get_style_features(style_type: str) -> Dict:
    """获取指定风格类型的特征配置

    Args:
        style_type: 风格类型，如"知乎"、"小红书"等

    Returns:
        Dict: 风格特征配置字典
    """
    return STYLE_FEATURES.get(style_type, {})

def get_style_description(style_type: str) -> str:
    """获取指定风格类型的描述

    Args:
        style_type: 风格类型，如"知乎"、"小红书"等

    Returns:
        str: 风格描述
    """
    return STYLE_DESCRIPTIONS.get(style_type, "未知风格")

def get_platform_style_type(platform_id: str) -> Optional[str]:
    """根据平台ID获取对应的风格类型

    Args:
        platform_id: 平台ID，如"zhihu"、"xiaohongshu"等

    Returns:
        Optional[str]: 风格类型，如"知乎"、"小红书"等，如果不存在则返回None
    """
    return PLATFORM_TO_STYLE_MAP.get(platform_id)

def get_style_by_formality(formality_level: int) -> List[str]:
    """根据正式程度获取符合的风格类型

    Args:
        formality_level: 正式程度，1-5，越高越正式

    Returns:
        List[str]: 符合该正式程度的风格类型列表
    """
    return [
        style for style, features in STYLE_FEATURES.items()
        if features.get("formality") == formality_level
    ]

def get_similar_styles(style_type: str, count: int = 3) -> List[str]:
    """获取与指定风格类型相似的其他风格

    Args:
        style_type: 风格类型，如"知乎"、"小红书"等
        count: 返回的相似风格数量

    Returns:
        List[str]: 相似风格类型列表
    """
    if style_type not in STYLE_FEATURES:
        return []

    # 当前风格的正式程度
    current_formality = STYLE_FEATURES[style_type].get("formality", 3)

    # 寻找相似正式程度的风格
    similar_styles = [
        s for s in STYLE_FEATURES
        if s != style_type and abs(STYLE_FEATURES[s].get("formality", 3) - current_formality) <= 1
    ]

    # 排序并限制数量
    return sorted(similar_styles)[:count]

def get_style_config() -> StyleTypeConfig:
    """获取风格类型配置实例

    Returns:
        StyleTypeConfig: 风格类型配置实例
    """
    return StyleTypeConfig()
