"""反馈模型

该模块定义了系统中各种反馈相关的数据模型，用于收集和处理用户和系统的反馈信息。
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ResearchFeedback:
    """研究反馈

    用于收集对研究结果的反馈，可以来自人类或者系统。
    """
    feedback_text: str
    accuracy_rating: Optional[float] = None  # 1-10的准确性评分
    completeness_rating: Optional[float] = None  # 1-10的完整性评分
    suggested_improvements: List[str] = field(default_factory=list)
    feedback_source: str = "system"  # system或human

    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "feedback_text": self.feedback_text,
            "accuracy_rating": self.accuracy_rating,
            "completeness_rating": self.completeness_rating,
            "suggested_improvements": self.suggested_improvements,
            "feedback_source": self.feedback_source
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ResearchFeedback':
        """从字典创建实例"""
        return cls(
            feedback_text=data["feedback_text"],
            accuracy_rating=data.get("accuracy_rating"),
            completeness_rating=data.get("completeness_rating"),
            suggested_improvements=data.get("suggested_improvements", []),
            feedback_source=data.get("feedback_source", "system")
        )

@dataclass
class ContentFeedback:
    """内容反馈

    用于收集对生成内容的反馈。
    """
    content_id: str
    feedback_text: str
    rating: Optional[float] = None  # 1-10的综合评分
    feedback_categories: List[str] = field(default_factory=list)  # 例如：'clarity', 'relevance', 'accuracy'
    created_at: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None

    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "content_id": self.content_id,
            "feedback_text": self.feedback_text,
            "rating": self.rating,
            "feedback_categories": self.feedback_categories,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ContentFeedback':
        """从字典创建实例"""
        feedback = cls(
            content_id=data["content_id"],
            feedback_text=data["feedback_text"],
            rating=data.get("rating"),
            feedback_categories=data.get("feedback_categories", []),
            user_id=data.get("user_id")
        )

        if "created_at" in data:
            feedback.created_at = datetime.fromisoformat(data["created_at"])

        return feedback
