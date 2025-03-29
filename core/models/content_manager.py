"""模型管理服务

简化的模型访问层，提供对系统各种模型的统一访问接口。
职责是协调不同类型的模型管理器，不包含业务逻辑。
"""

from typing import Dict, List, Optional, Any, Type
from loguru import logger

# 导入基础组件
from .style.style_manager import StyleManager
from .article.article_manager import ArticleManager


class ModelService:
    """模型服务类

    提供对系统各类模型的统一访问接口，包括:
    - 风格模型
    - 文章模型
    - 内容类型

    不再使用单例模式，而是通过依赖注入方式使用。
    """

    def __init__(self, use_db: bool = True) -> None:
        """初始化模型服务

        Args:
            use_db: 是否使用数据库，默认为True
        """
        self.use_db = use_db
        self.initialized = False

        # 初始化组件
        self.initialize()

    def initialize(self) -> None:
        """初始化所有模型管理器"""
        if self.initialized:
            logger.debug("模型服务已初始化，跳过")
            return

        # 初始化组件
        StyleManager.initialize(self.use_db)
        ArticleManager.initialize(self.use_db)

        self.initialized = True
        logger.info("模型服务初始化完成")

    #----------------------------------#
    # 风格相关方法                     #
    #----------------------------------#

    def get_article_style(self, style_name: str) -> Optional[Any]:
        """获取指定名称的文章风格

        Args:
            style_name: 风格名称

        Returns:
            Optional[Any]: 风格对象或None
        """
        return StyleManager.get_article_style(style_name)

    def get_default_style(self) -> Any:
        """获取默认风格

        Returns:
            Any: 默认风格对象
        """
        return StyleManager.get_default_style()

    def get_all_styles(self) -> Dict[str, Any]:
        """获取所有风格

        Returns:
            Dict[str, Any]: 风格字典，键为风格名称
        """
        return StyleManager.get_all_styles()

    def create_style_from_description(self, description: str, options: Optional[Dict[str, Any]] = None) -> Any:
        """从描述创建风格

        Args:
            description: 风格描述文本
            options: 可选配置参数

        Returns:
            Any: 创建的风格对象
        """
        return StyleManager.create_style_from_description(description, options)

    def find_style_by_type(self, style_type: str) -> Optional[Any]:
        """根据类型查找风格

        Args:
            style_type: 风格类型

        Returns:
            Optional[Any]: 匹配的风格对象或None
        """
        return StyleManager.find_style_by_type(style_type)

    def save_style(self, style: Any) -> bool:
        """保存风格

        Args:
            style: 风格对象

        Returns:
            bool: 是否成功保存
        """
        return StyleManager.save_style(style)

    #----------------------------------#
    # 文章相关方法                     #
    #----------------------------------#

    def get_article(self, article_id: str) -> Optional[Any]:
        """获取指定ID的文章

        Args:
            article_id: 文章ID

        Returns:
            Optional[Any]: 文章对象或None
        """
        return ArticleManager.get_article(article_id)

    def save_article(self, article: Any) -> bool:
        """保存文章

        Args:
            article: 文章对象

        Returns:
            bool: 是否成功保存
        """
        return ArticleManager.save_article(article)

    def get_articles_by_status(self, status: str) -> List[Any]:
        """获取指定状态的文章

        Args:
            status: 文章状态

        Returns:
            List[Any]: 文章列表
        """
        return ArticleManager.get_articles_by_status(status)

    def update_article_status(self, article_id: str, status: str) -> bool:
        """更新文章状态

        Args:
            article_id: 文章ID
            status: 新状态

        Returns:
            bool: 是否成功更新
        """
        return ArticleManager.update_article_status(article_id, status)


# 为了兼容现有代码，提供ContentManager别名
ContentManager = ModelService
