from typing import AsyncGenerator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer

from backend.src.core.security import verify_access_token
from backend.src.services.ai_writing.manager import WritingSessionManager


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> UUID:
    """获取当前用户ID"""
    user_id = await verify_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return user_id


async def get_session_manager() -> WritingSessionManager:
    """获取写作会话管理器"""
    manager = WritingSessionManager()
    try:
        yield manager
    finally:
        await manager.cleanup()


async def verify_websocket_token(websocket: WebSocket) -> Optional[UUID]:
    """验证 WebSocket 连接的令牌"""
    try:
        token = websocket.headers.get("authorization", "").split(" ")[1]
        user_id = await verify_access_token(token)
        return user_id
    except Exception:
        return None
