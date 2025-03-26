"""
控制AI - GenFlow内容生产系统的智能控制中心

该模块提供自然语言理解和命令式接口的统一处理，
连接用户与专业团队（选题、研究、写作、风格和审核），
实现内容创作全流程的智能协调。

主要组件：
- ControlAI：核心控制AI类，实现自然语言处理和任务规划
- API：FastAPI实现的HTTP接口，支持REST和WebSocket通信
- Clients：与各专业团队API交互的客户端
"""

from core.control_ai.control_ai import ControlAI, IntentRecognitionResult, TaskPlan, ControlAIResponse
from core.control_ai.clients import (
    BaseClient,
    TopicClient,
    ResearchClient,
    WritingClient,
    StyleClient,
    ReviewClient,
    ClientFactory
)

__all__ = [
    'ControlAI',
    'IntentRecognitionResult',
    'TaskPlan',
    'ControlAIResponse',
    'BaseClient',
    'TopicClient',
    'ResearchClient',
    'WritingClient',
    'StyleClient',
    'ReviewClient',
    'ClientFactory'
]

__version__ = '1.0.0'
