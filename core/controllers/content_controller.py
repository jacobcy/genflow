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
        
        # 更新进度
        self.current_progress.start_stage(ProductionStage.TOPIC_DISCOVERY, count)
        self.current_progress.total_topics = count
        
        try:
            # 发现话题
            topics = await self.topic_crew.discover_topics(category, count)
            
            # 获取人工反馈
            topics = self.topic_crew.get_human_feedback(topics)
            
            # 过滤出通过的话题
            approved_topics = [
                topic for topic in topics
                if topic.status == "approved"
            ]
            
            # 更新进度
            self.current_progress.update_progress(
                stage=ProductionStage.TOPIC_DISCOVERY,
                completed_items=len(topics),
                avg_score=sum(topic.score for topic in topics) / len(topics) if topics else 0
            )
            self.current_progress.completed_topics = len(approved_topics)
            self.current_progress.complete_stage(ProductionStage.TOPIC_DISCOVERY)
            
            logger.info(f"话题发现完成，发现 {len(topics)} 个话题，通过 {len(approved_topics)} 个")
            return approved_topics
            
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
            # 进行研究
            research_result = await self.research_crew.research_topic(topic)
            logger.info(f"话题研究完成: {topic.title}")
            return research_result
            
        except Exception as e:
            logger.error(f"研究话题 '{topic.title}' 失败: {str(e)}")
            raise
    
    async def research_topics(self, topics: List[Topic]) -> List[Dict]:
        """批量研究话题
        
        Args:
            topics: 要研究的话题列表
            
        Returns:
            List[Dict]: 研究结果列表
        """
        logger.info(f"开始批量研究话题，数量: {len(topics)}")
        
        # 更新进度
        self.current_progress.start_stage(ProductionStage.TOPIC_RESEARCH, len(topics))
        
        research_results = []
        completed_count = 0
        total_score = 0
        error_count = 0
        
        for topic in topics:
            try:
                logger.info(f"研究话题: {topic.title}")
                
                # 进行研究
                research_result = await self.research_topic(topic)
                
                # 获取人工反馈
                research_result = self.research_crew.get_human_feedback(research_result)
                
                # 更新统计
                completed_count += 1
                total_score += research_result.human_feedback["average_score"]
                
                # 如果评分达标，生成文章大纲
                if research_result.human_feedback["average_score"] >= 0.7:
                    article = self.research_crew.generate_article_outline(research_result)
                    research_results.append({
                        "topic": topic,
                        "research_result": research_result,
                        "article_outline": article
                    })
                
            except Exception as e:
                error_count += 1
                logger.error(f"研究话题 '{topic.title}' 失败: {str(e)}")
                self.current_progress.add_error(
                    ProductionStage.TOPIC_RESEARCH,
                    f"研究话题 '{topic.title}' 失败: {str(e)}"
                )
            
            # 更新进度
            self.current_progress.update_progress(
                stage=ProductionStage.TOPIC_RESEARCH,
                completed_items=completed_count,
                avg_score=total_score / completed_count if completed_count > 0 else 0,
                error_count=error_count
            )
        
        self.current_progress.complete_stage(ProductionStage.TOPIC_RESEARCH)
        logger.info(f"话题研究阶段完成，通过 {len(research_results)} 个话题")
        return research_results
    
    async def write_article(self, topic: Topic, research_result: Dict) -> Article:
        """撰写单个文章
        
        Args:
            topic: 话题信息
            research_result: 研究结果
            
        Returns:
            Article: 生成的文章
        """
        logger.info(f"开始撰写文章: {topic.title}")
        
        try:
            # 进行写作
            article = await self.writing_crew.write_article(topic, research_result)
            logger.info(f"文章撰写完成: {article.title}")
            return article
            
        except Exception as e:
            logger.error(f"撰写文章 '{topic.title}' 失败: {str(e)}")
            raise
    
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
                writing_result = await self.writing_crew.write_article(
                    result["article_outline"],
                    platform
                )
                
                # 获取人工反馈
                writing_result = self.writing_crew.get_human_feedback(writing_result)
                
                # 更新统计
                completed_count += 1
                total_score += writing_result.human_feedback["average_score"]
                
                # 如果评分达标，更新文章
                if writing_result.human_feedback["average_score"] >= 0.7:
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
    
    async def adapt_style(self, article: Article, platform: Platform) -> Article:
        """适配单个文章风格
        
        Args:
            article: 原始文章
            platform: 目标平台
            
        Returns:
            Article: 风格适配后的文章
        """
        logger.info(f"开始适配文章风格: {article.title}")
        
        try:
            # 进行风格适配
            style_result = await self.style_crew.adapt_style(article, platform)
            logger.info(f"文章风格适配完成: {article.title}")
            return style_result.final_article
            
        except Exception as e:
            logger.error(f"适配文章风格 '{article.title}' 失败: {str(e)}")
            raise
    
    async def adapt_articles(
        self,
        writing_results: List[Dict],
        platform: Platform
    ) -> List[Dict]:
        """批量适配文章风格
        
        Args:
            writing_results: 写作结果列表
            platform: 目标平台
            
        Returns:
            List[Dict]: 适配结果列表
        """
        logger.info(f"开始批量适配文章风格，数量: {len(writing_results)}")
        
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
                
                # 进行风格适配
                adapted_article = await self.adapt_style(result["article"], platform)
                
                # 获取人工反馈
                feedback_score = self.style_crew.get_human_feedback(adapted_article, platform)
                
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
                
                # 获取人工反馈
                review_result = self.review_crew.get_human_feedback(review_result)
                
                # 更新统计
                completed_count += 1
                total_score += review_result.human_feedback["average_score"]
                
                # 如果评分达标，更新文章状态
                if review_result.human_feedback["average_score"] >= 0.7:
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
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """生产内容的完整流程
        
        从选题到发布的完整流程，支持单篇和多篇模式。
        
        Args:
            topic: 指定话题，如不提供则自动发现
            category: 话题类别，当topic不提供时使用
            platform: 目标平台，如不提供则使用默认平台
            topic_count: 话题数量，当topic不提供时使用
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 生产结果，包含文章和各阶段数据
        """
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
        }
        
        try:
            # 初始化各团队
            await self.initialize(platform)
            
            # 确保平台参数
            if not platform:
                platform = get_default_platform()
                
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
                article = await self.write_article(topic, research_result)
                self.current_progress.complete_stage(ProductionStage.ARTICLE_WRITING)
                result["stages"]["writing"] = {
                    "article_summary": {
                        "title": article.title,
                        "word_count": article.word_count,
                        "sections_count": len(article.sections)
                    },
                    "completed_at": datetime.now().isoformat()
                }
                
                # 阶段4: 风格适配
                self.current_progress.start_stage(ProductionStage.STYLE_ADAPTATION, 1)
                styled_article = await self.adapt_style(article, platform)
                self.current_progress.complete_stage(ProductionStage.STYLE_ADAPTATION)
                result["stages"]["style_adaptation"] = {
                    "platform": platform.name,
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
                
            # 多篇模式: 批量处理多个话题
            else:
                logger.info(f"开始批量生产内容，类别: {category}，数量: {topic_count}")
                
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
                
                # 阶段4: 风格适配
                adaptation_results = await self.adapt_articles(writing_results, platform)
                if not adaptation_results:
                    raise ValueError("风格适配未通过")
                    
                result["stages"]["style_adaptation"] = {
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
            
            # 完成生产
            self.current_progress.complete()
            
            # 最终结果
            result["end_time"] = datetime.now().isoformat()
            result["duration_seconds"] = (datetime.fromisoformat(result["end_time"]) - 
                                         datetime.fromisoformat(result["start_time"])).total_seconds()
            result["progress_summary"] = self.current_progress.get_summary()
            
            logger.info(f"内容生产完成，状态: {result['status']}")
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