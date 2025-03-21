from celery import shared_task
from typing import List
import logging
from app.models.article import Article
from app.models.platform import Publication
from app.extensions import db

logger = logging.getLogger(__name__)

@shared_task
def publish_article_task(article_id: int, platforms: List[str]):
    """异步发布文章到各个平台"""
    article = Article.query.get(article_id)
    if not article:
        logger.error(f"文章不存在: {article_id}")
        return
    
    results = []
    for platform in platforms:
        try:
            # 获取发布记录
            pub = Publication.query.filter_by(
                article_id=article_id,
                platform=platform
            ).first()
            
            if not pub:
                logger.error(f"发布记录不存在: {article_id} -> {platform}")
                continue
            
            # TODO: 调用具体平台的发布API
            # url = platform_api.publish(article.title, article.content)
            
            # 更新发布状态
            pub.status = 'published'
            # pub.url = url
            db.session.commit()
            
            results.append({
                'platform': platform,
                'status': 'success',
                # 'url': url
            })
            
        except Exception as e:
            logger.error(f"发布失败 {platform}: {str(e)}")
            results.append({
                'platform': platform,
                'status': 'failed',
                'error': str(e)
            })
    
    return results
