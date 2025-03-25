"""选题团队工作流程"""
from typing import List, Dict
from datetime import datetime
from crewai import Task, Crew, Process
from core.models.topic import Topic, TopicMetrics, TopicReference
from .topic_agents import TopicAgents

class TopicCrew:
    """选题团队"""
    
    def __init__(self):
        """初始化团队"""
        self.agents = TopicAgents()
        self.trend_analyzer = self.agents.create_trend_analyzer()
        self.topic_researcher = self.agents.create_topic_researcher()
        self.report_writer = self.agents.create_report_writer()
    
    def discover_topics(self, category: str = None, count: int = 5) -> List[Topic]:
        """发现热门话题
        
        Args:
            category: 话题分类
            count: 需要发现的话题数量
            
        Returns:
            List[Topic]: 话题列表
        """
        # 创建任务
        trend_analysis = Task(
            description=f"""
            1. 搜索{category or '所有领域'}的热门话题
            2. 分析每个话题的热度趋势
            3. 选出最具潜力的{count}个话题
            4. 收集每个话题的基础信息
            """,
            agent=self.trend_analyzer
        )
        
        topic_research = Task(
            description=f"""
            1. 深入分析每个话题的受众群体
            2. 评估话题的商业价值
            3. 分析竞争情况
            4. 收集相关参考资料
            """,
            agent=self.topic_researcher
        )
        
        report_writing = Task(
            description=f"""
            1. 整理所有话题信息
            2. 生成结构化的选题报告
            3. 为每个话题提供详细分析
            4. 添加数据支持的建议
            """,
            agent=self.report_writer
        )
        
        # 创建工作流
        crew = Crew(
            agents=[self.trend_analyzer, self.topic_researcher, self.report_writer],
            tasks=[trend_analysis, topic_research, report_writing],
            process=Process.sequential
        )
        
        # 执行工作流
        result = crew.kickoff()
        
        # 解析结果,生成Topic对象列表
        topics = []
        for item in result["topics"]:
            topic = Topic(
                id=f"topic_{len(topics)+1:03d}",
                title=item["title"],
                description=item["description"],
                category=item["category"],
                tags=item["tags"],
                metrics=TopicMetrics(**item["metrics"]),
                references=[TopicReference(**ref) for ref in item["references"]],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                status="pending"
            )
            topics.append(topic)
        
        return topics
    
    def analyze_topic(self, topic_id: str) -> Dict:
        """深入分析单个话题
        
        Args:
            topic_id: 话题ID
            
        Returns:
            Dict: 包含详细分析的字典
        """
        # 创建深入研究任务
        research = Task(
            description=f"""
            1. 深入研究话题 {topic_id}
            2. 分析话题的各个维度
            3. 提供详细的数据支持
            4. 给出可行性建议
            """,
            agent=self.topic_researcher
        )
        
        # 创建报告任务
        report = Task(
            description=f"""
            1. 整理研究结果
            2. 生成详细的分析报告
            3. 提供具体的建议
            4. 列出潜在风险
            """,
            agent=self.report_writer
        )
        
        # 创建工作流
        crew = Crew(
            agents=[self.topic_researcher, self.report_writer],
            tasks=[research, report],
            process=Process.sequential
        )
        
        # 执行工作流
        result = crew.kickoff()
        
        return {
            "topic_id": topic_id,
            "analysis": result["analysis"],
            "report": result["report"],
            "recommendations": result["recommendations"]
        }
    
    def get_human_feedback(self, topics: List[Topic]) -> List[Topic]:
        """获取人工反馈
        
        Args:
            topics: 话题列表
            
        Returns:
            List[Topic]: 更新后的话题列表
        """
        print("\n=== 请对以下话题进行评估 ===\n")
        
        for topic in topics:
            print(f"\n--- 话题: {topic.title} ---")
            print(f"描述: {topic.description}")
            print(f"分类: {topic.category}")
            print(f"标签: {', '.join(topic.tags)}")
            print("\n指标:")
            print(f"- 搜索量: {topic.metrics.search_volume}")
            print(f"- 趋势分数: {topic.metrics.trend_score:.2f}")
            print(f"- 竞争程度: {topic.metrics.competition_level:.2f}")
            print(f"- 预估价值: {topic.metrics.estimated_value:.2f}")
            
            # 获取反馈
            interest = input("\n请评分(0-1): ")
            priority = input("优先级(high/medium/low): ")
            notes = input("备注: ")
            
            # 更新话题状态
            topic.human_feedback = {
                "interest_level": float(interest),
                "priority": priority,
                "notes": notes
            }
            topic.status = "approved" if float(interest) >= 0.6 else "rejected"
            topic.updated_at = datetime.now()
        
        return topics

# 使用示例
async def main():
    crew = TopicCrew()
    
    # 发现话题
    topics = await crew.discover_topics(category="技术", count=3)
    
    # 获取人工反馈
    topics = crew.get_human_feedback(topics)
    
    # 深入分析获批话题
    for topic in topics:
        if topic.status == "approved":
            analysis = await crew.analyze_topic(topic.id)
            print(f"\n=== {topic.title} 分析报告 ===")
            print(analysis["report"])

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 