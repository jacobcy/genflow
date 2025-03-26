"""内容生产主控制器

该模块实现了内容生产的总体协调流程，整合各个专业团队完成从选题到发布的全流程。
"""

from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
import asyncio
import uuid
import logging

from core.models.topic import Topic
from core.models.article import Article
from core.models.platform import Platform, get_default_platform
from core.models.progress import ProductionProgress, ProductionStage, StageStatus
from core.agents.topic_crew import TopicCrew
from core.agents.research_crew import ResearchCrew
from core.agents.writing_crew import WritingCrew
from core.agents.review_crew import ReviewCrew
from core.agents.style_crew import StyleCrew
from core.tools.style_tools import StyleAdapter
from core.constants.platform_categories import get_platform_categories
from core.constants.content_types import get_content_type_from_categories

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
        self.topic_crew = TopicCrew()
        self.research_crew = ResearchCrew()
        self.writing_crew = WritingCrew()
        self.style_crew = StyleCrew()
        self.review_crew = ReviewCrew()
        self.style_adapter = StyleAdapter.get_instance()
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
        await self.topic_crew.initialize()
        await self.research_crew.initialize()
        await self.writing_crew.initialize()
        await self.style_crew.initialize(platform)
        await self.review_crew.initialize()

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
            # 发现话题
            topics = await self.topic_crew.run_workflow(category=category, count=count, auto_mode=is_auto)

            # 解析话题数据
            if isinstance(topics, dict) and "topics" in topics:
                # 从结果报告中提取话题列表
                topic_list = []
                for topic_data in topics.get("topics", []):
                    if isinstance(topic_data, dict) and topic_data.get("status") == "selected":
                        try:
                            # 构建话题对象
                            topic = Topic(**topic_data)
                            topic_list.append(topic)
                        except Exception as e:
                            logger.error(f"解析话题数据出错: {str(e)}")

                # 确保我们有足够的话题
                if not topic_list:
                    logger.warning("未找到选定的话题，使用所有话题")
                    for topic_data in topics.get("topics", [])[:count]:
                        if isinstance(topic_data, dict):
                            try:
                                topic = Topic(**topic_data)
                                topic.status = "approved"
                                topic_list.append(topic)
                            except Exception as e:
                                logger.error(f"解析备选话题数据出错: {str(e)}")
            else:
                # 假设topics已经是Topic对象列表
                topic_list = topics if isinstance(topics, list) else []

            # 更新进度
            self.current_progress.update_progress(
                stage=ProductionStage.TOPIC_DISCOVERY,
                completed_items=len(topic_list),
                avg_score=sum(getattr(topic, "score", 0) for topic in topic_list) / len(topic_list) if topic_list else 0
            )
            self.current_progress.completed_topics = len(topic_list)
            self.current_progress.complete_stage(ProductionStage.TOPIC_DISCOVERY)

            logger.info(f"话题发现完成，发现 {len(topic_list)} 个话题")
            return topic_list

        except Exception as e:
            logger.error(f"话题发现出错: {str(e)}")
            self.current_progress.add_error(
                ProductionStage.TOPIC_DISCOVERY,
                str(e)
            )
            raise

    async def research_topic(self, topic: Topic) -> Dict:
        """研究单个话题

        Args:
            topic: 要研究的话题

        Returns:
            Dict: 研究结果
        """
        logger.info(f"开始研究话题: {topic.title}")

        try:
            # 获取内容类型（如果存在）
            content_type = None
            if hasattr(topic, "metadata") and isinstance(topic.metadata, dict):
                content_type = topic.metadata.get("content_type")

            # 如果没有指定内容类型，但有平台信息，则根据平台分类确定内容类型
            if not content_type and hasattr(topic, "platform") and topic.platform:
                # 获取平台分类
                platform_categories = get_platform_categories(topic.platform)
                if platform_categories:
                    # 根据平台分类确定内容类型
                    content_type = get_content_type_from_categories(platform_categories)
                    logger.info(f"根据平台 {topic.platform} 的分类 {platform_categories} 自动确定内容类型: {content_type}")

                    # 更新topic元数据
                    if not hasattr(topic, "metadata") or not topic.metadata:
                        topic.metadata = {}
                    topic.metadata["content_type"] = content_type

            # 进行研究
            research_result = await self.research_crew.research_topic(
                topic.title,
                content_type=content_type
            )

            # 返回结果
            return {
                "topic": topic,
                "research_result": research_result,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"研究话题出错: {str(e)}")
            self.current_progress.add_error(
                ProductionStage.TOPIC_RESEARCH,
                f"研究话题 '{topic.title}' 出错: {str(e)}"
            )
            return {
                "topic": topic,
                "error": str(e),
                "status": "failed"
            }

    async def research_topics(self, topics: List[Topic]) -> List[Dict]:
        """研究多个话题

        Args:
            topics: 要研究的话题列表

        Returns:
            List[Dict]: 研究结果列表
        """
        logger.info(f"开始研究 {len(topics)} 个话题")
        is_auto = self.auto_stages[ProductionStage.TOPIC_RESEARCH]
        logger.info(f"话题研究模式: {'自动' if is_auto else '人工辅助'}")

        # 更新进度
        self.current_progress.start_stage(ProductionStage.TOPIC_RESEARCH, len(topics))

        if not topics:
            logger.warning("没有话题需要研究")
            self.current_progress.complete_stage(ProductionStage.TOPIC_RESEARCH)
            return []

        try:
            # 用于存储研究结果
            research_results = []

            # 如果是自动模式，并行研究所有话题
            if is_auto:
                tasks = []
                for topic in topics:
                    task = self.research_topic(topic)
                    tasks.append(task)

                # 并行执行所有研究任务
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # 处理结果
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"研究话题 '{topics[i].title}' 出错: {str(result)}")
                        self.current_progress.add_error(
                            ProductionStage.TOPIC_RESEARCH,
                            f"研究话题 '{topics[i].title}' 出错: {str(result)}"
                        )
                        research_results.append({
                            "topic": topics[i],
                            "error": str(result),
                            "status": "failed"
                        })
                    else:
                        research_results.append(result)

                        # 更新进度
                        self.current_progress.update_progress(
                            stage=ProductionStage.TOPIC_RESEARCH,
                            completed_items=len(research_results)
                        )

            # 如果是人工辅助模式，串行研究话题
            else:
                for i, topic in enumerate(topics):
                    result = await self.research_topic(topic)
                    research_results.append(result)

                    # 更新进度
                    self.current_progress.update_progress(
                        stage=ProductionStage.TOPIC_RESEARCH,
                        completed_items=i+1
                    )

            # 完成阶段
            self.current_progress.complete_stage(ProductionStage.TOPIC_RESEARCH)

            logger.info(f"完成 {len(research_results)} 个话题的研究")
            return research_results

        except Exception as e:
            logger.error(f"研究话题出错: {str(e)}")
            self.current_progress.add_error(
                ProductionStage.TOPIC_RESEARCH,
                str(e)
            )
            raise

    async def write_article(self, article: Article, platform: Platform) -> Article:
        """根据文章主题和内容创建全文

        Args:
            article: 文章信息对象，包含标题、主题、初始内容等
            platform: 目标发布平台，决定了内容类型和受众定位（注意：不涉及风格调整）

        Returns:
            Article: 创作完成的文章（不包含风格调整）
        """
        if not article:
            logger.error("无法创建文章：缺少文章对象")
            raise ValueError("缺少文章对象")

        if not platform:
            logger.warning("未指定发布平台，使用默认平台")
            platform = get_default_platform()

        try:
            # 获取content_type
            content_type = None
            if hasattr(article, "metadata") and isinstance(article.metadata, dict):
                content_type = article.metadata.get("content_type")

            # 如果没有指定内容类型，则根据平台分类确定内容类型
            if not content_type and platform:
                # 获取平台分类
                platform_categories = get_platform_categories(platform.name)
                if platform_categories:
                    # 根据平台分类确定内容类型
                    content_type = get_content_type_from_categories(platform_categories)
                    logger.info(f"根据平台 {platform.name} 的分类 {platform_categories} 自动确定内容类型: {content_type}")

                    # 更新article元数据
                    if not hasattr(article, "metadata") or not article.metadata:
                        article.metadata = {}
                    article.metadata["content_type"] = content_type

            logger.info(f"开始写作文章 '{article.title}'，平台: {platform.name}，内容类型: {content_type or '未指定'}")
            logger.info("注意：写作阶段仅专注于内容质量和结构，不考虑风格调整")

            # 初始化写作团队
            if not self.writing_crew:
                verbose = getattr(self, 'verbose', True)  # 如果self.verbose不存在，默认为True
                self.writing_crew = WritingCrew(verbose=verbose)

            # 执行写作流程，传递content_type参数
            writing_result = await self.writing_crew.write_article(
                article=article,
                platform=platform,
                content_type=content_type
            )

            # 处理写作结果
            if writing_result and writing_result.article:
                logger.info(f"文章写作完成: {writing_result.article.title}（内容质量和结构已完成，风格将在后续阶段调整）")
                return writing_result.article
            else:
                logger.warning("写作结果不完整，返回原始文章")
                return article

        except Exception as e:
            logger.error(f"写作过程发生错误: {str(e)}", exc_info=True)
            return article

    async def write_articles(
        self,
        research_results: List[Dict],
        platform: Platform
    ) -> List[Dict]:
        """批量写作文章

        Args:
            research_results: 研究结果列表
            platform: 目标平台

        Returns:
            List[Dict]: 写作结果列表
        """
        logger.info(f"开始批量写作文章，数量: {len(research_results)}")
        is_auto = self.auto_stages[ProductionStage.ARTICLE_WRITING]
        logger.info(f"文章写作模式: {'自动' if is_auto else '人工辅助'}")

        # 更新进度
        self.current_progress.start_stage(
            ProductionStage.ARTICLE_WRITING,
            len(research_results)
        )

        writing_results = []
        completed_count = 0
        total_score = 0
        error_count = 0

        for result in research_results:
            try:
                logger.info(f"写作文章: {result['article_outline'].title}")

                # 进行写作
                writing_result = await self.write_article(
                    result["article_outline"],
                    platform
                )

                # 获取人工反馈或自动评估
                if not is_auto:
                    writing_result = self.writing_crew.get_human_feedback(writing_result)
                    feedback_score = writing_result.human_feedback["average_score"]
                else:
                    # 自动评估写作结果
                    feedback_score = self.writing_crew.auto_evaluate_article(writing_result)
                    writing_result.auto_feedback = {"average_score": feedback_score}

                # 更新统计
                completed_count += 1
                total_score += feedback_score

                # 如果评分达标，更新文章
                if feedback_score >= 0.7:
                    article = self.writing_crew.update_article(writing_result)
                    writing_results.append({
                        "topic": result["topic"],
                        "research_result": result["research_result"],
                        "writing_result": writing_result,
                        "article": article
                    })

            except Exception as e:
                error_count += 1
                logger.error(f"写作文章失败: {str(e)}")
                self.current_progress.add_error(
                    ProductionStage.ARTICLE_WRITING,
                    f"写作文章 '{result['article_outline'].title}' 失败: {str(e)}"
                )

            # 更新进度
            self.current_progress.update_progress(
                stage=ProductionStage.ARTICLE_WRITING,
                completed_items=completed_count,
                avg_score=total_score / completed_count if completed_count > 0 else 0,
                error_count=error_count
            )

        self.current_progress.complete_stage(ProductionStage.ARTICLE_WRITING)
        logger.info(f"文章写作阶段完成，通过 {len(writing_results)} 个文章")
        return writing_results

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

        try:
            # 进行风格适配，传递style参数
            style_result = await self.style_crew.adapt_style(article, style, platform)
            logger.info(f"文章风格适配完成: {article.title}")
            return style_result.final_article

        except Exception as e:
            logger.error(f"适配文章风格 '{article.title}' 失败: {str(e)}")
            raise

    async def adapt_articles(
        self,
        writing_results: List[Dict],
        style: str,
        platform: Optional[Platform] = None
    ) -> List[Dict]:
        """批量适配文章风格

        Args:
            writing_results: 写作结果列表
            style: 指定的写作风格
            platform: 可选的目标平台，用于额外的平台特定约束

        Returns:
            List[Dict]: 适配结果列表
        """
        logger.info(f"开始批量适配文章风格，数量: {len(writing_results)}, 风格: {style}")
        is_auto = self.auto_stages[ProductionStage.STYLE_ADAPTATION]
        logger.info(f"风格适配模式: {'自动' if is_auto else '人工辅助'}")

        # 更新进度
        self.current_progress.start_stage(
            ProductionStage.STYLE_ADAPTATION,
            len(writing_results)
        )

        adaptation_results = []
        completed_count = 0
        total_score = 0
        error_count = 0

        for result in writing_results:
            try:
                logger.info(f"适配文章: {result['article'].title}")

                # 进行风格适配，传递style参数
                adapted_article = await self.adapt_style(result["article"], style, platform)

                # 获取人工反馈或自动评估
                if not is_auto:
                    feedback_score = self.style_crew.get_human_feedback(adapted_article, style, platform)
                else:
                    # 自动评估适配效果
                    feedback_score = self.style_crew.auto_evaluate_style(adapted_article, style, platform)

                # 更新统计
                completed_count += 1
                total_score += feedback_score

                # 如果评分达标,保存适配结果
                if feedback_score >= 0.7:
                    adaptation_results.append({
                        "topic": result["topic"],
                        "research_result": result["research_result"],
                        "writing_result": result["writing_result"],
                        "article": adapted_article
                    })

            except Exception as e:
                error_count += 1
                logger.error(f"适配文章风格失败: {str(e)}")
                self.current_progress.add_error(
                    ProductionStage.STYLE_ADAPTATION,
                    f"适配文章 '{result['article'].title}' 失败: {str(e)}"
                )

            # 更新进度
            self.current_progress.update_progress(
                stage=ProductionStage.STYLE_ADAPTATION,
                completed_items=completed_count,
                avg_score=total_score / completed_count if completed_count > 0 else 0,
                error_count=error_count
            )

        self.current_progress.complete_stage(ProductionStage.STYLE_ADAPTATION)
        logger.info(f"文章风格适配阶段完成，通过 {len(adaptation_results)} 个文章")
        return adaptation_results

    async def review_article(self, article: Article) -> Dict:
        """审核单个文章

        Args:
            article: 要审核的文章

        Returns:
            Dict: 审核结果
        """
        logger.info(f"开始审核文章: {article.title}")

        try:
            # 进行审核
            review_result = await self.review_crew.review_article(article)
            logger.info(f"文章审核完成: {article.title}")
            return review_result

        except Exception as e:
            logger.error(f"审核文章 '{article.title}' 失败: {str(e)}")
            raise

    async def review_articles(
        self,
        writing_results: List[Dict],
        platform: Platform
    ) -> List[Dict]:
        """批量审核文章

        Args:
            writing_results: 写作结果列表
            platform: 目标平台

        Returns:
            List[Dict]: 审核结果列表
        """
        logger.info(f"开始批量审核文章，数量: {len(writing_results)}")
        is_auto = self.auto_stages[ProductionStage.ARTICLE_REVIEW]
        logger.info(f"文章审核模式: {'自动' if is_auto else '人工辅助'}")

        # 更新进度
        self.current_progress.start_stage(
            ProductionStage.ARTICLE_REVIEW,
            len(writing_results)
        )

        review_results = []
        completed_count = 0
        total_score = 0
        error_count = 0

        for result in writing_results:
            try:
                logger.info(f"审核文章: {result['article'].title}")

                # 进行审核
                review_result = await self.review_article(result["article"])

                # 获取人工反馈或自动评估
                if not is_auto:
                    review_result = self.review_crew.get_human_feedback(review_result)
                    feedback_score = review_result.human_feedback["average_score"]
                else:
                    # 自动评估审核结果
                    feedback_score = self.review_crew.auto_evaluate_review(review_result)
                    review_result.auto_feedback = {"average_score": feedback_score}

                # 更新统计
                completed_count += 1
                total_score += feedback_score

                # 如果评分达标，更新文章状态
                if feedback_score >= 0.7:
                    article = self.review_crew.update_article_status(review_result)
                    if article.status == "approved":
                        review_results.append({
                            "topic": result["topic"],
                            "research_result": result["research_result"],
                            "writing_result": result["writing_result"],
                            "review_result": review_result,
                            "article": article
                        })

            except Exception as e:
                error_count += 1
                logger.error(f"审核文章失败: {str(e)}")
                self.current_progress.add_error(
                    ProductionStage.ARTICLE_REVIEW,
                    f"审核文章 '{result['article'].title}' 失败: {str(e)}"
                )

            # 更新进度
            self.current_progress.update_progress(
                stage=ProductionStage.ARTICLE_REVIEW,
                completed_items=completed_count,
                avg_score=total_score / completed_count if completed_count > 0 else 0,
                error_count=error_count
            )

        self.current_progress.complete_stage(ProductionStage.ARTICLE_REVIEW)
        logger.info(f"文章审核阶段完成，通过 {len(review_results)} 个文章")
        return review_results

    async def produce_content(
        self,
        topic: Optional[Topic] = None,
        category: Optional[str] = None,
        platform: Optional[Platform] = None,
        topic_count: int = 1,
        progress_callback: Optional[Callable] = None,
        mode: str = 'human',
        auto_stages: Optional[List[str]] = None,
        style: Optional[str] = None
    ) -> Dict:
        """生产内容的完整流程

        从选题到发布的完整流程，支持单篇和多篇模式，可配置各阶段的自动化程度。

        Args:
            topic: 指定话题，如不提供则自动发现
            category: 话题类别，当topic不提供时使用
            platform: 目标平台，如不提供则使用默认平台
            topic_count: 话题数量，当topic不提供时使用
            progress_callback: 进度回调函数
            mode: 生产模式，可选 'auto'(全自动), 'human'(全人工辅助), 'mixed'(混合模式)
            auto_stages: 当mode为'mixed'时，指定自动执行的阶段列表
            style: 指定的写作风格，如不提供则尝试从topic或platform中获取

        Returns:
            Dict: 生产结果，包含文章和各阶段数据
        """
        # 设置自动化模式
        if auto_stages and mode == 'mixed':
            stage_map = {
                "topic_discovery": ProductionStage.TOPIC_DISCOVERY,
                "topic_research": ProductionStage.TOPIC_RESEARCH,
                "article_writing": ProductionStage.ARTICLE_WRITING,
                "style_adaptation": ProductionStage.STYLE_ADAPTATION,
                "article_review": ProductionStage.ARTICLE_REVIEW
            }
            # 转换字符串阶段名为枚举
            auto_stages_enum = [stage_map[s] for s in auto_stages if s in stage_map]
            self.set_auto_mode(mode, auto_stages_enum)
        else:
            self.set_auto_mode(mode)

        # 初始化进度跟踪
        production_id = str(uuid.uuid4())
        self.current_progress = ProductionProgress(production_id)

        # 初始化结果数据
        result = {
            "status": "success",
            "production_id": production_id,
            "start_time": datetime.now().isoformat(),
            "process": "topic_discovery -> research -> writing -> style -> review",
            "stages": {},
            "mode": mode
        }

        # 记录自动化阶段
        result["auto_stages"] = [s.value for s, v in self.auto_stages.items() if v]

        try:
            # 初始化各团队
            await self.initialize(platform)

            # 确保平台参数
            if not platform:
                platform = get_default_platform()

            # 获取style参数
            # 1. 如果直接提供了style参数，使用它
            # 2. 尝试从topic.metadata中获取
            # 3. 尝试从platform中获取一个默认风格
            # 4. 使用"default"作为默认值
            used_style = style
            if not used_style and topic and hasattr(topic, "metadata") and isinstance(topic.metadata, dict):
                used_style = topic.metadata.get("style")
            if not used_style and platform and hasattr(platform, "style_type"):
                used_style = platform.style_type
            if not used_style:
                used_style = "default"

            logger.info(f"使用风格: {used_style}")

            # 单篇模式: 处理单个话题
            if topic:
                logger.info(f"开始处理单个话题: {topic.title}")

                # 阶段1: 话题准备
                self.current_progress.start_stage(ProductionStage.TOPIC_DISCOVERY, 1)
                self.current_progress.complete_stage(ProductionStage.TOPIC_DISCOVERY)
                result["stages"]["topic_discovery"] = {
                    "topic": topic.to_dict() if hasattr(topic, "to_dict") else {"title": topic.title},
                    "completed_at": datetime.now().isoformat()
                }

                # 阶段2: 研究
                self.current_progress.start_stage(ProductionStage.TOPIC_RESEARCH, 1)
                research_result = await self.research_topic(topic)
                self.current_progress.complete_stage(ProductionStage.TOPIC_RESEARCH)
                result["stages"]["research"] = {
                    "result_summary": {
                        "key_findings_count": len(research_result.get("key_findings", [])),
                        "sources_count": len(research_result.get("sources", [])),
                    },
                    "completed_at": datetime.now().isoformat()
                }

                # 阶段3: 写作
                self.current_progress.start_stage(ProductionStage.ARTICLE_WRITING, 1)
                article = await self.write_article(topic, platform)
                self.current_progress.complete_stage(ProductionStage.ARTICLE_WRITING)
                result["stages"]["writing"] = {
                    "article_summary": {
                        "title": article.title,
                        "word_count": article.word_count,
                        "sections_count": len(article.sections)
                    },
                    "completed_at": datetime.now().isoformat()
                }

                # 阶段4: 风格适配 - 使用提取的style参数
                self.current_progress.start_stage(ProductionStage.STYLE_ADAPTATION, 1)
                styled_article = await self.adapt_style(article, used_style, platform)
                self.current_progress.complete_stage(ProductionStage.STYLE_ADAPTATION)
                result["stages"]["style_adaptation"] = {
                    "style": used_style,
                    "platform": platform.name if platform else None,
                    "changes_summary": {
                        "tone_adjusted": True,
                        "format_adjusted": True,
                        "structure_adjusted": True
                    },
                    "completed_at": datetime.now().isoformat()
                }

                # 阶段5: 审核
                self.current_progress.start_stage(ProductionStage.ARTICLE_REVIEW, 1)
                review_result = await self.review_article(styled_article)
                self.current_progress.complete_stage(ProductionStage.ARTICLE_REVIEW)
                result["stages"]["review"] = {
                    "score": review_result.get("overall_score", 0),
                    "passed": review_result.get("passed", False),
                    "improvement_suggestions": review_result.get("improvement_suggestions", []),
                    "completed_at": datetime.now().isoformat()
                }

                # 保存生产结果
                production_result = ContentProductionResult(
                    topic=topic,
                    research_data=research_result,
                    article=styled_article,
                    review_data=review_result,
                    platform=platform
                )
                production_result.status = "completed"
                self.production_results.append(production_result)

                # 加入最终结果
                result["final_article"] = styled_article.to_dict() if hasattr(styled_article, "to_dict") else styled_article
                result["review_result"] = review_result
                result["style"] = used_style

            # 多篇模式: 批量处理多个话题
            else:
                logger.info(f"开始批量生产内容，类别: {category}，数量: {topic_count}，模式: {mode}，风格: {used_style}")

                # 阶段1: 话题发现
                topics = await self.discover_topics(category or "technology", topic_count)
                if not topics:
                    raise ValueError(f"未能在类别 {category} 中发现合适话题")

                result["stages"]["topic_discovery"] = {
                    "topics": [topic.to_dict() if hasattr(topic, "to_dict") else {"title": topic.title} for topic in topics],
                    "completed_at": datetime.now().isoformat()
                }

                # 阶段2: 话题研究
                research_results = await self.research_topics(topics)
                if not research_results:
                    raise ValueError("话题研究未通过")

                result["stages"]["research"] = {
                    "results_count": len(research_results),
                    "completed_at": datetime.now().isoformat()
                }

                # 阶段3: 文章写作
                writing_results = await self.write_articles(research_results, platform)
                if not writing_results:
                    raise ValueError("文章写作未通过")

                result["stages"]["writing"] = {
                    "articles_count": len(writing_results),
                    "completed_at": datetime.now().isoformat()
                }

                # 阶段4: 风格适配 - 使用提取的style参数
                adaptation_results = await self.adapt_articles(writing_results, used_style, platform)
                if not adaptation_results:
                    raise ValueError("风格适配未通过")

                result["stages"]["style_adaptation"] = {
                    "style": used_style,
                    "adapted_count": len(adaptation_results),
                    "completed_at": datetime.now().isoformat()
                }

                # 阶段5: 文章审核
                review_results = await self.review_articles(adaptation_results, platform)
                if not review_results:
                    raise ValueError("文章审核未通过")

                result["stages"]["review"] = {
                    "reviewed_count": len(review_results),
                    "passed_count": len([r for r in review_results if r["article"].status == "approved"]),
                    "completed_at": datetime.now().isoformat()
                }

                # 保存生产结果
                production_results = []
                for res in review_results:
                    prod_result = ContentProductionResult(
                        topic=res["topic"],
                        research_data=res["research_result"].__dict__,
                        article=res["article"],
                        review_data=res["review_result"].__dict__,
                        platform=platform
                    )
                    prod_result.status = "completed"
                    self.production_results.append(prod_result)
                    production_results.append(prod_result)

                # 加入最终结果
                result["final_articles"] = [
                    res["article"].to_dict() if hasattr(res["article"], "to_dict") else res["article"]
                    for res in review_results
                ]
                result["review_results"] = [
                    res["review_result"].__dict__ if hasattr(res["review_result"], "__dict__") else res["review_result"]
                    for res in review_results
                ]
                result["style"] = used_style

            # 完成生产
            self.current_progress.complete()

            # 最终结果
            result["end_time"] = datetime.now().isoformat()
            result["duration_seconds"] = (datetime.fromisoformat(result["end_time"]) -
                                         datetime.fromisoformat(result["start_time"])).total_seconds()
            result["progress_summary"] = self.current_progress.get_summary()

            logger.info(f"内容生产完成，状态: {result['status']}, 模式: {mode}, 风格: {used_style}")
            return result

        except Exception as e:
            logger.error(f"内容生产过程出错: {str(e)}")
            self.current_progress.fail()

            result["status"] = "error"
            result["error"] = str(e)
            result["end_time"] = datetime.now().isoformat()
            result["duration_seconds"] = (datetime.fromisoformat(result["end_time"]) -
                                         datetime.fromisoformat(result["start_time"])).total_seconds()

            # 记录中断时的阶段
            if self.current_progress and self.current_progress.current_stage:
                result["interrupted_stage"] = self.current_progress.current_stage.value

            # 添加错误日志
            result["error_logs"] = self.current_progress.error_logs if self.current_progress else []

            return result

    def get_progress(self) -> Dict:
        """获取当前进度

        Returns:
            Dict: 进度摘要
        """
        if self.current_progress:
            return self.current_progress.get_summary()
        return {}

    def pause_production(self):
        """暂停生产"""
        if self.current_progress:
            self.current_progress.pause()
            logger.info("已暂停生产")

    def resume_production(self):
        """恢复生产"""
        if self.current_progress:
            self.current_progress.resume()
            logger.info("已恢复生产")

