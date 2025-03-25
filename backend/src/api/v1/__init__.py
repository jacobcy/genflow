from fastapi import APIRouter

from api.v1.endpoints import auth, users, articles


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
