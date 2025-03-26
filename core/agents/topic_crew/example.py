"""TopicCrew使用示例

这个脚本演示了如何使用TopicCrew进行话题发现和分析。
"""
import os
import sys
import asyncio
import json

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

# 导入必要的模块
from core.config import Config
from core.agents.topic_crew.topic_crew import TopicCrew

async def discover_topics_example():
    """话题发现示例"""
    print("====== 话题发现示例 ======")

    # 初始化配置和团队
    config = Config()
    crew = TopicCrew(config=config)

    # 发现话题
    topics = await crew.discover_topics(
        category="科技",  # 可选参数，指定话题分类
        count=3          # 需要发现的话题数量
    )

    # 输出结果
    print(f"\n发现了 {len(topics)} 个话题:\n")
    for topic in topics:
        print(f"- {topic.title}: {topic.description}")

    return topics

async def analyze_topic_example(topic_id: str):
    """话题分析示例"""
    print(f"\n====== 话题分析示例: {topic_id} ======")

    # 初始化配置和团队
    config = Config()
    crew = TopicCrew(config=config)

    # 分析话题
    analysis = await crew.analyze_topic(topic_id)

    # 输出分析结果
    print("\n分析结果摘要:")
    print(f"- 主要结论: {analysis.get('analysis', {}).get('conclusion', '无')}")
    print(f"- 建议数量: {len(analysis.get('recommendations', []))}")

    return analysis

async def full_workflow_example():
    """完整工作流程示例"""
    print("\n====== 完整工作流程示例 ======")

    # 初始化配置和团队
    config = Config()
    crew = TopicCrew(config=config)

    # 运行完整工作流程
    result = await crew.run_full_workflow(
        category="教育",  # 可选参数，指定话题分类
        count=2          # 需要发现的话题数量
    )

    # 输出结果摘要
    print("\n工作流程完成:")
    print(f"- 总话题数: {result['total_topics']}")
    print(f"- 获批话题数: {result['approved_topics']}")

    # 保存结果到文件
    with open("topic_analysis_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n结果已保存到 topic_analysis_result.json")

    return result

async def custom_agent_example():
    """自定义智能体示例"""
    print("\n====== 自定义智能体示例 ======")

    from core.agents.topic_crew.topic_agents import TopicAgents
    from crewai import Task, Crew, Process

    # 初始化智能体
    agents = TopicAgents()

    # 获取所有智能体
    all_agents = agents.create_all_agents()
    trend_analyzer = all_agents["trend_analyzer"]

    # 创建自定义任务
    custom_task = Task(
        description="""
        ## 特定平台趋势分析

        请分析今日头条平台上的热门教育类话题:
        1. 获取头条平台的教育类热点话题
        2. 分析这些话题的特点和受众
        3. 提供话题价值评估

        输出为JSON格式，包含分析结果。
        """,
        expected_output="头条平台教育类热点话题分析(JSON格式)",
        agent=trend_analyzer
    )

    # 创建简单团队
    crew = Crew(
        agents=[trend_analyzer],
        tasks=[custom_task],
        verbose=True
    )

    # 执行任务
    result = await crew.kickoff()

    # 输出结果摘要
    print("\n分析完成:")
    if isinstance(result, dict) and "topics" in result:
        print(f"- 分析了 {len(result['topics'])} 个话题")

    return result

async def main():
    """主函数"""
    # 选择要运行的示例(取消注释)

    # 示例1: 话题发现
    topics = await discover_topics_example()

    # 示例2: 话题分析(需要有效的话题ID)
    if topics and len(topics) > 0:
        await analyze_topic_example(topics[0].id)

    # 示例3: 完整工作流程(包含人工反馈)
    # await full_workflow_example()

    # 示例4: 自定义智能体和任务
    # await custom_agent_example()

if __name__ == "__main__":
    asyncio.run(main())
