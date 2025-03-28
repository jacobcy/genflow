"""内容生产主控制器

该模块实现了内容生产的总体协调流程，整合各个专业团队完成从选题到发布的全流程。
"""

from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import logging
import uuid

from core.models.topic import Topic
from core.models.article import Article
from core.models.platform import Platform, get_default_platform
from core.models.progress import ProductionProgress, ProductionStage, StageStatus

from core.controllers.team_adapter import (
    TopicTeamAdapter,
    ResearchTeamAdapter,
    WritingTeamAdapter,
    StyleTeamAdapter,
    ReviewTeamAdapter
)

logger = logging.getLogger(__name__)

class ContentProductionResult:
    """内容生产结果"""
    def __init__(
        self,
        topic: Topic,
        research_data: Dict,
        article: Article,
        review_data: Dict,
        platform: Platform
    ):
        self.topic = topic
        self.research_data = research_data
        self.article = article
        self.review_data = review_data
        self.platform = platform
        self.created_at = datetime.now()
        self.status = "pending"

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "topic": self.topic.to_dict() if hasattr(self.topic, "to_dict") else self.topic,
            "research_data": self.research_data,
            "article": self.article.to_dict() if hasattr(self.article, "to_dict") else self.article,
            "review_data": self.review_data,
            "platform": self.platform.to_dict() if hasattr(self.platform, "to_dict") else self.platform.name,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }

