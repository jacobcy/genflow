from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from typing import Optional

from db.session import get_db
from schemas.common import APIResponse
from schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    VerifyResponse,
    LogoutResponse,
    User
)
from services.auth_service import AuthService, get_current_user
from core.exceptions import AuthException
from core.config import settings
from api.deps import get_refresh_token_from_cookie


router = APIRouter()


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """用户登录，获取JWT令牌"""
    auth_service = AuthService(db)
    result = auth_service.login(email=login_data.email, password=login_data.password)
    if not result:
        raise AuthException(
            error_code="AUTH_001",
            message="邮箱或密码不正确",
            target="credentials",
            source="auth.login"
        )

    # 设置刷新令牌到cookie
    response.set_cookie(
        key="refresh_token",
        value=result["tokens"]["refreshToken"]["token"],
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        samesite="lax",
        secure=not settings.DEBUG
    )

    return APIResponse(data=result)


@router.post("/refresh", response_model=APIResponse[RefreshTokenResponse])
async def refresh_token(
    refresh_data: Optional[RefreshTokenRequest] = None,
    cookie_token: Optional[str] = Depends(get_refresh_token_from_cookie),
    db: Session = Depends(get_db)
):
    """使用刷新令牌获取新的访问令牌"""
    auth_service = AuthService(db)

    # 优先从请求体中获取token，如果没有则从cookie中获取
    refresh_token = refresh_data.refreshToken if refresh_data and refresh_data.refreshToken else cookie_token

    if not refresh_token:
        raise AuthException(
            error_code="AUTH_002",
            message="无效的刷新令牌",
            target="refreshToken",
            source="auth.refresh"
        )

    result = auth_service.refresh_token(refresh_token)
    if not result:
        raise AuthException(
            error_code="AUTH_002",
            message="无效的刷新令牌",
            target="refreshToken",
            source="auth.refresh"
        )
    return APIResponse(data={"accessToken": result})


@router.post("/logout", response_model=APIResponse[LogoutResponse])
async def logout(
    response: Response,
    _: User = Depends(get_current_user)
):
    """用户登出，删除客户端令牌和cookie"""
    # 清除refresh token cookie
    response.delete_cookie(key="refresh_token")

    return APIResponse(data={"success": True})


@router.get("/verify", response_model=APIResponse[VerifyResponse])
async def verify_token(current_user: User = Depends(get_current_user)):
    """验证当前用户的令牌"""
    user_data = {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
        "name": current_user.name,
        "is_active": current_user.is_active
    }
    return APIResponse(data={"authenticated": True, "user": user_data})
