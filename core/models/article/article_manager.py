"""文章管理模块

提供文章的创建、加载和管理功能。
负责文章的存储和检索，支持文件和数据库双存储。
"""

from typing import Dict, List, Optional, Any
import os
import json
from datetime import datetime
from loguru import logger

from .article import Article
from ..infra.base_manager import BaseManager


class ArticleManager(BaseManager[Article]):
    """文章管理器

    管理文章的持久化操作，包括加载、存储和检索。
    继承自BaseManager，提供通用的CRUD操作。
    支持文件存储和数据库存储。
    """

    _articles: Dict[str, Article] = {}
    _article_dir: str = ""
    _initialized: bool = False

    # 模型类定义
    _model_class = Article
    _id_field = "id"
    _timestamp_field = "updated_at"
    _metadata_field = "metadata"

    # 将_articles映射到BaseManager的_entities
    _entities = _articles

    @classmethod
    def initialize(cls, use_db: bool = False) -> None:
        """初始化管理器

        Args:
            use_db: 是否使用数据库，默认为False
        """
        if cls._initialized:
            return

        # 调用父类初始化
        super().initialize(use_db)

        # 设置文章目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cls._article_dir = os.path.join(current_dir, "../../../data/articles")

        # 确保目录存在
        os.makedirs(cls._article_dir, exist_ok=True)

        # 加载文章
        cls.load_articles()

        # 如果使用数据库，初始化数据库连接
        if cls._use_db:
            try:
                # 导入数据库初始化模块
                from core.models.db.initialize import initialize_all

                # 初始化数据库
                initialize_all()

                logger.info("文章数据库初始化成功")
            except ImportError as e:
                logger.warning(f"数据库模块导入失败: {str(e)}")
            except Exception as e:
                logger.error(f"数据库初始化失败: {str(e)}")

        cls._initialized = True
        logger.info(f"文章管理器初始化完成，已加载 {len(cls._articles)} 篇文章")

    @classmethod
    def load_articles(cls) -> None:
        """从文件加载文章"""
        try:
            article_files = [f for f in os.listdir(cls._article_dir) if f.endswith('.json')]

            for file_name in article_files:
                file_path = os.path.join(cls._article_dir, file_name)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        article_data = json.load(f)

                    # 处理日期字段
                    if 'created_at' in article_data and isinstance(article_data['created_at'], str):
                        try:
                            article_data['created_at'] = datetime.fromisoformat(article_data['created_at'])
                        except:
                            article_data['created_at'] = datetime.now()

                    if 'updated_at' in article_data and isinstance(article_data['updated_at'], str):
                        try:
                            article_data['updated_at'] = datetime.fromisoformat(article_data['updated_at'])
                        except:
                            article_data['updated_at'] = datetime.now()

                    # 使用Article类创建实例
                    article = Article(**article_data)
                    cls._articles[article.id] = article

                    logger.debug(f"已加载文章: {article.title} (ID: {article.id})")
                except Exception as e:
                    logger.error(f"加载文章文件 {file_name} 失败: {str(e)}")

        except Exception as e:
            logger.error(f"加载文章目录失败: {str(e)}")

    @classmethod
    def get_article(cls, article_id: str) -> Optional[Article]:
        """获取指定ID的文章

        Args:
            article_id: 文章ID

        Returns:
            Optional[Article]: 文章对象或None
        """
        cls.ensure_initialized()

        # 首先从内存中查找
        article = cls.get_entity(article_id)
        if article or not cls._use_db:
            return article

        # 如果内存中没有且使用数据库，从数据库查找
        try:
            # 导入仓库
            from core.models.db.repository import ArticleRepository

            # 创建仓库实例
            article_repo = ArticleRepository()

            # 获取文章
            db_article = article_repo.get(article_id)
            if not db_article:
                return None

            # 转换为Article对象
            article_dict = db_article.to_dict() if hasattr(db_article, 'to_dict') else dict(db_article)
            article = Article(**article_dict)

            # 缓存到内存
            cls._articles[article_id] = article

            return article
        except Exception as e:
            logger.error(f"从数据库获取文章失败: {str(e)}")
            return None

    @classmethod
    def get_articles_by_status(cls, status: str) -> List[Article]:
        """获取指定状态的文章

        Args:
            status: 文章状态

        Returns:
            List[Article]: 文章列表
        """
        cls.ensure_initialized()

        # 从内存中获取
        memory_articles = [article for article in cls._articles.values() if article.status == status]

        # 如果不使用数据库，直接返回内存中的结果
        if not cls._use_db:
            return memory_articles

        # 从数据库获取
        try:
            # 导入仓库
            from core.models.db.repository import ArticleRepository

            # 创建仓库实例
            article_repo = ArticleRepository()

            # 使用筛选条件查询
            try:
                # 查询符合条件的文章
                db_articles = article_repo.find_by_field("status", status)

                # 转换为Article对象列表
                db_article_objects = []
                for db_article in db_articles:
                    article_dict = db_article.to_dict() if hasattr(db_article, 'to_dict') else dict(db_article)
                    article = Article(**article_dict)

                    # 缓存到内存
                    if article.id not in cls._articles:
                        cls._articles[article.id] = article

                    db_article_objects.append(article)

                # 合并去重
                all_articles = {article.id: article for article in memory_articles + db_article_objects}
                return list(all_articles.values())
            except AttributeError:
                # 如果仓库没有find_by_field方法，使用遍历查询
                all_articles = article_repo.get_all()
                filtered_articles = []

                for db_article in all_articles:
                    if getattr(db_article, "status", None) == status:
                        article_dict = db_article.to_dict() if hasattr(db_article, 'to_dict') else dict(db_article)
                        article = Article(**article_dict)

                        # 缓存到内存
                        if article.id not in cls._articles:
                            cls._articles[article.id] = article

                        filtered_articles.append(article)

                # 合并去重
                all_articles = {article.id: article for article in memory_articles + filtered_articles}
                return list(all_articles.values())

        except Exception as e:
            logger.error(f"从数据库获取文章列表失败: {str(e)}")
            return memory_articles

    @classmethod
    def save_article(cls, article: Article) -> bool:
        """保存文章

        Args:
            article: 文章对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()

        # 更新内存
        update_result = cls.save_entity(article)

        success = True

        # 保存到文件
        try:
            file_path = os.path.join(cls._article_dir, f"{article.id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(article.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存文章到文件失败: {str(e)}")
            success = False

        # 如果使用数据库，保存到数据库
        if cls._use_db:
            try:
                # 导入仓库
                from core.models.db.repository import ArticleRepository

                # 创建仓库实例
                article_repo = ArticleRepository()

                # 转换为字典
                article_dict = article.to_dict()

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

                if not result:
                    logger.error(f"保存文章到数据库失败: {article.id}")
                    success = False
            except Exception as e:
                logger.error(f"保存文章到数据库失败: {str(e)}")
                success = False

        if success:
            logger.info(f"已保存文章: {article.title} (ID: {article.id})")
        return success and update_result

    @classmethod
    def delete_article(cls, article_id: str) -> bool:
        """删除文章

        Args:
            article_id: 文章ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()

        # 从内存中删除
        memory_result = cls.delete_entity(article_id)
        success = True

        # 从文件中删除
        try:
            file_path = os.path.join(cls._article_dir, f"{article_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"删除文章文件失败: {str(e)}")
            success = False

        # 如果使用数据库，从数据库中删除
        if cls._use_db:
            try:
                # 导入仓库
                from core.models.db.repository import ArticleRepository

                # 创建仓库实例
                article_repo = ArticleRepository()

                # 删除文章
                db_result = article_repo.delete(article_id)
                if not db_result:
                    logger.warning(f"从数据库删除文章失败，可能不存在: {article_id}")
                    success = False
            except Exception as e:
                logger.error(f"从数据库删除文章失败: {str(e)}")
                success = False

        if success and memory_result:
            logger.info(f"已删除文章: {article_id}")
        return success and memory_result

    @classmethod
    def list_articles(cls) -> List[str]:
        """获取所有文章ID列表

        Returns:
            List[str]: 文章ID列表
        """
        return cls.list_entities()

    @classmethod
    def update_article_status(cls, article_id: str, status: str) -> bool:
        """更新文章状态

        Args:
            article_id: 文章ID
            status: 新状态

        Returns:
            bool: 是否成功更新
        """
        cls.ensure_initialized()

        # 获取文章
        article = cls.get_article(article_id)
        if not article:
            logger.warning(f"更新状态失败: 未找到文章 {article_id}")
            return False

        # 更新状态
        article.status = status

        # 保存更新
        return cls.save_article(article)
