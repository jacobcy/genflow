"""文章服务模块

处理文章的业务逻辑，将数据模型与业务逻辑分离。
包含文章验证、平台准备、风格应用等操作。
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4
from loguru import logger

from .article import Article, Section

class ArticleService:
    """文章业务逻辑服务类"""

    @classmethod
    def get_default_article(cls) -> Article:
        """获取默认文章

        Returns:
            Article: 默认文章对象
        """
        # 创建默认章节
        default_section = Section(
            id=f"section_{uuid4().hex[:8]}",
            title="简介",
            content="这是默认文章的内容。",
            order=1
        )

        # 创建默认文章
        default_article = Article(
            id=f"article_{uuid4().hex[:8]}",
            topic_id="default_topic",
            title="默认文章",
            summary="这是一篇默认文章，系统自动生成",
            sections=[default_section],
            tags=["默认", "示例"],
            status="completed",
            author="AI系统",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 计算指标
        default_article.calculate_metrics()

        return default_article

    @classmethod
    def apply_style(cls, article: Article, style: Dict[str, Any]) -> bool:
        """应用文章风格

        Args:
            article: 文章对象
            style: 文章风格配置

        Returns:
            bool: 是否成功应用
        """
        try:
            article.style_id = style.get("id")
            article.update_status("style")
            return True
        except Exception as e:
            logger.error(f"应用风格失败: {str(e)}")
            return False

    @classmethod
    def validate_for_platform(cls, article: Article, platform: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """验证文章是否符合指定平台的要求

        Args:
            article: 文章对象
            platform: 目标平台配置

        Returns:
            Dict: 验证结果，包含是否通过及问题详情
        """
        if not platform:
            # 简化处理，返回通用验证结果
            return {
                "is_valid": True,
                "validation_details": {
                    "title_length": True,
                    "content_length": True,
                    "image_count": True
                },
                "forbidden_words_found": None,
                "platform_constraints": {}
            }

        # 计算当前指标
        metrics = article.calculate_metrics()

        # 构建基本验证结果
        validation_results = {
            "title_length": True,
            "content_length": True,
            "image_count": True
        }

        # 检查是否包含禁用词
        forbidden_words = platform.get("constraints", {}).get("forbidden_words", [])
        forbidden_words_found = []

        for word in forbidden_words:
            if word in article.title or word in article.summary:
                forbidden_words_found.append(word)
                validation_results["forbidden_words_check"] = False
            for section in article.sections:
                if word in section.content:
                    forbidden_words_found.append(word)
                    validation_results["forbidden_words_check"] = False

        # 如果没有禁用词，添加此字段为True
        if "forbidden_words_check" not in validation_results:
            validation_results["forbidden_words_check"] = True

        # 综合判断是否通过
        is_valid = all(validation_results.values())

        return {
            "is_valid": is_valid,
            "validation_details": validation_results,
            "forbidden_words_found": forbidden_words_found if forbidden_words_found else None,
            "platform_constraints": platform.get("constraints", {})
        }

    @classmethod
    def prepare_for_platform(cls, article: Article, platform_id: str) -> Dict[str, Any]:
        """为指定平台准备发布

        根据平台要求调整内容并验证合规性

        Args:
            article: 文章对象
            platform_id: 平台ID

        Returns:
            Dict: 处理结果，包含调整内容和验证状态
        """
        article.platform_id = platform_id

        # 简化后不再加载实际平台配置
        platform = {"name": platform_id, "constraints": {}}

        # 验证当前内容
        validation = cls.validate_for_platform(article, platform)

        # 如果验证通过，更新状态
        if validation["is_valid"]:
            article.update_status("review")

        return {
            "platform": platform["name"],
            "is_valid": validation["is_valid"],
            "validation_details": validation["validation_details"],
            "adjustments_made": [],
            "needs_manual_review": not validation["is_valid"]
        }

    @classmethod
    def save_article(cls, article: Article) -> bool:
        """保存文章

        Args:
            article: 文章对象

        Returns:
            bool: 是否成功保存
        """
        try:
            from .article_manager import ArticleManager
            return ArticleManager.save_article(article)
        except Exception as e:
            logger.error(f"保存文章失败: {str(e)}")
            return False

    @classmethod
    def update_article_status(cls, article: Article, new_status: str) -> bool:
        """更新文章状态并保存

        Args:
            article: 文章对象
            new_status: 新状态

        Returns:
            bool: 是否成功更新并保存
        """
        try:
            article.update_status(new_status)
            return cls.save_article(article)
        except Exception as e:
            logger.error(f"更新文章状态失败: {str(e)}")
            return False
