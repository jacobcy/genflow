from typing import List, Dict
from app.models.article import Article
from app.models.platform import Publication
from app.extensions import db
from app.tasks.article_tasks import publish_article_task

class ArticleService:
    def create_article(self, title: str, content: str, author_id: int) -> Article:
        """创建新文章"""
        article = Article(
            title=title,
            content=content,
            author_id=author_id
        )
        db.session.add(article)
        db.session.commit()
        return article
    
    def get_article(self, article_id: int) -> Article:
        """获取文章详情"""
        return Article.query.get_or_404(article_id)
    
    def publish_article(self, article_id: int, platforms: List[str]) -> Dict:
        """发布文章到指定平台"""
        article = self.get_article(article_id)
        
        # 创建发布记录
        publications = []
        for platform in platforms:
            pub = Publication(
                article_id=article_id,
                platform=platform
            )
            db.session.add(pub)
            publications.append(pub)
        
        db.session.commit()
        
        # 异步发布任务
        task = publish_article_task.delay(article_id, platforms)
        return task
