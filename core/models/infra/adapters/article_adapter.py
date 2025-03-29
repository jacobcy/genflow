"""文章适配器

负责文章数据的数据库访问操作。
"""

from typing import Dict, List, Optional, Any
from loguru import logger


class ArticleAdapter:
    """文章适配器，负责处理文章相关的数据库操作"""

    _is_initialized: bool = False

    @classmethod
    def initialize(cls) -> bool:
        """初始化数据库连接

        Returns:
            bool: 是否成功初始化
        """
        if cls._is_initialized:
            return True

        try:
            # 导入数据库初始化模块
            from core.models.db.initialize import initialize_all

            # 初始化数据库
            initialize_all()

            cls._is_initialized = True
            logger.info("文章适配器初始化成功")
            return True
        except ImportError as e:
            logger.warning(f"数据库模块导入失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            return False

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
            from core.models.db.repository import ArticleRepository

            # 创建仓库实例
            article_repo = ArticleRepository()

            # 转换为字典
            article_dict = cls._get_article_dict(article)

            # 保存文章
            if hasattr(article, 'id') and article.id:
                # 如果有ID，尝试更新
                result = article_repo.update(article.id, article_dict)
                if result is None:
                    # 如果更新失败（记录不存在），创建新记录
                    result = article_repo.create(article_dict)
            else:
                # 创建新记录
                result = article_repo.create(article_dict)

            if result:
                logger.info(f"已保存文章: {getattr(article, 'id', '(新文章)')}")
                return True
            else:
                logger.error(f"保存文章失败: {getattr(article, 'id', '(新文章)')}")
                return False
        except Exception as e:
            logger.error(f"保存文章失败: {str(e)}")
            return False

    @staticmethod
    def _get_article_dict(article: Any) -> Dict[str, Any]:
        """将文章对象转换为字典

        Args:
            article: 文章对象

        Returns:
            Dict[str, Any]: 文章字典
        """
        if hasattr(article, "dict"):
            # Pydantic模型
            return article.dict()
        elif hasattr(article, "to_dict"):
            # 自定义to_dict方法
            return article.to_dict()

        # 尝试将对象属性转换为字典
        return {
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
            from core.models.db.repository import ArticleRepository

            # 创建仓库实例
            article_repo = ArticleRepository()

            # 获取文章
            article = article_repo.get(article_id)
            if not article:
                return None

            # 返回字典格式
            if hasattr(article, 'to_dict'):
                return article.to_dict()
            return dict(article)
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
            from core.models.db.repository import ArticleRepository

            # 创建仓库实例
            article_repo = ArticleRepository()

            # 使用筛选条件查询
            articles = article_repo.db.query(article_repo.model).filter(article_repo.model.status == status).all()

            # 转换为字典列表
            return [
                article.to_dict() if hasattr(article, 'to_dict') else dict(article)
                for article in articles
            ]
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
            from core.models.db.repository import ArticleRepository

            # 创建仓库实例
            article_repo = ArticleRepository()

            # 获取文章
            article = article_repo.get(article_id)
            if not article:
                logger.warning(f"更新状态失败: 未找到文章 {article_id}")
                return False

            # 更新状态
            article.status = status
            article_repo.db.commit()

            logger.info(f"已更新文章 {article_id} 状态为 {status}")
            return True
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
            from core.models.db.repository import ArticleRepository

            # 创建仓库实例
            article_repo = ArticleRepository()

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
