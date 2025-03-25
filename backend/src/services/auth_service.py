from datetime import datetime, timedelta
from typing import Dict, Optional, Union
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from core.config import settings
from core.security import TokenPayload, create_access_token, create_refresh_token
from db.session import get_db
from models.user import User
from schemas.auth import Token, TokenPair, User as UserSchema
from services.user_service import UserService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def login(self, email: str, password: str) -> Optional[Dict]:
        user = self.user_service.authenticate(email=email, password=password)
        if not user:
            return None
        if not self.user_service.is_active(user):
            return None

        # 生成令牌
        access_token = create_access_token(user.id, role=user.role)
        refresh_token = create_refresh_token(user.id, role=user.role)

        # 格式化响应
        return {
            "tokens": {
                "accessToken": {
                    "token": access_token,
                    "expiresIn": settings.ACCESS_TOKEN_EXPIRE_SECONDS
                },
                "refreshToken": {
                    "token": refresh_token,
                    "expiresIn": settings.REFRESH_TOKEN_EXPIRE_SECONDS
                }
            },
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role,
                "name": user.name,
                "is_active": user.is_active
            }
        }

    def refresh_token(self, refresh_token: str) -> Optional[Token]:
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_data = TokenPayload(**payload)

            # 检查令牌是否过期
            if token_data.exp and datetime.fromtimestamp(token_data.exp) < datetime.now():
                return None

            user = self.user_service.get_by_id(token_data.sub)
            if not user:
                return None
            if not self.user_service.is_active(user):
                return None

            # 生成新的访问令牌
            access_token = create_access_token(user.id, role=user.role)
            return Token(token=access_token, expiresIn=settings.ACCESS_TOKEN_EXPIRE_SECONDS)

        except (JWTError, ValueError):
            return None

    def verify_token(self, token: str) -> Optional[Dict]:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_data = TokenPayload(**payload)

            # 检查令牌是否过期
            if token_data.exp and datetime.fromtimestamp(token_data.exp) < datetime.now():
                return None

            user = self.user_service.get_by_id(token_data.sub)
            if not user:
                return None
            if not self.user_service.is_active(user):
                return None

            return {
                "authenticated": True,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "role": user.role,
                    "name": user.name,
                    "is_active": user.is_active
                }
            }

        except (JWTError, ValueError):
            return None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    auth_service = AuthService(db)
    result = auth_service.verify_token(token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db.query(User).filter(User.id == uuid.UUID(result["user"]["id"])).first()
