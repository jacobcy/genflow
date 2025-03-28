"""数据库适配器接口

为ContentManager提供统一的数据库访问接口，
负责在模型层和数据库层之间进行转换和协调。
"""

from typing import Dict, List, Optional, Any, Type, TypeVar
import importlib
from loguru import logger
import time

# 定义泛型类型变量
T = TypeVar('T')

class DBAdapter:
    """数据库适配器，为ContentManager提供统一的数据库操作接口"""

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
            # 导入数据库初始化模块
            from core.db.initialize import initialize_all

            # 初始化数据库
            initialize_all()

            cls._is_initialized = True
            logger.info("数据库适配器初始化成功")
            return True
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
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入迁移工具
            from core.db.migrate_configs import migrate_all

            # 执行迁移，在sync_mode下执行完整同步（包括删除不存在的配置）
            migrate_all(sync_mode=sync_mode)

            logger.info(f"配置文件已成功同步到数据库 (sync_mode={sync_mode})")
            return True
        except Exception as e:
            logger.error(f"同步配置文件到数据库失败: {str(e)}")
            return False

    @classmethod
    def load_content_types(cls) -> Dict[str, Any]:
        """从数据库加载所有内容类型

        Returns:
            Dict[str, Any]: 内容类型字典
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return {}

            # 导入仓库
            from core.db.repository import content_type_repo

            # 获取所有内容类型
            content_types = content_type_repo.get_all()
            return {ct.id: ct for ct in content_types}
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
            # 初始化数据库
            if not cls.initialize():
                return {}

            # 导入仓库
            from core.db.repository import article_style_repo

            # 获取所有文章风格
            styles = article_style_repo.get_all()
            return {style.name: style for style in styles}
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
            # 初始化数据库
            if not cls.initialize():
                return {}

            # 导入仓库
            from core.db.repository import platform_repo

            # 获取所有平台
            platforms = platform_repo.get_all()
            return {platform.id: platform for platform in platforms}
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
            # 初始化数据库
            if not cls.initialize():
                return None

            # 导入仓库
            from core.db.repository import content_type_repo

            # 获取内容类型
            return content_type_repo.get(content_type_id)
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
            # 初始化数据库
            if not cls.initialize():
                return None

            # 导入仓库
            from core.db.repository import article_style_repo

            # 获取文章风格
            return article_style_repo.get(style_name)
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
            # 初始化数据库
            if not cls.initialize():
                return None

            # 导入仓库
            from core.db.repository import platform_repo

            # 获取平台
            return platform_repo.get(platform_id)
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
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.db.repository import content_type_repo

            # 转换为字典
            if hasattr(content_type, "to_dict"):
                content_type_dict = content_type.to_dict()
            else:
                content_type_dict = {
                    "id": content_type.id,
                    "name": content_type.name,
                    "description": getattr(content_type, "description", ""),
                    "default_word_count": getattr(content_type, "default_word_count", "1000"),
                    "is_enabled": getattr(content_type, "is_enabled", True),
                    "prompt_template": getattr(content_type, "prompt_template", ""),
                    "output_format": getattr(content_type, "output_format", {}),
                    "required_elements": getattr(content_type, "required_elements", {}),
                    "optional_elements": getattr(content_type, "optional_elements", {}),
                }

            # 检查是否已存在
            existing = content_type_repo.get(content_type.id)
            if existing:
                # 更新
                content_type_repo.update(content_type.id, content_type_dict)
                logger.info(f"已更新内容类型: {content_type.id}")
            else:
                # 创建
                content_type_repo.create(content_type_dict)
                logger.info(f"已创建内容类型: {content_type.id}")

            return True
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
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.db.repository import article_style_repo

            # 转换为字典
            if hasattr(style, "to_dict"):
                style_dict = style.to_dict()
            else:
                style_dict = {
                    "name": style.name,
                    "description": getattr(style, "description", ""),
                    "is_enabled": getattr(style, "is_enabled", True),
                    "tone": getattr(style, "tone", ""),
                    "style_characteristics": getattr(style, "style_characteristics", {}),
                    "language_preference": getattr(style, "language_preference", {}),
                    "writing_format": getattr(style, "writing_format", {}),
                    "prompt_template": getattr(style, "prompt_template", ""),
                    "example": getattr(style, "example", ""),
                }

            # 检查是否已存在
            existing = article_style_repo.get(style.name)
            if existing:
                # 更新
                article_style_repo.update(style.name, style_dict)
                logger.info(f"已更新文章风格: {style.name}")
            else:
                # 创建
                article_style_repo.create(style_dict)
                logger.info(f"已创建文章风格: {style.name}")

            return True
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
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.db.repository import platform_repo

            # 转换为字典
            if hasattr(platform, "to_dict"):
                platform_dict = platform.to_dict()
            else:
                platform_dict = {
                    "id": platform.id,
                    "name": platform.name,
                    "description": getattr(platform, "description", ""),
                    "is_enabled": getattr(platform, "is_enabled", True),
                    "platform_type": getattr(platform, "platform_type", ""),
                    "url": getattr(platform, "url", ""),
                    "logo_url": getattr(platform, "logo_url", ""),
                    "max_title_length": getattr(platform, "max_title_length", {}),
                    "max_content_length": getattr(platform, "max_content_length", {}),
                    "allowed_media_types": getattr(platform, "allowed_media_types", {}),
                    "api_config": getattr(platform, "api_config", {}),
                }

            # 检查是否已存在
            existing = platform_repo.get(platform.id)
            if existing:
                # 更新
                platform_repo.update(platform.id, platform_dict)
                logger.info(f"已更新平台配置: {platform.id}")
            else:
                # 创建
                platform_repo.create(platform_dict)
                logger.info(f"已创建平台配置: {platform.id}")

            return True
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
            # 初始化数据库
            if not cls.initialize():
                return None

            # 导入模型
            from core.db.models import get_default_content_type

            # 获取默认内容类型
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
            # 初始化数据库
            if not cls.initialize():
                return None

            # 导入模型
            from core.db.models import get_default_article_style

            # 获取默认文章风格
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
            # 初始化数据库
            if not cls.initialize():
                return None

            # 导入模型
            from core.db.models import get_default_platform

            # 获取默认平台
            return get_default_platform()
        except Exception as e:
            logger.error(f"获取默认平台配置失败: {str(e)}")
            return None

    @classmethod
    def save_article(cls, article: Any) -> bool:
        """保存文章到数据库

        Args:
            article: 文章对象

        Returns:
            bool: 是否成功保存
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.db.repository import article_repo

            # 转换为字典
            if hasattr(article, "dict"):
                # Pydantic模型
                article_dict = article.dict()
            elif hasattr(article, "to_dict"):
                # 自定义to_dict方法
                article_dict = article.to_dict()
            else:
                # 尝试将对象属性转换为字典
                article_dict = {
                    "id": article.id,
                    "topic_id": getattr(article, "topic_id", ""),
                    "outline_id": getattr(article, "outline_id", None),
                    "title": getattr(article, "title", ""),
                    "summary": getattr(article, "summary", ""),
                    "sections": getattr(article, "sections", []),
                    "tags": getattr(article, "tags", []),
                    "keywords": getattr(article, "keywords", []),
                    "cover_image": getattr(article, "cover_image", None),
                    "cover_image_alt": getattr(article, "cover_image_alt", None),
                    "images": getattr(article, "images", []),
                    "content_type": getattr(article, "content_type", "default"),
                    "categories": getattr(article, "categories", []),
                    "author": getattr(article, "author", "AI"),
                    "created_at": getattr(article, "created_at", None),
                    "updated_at": getattr(article, "updated_at", None),
                    "word_count": getattr(article, "word_count", 0),
                    "read_time": getattr(article, "read_time", 0),
                    "version": getattr(article, "version", 1),
                    "status": getattr(article, "status", "initialized"),
                    "is_published": getattr(article, "is_published", False),
                    "style_name": getattr(article, "style_name", None),
                    "platform_id": getattr(article, "platform_id", None),
                    "platform_url": getattr(article, "platform_url", None),
                    "review": getattr(article, "review", {}),
                    "metadata": getattr(article, "metadata", {})
                }

            # 保存文章
            result = article_repo.create_or_update(article_dict)

            if result:
                logger.info(f"已保存文章: {article.id}")
                return True
            else:
                logger.error(f"保存文章失败: {article.id}")
                return False
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
            # 初始化数据库
            if not cls.initialize():
                return None

            # 导入仓库
            from core.db.repository import article_repo

            # 获取文章
            article = article_repo.get(article_id)
            if not article:
                return None

            # 返回字典格式
            return article.to_dict()
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
            # 初始化数据库
            if not cls.initialize():
                return []

            # 导入仓库
            from core.db.repository import article_repo

            # 获取文章
            return article_repo.get_by_status(status)
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
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.db.repository import article_repo

            # 更新状态
            result = article_repo.update_status(article_id, status)
            return result is not None
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
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.db.repository import article_repo

            # 删除文章
            success = article_repo.delete(article_id)

            if success:
                logger.info(f"成功删除文章: {article_id}")
            else:
                logger.warning(f"删除文章失败, 未找到文章: {article_id}")

            return success
        except Exception as e:
            logger.error(f"删除文章失败: {str(e)}")
            return False

    # 话题相关方法

    @classmethod
    def get_topic(cls, topic_id: str) -> Optional[Dict[str, Any]]:
        """获取指定ID的话题

        Args:
            topic_id: 话题ID

        Returns:
            Optional[Dict[str, Any]]: 话题数据，如果未找到则返回None
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return None

            # 导入仓库
            from core.db.repository import topic_repo

            # 获取话题
            topic = topic_repo.get(topic_id)
            if topic:
                return topic.to_dict()
            return None
        except Exception as e:
            logger.error(f"获取话题失败: {str(e)}")
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
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.db.repository import topic_repo

            # 转换为字典
            if hasattr(topic, "to_dict"):
                topic_dict = topic.to_dict()
            else:
                # 尝试从对象属性构建字典
                topic_dict = {}
                for key in ['id', 'title', 'platform', 'description', 'url', 'mobile_url',
                           'cover', 'hot', 'trend_score', 'timestamp', 'fetch_time',
                           'expire_time', 'categories', 'tags', 'content_type', 'status']:
                    if hasattr(topic, key):
                        topic_dict[key] = getattr(topic, key)

            # 确保必须的字段
            if 'id' not in topic_dict or 'title' not in topic_dict or 'platform' not in topic_dict:
                logger.error("保存话题失败: 缺少必要字段(id, title, platform)")
                return False

            # 确保时间戳字段
            if 'timestamp' not in topic_dict:
                topic_dict['timestamp'] = int(time.time())
            if 'fetch_time' not in topic_dict:
                topic_dict['fetch_time'] = int(time.time())
            if 'expire_time' not in topic_dict:
                # 默认7天后过期
                topic_dict['expire_time'] = int(time.time()) + 7 * 24 * 60 * 60

            # 检查是否已存在
            existing = topic_repo.get(topic_dict['id'])
            if existing:
                # 更新
                updated = topic_repo.update(topic_dict['id'], topic_dict)
                if updated:
                    logger.info(f"成功更新话题: {topic_dict['id']}")
                    return True
                else:
                    logger.error(f"更新话题失败: {topic_dict['id']}")
                    return False
            else:
                # 创建
                created = topic_repo.create(topic_dict)
                if created:
                    logger.info(f"成功创建话题: {topic_dict['id']}")
                    return True
                else:
                    logger.error(f"创建话题失败")
                    return False
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
            # 初始化数据库
            if not cls.initialize():
                return []

            # 导入仓库
            from core.db.repository import topic_repo

            # 获取话题
            return topic_repo.get_by_platform(platform)
        except Exception as e:
            logger.error(f"获取平台话题失败: {str(e)}")
            return []

    @classmethod
    def get_topics_by_status(cls, status: str) -> List[Dict[str, Any]]:
        """获取指定状态的所有话题

        Args:
            status: 话题状态

        Returns:
            List[Dict[str, Any]]: 话题列表
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return []

            # 导入仓库
            from core.db.repository import topic_repo

            # 获取话题
            return topic_repo.get_by_status(status)
        except Exception as e:
            logger.error(f"获取状态话题失败: {str(e)}")
            return []

    @classmethod
    def update_topic_status(cls, topic_id: str, status: str) -> bool:
        """更新话题状态

        Args:
            topic_id: 话题ID
            status: 新状态

        Returns:
            bool: 是否成功更新
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.db.repository import topic_repo

            # 更新状态
            updated = topic_repo.update_status(topic_id, status)

            if updated:
                logger.info(f"成功更新话题状态: {topic_id} -> {status}")
                return True
            else:
                logger.warning(f"更新话题状态失败, 未找到话题: {topic_id}")
                return False
        except Exception as e:
            logger.error(f"更新话题状态失败: {str(e)}")
            return False

    @classmethod
    def delete_topic(cls, topic_id: str) -> bool:
        """删除话题

        Args:
            topic_id: 话题ID

        Returns:
            bool: 是否成功删除
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.db.repository import topic_repo

            # 删除话题
            success = topic_repo.delete(topic_id)

            if success:
                logger.info(f"成功删除话题: {topic_id}")
            else:
                logger.warning(f"删除话题失败, 未找到话题: {topic_id}")

            return success
        except Exception as e:
            logger.error(f"删除话题失败: {str(e)}")
            return False

    @classmethod
    def sync_topics_from_redis(cls, topics_data: List[Dict[str, Any]]) -> List[str]:
        """从Redis同步话题数据到数据库

        Args:
            topics_data: 话题数据列表

        Returns:
            List[str]: 成功同步的话题ID列表
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return []

            # 导入仓库
            from core.db.repository import topic_repo

            # 同步数据
            return topic_repo.sync_from_redis(topics_data)
        except Exception as e:
            logger.error(f"从Redis同步话题数据失败: {str(e)}")
            return []

    @classmethod
    def get_trending_topics(cls, limit: int = 100) -> List[Dict[str, Any]]:
        """获取热门话题列表

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict[str, Any]]: 话题列表
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return []

            # 导入仓库
            from core.db.repository import topic_repo

            # 获取热门话题
            return topic_repo.get_trending_topics(limit)
        except Exception as e:
            logger.error(f"获取热门话题失败: {str(e)}")
            return []

    @classmethod
    def get_latest_topics(cls, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最新的话题列表

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict[str, Any]]: 话题列表
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return []

            # 导入仓库
            from core.db.repository import topic_repo

            # 获取最新话题
            return topic_repo.get_latest(limit)
        except Exception as e:
            logger.error(f"获取最新话题失败: {str(e)}")
            return []

    @classmethod
    def get_outline(cls, outline_id: str) -> Optional[Any]:
        """获取指定ID的文章大纲

        本方法不从数据库获取大纲，而是从临时存储中获取，
        因为大纲是临时对象，不需要持久化到数据库。

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[Any]: 大纲对象，如不存在则返回None
        """
        try:
            # 从临时存储获取大纲
            from core.models.managers.outline_manager import OutlineManager
            return OutlineManager.get_outline(outline_id)
        except Exception as e:
            logger.error(f"获取大纲失败: {str(e)}")
            return None

    @classmethod
    def save_outline(cls, outline: Any, outline_id: Optional[str] = None) -> Optional[str]:
        """保存文章大纲到临时存储

        本方法不将大纲保存到数据库，而是保存到临时存储，
        因为大纲是临时对象，不需要持久化到数据库。

        Args:
            outline: 大纲对象
            outline_id: 可选的大纲ID，如不提供则自动生成

        Returns:
            Optional[str]: 大纲ID，如保存失败则返回None
        """
        try:
            # 保存到临时存储
            from core.models.managers.outline_manager import OutlineManager
            return OutlineManager.save_outline(outline, outline_id)
        except Exception as e:
            logger.error(f"保存大纲失败: {str(e)}")
            return None

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除文章大纲

        从临时存储中删除指定的大纲。

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        try:
            # 从临时存储删除
            from core.models.managers.outline_manager import OutlineManager
            return OutlineManager.delete_outline(outline_id)
        except Exception as e:
            logger.error(f"删除大纲失败: {str(e)}")
            return False

    @classmethod
    def list_outlines(cls) -> List[str]:
        """列出所有大纲ID

        获取当前存储在临时存储中的所有大纲ID。

        Returns:
            List[str]: 大纲ID列表
        """
        try:
            # 列出临时存储中的所有大纲
            from core.models.managers.outline_manager import OutlineManager
            return OutlineManager.list_outlines()
        except Exception as e:
            logger.error(f"列出大纲失败: {str(e)}")
            return []
