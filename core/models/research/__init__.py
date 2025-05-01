"""研究报告模块

提供基础研究报告和话题研究报告的数据模型与服务接口。
"""

from .basic_research import (
    BasicResearch,
    KeyFinding,
    Source,
    ExpertInsight,
    ArticleSection
)

from .research import TopicResearch

from .research_factory import ResearchFactory
from .research_storage import ResearchStorage
from .research_adapter import ResearchAdapter

# 导出主要类，方便使用
__all__ = [
    'BasicResearch',
    'TopicResearch',
    'KeyFinding',
    'Source',
    'ExpertInsight',
    'ArticleSection',
    'ResearchFactory',
    'ResearchStorage',
    'ResearchAdapter'
]
