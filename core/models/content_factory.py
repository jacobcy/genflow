"""模型组件注册

提供一个轻量级的方式加载各种模型组件。
删除了不必要的工厂层，使结构更加扁平。
"""

from typing import Dict, Optional, Any
from loguru import logger

# 直接导入所需组件，简化依赖链
# 这些导入可以根据实际需要修改
from .style.style_manager import StyleManager
from .article.article_manager import ArticleManager


def initialize_model_components(use_db: bool = True) -> None:
    """初始化所有模型组件

    Args:
        use_db: 是否使用数据库，默认为True
    """
    # 初始化各组件
    StyleManager.initialize(use_db)
    ArticleManager.initialize(use_db)

    logger.info("模型组件初始化完成")


def get_component(component_name: str) -> Optional[Any]:
    """获取指定名称的组件

    这是一个简单的辅助函数，根据名称返回对应组件。
    如果将来需要，可以扩展为更复杂的组件注册表。

    Args:
        component_name: 组件名称

    Returns:
        Optional[Any]: 组件类或None
    """
    components = {
        "style": StyleManager,
        "article": ArticleManager,
    }

    return components.get(component_name)
