"""文章管理模块

提供文章的创建、加载和管理功能。
作为持久化层，负责文章的存储和检索。
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
        return cls.get_entity(article_id)

    @classmethod
    def get_articles_by_status(cls, status: str) -> List[Article]:
        """获取指定状态的文章

        Args:
            status: 文章状态

        Returns:
            List[Article]: 文章列表
        """
        cls.ensure_initialized()
        return [article for article in cls._articles.values() if article.status == status]

    @classmethod
    def save_article(cls, article: Article) -> bool:
        """保存文章

        Args:
            article: 文章对象

        Returns:
            bool: 是否成功保存
        """
        # 调用基类的save_entity方法
        if not cls.save_entity(article):
            return False

        try:
            # 保存到文件
            file_path = os.path.join(cls._article_dir, f"{article.id}.json")

            # 将对象转换为字典并写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(article.to_dict(), f, ensure_ascii=False, indent=2)

            logger.info(f"已保存文章: {article.title} (ID: {article.id})")
            return True
        except Exception as e:
            logger.error(f"保存文章到文件失败: {str(e)}")
            return False

    @classmethod
    def delete_article(cls, article_id: str) -> bool:
        """删除文章

        Args:
            article_id: 文章ID

        Returns:
            bool: 是否成功删除
        """
        # 使用基类删除实体
        if not cls.delete_entity(article_id):
            return False

        try:
            # 从文件中删除
            file_path = os.path.join(cls._article_dir, f"{article_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)

            logger.info(f"已删除文章文件: {article_id}")
            return True
        except Exception as e:
            logger.error(f"删除文章文件失败: {str(e)}")
            return False

    @classmethod
    def list_articles(cls) -> List[str]:
        """获取所有文章ID列表

        Returns:
            List[str]: 文章ID列表
        """
        return cls.list_entities()
