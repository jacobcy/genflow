"""风格化团队

该模块实现了负责内容风格化的智能体团队，主要任务是根据不同平台的风格要求
对内容进行改写和适配。支持直接从文本改写风格，不依赖于话题和大纲。
"""

from .style_crew import StyleCrew, StyleWorkflowResult
from .style_adapter import StyleTeamAdapter

__all__ = ['StyleCrew', 'StyleWorkflowResult', 'StyleTeamAdapter']
