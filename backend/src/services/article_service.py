from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
import uuid

from sqlalchemy import desc, asc, and_, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import functions as func

from models.article import Article, Tag, ArticleStatus
from models.user import User
from schemas.article import ArticleCreate, ArticleUpdate
from core.exceptions import ResourceException


class ArticleService:
    def __init__(self, db: Session):
        self.db = db

    def get_articles(
        self,
        page: int = 1,
        per_page: int = 10,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        author_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """获取文章列表"""
        query = self.db.query(Article).filter(Article.is_deleted == False)

        # 应用筛选条件
        if status:
            query = query.filter(Article.status == status)

        if tags:
            query = query.join(Article.tags).filter(Tag.name.in_(tags))

        if created_after:
            query = query.filter(Article.created_at >= created_after)

        if created_before:
            query = query.filter(Article.created_at <= created_before)

        if author_id:
            query = query.filter(Article.author_id == author_id)

        # 获取总数
        total = query.count()

        # 排序和分页
        query = query.order_by(desc(Article.created_at))
        query = query.offset((page - 1) * per_page).limit(per_page)

        # 加载关联数据
        query = query.options(
            joinedload(Article.author),
            joinedload(Article.tags)
        )

        articles = query.all()

        return {
            "items": articles,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    def get_article(self, article_id: UUID) -> Article:
        """获取文章详情"""
        article = self.db.query(Article).filter(
            Article.id == article_id,
            Article.is_deleted == False
        ).options(
            joinedload(Article.author),
            joinedload(Article.tags)
        ).first()

        if not article:
            raise ResourceException(
                error_code="RES_001",
                message="文章不存在",
                target="article_id",
                source="article_service.get_article"
            )

        return article

    def increment_view_count(self, article_id: UUID) -> None:
        """增加文章浏览量"""
        article = self.get_article(article_id)
        article.view_count += 1
        self.db.commit()

    def create_article(
        self,
        data: ArticleCreate,
        author_id: UUID
    ) -> Article:
        """创建文章"""
        # 确保作者存在
        author = self.db.query(User).filter(User.id == author_id).first()
        if not author:
            raise ResourceException(
                error_code="RES_001",
                message="作者不存在",
                target="author_id",
                source="article_service.create_article"
            )

        # 创建文章
        article = Article(
            id=uuid.uuid4(),
            title=data.title,
            content=data.content,
            summary=data.summary,
            cover_image=data.cover_image,
            author_id=author_id,
            status=ArticleStatus.DRAFT.value
        )

        # 处理标签
        if data.tags:
            article.tags = self._get_or_create_tags(data.tags)

        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def update_article(
        self,
        article_id: UUID,
        data: ArticleUpdate,
        current_user_id: UUID
    ) -> Article:
        """更新文章"""
        article = self.get_article(article_id)

        # 权限检查
        if article.author_id != current_user_id and self._is_not_admin(current_user_id):
            raise ResourceException(
                error_code="RES_003",
                message="无权限修改此文章",
                target="article_id",
                source="article_service.update_article"
            )

        # 已发布文章不能修改状态
        if article.status == ArticleStatus.PUBLISHED.value:
            if data.title:
                article.title = data.title
            if data.summary:
                article.summary = data.summary
            if data.cover_image:
                article.cover_image = data.cover_image
            if data.tags:
                article.tags = self._get_or_create_tags(data.tags)
            # 已发布文章不能修改内容
        else:
            # 草稿状态可以修改所有内容
            if data.title:
                article.title = data.title
            if data.content:
                article.content = data.content
            if data.summary:
                article.summary = data.summary
            if data.cover_image:
                article.cover_image = data.cover_image
            if data.tags is not None:
                article.tags = self._get_or_create_tags(data.tags)

        self.db.commit()
        self.db.refresh(article)
        return article

    def publish_article(
        self,
        article_id: UUID,
        current_user_id: UUID
    ) -> Article:
        """发布文章"""
        article = self.get_article(article_id)

        # 权限检查
        if article.author_id != current_user_id and self._is_not_admin(current_user_id):
            raise ResourceException(
                error_code="RES_003",
                message="无权限发布此文章",
                target="article_id",
                source="article_service.publish_article"
            )

        # 已发布的文章不能重复发布
        if article.status == ArticleStatus.PUBLISHED.value:
            raise ResourceException(
                error_code="RES_002",
                message="文章已发布",
                target="article_id",
                source="article_service.publish_article"
            )

        # 发布文章
        article.status = ArticleStatus.PUBLISHED.value
        article.published_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(article)
        return article

    def delete_article(
        self,
        article_id: UUID,
        current_user_id: UUID
    ) -> None:
        """删除文章（软删除）"""
        article = self.get_article(article_id)

        # 权限检查
        if article.author_id != current_user_id and self._is_not_admin(current_user_id):
            raise ResourceException(
                error_code="RES_003",
                message="无权限删除此文章",
                target="article_id",
                source="article_service.delete_article"
            )

        # 软删除
        article.is_deleted = True

        self.db.commit()

    def _get_or_create_tags(self, tag_names: List[str]) -> List[Tag]:
        """获取或创建标签"""
        tags = []
        for name in tag_names:
            tag = self.db.query(Tag).filter(Tag.name == name).first()
            if not tag:
                tag = Tag(name=name)
                self.db.add(tag)
            tags.append(tag)
        return tags

    def _is_not_admin(self, user_id: UUID) -> bool:
        """检查用户是否不是管理员"""
        user = self.db.query(User).filter(User.id == user_id).first()
        return not user or user.role != "admin"
