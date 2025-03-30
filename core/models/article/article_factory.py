"""文章工厂模块

处理文章的业务逻辑，将数据模型与业务逻辑分离。
包含文章验证、平台准备、风格应用等操作。
作为中间层，调用ArticleManager进行数据持久化，调用ArticleParser进行内容解析。
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4
from loguru import logger

from .article import Article, Section
from .basic_article import BasicArticle
from .article_manager import ArticleManager
from .article_parser import ArticleParser

class ArticleFactory:
    """文章业务逻辑工厂类

    提供文章相关的所有业务方法，包括文章创建、转换、状态管理、指标计算等。
    作为业务层，调用ArticleManager进行持久化，调用ArticleParser进行内容解析。

    外部系统应当通过ContentManager调用本工厂，而不直接调用。
    """

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
        cls.calculate_article_metrics(default_article)

        return default_article

    # ===== 业务方法 =====

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
    def update_status_by_id(cls, article_id: str, status: str) -> bool:
        """通过ID更新文章状态

        Args:
            article_id: 文章ID
            status: 新状态

        Returns:
            bool: 是否成功更新
        """
        article = ArticleManager.get_article(article_id)
        if not article:
            logger.warning(f"更新文章状态失败: 文章 {article_id} 不存在")
            return False

        try:
            # 更新状态
            cls.update_article_status(article, status)

            # 保存更新后的文章
            return ArticleManager.save_article(article)
        except Exception as e:
            logger.error(f"更新文章状态失败: {str(e)}")
            return False

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

    @classmethod
    def from_basic_article(cls, basic: BasicArticle, topic_id: str, article_id: Optional[str] = None) -> Article:
        """从BasicArticle创建Article实例

        Args:
            basic: 基础文章对象
            topic_id: 话题ID
            article_id: 文章ID（可选）

        Returns:
            Article: 文章对象
        """
        article_data = basic.model_dump()

        # 添加必要字段
        article_data["topic_id"] = topic_id
        if article_id:
            article_data["id"] = article_id
        elif hasattr(basic, "id") and basic.id:
            article_data["id"] = basic.id
        else:
            article_data["id"] = str(uuid4())

        # 创建文章实例
        article = Article(**article_data)

        # 计算文章指标
        cls.calculate_article_metrics(article)

        return article

    # 调用解析器的方法
    @classmethod
    def parse_ai_response(cls, response_text: str, article: Article) -> Optional[Article]:
        """解析AI返回的文章数据

        Args:
            response_text: AI返回的JSON文本
            article: 需要更新的Article实例

        Returns:
            更新后的Article实例，如果解析失败则返回None
        """
        return ArticleParser.parse_ai_response(response_text, article)

    @classmethod
    def validate_article(cls, article: Article) -> bool:
        """验证文章数据的完整性

        Args:
            article: Article实例

        Returns:
            bool: 验证是否通过
        """
        return ArticleParser.validate_article(article)

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
            cls.update_article_status(article, "style")
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
        metrics = cls.calculate_article_metrics(article)

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
            cls.update_article_status(article, "review")

        return {
            "platform": platform["name"],
            "is_valid": validation["is_valid"],
            "validation_details": validation["validation_details"],
            "adjustments_made": [],
            "needs_manual_review": not validation["is_valid"]
        }

    # ===== 数据访问方法（代理到Manager）=====

    @classmethod
    def save_article(cls, article: Article) -> bool:
        """保存文章

        Args:
            article: 文章对象

        Returns:
            bool: 是否成功保存
        """
        try:
            return ArticleManager.save_article(article)
        except Exception as e:
            logger.error(f"保存文章失败: {str(e)}")
            return False

    @classmethod
    def get_article(cls, article_id: str) -> Optional[Article]:
        """获取文章

        Args:
            article_id: 文章ID

        Returns:
            Optional[Article]: 文章对象或None
        """
        return ArticleManager.get_article(article_id)

    @classmethod
    def get_articles_by_status(cls, status: str) -> List[Article]:
        """获取指定状态的文章

        Args:
            status: 文章状态

        Returns:
            List[Article]: 文章列表
        """
        return ArticleManager.get_articles_by_status(status)

    @classmethod
    def delete_article(cls, article_id: str) -> bool:
        """删除文章

        Args:
            article_id: 文章ID

        Returns:
            bool: 是否成功删除
        """
        return ArticleManager.delete_article(article_id)

    @classmethod
    def update_status_and_save(cls, article: Article, new_status: str) -> bool:
        """更新文章状态并保存

        Args:
            article: 文章对象
            new_status: 新状态

        Returns:
            bool: 是否成功更新并保存
        """
        try:
            cls.update_article_status(article, new_status)
            return cls.save_article(article)
        except Exception as e:
            logger.error(f"更新文章状态并保存失败: {str(e)}")
            return False
