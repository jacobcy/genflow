"""向后兼容桥接模块

此模块作为向后兼容层，真正的工具类已移至util目录下的各个子模块。
"""

# 从子模块导入所有工具类，保持导入兼容性
from .util.json_loader import JsonModelLoader
from .util.article_parser import ArticleParser
from .util.outline_converter import OutlineConverter
from .managers.outline_manager import OutlineManager
from .managers.style_factory import StyleFactory

# 导出所有类
__all__ = ['JsonModelLoader', 'ArticleParser', 'OutlineConverter', 'OutlineManager', 'StyleFactory']
