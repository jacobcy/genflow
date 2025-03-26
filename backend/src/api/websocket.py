from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from ..core.websocket import websocket_manager
from ..db.session import get_db
from ..services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    db: Session = Depends(get_db)
):
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()

            # 处理心跳
            if data == "ping":
                websocket_manager.update_heartbeat(client_id)
                await websocket.send_text("pong")
                continue

            # 处理 AI 消息
            try:
                response = await ai_service.process_message(data)
                await websocket_manager.send_personal_message(response, client_id)
            except Exception as e:
                await websocket_manager.send_personal_message(
                    f"Error processing message: {str(e)}",
                    client_id
                )

    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
        await websocket_manager.broadcast(f"Client #{client_id} left the chat")
