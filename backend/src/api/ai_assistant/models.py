from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field


class WritingStage(str, Enum):
    """写作阶段"""
    TOPIC = "topic"         # 主题规划
    WRITING = "writing"     # 写作中
    OPTIMIZATION = "optimization"  # 优化
    REVIEW = "review"       # 审阅


class WritingProgress(BaseModel):
    """写作进度"""
    stage: WritingStage
    status: str = Field(..., description="idle | processing | waiting")
    progress: float = Field(..., ge=0, le=100)
    estimated_time: Optional[int] = None
    current_step: Optional[str] = None


class MessageType(str, Enum):
    """消息类型"""
    TEXT = "text"
    MARKDOWN = "markdown"
    SUGGESTION = "suggestion"
    OUTLINE = "outline"
    ANALYSIS = "analysis"


class Message(BaseModel):
    """消息模型"""
    id: UUID
    role: str = Field(..., description="ai | user | system")
    content: str
    type: MessageType
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class WebSocketEvent(BaseModel):
    """WebSocket 事件模型"""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionContext(BaseModel):
    """会话上下文"""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    target_length: Optional[int] = None


class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    article_id: Optional[UUID] = None
    initial_stage: WritingStage = WritingStage.TOPIC
    context: SessionContext


class ActionButton(BaseModel):
    """动作按钮"""
    id: str
    text: str
    action: str
    type: str = Field(..., description="primary | secondary | warning")
    disabled: bool = False
    tooltip: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """会话响应"""
    session_id: UUID
    progress: WritingProgress
    available_actions: List[ActionButton]


class APIResponse(BaseModel):
    """API 统一响应格式"""
    data: Any
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "timestamp": datetime.utcnow(),
            "request_id": None
        }
    )


class ErrorResponse(BaseModel):
    """错误响应"""
    error: Dict[str, Any]
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "timestamp": datetime.utcnow(),
            "request_id": None
        }
    )
