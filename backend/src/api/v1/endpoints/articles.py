from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Body, HTTPException, status, Path
from sqlalchemy.orm import Session

from db.session import get_db
from models.article import ArticleStatus
from schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListResponse,
    ArticlePublishResponse
)
from schemas.common import APIResponse
from services.article_service import ArticleService
from services.auth_service import get_current_user
from schemas.auth import User as UserSchema


router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse[ArticleResponse])
async def create_article(
    article_in: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """创建文章"""
    article_service = ArticleService(db)
    article = article_service.create_article(
        data=article_in,
        author_id=current_user.id
    )
    return APIResponse(data=article)


@router.get("", response_model=APIResponse[List[ArticleListResponse]])
async def get_articles(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="文章状态: draft或published"),
    tags: Optional[List[str]] = Query(None, description="标签筛选"),
    created_after: Optional[datetime] = Query(None, description="创建时间起始"),
    created_before: Optional[datetime] = Query(None, description="创建时间结束"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """获取文章列表"""
    # 验证status参数
    if status and status not in [ArticleStatus.DRAFT.value, ArticleStatus.PUBLISHED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的状态参数: {status}"
        )

    article_service = ArticleService(db)
    result = article_service.get_articles(
        page=page,
        per_page=per_page,
        status=status,
        tags=tags,
        created_after=created_after,
        created_before=created_before
    )

    return APIResponse(
        data=result["items"],
        metadata={
            "page": result["page"],
            "pageSize": result["per_page"],
            "total": result["total"],
            "totalPages": result["total_pages"]
        }
    )


@router.get("/{id}", response_model=APIResponse[ArticleResponse])
async def get_article(
    id: UUID = Path(..., description="文章ID"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """获取文章详情"""
    article_service = ArticleService(db)
    article = article_service.get_article(id)

    # 增加浏览量（仅当不是作者本人查看时）
    if str(article.author_id) != str(current_user.id):
        article_service.increment_view_count(id)

    return APIResponse(data=article)


@router.put("/{id}", response_model=APIResponse[ArticleResponse])
async def update_article(
    id: UUID = Path(..., description="文章ID"),
    article_in: ArticleUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """更新文章"""
    article_service = ArticleService(db)
    article = article_service.update_article(
        article_id=id,
        data=article_in,
        current_user_id=current_user.id
    )
    return APIResponse(data=article)


@router.post("/{id}/publish", response_model=APIResponse[ArticlePublishResponse])
async def publish_article(
    id: UUID = Path(..., description="文章ID"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """发布文章"""
    article_service = ArticleService(db)
    article = article_service.publish_article(
        article_id=id,
        current_user_id=current_user.id
    )
    return APIResponse(data=article)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    id: UUID = Path(..., description="文章ID"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """删除文章"""
    article_service = ArticleService(db)
    article_service.delete_article(
        article_id=id,
        current_user_id=current_user.id
    )
    return None
