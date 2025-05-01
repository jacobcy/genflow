"""反馈模块

提供反馈相关的数据模型和操作。
"""

from .feedback import ResearchFeedback, ContentFeedback
from .feedback_factory import FeedbackFactory

__all__ = [
    'ResearchFeedback',
    'ContentFeedback',
    'FeedbackFactory'
]