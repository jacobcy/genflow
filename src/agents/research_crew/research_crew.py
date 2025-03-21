"""研究团队工作流程"""
from typing import List, Dict, Optional
from datetime import datetime
from crewai import Task, Crew, Process
from src.models.topic import Topic
from src.models.article import Article, Section
from .research_agents import ResearchAgents

class ResearchResult:
    """研究结果"""
    def __init__(
        self,
        topic: Topic,
        background: Dict,
        expert_insights: List[Dict],
        data_analysis: Dict,
        report: Dict
    ):
        self.topic = topic
        self.background = background
        self.expert_insights = expert_insights
        self.data_analysis = data_analysis
        self.report = report
        self.created_at = datetime.now()
        self.human_feedback: Optional[Dict] = None

class ResearchCrew:
    """研究团队"""
    
    def __init__(self):
        """初始化团队"""
        self.agents = ResearchAgents()
        self.background_researcher = self.agents.create_background_researcher()
        self.expert_finder = self.agents.create_expert_finder()
        self.data_analyst = self.agents.create_data_analyst()
        self.research_writer = self.agents.create_research_writer()
    
    async def research_topic(self, topic: Topic) -> ResearchResult:
        """研究话题
        
        Args:
            topic: 要研究的话题
            
        Returns:
            ResearchResult: 研究结果
        """
        # 1. 背景研究任务
        background_research = Task(
            description=f"""
            1. 深入研究话题"{topic.title}"的背景信息
            2. 收集历史发展脉络
            3. 分析当前现状
            4. 预测未来趋势
            5. 整理重要参考资料
            """,
            agent=self.background_researcher
        )
        
        # 2. 专家观点任务
        expert_research = Task(
            description=f"""
            1. 寻找该领域的权威专家
            2. 收集专家的重要观点
            3. 分析观点的价值
            4. 对比不同观点
            5. 总结关键见解
            """,
            agent=self.expert_finder
        )
        
        # 3. 数据分析任务
        data_analysis = Task(
            description=f"""
            1. 收集相关数据
            2. 分析数据规律
            3. 发现潜在趋势
            4. 生成数据报告
            5. 提供数据支持的建议
            """,
            agent=self.data_analyst
        )
        
        # 4. 报告撰写任务
        report_writing = Task(
            description=f"""
            1. 整合所有研究成果
            2. 组织报告结构
            3. 撰写详细报告
            4. 提供研究建议
            5. 标注重要参考
            """,
            agent=self.research_writer
        )
        
        # 创建工作流
        crew = Crew(
            agents=[
                self.background_researcher,
                self.expert_finder,
                self.data_analyst,
                self.research_writer
            ],
            tasks=[
                background_research,
                expert_research,
                data_analysis,
                report_writing
            ],
            process=Process.sequential
        )
        
        # 执行工作流
        result = crew.kickoff()
        
        # 整理研究结果
        research_result = ResearchResult(
            topic=topic,
            background=result["background"],
            expert_insights=result["expert_insights"],
            data_analysis=result["data_analysis"],
            report=result["report"]
        )
        
        return research_result
    
    def get_human_feedback(self, research_result: ResearchResult) -> ResearchResult:
        """获取人工反馈
        
        Args:
            research_result: 研究结果
            
        Returns:
            ResearchResult: 更新后的研究结果
        """
        print("\n=== 研究报告评审 ===\n")
        print(f"话题: {research_result.topic.title}")
        
        print("\n1. 背景研究质量 (0-1):")
        print("- 历史脉络完整性")
        print("- 现状分析准确性")
        print("- 趋势预测合理性")
        background_score = float(input("请评分: "))
        
        print("\n2. 专家观点质量 (0-1):")
        print("- 专家权威性")
        print("- 观点价值")
        print("- 分析深度")
        expert_score = float(input("请评分: "))
        
        print("\n3. 数据分析质量 (0-1):")
        print("- 数据可靠性")
        print("- 分析专业性")
        print("- 结论合理性")
        data_score = float(input("请评分: "))
        
        print("\n4. 总体评价:")
        comments = input("评审意见: ")
        
        # 更新反馈
        research_result.human_feedback = {
            "background_score": background_score,
            "expert_score": expert_score,
            "data_score": data_score,
            "average_score": (background_score + expert_score + data_score) / 3,
            "comments": comments,
            "reviewed_at": datetime.now()
        }
        
        return research_result
    
    def generate_article_outline(self, research_result: ResearchResult) -> Article:
        """根据研究结果生成文章大纲
        
        Args:
            research_result: 研究结果
            
        Returns:
            Article: 文章大纲
        """
        # 从研究报告中提取关键信息
        report = research_result.report
        
        # 创建文章大纲
        article = Article(
            id=f"article_{research_result.topic.id}",
            topic_id=research_result.topic.id,
            title=report["title"],
            summary=report["summary"],
            sections=[
                Section(
                    title=section["title"],
                    content=section["outline"],
                    order=idx + 1
                )
                for idx, section in enumerate(report["sections"])
            ],
            status="draft"
        )
        
        return article

# 使用示例
async def main():
    # 创建一个示例话题
    topic = Topic(
        id="topic_001",
        title="Python异步编程最佳实践",
        description="探讨Python异步编程的发展、应用场景和最佳实践",
        category="技术",
        tags=["Python", "异步编程", "并发"]
    )
    
    # 创建研究团队
    crew = ResearchCrew()
    
    # 进行研究
    research_result = await crew.research_topic(topic)
    
    # 获取人工反馈
    research_result = crew.get_human_feedback(research_result)
    
    # 生成文章大纲
    if research_result.human_feedback["average_score"] >= 0.7:
        article = crew.generate_article_outline(research_result)
        print("\n=== 文章大纲 ===")
        print(f"标题: {article.title}")
        print(f"摘要: {article.summary}")
        print("\n章节:")
        for section in article.sections:
            print(f"\n{section.order}. {section.title}")
            print(section.content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 