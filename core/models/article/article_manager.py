"""文章管理模块

提供文章的创建、加载和管理功能。
简化的文章管理器实现，专注于核心功能。
"""

from typing import Dict, List, Optional, Any
import os
import json
from datetime import datetime
from uuid import uuid4
from loguru import logger


class Article:
    """文章模型

    表示一篇完整的文章，包含基本信息、内容和元数据。
    """

    def __init__(self,
                 id: Optional[str] = None,
                 title: str = "",
                 content: str = "",
                 author: str = "",
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 status: str = "draft",
                 **kwargs):
        """初始化文章

        Args:
            id: 文章ID，如果为None则自动生成
            title: 文章标题
            content: 文章内容
            author: 作者
            created_at: 创建时间，如果为None则使用当前时间
            updated_at: 更新时间，如果为None则使用当前时间
            status: 文章状态，默认为草稿
        """
        self.id = id or str(uuid4())
        self.title = title
        self.content = content
        self.author = author
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.status = status

        # 保存其它属性
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        Returns:
            Dict[str, Any]: 文章属性字典
        """
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result

    def update_status(self, status: str) -> None:
        """更新文章状态

        Args:
            status: 新状态
        """
        self.status = status
        self.updated_at = datetime.now()


class ArticleManager:
    """文章管理器

    管理文章的加载、存储和检索。
    """

    _articles: Dict[str, Article] = {}
    _article_dir: str = ""
    _initialized: bool = False

    @classmethod
    def initialize(cls, use_db: bool = False) -> None:
        """初始化管理器

        Args:
            use_db: 是否使用数据库，默认为False
        """
        if cls._initialized:
            return

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
        if not cls._initialized:
            cls.initialize()

        return cls._articles.get(article_id)

    @classmethod
    def get_articles_by_status(cls, status: str) -> List[Article]:
        """获取指定状态的文章

        Args:
            status: 文章状态

        Returns:
            List[Article]: 文章列表
        """
        if not cls._initialized:
            cls.initialize()

        return [article for article in cls._articles.values() if article.status == status]

    @classmethod
    def save_article(cls, article: Article) -> bool:
        """保存文章

        Args:
            article: 文章对象

        Returns:
            bool: 是否成功保存
        """
        if not cls._initialized:
            cls.initialize()

        try:
            # 更新时间
            article.updated_at = datetime.now()

            # 保存到内存
            cls._articles[article.id] = article

            # 保存到文件
            file_path = os.path.join(cls._article_dir, f"{article.id}.json")

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(article.to_dict(), f, ensure_ascii=False, indent=2)

            logger.info(f"已保存文章: {article.title} (ID: {article.id})")
            return True
        except Exception as e:
            logger.error(f"保存文章失败: {str(e)}")
            return False

    @classmethod
    def update_article_status(cls, article_id: str, status: str) -> bool:
        """更新文章状态

        Args:
            article_id: 文章ID
            status: 新状态

        Returns:
            bool: 是否成功更新
        """
        if not cls._initialized:
            cls.initialize()

        article = cls.get_article(article_id)
        if not article:
            logger.error(f"更新文章状态失败: 文章 {article_id} 不存在")
            return False

        try:
            # 更新状态
            article.update_status(status)

            # 保存文章
            return cls.save_article(article)
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
        if not cls._initialized:
            cls.initialize()

        if article_id not in cls._articles:
            logger.warning(f"删除文章失败: 文章 {article_id} 不存在")
            return False

        try:
            # 从内存中删除
            del cls._articles[article_id]

            # 从文件中删除
            file_path = os.path.join(cls._article_dir, f"{article_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)

            logger.info(f"已删除文章: {article_id}")
            return True
        except Exception as e:
            logger.error(f"删除文章失败: {str(e)}")
            return False
