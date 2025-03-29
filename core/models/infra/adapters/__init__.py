"""适配器模块

提供针对不同数据实体的数据库访问适配器。
"""

from core.models.infra.adapters.article_adapter import ArticleAdapter
from core.models.infra.adapters.topic_adapter import TopicAdapter
from core.models.infra.adapters.outline_adapter import OutlineAdapter
from core.models.infra.adapters.config_adapter import ConfigAdapter

__all__ = [
    'ArticleAdapter',
    'TopicAdapter',
    'OutlineAdapter',
    'ConfigAdapter',
]
