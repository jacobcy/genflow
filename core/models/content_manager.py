"""内容类型和文章风格管理器

该模块提供统一的接口来加载和管理内容类型和文章风格配置。
作为上层应用与具体配置之间的桥梁。
"""

from typing import Dict, List, Optional, Any
import importlib
from loguru import logger

class ContentManager:
    """内容类型和文章风格统一管理器

    该类是配置和文章管理的统一接口，作为外部访问的入口点。
    不包含具体业务逻辑，仅作为适配器将请求转发给相应的服务类。

    内部委托关系：
    - 配置相关操作 -> ConfigService
    - 文章相关操作 -> ArticleService
    - 数据库操作 -> DBAdapter

    这种设计确保了：
    1. 对外接口保持一致性和向后兼容
    2. 内部实现可以灵活变更而不影响上层应用
    3. 职责分离，每个组件专注于自己的职责
    """

    _is_initialized: bool = False
    _use_db: bool = True

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化管理器

        初始化所有服务组件，包括配置服务和文章服务

        Args:
            use_db: 是否使用数据库存储，默认为True
        """
        cls._use_db = use_db

        # 标记初始化完成
        cls._is_initialized = True
        logger.info("ContentManager初始化完成")

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化"""
        if not cls._is_initialized:
            cls.initialize()

    #----------------------------------#
    # 内容类型相关方法                  #
    #----------------------------------#

    @classmethod
    def get_content_type(cls, content_type_id: str) -> Optional[Any]:
        """获取指定ID的内容类型"""
        cls.ensure_initialized()

        # 直接实现，不依赖于ConfigService
        try:
            from .content_type import ContentType
            return ContentType.from_id(content_type_id)
        except (ImportError, AttributeError, ValueError) as e:
            logger.error(f"获取内容类型失败: {str(e)}")
            return None

    @classmethod
    def get_all_content_types(cls) -> Dict[str, Any]:
        """获取所有内容类型配置"""
        cls.ensure_initialized()

        # 直接实现，不依赖于ConfigService
        try:
            from .content_type import ContentType
            return ContentType.get_all_content_types()
        except (ImportError, AttributeError) as e:
            logger.error(f"获取内容类型配置失败: {str(e)}")
            return {}

    @classmethod
    def get_content_type_by_category(cls, category: str) -> Optional[Any]:
        """根据类别名称获取内容类型"""
        cls.ensure_initialized()

        # 直接实现，不依赖于ConfigService
        try:
            from .content_type import get_content_type_by_category
            return get_content_type_by_category(category)
        except (ImportError, AttributeError) as e:
            logger.error(f"根据类别获取内容类型失败: {str(e)}")
            return None

    @classmethod
    def save_content_type(cls, content_type: Any) -> bool:
        """保存内容类型到数据库"""
        cls.ensure_initialized()

        # 直接使用DBAdapter，不依赖ConfigService
        try:
            from .db_adapter import DBAdapter
            return DBAdapter.save_content_type(content_type)
        except Exception as e:
            logger.error(f"保存内容类型失败: {str(e)}")
            return False

    #----------------------------------#
    # 文章风格相关方法                  #
    #----------------------------------#

    @classmethod
    def get_article_style(cls, style_id: str) -> Optional[Any]:
        """获取指定ID的文章风格"""
        cls.ensure_initialized()

        # 直接实现，不依赖于ConfigService
        try:
            from .article_style import ArticleStyle
            return ArticleStyle.from_id(style_id)
        except (ImportError, AttributeError, ValueError) as e:
            logger.error(f"获取文章风格失败: {str(e)}")
            return None

    @classmethod
    def get_all_article_styles(cls) -> Dict[str, Any]:
        """获取所有文章风格配置"""
        cls.ensure_initialized()

        # 直接实现，不依赖于ConfigService
        try:
            from .article_style import ArticleStyle
            return ArticleStyle.get_all_styles()
        except (ImportError, AttributeError) as e:
            logger.error(f"获取文章风格配置失败: {str(e)}")
            return {}

    @classmethod
    def get_platform_style(cls, platform: str) -> Optional[Any]:
        """根据平台名称获取对应的风格配置"""
        cls.ensure_initialized()

        # 直接实现，不依赖于ConfigService
        try:
            from .article_style import get_platform_style
            return get_platform_style(platform)
        except (ImportError, AttributeError) as e:
            logger.error(f"获取平台风格配置失败: {str(e)}")
            return None

    @classmethod
    def save_article_style(cls, style: Any) -> bool:
        """保存文章风格到数据库"""
        cls.ensure_initialized()

        # 直接使用DBAdapter，不依赖ConfigService
        try:
            from .db_adapter import DBAdapter
            return DBAdapter.save_article_style(style)
        except Exception as e:
            logger.error(f"保存文章风格失败: {str(e)}")
            return False

    #----------------------------------#
    # 平台相关方法                     #
    #----------------------------------#

    @classmethod
    def get_platform(cls, platform_id: str) -> Optional[Any]:
        """获取指定ID的平台配置"""
        cls.ensure_initialized()

        # 直接实现，不依赖于ConfigService
        try:
            from .platform import Platform, get_platform
            return get_platform(platform_id)
        except (ImportError, AttributeError, ValueError) as e:
            logger.error(f"获取平台配置失败: {str(e)}")
            return None

    @classmethod
    def get_all_platforms(cls) -> Dict[str, Any]:
        """获取所有平台配置"""
        cls.ensure_initialized()

        # 直接实现，不依赖于ConfigService
        try:
            from .platform import Platform, get_all_platforms
            return get_all_platforms()
        except (ImportError, AttributeError) as e:
            logger.error(f"获取平台配置失败: {str(e)}")
            return {}

    @classmethod
    def reload_platform(cls, platform_id: str) -> Optional[Any]:
        """重新加载特定平台配置"""
        cls.ensure_initialized()

        # 直接实现，不依赖ConfigService
        try:
            from .platform import get_platform
            # 强制重新加载平台配置
            return get_platform(platform_id)
        except Exception as e:
            logger.error(f"重新加载平台配置失败: {str(e)}")
            return None

    @classmethod
    def reload_all_platforms(cls) -> Dict[str, Any]:
        """重新加载所有平台配置"""
        cls.ensure_initialized()

        # 直接实现，不依赖ConfigService
        try:
            from .platform import get_all_platforms
            # 获取所有平台配置
            return get_all_platforms()
        except Exception as e:
            logger.error(f"重新加载所有平台配置失败: {str(e)}")
            return {}

    @classmethod
    def save_platform(cls, platform: Any) -> bool:
        """保存平台配置到数据库"""
        cls.ensure_initialized()

        # 直接使用DBAdapter，不依赖ConfigService
        try:
            from .db_adapter import DBAdapter
            return DBAdapter.save_platform(platform)
        except Exception as e:
            logger.error(f"保存平台配置失败: {str(e)}")
            return False

    #----------------------------------#
    # 兼容性相关方法                    #
    #----------------------------------#

    @classmethod
    def is_compatible(cls, content_type_id: str, style_id: str) -> bool:
        """检查内容类型和风格是否兼容"""
        cls.ensure_initialized()

        # 直接实现，不依赖ConfigService
        try:
            # 获取内容类型和风格
            content_type = cls.get_content_type(content_type_id)
            if not content_type:
                return False

            # 检查风格ID是否在兼容列表中
            return style_id in content_type.compatible_styles
        except Exception as e:
            logger.error(f"检查兼容性失败: {str(e)}")
            return False

    @classmethod
    def get_recommended_style_for_content_type(cls, content_type_id: str) -> Optional[Any]:
        """获取适合指定内容类型的推荐风格"""
        cls.ensure_initialized()

        # 直接实现，不依赖ConfigService
        try:
            # 获取内容类型
            content_type = cls.get_content_type(content_type_id)
            if not content_type or not content_type.compatible_styles:
                return None

            # 返回第一个兼容的风格
            compatible_style_id = content_type.compatible_styles[0]
            return cls.get_article_style(compatible_style_id)
        except Exception as e:
            logger.error(f"获取推荐风格失败: {str(e)}")
            return None

    #----------------------------------#
    # 同步相关方法                      #
    #----------------------------------#

    @classmethod
    def sync_configs_to_db(cls, sync_mode: bool = False) -> bool:
        """同步所有配置到数据库"""
        cls.ensure_initialized()

        # 直接使用DBAdapter，不依赖于ConfigService
        try:
            from .db_adapter import DBAdapter
            return DBAdapter.sync_config_to_db(sync_mode)
        except Exception as e:
            logger.error(f"同步配置到数据库失败: {str(e)}")
            return False

    @classmethod
    def sync_configs_to_db_full(cls) -> bool:
        """完整同步所有配置到数据库"""
        cls.ensure_initialized()

        # 直接使用DBAdapter，不依赖于ConfigService
        try:
            from .db_adapter import DBAdapter
            return DBAdapter.sync_config_to_db(True)
        except Exception as e:
            logger.error(f"完整同步配置到数据库失败: {str(e)}")
            return False

    #----------------------------------#
    # 文章相关方法                      #
    #----------------------------------#

    @classmethod
    def get_article(cls, article_id: str) -> Optional[Any]:
        """获取指定ID的文章"""
        cls.ensure_initialized()
        from .article_service import ArticleService
        return ArticleService.get_article(article_id)

    @classmethod
    def save_article(cls, article: Any) -> bool:
        """保存文章到数据库"""
        cls.ensure_initialized()
        from .article_service import ArticleService
        return ArticleService.save_article(article)

    @classmethod
    def update_article_status(cls, article: Any, new_status: str) -> bool:
        """更新文章状态并保存"""
        cls.ensure_initialized()
        from .article_service import ArticleService
        return ArticleService.update_article_status(article, new_status)

    @classmethod
    def get_articles_by_status(cls, status: str) -> List[Any]:
        """获取指定状态的所有文章"""
        cls.ensure_initialized()
        from .article_service import ArticleService
        return ArticleService.get_articles_by_status(status)

    @classmethod
    def delete_article(cls, article_id: str) -> bool:
        """删除文章"""
        cls.ensure_initialized()
        from .article_service import ArticleService
        return ArticleService.delete_article(article_id)

    #----------------------------------#
    # 话题相关方法                      #
    #----------------------------------#

    @classmethod
    def get_topic(cls, topic_id: str) -> Optional[Any]:
        """获取指定ID的话题

        Args:
            topic_id: 话题ID

        Returns:
            Optional[Any]: 话题对象，如未找到则返回None
        """
        cls.ensure_initialized()

        # 导入服务依赖
        from .topic_service import TopicService
        return TopicService.get_topic(topic_id)

    @classmethod
    def save_topic(cls, topic: Any) -> bool:
        """保存话题到数据库

        Args:
            topic: 话题对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()

        # 导入服务依赖
        from .topic_service import TopicService
        return TopicService.save_topic(topic)

    @classmethod
    def update_topic_status(cls, topic_id: str, status: str) -> bool:
        """更新话题状态

        Args:
            topic_id: 话题ID
            status: 新状态

        Returns:
            bool: 是否成功更新
        """
        cls.ensure_initialized()

        # 导入服务依赖
        from .topic_service import TopicService
        return TopicService.update_topic_status(topic_id, status)

    @classmethod
    def get_topics_by_platform(cls, platform: str) -> List[Any]:
        """获取指定平台的所有话题

        Args:
            platform: 平台标识

        Returns:
            List[Any]: 话题列表
        """
        cls.ensure_initialized()

        # 导入服务依赖
        from .topic_service import TopicService
        return TopicService.get_topics_by_platform(platform)

    @classmethod
    def get_topics_by_status(cls, status: str) -> List[Any]:
        """获取指定状态的所有话题

        Args:
            status: 话题状态

        Returns:
            List[Any]: 话题列表
        """
        cls.ensure_initialized()

        # 导入服务依赖
        from .topic_service import TopicService
        return TopicService.get_topics_by_status(status)

    @classmethod
    def delete_topic(cls, topic_id: str) -> bool:
        """删除话题

        Args:
            topic_id: 话题ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()

        # 导入服务依赖
        from .topic_service import TopicService
        return TopicService.delete_topic(topic_id)

    @classmethod
    def sync_topics_from_redis(cls, topics_data: List[Dict[str, Any]]) -> List[str]:
        """从Redis同步话题数据到数据库（仅用于批量迁移）

        注意：此方法主要用于批量迁移或备份目的，正常内容生产流程中
        不应该直接调用此方法，而应使用select_topic_for_production方法
        来选择并持久化单个话题。

        Args:
            topics_data: 话题数据列表

        Returns:
            List[str]: 成功同步的话题ID列表
        """
        cls.ensure_initialized()

        # 导入服务依赖
        from .topic_service import TopicService
        return TopicService.sync_from_redis(topics_data)

    @classmethod
    def get_trending_topics(cls, limit: int = 100) -> List[Any]:
        """获取热门话题列表

        Args:
            limit: 返回数量限制

        Returns:
            List[Any]: 话题列表
        """
        cls.ensure_initialized()

        # 导入服务依赖
        from .topic_service import TopicService
        return TopicService.get_trending_topics(limit)

    @classmethod
    def get_latest_topics(cls, limit: int = 100) -> List[Any]:
        """获取最新的话题列表

        Args:
            limit: 返回数量限制

        Returns:
            List[Any]: 话题列表
        """
        cls.ensure_initialized()

        # 导入服务依赖
        from .topic_service import TopicService
        return TopicService.get_latest_topics(limit)

    @classmethod
    def select_topic_for_production(cls, platform: str, content_type: str = None) -> Optional[Any]:
        """为内容生产选择合适的话题

        从数据库中获取状态为pending的话题，按照综合评分选择最适合的一个，
        并将其状态更新为selected

        注意：该方法假设话题已经被保存到数据库中，controller层应该
        确保在调用此方法前，已经将所需的话题保存到了数据库。

        Args:
            platform: 平台标识
            content_type: 内容类型ID，可选

        Returns:
            Optional[Any]: 选择的话题对象，如无合适话题则返回None
        """
        cls.ensure_initialized()

        # 导入服务依赖
        from .topic_service import TopicService
        return TopicService.select_topic_for_production(platform, content_type)
