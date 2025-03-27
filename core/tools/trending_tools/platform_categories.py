"""平台分类映射配置

该模块定义了各平台所属的分类标签，用于实现分类查询功能。
每个平台可以属于多个分类，支持灵活的分类查询。

使用方法:
    from .platform_categories import PLATFORM_CATEGORIES

    # 获取平台的所有分类
    categories = PLATFORM_CATEGORIES["weibo"]  # ["社交", "热点", "时事"]

    # 查询某个分类下的所有平台
    platforms = [
        platform for platform, categories
        in PLATFORM_CATEGORIES.items()
        if "技术" in categories
    ]
"""

PLATFORM_CATEGORIES = {
    # 社交媒体平台
    "weibo": ["社交", "热点", "时事"],
    "douyin": ["社交", "娱乐", "短视频"],
    "kuaishou": ["社交", "娱乐", "短视频"],

    # 技术社区平台
    "github": ["技术", "开发", "编程", "AI"],
    "v2ex": ["技术", "互联网", "讨论", "AI"],
    "juejin": ["技术", "开发", "学习", "AI"],
    "csdn": ["技术", "编程", "学习", "AI"],
    "51cto": ["技术", "编程", "学习"],
    "52pojie": ["技术", "安全", "破解"],
    "hostloc": ["技术", "主机", "讨论"],
    "linuxdo": ["技术", "Linux", "开发"],
    "nodeseek": ["技术", "主机", "讨论"],

    # 新闻资讯平台
    "36kr": ["科技", "创业", "商业", "AI"],
    "sina-news": ["新闻", "时事", "综合"],
    "qq-news": ["新闻", "时事", "综合"],
    "netease-news": ["新闻", "时事", "综合"],
    "baidu": ["热点", "时事", "综合"],
    "toutiao": ["新闻", "热点", "综合"],
    "thepaper": ["新闻", "时事", "深度"],
    "huxiu": ["科技", "商业", "深度", "AI"],
    "ifanr": ["科技", "数码", "互联网", "AI"],
    "geekpark": ["科技", "创新", "互联网", "AI"],
    "sina": ["新闻", "时事", "综合"],
    "nytimes": ["新闻", "国际", "深度"],

    # 问答平台
    "zhihu": ["知识", "问答", "综合"],
    "zhihu-daily": ["知识", "科普", "深度"],

    # 游戏社区平台
    "genshin": ["游戏", "二次元", "米哈游"],
    "miyoushe": ["游戏", "二次元", "米哈游"],
    "ngabbs": ["游戏", "讨论", "综合"],
    "lol": ["游戏", "电竞", "英雄联盟"],
    "starrail": ["游戏", "二次元", "米哈游"],
    "honkai": ["游戏", "二次元", "米哈游"],

    # 娱乐平台
    "bilibili": ["娱乐", "二次元", "视频"],
    "acfun": ["娱乐", "二次元", "视频"],
    "douban-movie": ["娱乐", "电影", "评论"],
    "douban-group": ["社交", "讨论", "兴趣"],
    "yystv": ["游戏", "电竞", "资讯"],

    # 生活服务
    "smzdm": ["购物", "优惠", "消费"],
    "sspai": ["数码", "效率", "生活"],
    "coolapk": ["数码", "应用", "安卓"],
    "dgtle": ["数码", "摄影", "设计"],
    "weread": ["阅读", "书籍", "知识"],

    # 其他平台
    "guokr": ["科普", "知识", "科技"],
    "jianshu": ["创作", "阅读", "博客"],
    "ithome": ["科技", "数码", "资讯"],
    "ithome-xijiayi": ["科技", "数码", "资讯"],
    "producthunt": ["产品", "创新", "科技"],
    "hackernews": ["技术", "创业", "国际"],
    "hellogithub": ["技术", "开源", "编程"],
    "tieba": ["社交", "兴趣", "讨论"],
    "earthquake": ["资讯", "地震", "监测"],
    "weatheralarm": ["资讯", "天气", "预警"]
}

# 分类标签集合（用于验证和查询）
CATEGORY_TAGS = {
    # 平台属性
    "社交", "技术", "新闻", "知识", "游戏", "娱乐", "购物", "数码", "阅读",

    # 内容属性
    "热点", "时事", "开发", "编程", "互联网", "科技", "创业", "商业", "问答",
    "科普", "二次元", "电竞", "优惠", "效率", "安全", "创新", "开源", "AI",

    # 内容形式
    "短视频", "讨论", "综合", "深度", "视频", "评论", "博客", "资讯",

    # 平台特色
    "Linux", "主机", "米哈游", "英雄联盟", "应用", "安卓", "摄影", "设计",

    # 其他属性
    "学习", "国际", "消费", "生活", "监测", "预警"
}

def get_platforms_by_category(category: str) -> list:
    """根据分类获取相关平台列表

    Args:
        category: 分类标签

    Returns:
        list: 该分类下的平台列表
    """
    return [
        platform for platform, categories
        in PLATFORM_CATEGORIES.items()
        if category in categories
    ]

def get_platform_categories(platform: str) -> list:
    """获取平台的所有分类标签

    Args:
        platform: 平台名称

    Returns:
        list: 平台的分类标签列表
    """
    return PLATFORM_CATEGORIES.get(platform, [])