# 使用示例
async def main():
    """主函数"""
    try:
        # 创建一个示例平台
        platform = Platform(
            id="zhihu",
            name="知乎",
            url="https://www.zhihu.com",
            content_rules={
                "min_words": 1000,
                "max_words": 5000,
                "allowed_tags": ["Python", "编程", "技术"]
            }
        )

        # 创建控制器
        controller = ContentController()

        # 生产内容
        results = await controller.produce_content(
            category="技术",
            platform=platform,
            topic_count=1
        )

        # 打印进度摘要
        progress = controller.get_progress()
        print("\n=== 生产进度摘要 ===")
        print(f"生产ID: {progress['production_id']}")
        print(f"当前阶段: {progress['current_stage']}")
        print(f"阶段状态: {progress['stage_status']}")
        print(f"总进度: {progress['progress_percentage']}%")
        print(f"总耗时: {progress['duration']:.2f}秒")

        # 打印生产结果
        print("\n=== 生产结果 ===")
        if "final_article" in results:
            print(f"文章: {results['final_article']['title']}")
        elif "final_articles" in results:
            for idx, article in enumerate(results["final_articles"]):
                print(f"\n文章 {idx+1}: {article['title']}")

        print(f"状态: {results['status']}")
        print(f"耗时: {results['duration_seconds']:.2f}秒")

    except Exception as e:
        print(f"\n生产失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
