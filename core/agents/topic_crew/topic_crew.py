"""选题团队工作流程

这个模块定义了选题团队的简化工作流程，主要是获取热搜话题并辅助人工决策。
工作流程专注于从热搜平台获取话题信息，由人工编辑做最终决策。
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import asyncio
import logging
import traceback
from crewai import Task, Crew, Process
from core.models.topic import Topic, TopicMetrics, TopicReference
from core.config import Config
from .topic_agents import TopicAgents

# 配置日志
logger = logging.getLogger("topic_crew")

class TopicCrew:
    """选题团队

    这个类管理选题团队的简化工作流程，获取热搜话题并提供建议，
    以人工为主，AI辅助决策。
    """

    def __init__(self, config: Optional[Config] = None):
        """初始化团队

        Args:
            config: 配置对象，如果为None则创建默认配置
        """
        # 加载配置
        self.config = config or Config()

        # 初始化智能体
        logger.info("初始化选题团队智能体...")
        self.agents = TopicAgents(config=self.config)
        self.topic_advisor = self.agents.create_topic_advisor()

        # 创建所有智能体的字典，便于通过名称访问
        self.all_agents = {
            "topic_advisor": self.topic_advisor
        }
        logger.info("选题团队初始化完成")

    async def suggest_topics(self, category: Optional[str] = None, count: int = 5) -> List[Topic]:
        """建议热门话题

        Args:
            category: 话题分类，为None则搜索所有分类
            count: 需要建议的话题数量

        Returns:
            List[Topic]: 话题列表
        """
        logger.info(f"开始获取热门话题建议：分类={category or '全部'}，数量={count}")

        # 创建任务
        topic_suggestion_task = self._create_topic_suggestion_task(category, count)

        # 创建工作流
        crew = Crew(
            agents=[self.topic_advisor],
            tasks=[topic_suggestion_task],
            process=Process.sequential,
            verbose=True
        )

        # 执行工作流
        logger.info("启动话题获取流程...")
        result = await self._execute_crew(crew)

        # 解析结果，生成Topic对象列表
        topics = self._parse_topics_result(result)
        logger.info(f"话题获取完成，共发现 {len(topics)} 个话题")
        return topics

    async def get_topic_details(self, topic_id: str) -> Dict:
        """获取话题详情

        Args:
            topic_id: 话题ID或完整名称

        Returns:
            Dict: 包含话题详情的字典
        """
        logger.info(f"获取话题详情：{topic_id}")

        # 创建获取详情任务
        details_task = self._create_topic_details_task(topic_id)

        # 创建工作流
        crew = Crew(
            agents=[self.topic_advisor],
            tasks=[details_task],
            process=Process.sequential,
            verbose=True
        )

        # 执行工作流
        logger.info("启动话题详情获取流程...")
        result = await self._execute_crew(crew)

        return result

    def get_human_decision(self, topics: List[Topic]) -> List[Topic]:
        """获取人工决策

        Args:
            topics: 话题列表

        Returns:
            List[Topic]: 更新后的话题列表
        """
        logger.info(f"获取人工决策，共 {len(topics)} 个话题")
        print("\n=== 请对以下话题进行决策 ===\n")

        for topic in topics:
            self._display_topic_info(topic)

            # 获取决策
            decision = self._get_valid_input(
                "是否选择此话题 (yes/no): ",
                lambda x: x.lower() in ["yes", "no", "y", "n"]
            )
            notes = input("备注 (可选): ")

            # 更新话题状态
            topic.human_feedback = {
                "decision": decision.lower() in ["yes", "y"],
                "notes": notes
            }
            topic.status = "selected" if decision.lower() in ["yes", "y"] else "rejected"
            topic.updated_at = datetime.now()

            logger.info(f"话题 '{topic.title}' 决策: {decision}, 状态: {topic.status}")

        selected_count = len([t for t in topics if t.status == "selected"])
        logger.info(f"人工决策完成，{selected_count}/{len(topics)} 个话题被选中")
        return topics

    async def run_workflow(self, category: Optional[str] = None, count: int = 10) -> Dict:
        """运行简化的工作流程

        Args:
            category: 话题分类
            count: 话题数量

        Returns:
            Dict: 工作流程结果
        """
        logger.info(f"开始执行简化工作流程: 分类={category or '全部'}, 数量={count}")

        # 1. 获取话题建议
        logger.info("=== 获取话题建议 ===")
        print("=== 开始获取话题建议 ===")
        topics = await self.suggest_topics(category=category, count=count)
        logger.info(f"=== 获取了 {len(topics)} 个话题建议 ===")
        print(f"=== 获取了 {len(topics)} 个话题建议 ===")

        # 2. 获取人工决策
        logger.info("=== 开始获取人工决策 ===")
        topics = self.get_human_decision(topics)

        # 3. 生成结果报告
        logger.info("生成结果报告")
        result_report = {
            "timestamp": datetime.now().isoformat(),
            "category": category or "全部",
            "total_topics": len(topics),
            "selected_topics": len([t for t in topics if t.status == "selected"]),
            "topics": [topic.dict() for topic in topics]
        }

        logger.info(f"工作流程执行完成")
        return result_report

    # ================ 辅助方法 ================

    def _create_topic_suggestion_task(self, category: Optional[str], count: int) -> Task:
        """创建话题建议任务

        Args:
            category: 话题分类
            count: 需要建议的话题数量

        Returns:
            Task: 话题建议任务
        """
        logger.info(f"创建话题建议任务: 分类={category or '全部'}, 数量={count}")
        return Task(
            description=f"""
            ## 热门话题建议任务

            请完成以下步骤:

            1. 获取{category or '所有类别'}的热门话题
            2. 从中筛选出最适合内容创作的{count}个话题
            3. 为每个话题提供简要分析和推荐理由

            要求输出为JSON格式，包含以下字段:
            - topics: 话题列表，每个话题包含:
              - title: 话题标题
              - description: 简要描述(200字以内)
              - category: 话题类别
              - tags: 标签列表(3-5个)
              - recommendation_reason: 推荐理由(简洁明了)
            """,
            expected_output=f"包含{count}个推荐话题的JSON数据",
            agent=self.topic_advisor
        )

    def _create_topic_details_task(self, topic_id: str) -> Task:
        """创建话题详情任务

        Args:
            topic_id: 话题ID

        Returns:
            Task: 话题详情任务
        """
        logger.info(f"创建话题详情任务: {topic_id}")
        return Task(
            description=f"""
            ## 话题详情获取任务

            请获取话题 "{topic_id}" 的详细信息:

            1. 获取话题的完整描述和背景
            2. 分析话题当前热度和趋势
            3. 提供创作该话题的建议方向

            要求输出为JSON格式，包含话题的详细信息。
            """,
            expected_output="话题详情的JSON数据",
            agent=self.topic_advisor
        )

    async def _execute_crew(self, crew: Crew) -> Any:
        """执行团队工作流

        Args:
            crew: 团队对象

        Returns:
            Any: 执行结果
        """
        try:
            logger.info("开始执行团队工作流")
            result = await crew.kickoff()
            logger.info("团队工作流执行完成")
            return result
        except Exception as e:
            error_msg = f"团队执行出错: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            # 记录错误并返回空结果
            return {"error": error_msg, "traceback": traceback.format_exc()}

    def _parse_topics_result(self, result: Dict) -> List[Topic]:
        """解析话题结果

        Args:
            result: 原始结果字典

        Returns:
            List[Topic]: 话题对象列表
        """
        logger.info("开始解析话题结果")
        topics = []

        # 处理可能的错误情况
        if "error" in result:
            logger.error(f"解析结果时发现错误: {result['error']}")
            return topics

        # 确保topics字段存在
        if "topics" not in result:
            logger.warning("结果中未找到topics字段")
            return topics

        # 解析每个话题
        for i, item in enumerate(result["topics"]):
            try:
                topic = Topic(
                    id=f"topic_{len(topics)+1:03d}",
                    title=item["title"],
                    description=item["description"],
                    category=item.get("category", "未分类"),
                    tags=item.get("tags", []),
                    metrics=TopicMetrics(
                        search_volume=item.get("metrics", {}).get("search_volume", 0),
                        trend_score=item.get("metrics", {}).get("trend_score", 0.0),
                        competition_level=item.get("metrics", {}).get("competition_level", 0.0),
                        estimated_value=item.get("metrics", {}).get("estimated_value", 0.0)
                    ),
                    references=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    status="pending",
                    recommendation_reason=item.get("recommendation_reason", "")
                )
                topics.append(topic)
                logger.info(f"成功解析话题: {topic.title}")
            except Exception as e:
                logger.error(f"解析话题 {i+1} 时出错: {str(e)}")
                continue

        logger.info(f"话题结果解析完成，共 {len(topics)} 个有效话题")
        return topics

    def _display_topic_info(self, topic: Topic) -> None:
        """显示话题信息

        Args:
            topic: 话题对象
        """
        print(f"\n--- 话题: {topic.title} ---")
        print(f"描述: {topic.description}")
        print(f"分类: {topic.category}")
        print(f"标签: {', '.join(topic.tags)}")
        if hasattr(topic, 'recommendation_reason') and topic.recommendation_reason:
            print(f"\n推荐理由: {topic.recommendation_reason}")

    def _get_valid_input(self, prompt: str, validator: callable) -> str:
        """获取有效输入

        Args:
            prompt: 提示信息
            validator: 验证函数

        Returns:
            str: 有效的输入
        """
        while True:
            try:
                value = input(prompt)
                if validator(value):
                    return value
            except ValueError:
                pass
            print("输入无效，请重新输入")

# 使用示例
async def main():
    crew = TopicCrew()

    # 获取话题建议
    topics = await crew.suggest_topics(category="科技", count=5)

    # 获取人工决策
    topics = crew.get_human_decision(topics)

    # 查看选定的话题
    selected_topics = [t for t in topics if t.status == "selected"]
    print(f"\n=== 选定了 {len(selected_topics)} 个话题 ===")
    for topic in selected_topics:
        print(f"- {topic.title}")

if __name__ == "__main__":
    asyncio.run(main())
