from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    token: str
    expiresIn: int


class TokenPair(BaseModel):
    accessToken: Token
    refreshToken: Token


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    name: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str
    name: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDB(UserBase):
    id: str
    is_active: bool = True


class User(UserInDB):
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., description="用户密码")


class LoginResponse(BaseModel):
    tokens: TokenPair
    user: User


class RefreshTokenRequest(BaseModel):
    refreshToken: str = Field(..., description="刷新令牌")


class RefreshTokenResponse(BaseModel):
    accessToken: Token


class VerifyResponse(BaseModel):
    authenticated: bool = True
    user: User


class LogoutResponse(BaseModel):
    success: bool = True


class ErrorResponse(BaseModel):
    code: str
    message: str
    target: Optional[str] = None
    source: Optional[str] = None
