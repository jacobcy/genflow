from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import logging
from crewai.tasks.task_output import TaskOutput
from core.models.research.research import BasicResearch
from core.models.feedback import ResearchFeedback

# 配置日志
logger = logging.getLogger("research_result")

@dataclass
class ResearchWorkflowResult:
    """研究工作流结果模型

    保存研究工作流执行的完整结果，包括所有任务输出和最终研究报告
    """
    # 标识信息
    id: str = field(default_factory=lambda: f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: datetime = field(default_factory=datetime.now)

    # 输入参数
    topic: str = ""
    topic_id: Optional[str] = None

    # 工作流执行结果
    background_research: Optional[TaskOutput] = None
    expert_insights: Optional[TaskOutput] = None
    data_analysis: Optional[TaskOutput] = None
    research_report: Optional[TaskOutput] = None

    # 最终研究结果
    result: Optional[BasicResearch] = None

    # 反馈信息
    feedback: Optional[ResearchFeedback] = None

    # 新添加的属性
    experts: List[str] = field(default_factory=list)
    research_results: str = ""

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典形式的结果
        """
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "topic": self.topic,
            "topic_id": self.topic_id,
            "background_research": getattr(self.background_research, "raw_output", str(self.background_research)) if self.background_research else None,
            "expert_insights": getattr(self.expert_insights, "raw_output", str(self.expert_insights)) if self.expert_insights else None,
            "data_analysis": getattr(self.data_analysis, "raw_output", str(self.data_analysis)) if self.data_analysis else None,
            "research_report": getattr(self.research_report, "raw_output", str(self.research_report)) if self.research_report else None,
            "result": self.result.to_dict() if self.result else None,
            "feedback": self.feedback.to_dict() if self.feedback else None,
            "experts": self.experts,
            "research_results": self.research_results,
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        """转换为JSON字符串

        Returns:
            str: JSON字符串形式的结果
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def save_to_file(self, filepath: str) -> None:
        """保存结果到文件

        Args:
            filepath: 文件路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        logger.info(f"研究工作流结果已保存到文件: {filepath}")
