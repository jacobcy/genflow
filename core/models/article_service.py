"""文章服务模块

处理文章业务逻辑，保持模型层专注于数据结构。
从Article模型中移出的业务方法放置在这里。
"""

from typing import Dict, Optional, Any
from datetime import datetime
from loguru import logger

from core.models.article.article import Article, Section


class ArticleService:
    """文章服务类

    提供文章相关的业务逻辑方法，包括状态管理、指标计算等。
    """

    @classmethod
    def update_article_status(cls, article: Article, new_status: str) -> None:
        """更新文章状态并记录时间

        Args:
            article: 文章对象
            new_status: 新状态
        """
        article.status = new_status
        article.updated_at = datetime.now()

        # 记录状态变更到元数据
        if "status_history" not in article.metadata:
            article.metadata["status_history"] = []

        article.metadata["status_history"].append({
            "status": new_status,
            "timestamp": article.updated_at.isoformat()
        })

    @classmethod
    def calculate_article_metrics(cls, article: Article) -> Dict[str, Any]:
        """计算文章指标

        Args:
            article: 文章对象

        Returns:
            Dict[str, Any]: 文章指标统计
        """
        # 计算总字数
        total_words = len(article.title) + len(article.summary)
        for section in article.sections:
            total_words += len(section.title) + len(section.content)

        # 估算阅读时间 (假设平均阅读速度400字/分钟)
        read_time = max(1, round(total_words / 400))

        # 更新指标
        article.word_count = total_words
        article.read_time = read_time

        return {
            "word_count": total_words,
            "read_time": read_time,
            "section_count": len(article.sections),
            "image_count": len(article.images) + (1 if article.cover_image else 0)
        }