class ContentController:
    """内容生产主控制器

    协调各个专业团队，完成从选题到发布的全流程内容生产。
    支持多话题批量处理、进度跟踪、人工反馈和生产流程控制。
    可配置全自动、全人工辅助或混合模式。
    """

    def __init__(self):
        """初始化内容生产控制器"""
        # 使用团队适配器替代直接的团队实例
        self.topic_team = TopicTeamAdapter()
        self.research_team = ResearchTeamAdapter()
        self.writing_team = WritingTeamAdapter()
        self.style_team = StyleTeamAdapter()
        self.review_team = ReviewTeamAdapter()

        self.production_results = []
        self.current_progress = None

        # 默认所有阶段都需要人工辅助
        self.auto_stages = {
            ProductionStage.TOPIC_DISCOVERY: False,
            ProductionStage.TOPIC_RESEARCH: False,
            ProductionStage.ARTICLE_WRITING: False,
            ProductionStage.STYLE_ADAPTATION: False,
            ProductionStage.ARTICLE_REVIEW: False
        }

    def set_auto_mode(self, mode: str, stages: Optional[List[ProductionStage]] = None):
        """设置自动化模式

        Args:
            mode: 模式，可选 'auto'(全自动), 'human'(全人工辅助), 'mixed'(混合模式)
            stages: 当mode为'mixed'时，指定自动执行的阶段列表
        """
        if mode == 'auto':
            # 全自动模式
            for stage in self.auto_stages:
                self.auto_stages[stage] = True
        elif mode == 'human':
            # 全人工辅助模式
            for stage in self.auto_stages:
                self.auto_stages[stage] = False
        elif mode == 'mixed' and stages:
            # 混合模式，只有指定的阶段自动执行
            for stage in self.auto_stages:
                self.auto_stages[stage] = stage in stages

        logger.info(f"已设置为{mode}模式，自动化阶段: {[s.value for s, v in self.auto_stages.items() if v]}")

    async def initialize(self, platform: Optional[Platform] = None):
        """初始化各个团队

        Args:
            platform: 目标平台，如果不提供则使用默认配置
        """
        # 初始化所有团队适配器
        await self.topic_team.initialize()
        await self.research_team.initialize()
        await self.writing_team.initialize()
        await self.style_team.initialize()
        await self.review_team.initialize()

    async def discover_topics(self, category: str, count: int = 3) -> List[Topic]:
        """发现话题

        Args:
            category: 话题类别
            count: 需要的话题数量

        Returns:
            List[Topic]: 发现的话题列表
        """
        logger.info(f"开始发现话题，类别: {category}，数量: {count}")
        is_auto = self.auto_stages[ProductionStage.TOPIC_DISCOVERY]
        logger.info(f"话题发现模式: {'自动' if is_auto else '人工辅助'}")

        # 更新进度
        self.current_progress.start_stage(ProductionStage.TOPIC_DISCOVERY, count)
        self.current_progress.total_topics = count

        try:
            # 使用话题团队适配器发现话题
            topics = await self.topic_team.generate_topics(
                category=category,
                count=count,
                options={"auto_mode": is_auto}
            )

            # 更新进度
            self.current_progress.update_progress(
                stage=ProductionStage.TOPIC_DISCOVERY,
                completed_items=len(topics),
                avg_score=sum(getattr(topic, "score", 0) for topic in topics) / len(topics) if topics else 0
            )
            self.current_progress.completed_topics = len(topics)
            self.current_progress.complete_stage(ProductionStage.TOPIC_DISCOVERY)

            logger.info(f"话题发现完成，发现 {len(topics)} 个话题")
            return topics

        except Exception as e:
            logger.error(f"话题发现出错: {str(e)}")
            self.current_progress.add_error(
                ProductionStage.TOPIC_DISCOVERY,
                str(e)
            )
            raise

    async def research_topic(self, topic: Union[str, Topic]) -> Dict:
        """研究单个话题

        Args:
            topic: 要研究的话题(字符串或Topic对象)

        Returns:
            Dict: 研究结果
        """
        # 处理不同类型的topic
        topic_title = topic if isinstance(topic, str) else getattr(topic, 'title', str(topic))
        logger.info(f"开始研究话题: {topic_title}")

        # 更新进度，标记研究阶段开始
        self.current_progress.start_stage(ProductionStage.TOPIC_RESEARCH, 1)

        try:
            # 使用研究团队适配器进行研究
            research_result = await self.research_team.research_topic(topic=topic, depth="medium")

            # 确保研究结果是字典格式，如果直接返回BasicResearch对象需要转换
            if not isinstance(research_result, dict) and hasattr(research_result, 'to_dict'):
                research_data = research_result.to_dict()
            else:
                research_data = research_result

            # 更新进度
            score = 0
            if isinstance(research_data, dict):
                score = research_data.get("score", 0)
            elif hasattr(research_result, 'score'):
                score = research_result.score

            self.current_progress.update_progress(
                stage=ProductionStage.TOPIC_RESEARCH,
                completed_items=1,
                avg_score=score
            )
            self.current_progress.complete_stage(ProductionStage.TOPIC_RESEARCH)

            return {
                "topic": topic,
                "research_result": research_result,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"研究话题出错: {str(e)}")
            self.current_progress.add_error(
                ProductionStage.TOPIC_RESEARCH,
                f"研究话题 '{topic_title}' 出错: {str(e)}"
            )
            return {
                "topic": topic,
                "error": str(e),
                "status": "failed"
            }

    async def write_article(self, article: Article, platform: Platform) -> Article:
        """根据文章主题和内容创建全文

        Args:
            article: 文章信息对象，包含标题、主题、初始内容等
            platform: 目标发布平台，决定了内容类型和受众定位

        Returns:
            Article: 创作完成的文章
        """
        if not article:
            logger.error("无法创建文章：缺少文章对象")
            raise ValueError("缺少文章对象")

        if not platform:
            logger.warning("未指定发布平台，使用默认平台")
            platform = get_default_platform()

        # 更新进度，标记写作阶段开始
        self.current_progress.start_stage(ProductionStage.ARTICLE_WRITING, 1)

        try:
            # 处理研究数据，支持不同类型
            research_data = article.metadata.get("research_data", {})

            # 如果是BasicResearch对象，转换为字典
            if hasattr(research_data, 'to_dict'):
                research_dict = research_data.to_dict()
            else:
                research_dict = research_data if isinstance(research_data, dict) else {"data": str(research_data)}

            # 获取话题对象，支持字符串或Topic对象
            topic = getattr(article, 'topic', None)
            if not topic and hasattr(article, 'topic_id') and article.topic_id:
                # 如果没有topic对象但有topic_id，创建一个临时topic对象
                topic = Topic(id=article.topic_id, title=article.title)
            elif not topic:
                # 创建一个简单的topic字典
                topic = {"title": article.title}

            # 使用写作团队适配器创作文章
            writing_result = await self.writing_team.write_content(
                topic=topic,
                research_data=research_dict,
                style=article.style.tone if hasattr(article, "style") and hasattr(article.style, "tone") else None
            )

            if writing_result and "content" in writing_result:
                article.content = writing_result["content"]
                # 不直接修改状态，让progress对象管理状态
                logger.info(f"文章写作完成: {article.title}")

                # 更新进度
                score = writing_result.get("score", 0) if isinstance(writing_result, dict) else 0
                self.current_progress.update_progress(
                    stage=ProductionStage.ARTICLE_WRITING,
                    completed_items=1,
                    avg_score=score
                )
                self.current_progress.complete_stage(ProductionStage.ARTICLE_WRITING)

                return article
            else:
                logger.warning("写作结果不完整")

                # 更新进度，标记错误
                self.current_progress.add_error(
                    ProductionStage.ARTICLE_WRITING,
                    "写作结果不完整"
                )

                return article

        except Exception as e:
            logger.error(f"写作过程发生错误: {str(e)}", exc_info=True)

            # 更新进度，标记错误
            self.current_progress.add_error(
                ProductionStage.ARTICLE_WRITING,
                f"写作过程发生错误: {str(e)}"
            )

            return article

    async def adapt_style(self, article: Article, style: str, platform: Optional[Platform] = None) -> Article:
        """适配单个文章风格

        Args:
            article: 原始文章
            style: 指定的写作风格
            platform: 可选的目标平台，用于额外的平台特定约束

        Returns:
            Article: 风格适配后的文章
        """
        logger.info(f"开始适配文章风格: {article.title}, 风格: {style}")

        # 更新进度，标记风格适配阶段开始
        self.current_progress.start_stage(ProductionStage.STYLE_ADAPTATION, 1)

        try:
            # 获取话题对象，支持字符串或Topic对象
            topic = getattr(article, 'topic', None)
            if not topic and hasattr(article, 'topic_id') and article.topic_id:
                # 如果没有topic对象但有topic_id，创建一个临时topic对象
                topic = Topic(id=article.topic_id, title=article.title)
            elif not topic:
                # 创建一个简单的topic字典
                topic = {"title": article.title}

            # 使用风格团队适配器调整文章风格
            styled_content = await self.style_team.apply_style(
                topic=topic,
                content=article.content,
                style=style
            )

            if styled_content:
                article.content = styled_content
                if hasattr(article, 'style') and hasattr(article.style, 'tone'):
                    article.style.tone = style
                # 不直接修改状态，让progress对象管理状态

            logger.info(f"文章风格适配完成: {article.title}")

            # 更新进度
            self.current_progress.update_progress(
                stage=ProductionStage.STYLE_ADAPTATION,
                completed_items=1,
                avg_score=1.0 # 暂时缺少评分机制
            )
            self.current_progress.complete_stage(ProductionStage.STYLE_ADAPTATION)

            return article

        except Exception as e:
            logger.error(f"适配文章风格 '{article.title}' 失败: {str(e)}")

            # 更新进度，标记错误
            self.current_progress.add_error(
                ProductionStage.STYLE_ADAPTATION,
                f"适配文章风格失败: {str(e)}"
            )

            raise

    async def review_article(self, article: Article) -> Dict:
        """审核单个文章

        Args:
            article: 要审核的文章

        Returns:
            Dict: 审核结果
        """
        logger.info(f"开始审核文章: {article.title}")

        # 更新进度，标记审核阶段开始
        self.current_progress.start_stage(ProductionStage.ARTICLE_REVIEW, 1)

        try:
            # 获取话题对象，支持字符串或Topic对象
            topic = getattr(article, 'topic', None)
            if not topic and hasattr(article, 'topic_id') and article.topic_id:
                # 如果没有topic对象但有topic_id，创建一个临时topic对象
                topic = Topic(id=article.topic_id, title=article.title)
            elif not topic:
                # 创建一个简单的topic字典
                topic = {"title": article.title}

            # 使用审核团队适配器审核文章
            review_result = await self.review_team.review_content(
                topic=topic,
                content=article.content
            )

            logger.info(f"文章审核完成: {article.title}")

            # 更新进度
            score = review_result.get("score", 0) if isinstance(review_result, dict) else 0
            self.current_progress.update_progress(
                stage=ProductionStage.ARTICLE_REVIEW,
                completed_items=1,
                avg_score=score
            )
            self.current_progress.complete_stage(ProductionStage.ARTICLE_REVIEW)

            return review_result

        except Exception as e:
            logger.error(f"审核文章 '{article.title}' 失败: {str(e)}")

            # 更新进度，标记错误
            self.current_progress.add_error(
                ProductionStage.ARTICLE_REVIEW,
                f"审核文章失败: {str(e)}"
            )

            raise

    async def produce_content(
        self,
        category: Optional[str] = None,
        topic: Optional[Union[str, Topic]] = None,
        style: Optional[str] = None,
        content_type: Optional[str] = None,
        platform: Optional[Platform] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """生产内容的完整流程

        从选题到发布的完整流程，支持单篇和多篇模式，可配置各阶段的自动化程度。

        Args:
            category: 话题类别
            topic: 指定话题(字符串或Topic对象)，如不提供则自动发现
            style: 指定的写作风格
            content_type: 内容类型
            platform: 目标平台，如不提供则使用默认平台
            options: 其他选项

        Returns:
            Dict: 生产结果
        """
        # 从 options 中提取参数
        options = options or {}
        topic_count = options.get("topic_count", 1)
        mode = options.get("mode", "human")
        auto_stages = options.get("auto_stages", None)

        # 设置自动化模式
        self.set_auto_mode(mode, auto_stages)

        # 创建文章实例
        article = Article(
            id=str(uuid.uuid4()),
            topic_id="",  # 稍后更新
            title="",     # 稍后更新
            summary=""    # 稍后更新
        )

        # 初始化进度跟踪
        production_id = str(uuid.uuid4())
        self.current_progress = ProductionProgress(production_id, article=article)

        # 初始化结果数据
        result = {
            "status": "success",
            "production_id": production_id,
            "start_time": datetime.now().isoformat(),
            "process": "topic_discovery -> research -> writing -> style -> review",
            "stages": {},
            "mode": mode
        }

        try:
            # 初始化各团队
            await self.initialize(platform)

            # 确保平台参数
            platform = platform or get_default_platform()

            # 1. 话题阶段
            if not topic:
                topics = await self.discover_topics(category, topic_count)
                topic = topics[0] if topics else None
                if not topic:
                    raise ValueError("未能获取有效话题")

            # 获取topic的基本信息
            topic_id = None
            topic_title = None
            if isinstance(topic, str):
                topic_title = topic
            else:
                # 假设是Topic对象
                topic_id = getattr(topic, 'id', None)
                topic_title = getattr(topic, 'title', str(topic))

            # 更新文章基本信息
            article.topic_id = topic_id or ""
            article.title = topic_title or ""
            article.summary = getattr(topic, "summary", "") if not isinstance(topic, str) else ""

            # 将topic转换为字典存储
            topic_dict = topic.to_dict() if hasattr(topic, "to_dict") else topic
            if isinstance(topic_dict, str):
                topic_dict = {"title": topic_dict}

            result["stages"]["topic"] = {
                "topic": topic_dict,
                "completed_at": datetime.now().isoformat()
            }

            # 2. 研究阶段
            research_result = await self.research_topic(topic)

            # 确保研究结果是一个字典
            research_data = research_result
            if isinstance(research_result, dict) and "research_result" in research_result:
                research_data = research_result["research_result"]

            # 转换BasicResearch对象为字典
            if hasattr(research_data, 'to_dict'):
                research_dict = research_data.to_dict()
            else:
                research_dict = research_data if isinstance(research_data, dict) else {"data": str(research_data)}

            result["stages"]["research"] = {
                "result": research_dict,
                "completed_at": datetime.now().isoformat()
            }

            # 3. 写作阶段
            article.metadata = {"research_data": research_data}
            article = await self.write_article(article, platform)

            article_dict = article.to_dict() if hasattr(article, "to_dict") else article
            result["stages"]["writing"] = {
                "article": article_dict,
                "completed_at": datetime.now().isoformat()
            }

            # 4. 风格阶段
            if style:
                article = await self.adapt_style(article, style, platform)
                result["stages"]["style"] = {
                    "style": style,
                    "completed_at": datetime.now().isoformat()
                }

            # 5. 审核阶段
            review_result = await self.review_article(article)
            result["stages"]["review"] = {
                "result": review_result,
                "completed_at": datetime.now().isoformat()
            }

            # 保存生产结果
            production_result = ContentProductionResult(
                topic=topic,
                research_data=research_data,
                article=article,
                review_data=review_result,
                platform=platform
            )
            production_result.status = "completed"
            self.production_results.append(production_result)

            # 完成生产
            self.current_progress.complete()  # 这会自动把文章状态设置为"completed"并保存到数据库
            final_article_dict = article.to_dict() if hasattr(article, "to_dict") else article
            result["final_article"] = final_article_dict
            result["end_time"] = datetime.now().isoformat()
            result["status"] = "completed"
            result["progress"] = self.current_progress.get_summary()  # 添加进度信息到结果

            logger.info(f"内容生产完成，ID: {production_id}")
            return result

        except Exception as e:
            logger.error(f"内容生产失败: {str(e)}")
            self.current_progress.fail()  # 这会自动把文章状态设置为"failed"并保存到数据库
            result["status"] = "failed"
            result["error"] = str(e)
            result["end_time"] = datetime.now().isoformat()
            result["progress"] = self.current_progress.get_summary()  # 添加进度信息到结果
            raise RuntimeError(f"内容生产失败: {str(e)}")  # 使用更明确的异常类型

    def get_progress(self) -> Dict:
        """获取当前进度

        Returns:
            Dict: 当前生产进度信息，包括各阶段状态和统计数据
        """
        if self.current_progress:
            progress_data = self.current_progress.get_summary()

            # 添加额外的元信息
            if hasattr(self.current_progress, 'article') and self.current_progress.article:
                article = self.current_progress.article
                progress_data["article_info"] = {
                    "id": article.id,
                    "title": article.title,
                    "status": article.status if hasattr(article, 'status') else None
                }

            return progress_data
        return {"status": "no_active_production"}

    def pause_production(self) -> Dict:
        """暂停生产

        Returns:
            Dict: 当前进度信息
        """
        if self.current_progress:
            self.current_progress.pause()  # 这会自动把文章状态设置为"paused"并保存到数据库
            logger.info("已暂停生产")
            return self.current_progress.get_summary()
        return {"status": "no_active_production"}

    def resume_production(self) -> Dict:
        """恢复生产

        Returns:
            Dict: 当前进度信息
        """
        if self.current_progress:
            self.current_progress.resume()  # 这会自动更新文章状态并保存到数据库
            logger.info("已恢复生产")
            return self.current_progress.get_summary()
        return {"status": "no_active_production"}
