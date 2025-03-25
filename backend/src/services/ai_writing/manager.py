from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import WebSocket, WebSocketDisconnect

from backend.src.api.ai_assistant.models import (
    CreateSessionRequest,
    Message,
    WebSocketEvent,
    WritingProgress,
    WritingStage,
    ActionButton,
    MessageType
)
from core.services.writing.interface import WritingInterface


class WritingSession:
    """写作会话"""
    def __init__(self, session_id: UUID, user_id: UUID, request: CreateSessionRequest):
        self.id = session_id
        self.user_id = user_id
        self.context = request.context
        self.progress = WritingProgress(
            stage=request.initial_stage,
            status="idle",
            progress=0
        )
        self.available_actions: List[ActionButton] = [
            ActionButton(
                id="generate_outline",
                text="生成大纲",
                action="generate_outline",
                type="primary"
            ),
            ActionButton(
                id="analyze_topic",
                text="分析主题",
                action="analyze_topic",
                type="secondary"
            )
        ]
        self.messages: List[Message] = []
        self.websocket: Optional[WebSocket] = None


class WritingSessionManager:
    """写作会话管理器"""
    def __init__(self):
        self.sessions: Dict[UUID, WritingSession] = {}
        self.core_interface = WritingInterface()

    async def cleanup(self):
        """清理资源"""
        for session_id in list(self.sessions.keys()):
            await self.core_interface.close_session(session_id)
        self.sessions.clear()

    async def create_session(self, user_id: UUID, request: CreateSessionRequest) -> WritingSession:
        """创建新的写作会话"""
        session_id = uuid4()
        session = WritingSession(session_id, user_id, request)
        self.sessions[session_id] = session

        # 创建 core 模块会话
        await self.core_interface.create_session(
            session_id=session_id,
            topic=request.context.title or "",
            style={
                "target_length": request.context.target_length
            }
        )

        return session

    async def get_session(self, session_id: UUID, user_id: UUID) -> Optional[WritingSession]:
        """获取会话信息"""
        session = self.sessions.get(session_id)
        if session and session.user_id == user_id:
            return session
        return None

    async def connect(self, session_id: UUID, user_id: UUID, websocket: WebSocket):
        """建立 WebSocket 连接"""
        session = await self.get_session(session_id, user_id)
        if session:
            session.websocket = websocket
            # 发送当前状态
            await websocket.send_json({
                "type": "session_state",
                "data": {
                    "progress": session.progress.dict(),
                    "available_actions": [action.dict() for action in session.available_actions]
                },
                "timestamp": datetime.utcnow().isoformat()
            })

    async def disconnect(self, session_id: UUID, user_id: UUID):
        """断开 WebSocket 连接"""
        session = await self.get_session(session_id, user_id)
        if session:
            session.websocket = None

    async def handle_event(self, session_id: UUID, user_id: UUID, event: WebSocketEvent):
        """处理 WebSocket 事件"""
        session = await self.get_session(session_id, user_id)
        if not session or not session.websocket:
            return

        try:
            # 根据事件类型调用相应的处理方法
            if event.type == "generate_outline":
                result = await self.core_interface.generate_outline(session_id)
                await self._send_message(session, "ai", result["outline"], MessageType.OUTLINE)

            elif event.type == "generate_content":
                section_id = event.data.get("section_id")
                if section_id:
                    result = await self.core_interface.generate_content(session_id, section_id)
                    await self._send_message(session, "ai", result["content"], MessageType.TEXT)

            elif event.type == "optimize_content":
                content = event.data.get("content")
                if content:
                    result = await self.core_interface.optimize_content(session_id, content)
                    await self._send_message(session, "ai", result["optimized_content"], MessageType.TEXT)

            elif event.type == "analyze_content":
                content = event.data.get("content")
                if content:
                    result = await self.core_interface.analyze_content(session_id, content)
                    await self._send_message(session, "ai", result["analysis"], MessageType.ANALYSIS)

            elif event.type == "get_suggestions":
                content = event.data.get("content")
                if content:
                    suggestions = await self.core_interface.get_suggestions(session_id, content)
                    await self._send_message(session, "ai", suggestions, MessageType.SUGGESTION)

        except Exception as e:
            await session.websocket.send_json({
                "type": "error",
                "data": {"message": str(e)},
                "timestamp": datetime.utcnow().isoformat()
            })

    async def _send_message(self, session: WritingSession, role: str, content: str, msg_type: MessageType):
        """发送消息到会话"""
        message = Message(
            id=uuid4(),
            role=role,
            content=content,
            type=msg_type,
            timestamp=datetime.utcnow()
        )
        session.messages.append(message)

        if session.websocket:
            await session.websocket.send_json({
                "type": "message",
                "data": message.dict(),
                "timestamp": datetime.utcnow().isoformat()
            })

    async def get_messages(self, session_id: UUID, user_id: UUID) -> List[Message]:
        """获取会话消息历史"""
        session = await self.get_session(session_id, user_id)
        if session:
            return session.messages
        return []

    async def send_message(self, session_id: UUID, user_id: UUID, message: Message) -> Message:
        """发送消息到会话"""
        session = await self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        # 将用户消息添加到历史记录
        session.messages.append(message)

        # 如果是用户消息，则需要处理并生成回复
        if message.role == "user":
            if message.type == MessageType.TEXT:
                # 根据消息内容调用相应的处理方法
                if "生成大纲" in message.content:
                    result = await self.core_interface.generate_outline(session_id)
                    await self._send_message(session, "ai", result["outline"], MessageType.OUTLINE)
                elif "优化内容" in message.content:
                    result = await self.core_interface.optimize_content(session_id, message.content)
                    await self._send_message(session, "ai", result["optimized_content"], MessageType.TEXT)
                else:
                    # 默认生成内容
                    result = await self.core_interface.generate_content(session_id, "default")
                    await self._send_message(session, "ai", result["content"], MessageType.TEXT)

        return message
