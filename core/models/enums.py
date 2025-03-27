"""共享枚举类型模块

该模块定义了在整个系统中共享使用的枚举类型，
以避免在不同模块中重复定义相同的枚举。
"""

from enum import Enum, auto

class ArticleSectionType(str, Enum):
    """文章部分/章节类型"""
    INTRODUCTION = "introduction"  # 引言
    BACKGROUND = "background"      # 背景
    MAIN_POINT = "main_point"      # 主要观点
    ANALYSIS = "analysis"          # 分析
    EXAMPLE = "example"            # 示例
    COMPARISON = "comparison"      # 对比
    CONCLUSION = "conclusion"      # 结论
    REFERENCE = "reference"        # 参考资料

class ContentCategory(str, Enum):
    """内容类型的分类枚举"""
    ARTICLE = "article"
    BLOG = "blog"
    STORY = "story"
    TUTORIAL = "tutorial"
    NEWS = "news"
    REPORT = "report"
    REVIEW = "review"
    GUIDE = "guide"
    OTHER = "other"

class CategoryType(str, Enum):
    """分类类型枚举"""
    PLATFORM = "平台属性"  # 社交、技术、新闻等
    CONTENT = "内容属性"   # 热点、时事、开发等
    FORMAT = "内容形式"    # 短视频、讨论、综合等
    FEATURE = "平台特色"   # Linux、主机、米哈游等
    OTHER = "其他属性"     # 学习、国际、消费等

class ProductionStage(str, Enum):
    """生产阶段"""
    TOPIC_DISCOVERY = "topic_discovery"  # 话题发现
    TOPIC_RESEARCH = "topic_research"    # 话题研究
    ARTICLE_WRITING = "article_writing"  # 文章写作
    STYLE_ADAPTATION = "style_adaptation"  # 风格适配
    ARTICLE_REVIEW = "article_review"    # 文章审核
    COMPLETED = "completed"              # 已完成
    FAILED = "failed"                    # 失败
    PAUSED = "paused"                    # 暂停

    @classmethod
    def to_article_status(cls, stage: 'ProductionStage') -> str:
        """转换为文章状态

        Args:
            stage: 生产阶段

        Returns:
            str: 文章状态
        """
        status_map = {
            cls.TOPIC_DISCOVERY: "topic",
            cls.TOPIC_RESEARCH: "research",
            cls.ARTICLE_WRITING: "writing",
            cls.STYLE_ADAPTATION: "style",
            cls.ARTICLE_REVIEW: "review",
            cls.COMPLETED: "completed",
            cls.FAILED: "failed",
            cls.PAUSED: "paused"
        }
        return status_map.get(stage, "initialized")

class StageStatus(str, Enum):
    """阶段状态"""
    PENDING = "pending"       # 等待中
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败
    PAUSED = "paused"         # 暂停
