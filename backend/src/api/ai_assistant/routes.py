from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status

from backend.src.api.ai_assistant.deps import get_current_user_id, get_session_manager, verify_websocket_token
from backend.src.api.ai_assistant.models import (
    APIResponse,
    CreateSessionRequest,
    Message,
    SessionResponse,
    WebSocketEvent,
)
from backend.src.services.ai_writing.manager import WritingSessionManager

router = APIRouter(prefix="/api/ai-assistant", tags=["ai-assistant"])


@router.websocket("/sessions/{session_id}/realtime")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: UUID,
    session_manager: WritingSessionManager = Depends(get_session_manager),
):
    """WebSocket 实时连接端点"""
    user_id = await verify_websocket_token(websocket)
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    try:
        # 注册连接
        await session_manager.connect(session_id, user_id, websocket)

        while True:
            # 接收消息
            data = await websocket.receive_json()
            event = WebSocketEvent(
                type=data.get("type"),
                data=data.get("data", {}),
                timestamp=datetime.utcnow()
            )

            # 处理消息
            await session_manager.handle_event(session_id, user_id, event)

    except WebSocketDisconnect:
        # 断开连接
        await session_manager.disconnect(session_id, user_id)
    except Exception as e:
        # 发生错误
        await websocket.send_json({
            "type": "error",
            "data": {"message": str(e)},
            "timestamp": datetime.utcnow().isoformat()
        })
        await session_manager.disconnect(session_id, user_id)


@router.post("/sessions", response_model=APIResponse)
async def create_session(
    request: CreateSessionRequest,
    user_id: UUID = Depends(get_current_user_id),
    session_manager: WritingSessionManager = Depends(get_session_manager),
) -> APIResponse:
    """创建写作会话"""
    session = await session_manager.create_session(user_id, request)
    return APIResponse(
        data=SessionResponse(
            session_id=session.id,
            progress=session.progress,
            available_actions=session.available_actions,
        )
    )


@router.get("/sessions/{session_id}", response_model=APIResponse)
async def get_session_status(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session_manager: WritingSessionManager = Depends(get_session_manager),
) -> APIResponse:
    """获取会话状态"""
    session = await session_manager.get_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return APIResponse(
        data=SessionResponse(
            session_id=session.id,
            progress=session.progress,
            available_actions=session.available_actions,
        )
    )


@router.get("/sessions/{session_id}/messages", response_model=APIResponse)
async def get_session_messages(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session_manager: WritingSessionManager = Depends(get_session_manager),
) -> APIResponse:
    """获取会话消息历史"""
    messages = await session_manager.get_messages(session_id, user_id)
    return APIResponse(data=messages)


@router.post("/sessions/{session_id}/messages", response_model=APIResponse)
async def send_message(
    session_id: UUID,
    message: Message,
    user_id: UUID = Depends(get_current_user_id),
    session_manager: WritingSessionManager = Depends(get_session_manager),
) -> APIResponse:
    """发送消息到会话"""
    response = await session_manager.send_message(session_id, user_id, message)
    return APIResponse(data=response)
