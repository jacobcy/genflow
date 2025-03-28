"""文章服务模块

处理文章的业务逻辑，将数据模型与业务逻辑分离。
包含文章验证、平台准备、风格应用等操作。
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from ..article import Article
from ..platform import Platform, get_default_platform
from ..article_style import ArticleStyle
from ..content_type import ContentType
from ..topic import Topic

class ArticleService:
    """文章业务逻辑服务类"""

    @classmethod
    def apply_style(cls, article: Article, style: ArticleStyle) -> bool:
        """应用文章风格

        Args:
            article: 文章对象
            style: 文章风格配置

        Returns:
            bool: 是否成功应用
        """
        try:
            article.style_id = style.id
            article.update_status("style")
            return True
        except Exception as e:
            logger.error(f"应用风格失败: {str(e)}")
            return False

    @classmethod
    def validate_for_platform(cls, article: Article, platform: Optional[Platform] = None) -> Dict[str, Any]:
        """验证文章是否符合指定平台的要求

        Args:
            article: 文章对象
            platform: 目标平台，如果为None则使用当前platform_id加载

        Returns:
            Dict: 验证结果，包含是否通过及问题详情
        """
        from ..platform import PLATFORM_CONFIGS

        if not platform:
            if not article.platform_id:
                # 未指定平台时使用默认平台
                platform = get_default_platform()
            else:
                # 尝试加载指定的平台
                platform = PLATFORM_CONFIGS.get(article.platform_id, get_default_platform())

        # 计算当前指标
        metrics = article.calculate_metrics()

        # 验证内容是否符合平台要求
        validation_results = platform.validate_content(
            title_length=len(article.title),
            content_length=metrics["word_count"],
            image_count=metrics["image_count"]
        )

        # 检查是否包含禁用词
        forbidden_words_found = []
        for word in platform.constraints.forbidden_words:
            if word in article.title or word in article.summary:
                forbidden_words_found.append(word)
            for section in article.sections:
                if word in section.content:
                    forbidden_words_found.append(word)

        # 组合验证结果
        validation_results["forbidden_words_check"] = len(forbidden_words_found) == 0

        # 综合判断是否通过
        is_valid = all(validation_results.values())

        return {
            "is_valid": is_valid,
            "validation_details": validation_results,
            "forbidden_words_found": forbidden_words_found if forbidden_words_found else None,
            "platform_constraints": platform.get_platform_constraints()
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
        from ..platform import PLATFORM_CONFIGS

        # 加载平台配置
        platform = PLATFORM_CONFIGS.get(platform_id, get_default_platform())
        article.platform_id = platform_id

        # 验证当前内容
        validation = cls.validate_for_platform(article, platform)

        # 如果验证未通过，可以在这里添加自动调整逻辑
        adjustments_made = []

        # 只有在验证通过或成功调整后才更新状态
        if validation["is_valid"]:
            article.update_status("review")

        return {
            "platform": platform.name,
            "is_valid": validation["is_valid"],
            "validation_details": validation["validation_details"],
            "adjustments_made": adjustments_made,
            "needs_manual_review": not validation["is_valid"]
        }

    @classmethod
    def get_content_type_instance(cls, article: Article) -> Optional[ContentType]:
        """获取内容类型实例

        Args:
            article: 文章对象

        Returns:
            Optional[ContentType]: 内容类型实例，如果未找到则返回None
        """
        try:
            return ContentType.from_name(article.content_type)
        except ValueError:
            return None

    @classmethod
    def get_topic(cls, article: Article) -> Optional[Topic]:
        """获取关联话题

        Args:
            article: 文章对象

        Returns:
            Optional[Topic]: 关联的话题实例，如果未找到则返回None
        """
        try:
            # 这里假设Topic有一个from_id方法，实际实现可能需要调整
            return Topic.from_id(article.topic_id)
        except (ValueError, AttributeError):
            return None

    @classmethod
    def save_article(cls, article: Article) -> bool:
        """保存文章到数据库

        Args:
            article: 文章对象

        Returns:
            bool: 是否成功保存
        """
        try:
            from ..content_manager import ContentManager
            return ContentManager.save_article(article)
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
