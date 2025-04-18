from core.models.feedback import ResearchFeedback
from core.models.research.research import BasicResearch

import logging

logger = logging.getLogger("research_crew")


def get_human_feedback(self, result: BasicResearch) -> ResearchFeedback:
    """获取研究结果的人类反馈

    Args:
        result: 研究结果对象

    Returns:
        ResearchFeedback: 反馈对象
    """
    logger.info("开始收集研究结果的人类反馈")

    # 在实际应用中，这里应该调用某种用户界面来收集反馈
    # 这里我们返回一个样例反馈
    feedback = ResearchFeedback(
        feedback_text="整体研究质量高，结构清晰，观点平衡，但可以增加一些最新发展趋势",
        accuracy_rating=8.5,
        completeness_rating=8.0,
        suggested_improvements=["增加最新行业发展趋势", "加强数据可视化", "扩展解决方案分析"],
        feedback_source="human"
    )

    # 如果有上次工作流结果，则更新反馈
    if self.last_workflow_result and self.last_workflow_result.result == result:
        self.last_workflow_result.feedback = feedback

    logger.info("人类反馈收集完成")
    return feedback
