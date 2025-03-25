"""平台权重和热度值配置

该模块定义了各平台的权重系数和默认热度值，用于标准化不同平台的热度计算。

使用方法:
    from .platform_weights import calculate_normalized_hot_score

    # 计算标准化后的热度值
    hot_score = calculate_normalized_hot_score(
        platform="weibo",
        raw_score=10000
    )  # 返回加权后的热度值
"""

# 平台权重配置
PLATFORM_WEIGHTS = {
    # 社交媒体平台（权重较高，受众广，传播快）
    "weibo": 1.0,      # 微博基准权重
    "douyin": 0.9,     # 抖音
    "kuaishou": 0.8,   # 快手
    "tieba": 0.7,      # 贴吧

    # 新闻资讯平台（权重较高，信息价值高）
    "baidu": 1.0,          # 百度热搜基准权重
    "sina-news": 0.9,      # 新浪新闻
    "qq-news": 0.9,        # 腾讯新闻
    "netease-news": 0.9,   # 网易新闻
    "toutiao": 0.9,        # 今日头条
    "sina": 0.8,           # 新浪网
    "36kr": 0.8,          # 36氪
    "thepaper": 0.8,      # 澎湃新闻
    "huxiu": 0.8,         # 虎嗅网
    "ifanr": 0.7,         # 爱范儿
    "geekpark": 0.7,      # 极客公园
    "nytimes": 0.7,       # 纽约时报

    # 技术社区（权重适中，专业性强）
    "github": 0.8,      # GitHub
    "v2ex": 0.7,       # V2EX
    "juejin": 0.7,     # 掘金
    "csdn": 0.6,       # CSDN
    "51cto": 0.6,      # 51CTO
    "52pojie": 0.6,    # 吾爱破解
    "hostloc": 0.5,    # Hostloc
    "linuxdo": 0.5,    # Linux中国
    "nodeseek": 0.5,   # NodeSeek
    "hackernews": 0.7, # Hacker News
    "hellogithub": 0.6,# HelloGitHub

    # 问答平台（权重适中，内容质量较高）
    "zhihu": 0.8,          # 知乎
    "zhihu-daily": 0.7,    # 知乎日报

    # 游戏社区（权重适中，垂直领域）
    "genshin": 0.7,      # 原神
    "miyoushe": 0.7,     # 米游社
    "ngabbs": 0.6,       # NGA
    "lol": 0.6,          # 英雄联盟
    "starrail": 0.6,     # 星穹铁道
    "honkai": 0.6,       # 崩坏
    "yystv": 0.5,        # 游研社

    # 娱乐平台（权重适中）
    "bilibili": 0.8,       # B站
    "acfun": 0.6,         # A站
    "douban-movie": 0.7,  # 豆瓣电影
    "douban-group": 0.6,  # 豆瓣小组

    # 科技数码（权重适中）
    "ithome": 0.7,         # IT之家
    "ithome-xijiayi": 0.6, # IT之家系统汇
    "sspai": 0.6,          # 少数派
    "coolapk": 0.6,        # 酷安
    "dgtle": 0.5,          # 数字尾巴

    # 生活服务（权重适中偏低）
    "smzdm": 0.6,     # 什么值得买
    "weread": 0.5,    # 微信读书
    "guokr": 0.6,     # 果壳
    "jianshu": 0.5,   # 简书

    # 其他平台（权重较低）
    "producthunt": 0.5,    # Product Hunt
    "earthquake": 0.7,     # 地震速报
    "weatheralarm": 0.7,   # 天气预警
}

# 默认热度值配置（当平台未返回热度值时使用）
DEFAULT_HOT_SCORES = {
    # 社交媒体平台
    "weibo": 10000,     # 微博基准热度
    "douyin": 8000,     # 抖音
    "kuaishou": 8000,   # 快手
    "tieba": 5000,      # 贴吧

    # 新闻资讯平台
    "baidu": 10000,         # 百度热搜
    "sina-news": 8000,      # 新浪新闻
    "qq-news": 8000,        # 腾讯新闻
    "netease-news": 8000,   # 网易新闻
    "toutiao": 8000,        # 今日头条
    "sina": 7000,           # 新浪网
    "36kr": 5000,          # 36氪
    "thepaper": 5000,      # 澎湃新闻
    "huxiu": 5000,         # 虎嗅网
    "ifanr": 4000,         # 爱范儿
    "geekpark": 4000,      # 极客公园
    "nytimes": 4000,       # 纽约时报

    # 技术社区
    "github": 1000,      # GitHub
    "v2ex": 800,        # V2EX
    "juejin": 800,      # 掘金
    "csdn": 600,        # CSDN
    "51cto": 500,       # 51CTO
    "52pojie": 500,     # 吾爱破解
    "hostloc": 300,     # Hostloc
    "linuxdo": 300,     # Linux中国
    "nodeseek": 300,    # NodeSeek
    "hackernews": 800,  # Hacker News
    "hellogithub": 500, # HelloGitHub

    # 问答平台
    "zhihu": 5000,          # 知乎
    "zhihu-daily": 3000,    # 知乎日报

    # 游戏社区
    "genshin": 2000,      # 原神
    "miyoushe": 2000,     # 米游社
    "ngabbs": 1500,       # NGA
    "lol": 1500,          # 英雄联盟
    "starrail": 1500,     # 星穹铁道
    "honkai": 1500,       # 崩坏
    "yystv": 1000,        # 游研社

    # 娱乐平台
    "bilibili": 5000,      # B站
    "acfun": 2000,        # A站
    "douban-movie": 3000, # 豆瓣电影
    "douban-group": 2000, # 豆瓣小组

    # 科技数码
    "ithome": 3000,         # IT之家
    "ithome-xijiayi": 2000, # IT之家系统汇
    "sspai": 2000,          # 少数派
    "coolapk": 2000,        # 酷安
    "dgtle": 1000,          # 数字尾巴

    # 生活服务
    "smzdm": 2000,     # 什么值得买
    "weread": 1500,    # 微信读书
    "guokr": 2000,     # 果壳
    "jianshu": 1500,   # 简书

    # 其他平台
    "producthunt": 1000,    # Product Hunt
    "earthquake": 3000,     # 地震速报
    "weatheralarm": 3000,   # 天气预警
}

def calculate_normalized_hot_score(platform: str, raw_score: int = None) -> int:
    """计算标准化的热度值

    Args:
        platform: 平台名称
        raw_score: 原始热度值，如果为None则使用默认值

    Returns:
        int: 标准化后的热度值

    计算规则：
    1. 如果提供了原始热度值，使用原始值，否则使用默认值
    2. 将热度值乘以平台权重得到最终热度
    3. 确保返回的热度值为正整数
    """
    # 获取平台权重，默认为0.5
    weight = PLATFORM_WEIGHTS.get(platform, 0.5)

    # 获取热度值
    if raw_score is None or raw_score <= 0:
        hot_score = DEFAULT_HOT_SCORES.get(platform, 1000)
    else:
        hot_score = raw_score

    # 计算加权热度值
    normalized_score = int(hot_score * weight)

    # 确保热度值为正整数
    return max(1, normalized_score)

def get_platform_weight(platform: str) -> float:
    """获取平台权重

    Args:
        platform: 平台名称

    Returns:
        float: 平台权重系数
    """
    return PLATFORM_WEIGHTS.get(platform, 0.5)

def get_default_hot_score(platform: str) -> int:
    """获取平台默认热度值

    Args:
        platform: 平台名称

    Returns:
        int: 默认热度值
    """
    return DEFAULT_HOT_SCORES.get(platform, 1000)
