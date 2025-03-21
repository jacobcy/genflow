"""内容生产主控制器"""
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import uuid
from src.models.topic import Topic
from src.models.article import Article
from src.models.platform import Platform
from src.models.progress import ProductionProgress, ProductionStage, StageStatus
from src.agents.topic_crew.topic_crew import TopicCrew
from src.agents.research_crew.research_crew import ResearchCrew
from src.agents.writing_crew.writing_crew import WritingCrew
from src.agents.review_crew.review_crew import ReviewCrew
from src.tools.style_tools.adapter import StyleAdapter
from src.tools.content_collectors.collector import ContentCollector
from src.tools.trending_tools.topic_trends import TrendingTopics
from src.tools.writing_tools.article_writer import ArticleWriter

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

class ContentController:
    """内容生产主控制器"""
    
    def __init__(self):
        """初始化团队"""
        self.topic_crew = TopicCrew()
        self.research_crew = ResearchCrew()
        self.writing_crew = WritingCrew()
        self.review_crew = ReviewCrew()
        self.production_results: List[ContentProductionResult] = []
        self.current_progress: Optional[ProductionProgress] = None
    
    async def discover_topics(self, category: str, count: int = 3) -> List[Topic]:
        """发现话题
        
        Args:
            category: 话题类别
            count: 话题数量
            
        Returns:
            List[Topic]: 发现的话题列表
        """
        print("\n=== 话题发现阶段 ===")
        
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
            
            return approved_topics
            
        except Exception as e:
            self.current_progress.add_error(
                ProductionStage.TOPIC_DISCOVERY,
                str(e)
            )
            raise
    
    async def research_topics(self, topics: List[Topic]) -> List[Dict]:
        """研究话题
        
        Args:
            topics: 要研究的话题列表
            
        Returns:
            List[Dict]: 研究结果列表
        """
        print("\n=== 话题研究阶段 ===")
        
        # 更新进度
        self.current_progress.start_stage(ProductionStage.TOPIC_RESEARCH, len(topics))
        
        research_results = []
        completed_count = 0
        total_score = 0
        error_count = 0
        
        for topic in topics:
            try:
                print(f"\n研究话题: {topic.title}")
                # 进行研究
                research_result = await self.research_crew.research_topic(topic)
                
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
        return research_results
    
    async def write_articles(
        self,
        research_results: List[Dict],
        platform: Platform
    ) -> List[Dict]:
        """写作文章
        
        Args:
            research_results: 研究结果列表
            platform: 目标平台
            
        Returns:
            List[Dict]: 写作结果列表
        """
        print("\n=== 文章写作阶段 ===")
        
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
                print(f"\n写作文章: {result['article_outline'].title}")
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
        return writing_results
    
    async def adapt_articles(
        self,
        writing_results: List[Dict],
        platform: Platform
    ) -> List[Dict]:
        """适配文章风格
        
        Args:
            writing_results: 写作结果列表
            platform: 目标平台
            
        Returns:
            List[Dict]: 适配结果列表
        """
        print("\n=== 风格适配阶段 ===")
        
        # 更新进度
        self.current_progress.start_stage(
            ProductionStage.STYLE_ADAPTATION,
            len(writing_results)
        )
        
        adaptation_results = []
        completed_count = 0
        total_score = 0
        error_count = 0
        
        # 创建风格适配器
        adapter = StyleAdapter(platform)
        
        for result in writing_results:
            try:
                print(f"\n适配文章: {result['article'].title}")
                # 进行风格适配
                adapted_article = await adapter.adapt_article(result["article"])
                
                # 获取人工反馈
                print("\n请对风格适配结果进行评分(0-1):")
                print("- 语气是否符合平台风格")
                print("- 格式是否符合平台要求")
                print("- 结构是否合理")
                print("- SEO优化是否到位")
                
                # 模拟人工反馈(实际应该由用户输入)
                feedback_score = 0.8
                
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
        return adaptation_results
    
    async def review_articles(
        self,
        writing_results: List[Dict],
        platform: Platform
    ) -> List[Dict]:
        """审核文章
        
        Args:
            writing_results: 写作结果列表
            platform: 目标平台
            
        Returns:
            List[Dict]: 审核结果列表
        """
        print("\n=== 文章审核阶段 ===")
        
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
                print(f"\n审核文章: {result['article'].title}")
                # 进行审核
                review_result = await self.review_crew.review_article(
                    result["article"],
                    platform
                )
                
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
        return review_results
    
    async def produce_content(
        self,
        category: str,
        platform: Platform,
        topic_count: int = 3
    ) -> List[ContentProductionResult]:
        """生产内容
        
        Args:
            category: 话题类别
            platform: 目标平台
            topic_count: 话题数量
            
        Returns:
            List[ContentProductionResult]: 内容生产结果列表
        """
        # 初始化进度跟踪
        production_id = str(uuid.uuid4())
        self.current_progress = ProductionProgress(production_id)
        
        try:
            # 1. 发现话题
            topics = await self.discover_topics(category, topic_count)
            if not topics:
                print("\n未发现合适的话题")
                self.current_progress.fail()
                return []
            
            # 2. 研究话题
            research_results = await self.research_topics(topics)
            if not research_results:
                print("\n话题研究未通过")
                self.current_progress.fail()
                return []
            
            # 3. 写作文章
            writing_results = await self.write_articles(research_results, platform)
            if not writing_results:
                print("\n文章写作未通过")
                self.current_progress.fail()
                return []
            
            # 4. 风格适配
            adaptation_results = await self.adapt_articles(writing_results, platform)
            if not adaptation_results:
                print("\n风格适配未通过")
                self.current_progress.fail()
                return []
            
            # 5. 审核文章
            review_results = await self.review_articles(adaptation_results, platform)
            if not review_results:
                print("\n文章审核未通过")
                self.current_progress.fail()
                return []
            
            # 6. 整理生产结果
            production_results = []
            for result in review_results:
                production_result = ContentProductionResult(
                    topic=result["topic"],
                    research_data=result["research_result"].__dict__,
                    article=result["article"],
                    review_data=result["review_result"].__dict__,
                    platform=platform
                )
                production_result.status = "completed"
                self.production_results.append(production_result)
                production_results.append(production_result)
            
            # 完成生产
            self.current_progress.complete()
            return production_results
            
        except Exception as e:
            print(f"\n生产过程出错: {str(e)}")
            self.current_progress.fail()
            raise
    
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
            print("\n已暂停生产")
    
    def resume_production(self):
        """恢复生产"""
        if self.current_progress:
            self.current_progress.resume()
            print("\n已恢复生产")

