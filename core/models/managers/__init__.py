"""内容管理器包

此包包含各种专门的内容管理器，每个管理器负责特定领域的管理功能。
采用分层设计，降低了各管理器之间的耦合，提高了代码的可维护性。
"""

# 导入所有管理器类，便于直接从包导入
try:
    from .style_manager import StyleManager
except ImportError:
    pass

try:
    from .outline_factory import OutlineFactory
except ImportError:
    pass

try:
    from .article_manager import ArticleManager
except ImportError:
    pass

try:
    from .platform_manager import PlatformManager
except ImportError:
    pass

try:
    from .topic_manager import TopicManager
except ImportError:
    pass

try:
    from .content_type_manager import ContentTypeManager
except ImportError:
    pass

# 导出管理器类
__all__ = [
    'StyleManager',
    'OutlineFactory',
    'ArticleManager',
    'PlatformManager',
    'TopicManager',
    'ContentTypeManager',
]
