"""数据库适配器接口

为ContentManager提供统一的数据库访问接口，
负责在模型层和数据库层之间进行转换和协调。
"""

from typing import Dict, List, Optional, Any, Type, TypeVar, Union
from loguru import logger

# 定义泛型类型变量
T = TypeVar('T')

class DBAdapter:
    """数据库适配器，为ContentManager提供统一的数据库操作接口

    此类主要用于向后兼容，实际功能已分拆到各个专门的适配器类中。
    """

    _is_initialized: bool = False

    @classmethod
    def initialize(cls) -> bool:
        """初始化数据库连接和表结构

        Returns:
            bool: 是否成功初始化
        """
        if cls._is_initialized:
            return True

        try:
            # 使用配置适配器初始化数据库
            from core.models.infra.adapters.config_adapter import ConfigAdapter
            result = ConfigAdapter.initialize()

            if result:
                cls._is_initialized = True
                logger.info("数据库适配器初始化成功")
            return result
        except ImportError as e:
            logger.warning(f"数据库模块导入失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            return False

    @classmethod
    def sync_config_to_db(cls, sync_mode: bool = True) -> bool:
        """同步配置文件到数据库

        将现有的配置文件数据同步到数据库中

        Args:
            sync_mode: 是否为同步模式。同步模式下会删除不在文件中的记录。

        Returns:
            bool: 是否成功同步
        """
        try:
            # 使用配置适配器同步配置
            from core.models.infra.adapters.config_adapter import ConfigAdapter
            return ConfigAdapter.sync_config_to_db(sync_mode)
        except Exception as e:
            logger.error(f"同步配置文件到数据库失败: {str(e)}")
            return False

    #
    # 配置相关方法 - 委托给ConfigAdapter
    #

    @classmethod
    def load_content_types(cls) -> Dict[str, Any]:
        """从数据库加载所有内容类型

        Returns:
            Dict[str, Any]: 内容类型字典
        """
        try:
            from core.models.infra.adapters.config_adapter import ConfigAdapter
            return ConfigAdapter.load_content_types()
        except Exception as e:
            logger.error(f"从数据库加载内容类型失败: {str(e)}")
            return {}

    @classmethod
    def load_article_styles(cls) -> Dict[str, Any]:
        """从数据库加载所有文章风格

        Returns:
            Dict[str, Any]: 文章风格字典，键为风格名称
        """
        try:
            from core.models.infra.adapters.config_adapter import ConfigAdapter
            return ConfigAdapter.load_article_styles()
        except Exception as e:
            logger.error(f"从数据库加载文章风格失败: {str(e)}")
            return {}

    @classmethod
    def load_platforms(cls) -> Dict[str, Any]:
        """从数据库加载所有平台配置

        Returns:
            Dict[str, Any]: 平台配置字典
        """
        try:
            from core.models.infra.adapters.config_adapter import ConfigAdapter
            return ConfigAdapter.load_platforms()
        except Exception as e:
            logger.error(f"从数据库加载平台配置失败: {str(e)}")
            return {}

    @classmethod
    def get_content_type(cls, content_type_id: str) -> Optional[Any]:
        """获取指定ID的内容类型

        Args:
            content_type_id: 内容类型ID

        Returns:
            Optional[Any]: 内容类型对象
        """
        try:
            from core.models.infra.adapters.config_adapter import ConfigAdapter
            return ConfigAdapter.get_content_type(content_type_id)
        except Exception as e:
            logger.error(f"获取内容类型失败: {str(e)}")
            return None

    @classmethod
    def get_article_style(cls, style_name: str) -> Optional[Any]:
        """获取指定名称的文章风格

        Args:
            style_name: 风格名称

        Returns:
            Optional[Any]: 文章风格对象
        """
        try:
            from core.models.infra.adapters.config_adapter import ConfigAdapter
            return ConfigAdapter.get_article_style(style_name)
        except Exception as e:
            logger.error(f"获取文章风格失败: {str(e)}")
            return None

    @classmethod
    def get_platform(cls, platform_id: str) -> Optional[Any]:
        """获取指定ID的平台配置

        Args:
            platform_id: 平台ID

        Returns:
            Optional[Any]: 平台配置对象
        """
        try:
            from core.models.infra.adapters.config_adapter import ConfigAdapter
            return ConfigAdapter.get_platform(platform_id)
        except Exception as e:
            logger.error(f"获取平台配置失败: {str(e)}")
            return None

    @classmethod
    def save_content_type(cls, content_type: Any) -> bool:
        """保存内容类型到数据库

        Args:
            content_type: 内容类型对象

        Returns:
            bool: 是否成功保存
        """
        try:
            from core.models.infra.adapters.config_adapter import ConfigAdapter
            return ConfigAdapter.save_content_type(content_type)
        except Exception as e:
            logger.error(f"保存内容类型失败: {str(e)}")
            return False

    @classmethod
    def save_article_style(cls, style: Any) -> bool:
        """保存文章风格到数据库

        Args:
            style: 文章风格对象

        Returns:
            bool: 是否成功保存
        """
        try:
            from core.models.infra.adapters.config_adapter import ConfigAdapter
            return ConfigAdapter.save_article_style(style)
        except Exception as e:
            logger.error(f"保存文章风格失败: {str(e)}")
            return False

    @classmethod
    def save_platform(cls, platform: Any) -> bool:
        """保存平台配置到数据库

        Args:
            platform: 平台配置对象

        Returns:
            bool: 是否成功保存
        """
        try:
            from core.models.infra.adapters.config_adapter import ConfigAdapter
            return ConfigAdapter.save_platform(platform)
        except Exception as e:
            logger.error(f"保存平台配置失败: {str(e)}")
            return False

    @classmethod
    def get_default_content_type(cls) -> Any:
        """获取默认内容类型

        Returns:
            Any: 默认内容类型对象
        """
        try:
            # 导入模型
            from core.models.db.model_manager import get_default_content_type
            return get_default_content_type()
        except Exception as e:
            logger.error(f"获取默认内容类型失败: {str(e)}")
            return None

    @classmethod
    def get_default_article_style(cls) -> Any:
        """获取默认文章风格

        Returns:
            Any: 默认文章风格对象
        """
        try:
            # 导入模型
            from core.models.db.model_manager import get_default_article_style
            return get_default_article_style()
        except Exception as e:
            logger.error(f"获取默认文章风格失败: {str(e)}")
            return None

    @classmethod
    def get_default_platform(cls) -> Any:
        """获取默认平台配置

        Returns:
            Any: 默认平台配置对象
        """
        try:
            # 导入模型
            from core.models.platform.platform import get_default_platform
            return get_default_platform()
        except Exception as e:
            logger.error(f"获取默认平台配置失败: {str(e)}")
            return None

    #
    # 文章相关方法 - 委托给ArticleAdapter
    #

    @classmethod
    def save_article(cls, article: Any) -> bool:
        """保存文章到数据库

        Args:
            article: 文章对象

        Returns:
            bool: 是否成功保存
        """
        try:
            from core.models.infra.adapters.article_adapter import ArticleAdapter
            return ArticleAdapter.save_article(article)
        except Exception as e:
            logger.error(f"保存文章失败: {str(e)}")
            return False

    @classmethod
    def get_article(cls, article_id: str) -> Optional[Dict[str, Any]]:
        """获取指定ID的文章

        Args:
            article_id: 文章ID

        Returns:
            Optional[Dict]: 文章数据字典
        """
        try:
            from core.models.infra.adapters.article_adapter import ArticleAdapter
            return ArticleAdapter.get_article(article_id)
        except Exception as e:
            logger.error(f"获取文章失败: {str(e)}")
            return None

    @classmethod
    def get_articles_by_status(cls, status: str) -> List[Dict[str, Any]]:
        """获取指定状态的所有文章

        Args:
            status: 文章状态

        Returns:
            List[Dict]: 文章列表
        """
        try:
            from core.models.infra.adapters.article_adapter import ArticleAdapter
            return ArticleAdapter.get_articles_by_status(status)
        except Exception as e:
            logger.error(f"获取文章失败: {str(e)}")
            return []

    @classmethod
    def update_article_status(cls, article_id: str, status: str) -> bool:
        """更新文章状态

        Args:
            article_id: 文章ID
            status: 新状态

        Returns:
            bool: 是否成功更新
        """
        try:
            from core.models.infra.adapters.article_adapter import ArticleAdapter
            return ArticleAdapter.update_article_status(article_id, status)
        except Exception as e:
            logger.error(f"更新文章状态失败: {str(e)}")
            return False

    @classmethod
    def delete_article(cls, article_id: str) -> bool:
        """删除文章

        Args:
            article_id: 文章ID

        Returns:
            bool: 是否成功删除
        """
        try:
            from core.models.infra.adapters.article_adapter import ArticleAdapter
            return ArticleAdapter.delete_article(article_id)
        except Exception as e:
            logger.error(f"删除文章失败: {str(e)}")
            return False

    #
    # 话题相关方法 - 委托给TopicAdapter
    #

    @classmethod
    def get_topic(cls, topic_id: str) -> Optional[Dict[str, Any]]:
        """从数据库获取指定ID的话题

        Args:
            topic_id: 话题ID

        Returns:
            Optional[Dict[str, Any]]: 话题数据，如不存在返回None
        """
        try:
            from core.models.infra.adapters.topic_adapter import TopicAdapter
            return TopicAdapter.get_topic(topic_id)
        except Exception as e:
            logger.error(f"获取话题[{topic_id}]失败: {str(e)}")
            return None

    @classmethod
    def save_topic(cls, topic: Any) -> bool:
        """保存话题到数据库

        Args:
            topic: 话题对象

        Returns:
            bool: 是否成功保存
        """
        try:
            from core.models.infra.adapters.topic_adapter import TopicAdapter
            return TopicAdapter.save_topic(topic)
        except Exception as e:
            logger.error(f"保存话题失败: {str(e)}")
            return False

    @classmethod
    def get_topics_by_platform(cls, platform: str) -> List[Dict[str, Any]]:
        """获取指定平台的所有话题

        Args:
            platform: 平台标识

        Returns:
            List[Dict[str, Any]]: 话题列表
        """
        try:
            from core.models.infra.adapters.topic_adapter import TopicAdapter
            return TopicAdapter.get_topics_by_platform(platform)
        except Exception as e:
            logger.error(f"获取平台话题失败: {str(e)}")
            return []

    #
    # 大纲相关方法 - 委托给OutlineAdapter
    #

    @classmethod
    def get_outline(cls, outline_id: str) -> Optional[Any]:
        """获取指定ID的大纲

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[Any]: 大纲对象或None
        """
        try:
            from core.models.infra.adapters.outline_adapter import OutlineAdapter
            return OutlineAdapter.get_outline(outline_id)
        except Exception as e:
            logger.error(f"从临时存储获取大纲失败: {e}")
            return None

    @classmethod
    def save_outline(cls, outline: Any, outline_id: Optional[str] = None) -> str:
        """保存大纲

        Args:
            outline: 大纲对象
            outline_id: 可选的大纲ID，如不提供则自动生成

        Returns:
            str: 大纲ID
        """
        try:
            from core.models.infra.adapters.outline_adapter import OutlineAdapter
            return OutlineAdapter.save_outline(outline, outline_id)
        except Exception as e:
            logger.error(f"保存大纲到临时存储失败: {e}")
            # 确保返回字符串，避免None
            return outline_id if outline_id else ""

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除大纲

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        try:
            from core.models.infra.adapters.outline_adapter import OutlineAdapter
            return OutlineAdapter.delete_outline(outline_id)
        except Exception as e:
            logger.error(f"从临时存储删除大纲失败: {e}")
            return False

    @classmethod
    def list_outlines(cls) -> List[str]:
        """获取所有大纲ID列表

        Returns:
            List[str]: 大纲ID列表
        """
        try:
            from core.models.infra.adapters.outline_adapter import OutlineAdapter
            return OutlineAdapter.list_outlines()
        except Exception as e:
            logger.error(f"获取大纲列表失败: {e}")
            return []