# 使用示例
async def main():
    # 创建一个示例平台
    platform = Platform(
        id="platform_001",
        name="掘金",
        url="https://juejin.cn",
        content_rules={
            "min_words": 1000,
            "max_words": 5000,
            "allowed_tags": ["Python", "编程", "技术"]
        }
    )
    
    # 创建控制器
    controller = ContentController()
    
    try:
        # 生产内容
        results = await controller.produce_content(
            category="技术",
            platform=platform,
            topic_count=3
        )
        
        # 打印进度摘要
        progress = controller.get_progress()
        print("\n=== 生产进度摘要 ===")
        print(f"生产ID: {progress['production_id']}")
        print(f"当前阶段: {progress['current_stage']}")
        print(f"阶段状态: {progress['stage_status']}")
        print(f"总进度: {progress['progress_percentage']}%")
        print(f"总耗时: {progress['duration']:.2f}秒")
        print(f"话题数: {progress['total_topics']}")
        print(f"完成数: {progress['completed_topics']}")
        print(f"错误数: {progress['error_count']}")
        
        print("\n各阶段统计:")
        for stage, stats in progress["stages"].items():
            print(f"\n{stage}:")
            print(f"- 状态: {stats['status']}")
            print(f"- 耗时: {stats['duration']:.2f}秒")
            print(f"- 完成项目: {stats['completed_items']}/{stats['total_items']}")
            print(f"- 成功率: {stats['success_rate']*100:.2f}%")
            print(f"- 平均评分: {stats['avg_score']:.2f}")
            print(f"- 错误数: {stats['error_count']}")
        
        # 打印生产结果
        print("\n=== 生产结果 ===")
        for result in results:
            print(f"\n文章: {result.article.title}")
            print(f"平台: {result.platform.name}")
            print(f"状态: {result.status}")
            print(f"创建时间: {result.created_at}")
    
    except Exception as e:
        print(f"\n生产失败: {str(e)}")
        # 打印错误日志
        if controller.current_progress:
            print("\n错误日志:")
            for error in controller.current_progress.error_logs:
                print(f"- [{error['stage'].value}] {error['time']}: {error['error']}")

if __name__ == "__main__":
    asyncio.run(main()) 