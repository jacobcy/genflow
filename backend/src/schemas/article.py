from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, constr


# 用户简化信息
class UserInfo(BaseModel):
    id: UUID
    name: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


# 标签相关模型
class TagBase(BaseModel):
    name: constr(min_length=1, max_length=20)


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    class Config:
        from_attributes = True


# 文章相关模型
class ArticleBase(BaseModel):
    title: constr(min_length=2, max_length=100)
    content: constr(min_length=10, max_length=50000)
    summary: Optional[constr(max_length=200)] = None
    cover_image: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list, max_items=5)

    @validator("tags")
    def validate_tags(cls, v):
        if v and any(len(tag) > 20 for tag in v):
            raise ValueError("标签长度不能超过20个字符")
        return v


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[constr(min_length=2, max_length=100)] = None
    content: Optional[constr(min_length=10, max_length=50000)] = None
    summary: Optional[constr(max_length=200)] = None
    cover_image: Optional[str] = None
    tags: Optional[List[str]] = None

    @validator("tags")
    def validate_tags(cls, v):
        if v and any(len(tag) > 20 for tag in v):
            raise ValueError("标签长度不能超过20个字符")
        if v and len(v) > 5:
            raise ValueError("标签数量不能超过5个")
        return v


class ArticleListResponse(BaseModel):
    id: UUID
    title: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    status: str
    author: UserInfo
    created_at: datetime
    published_at: Optional[datetime] = None
    view_count: int
    tags: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True

    @validator("tags", pre=True)
    def extract_tag_names(cls, v):
        if isinstance(v, list) and v and hasattr(v[0], "name"):
            return [tag.name for tag in v]
        return v


class ArticleResponse(ArticleBase):
    id: UUID
    status: str
    author_id: UUID
    author: UserInfo
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    view_count: int

    class Config:
        from_attributes = True

    @validator("tags", pre=True)
    def extract_tag_names(cls, v):
        if isinstance(v, list) and v and hasattr(v[0], "name"):
            return [tag.name for tag in v]
        return v


class ArticlePublishResponse(BaseModel):
    id: UUID
    status: str
    published_at: datetime

    class Config:
        from_attributes = True
