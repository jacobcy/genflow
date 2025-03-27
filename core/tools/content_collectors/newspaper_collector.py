import newspaper
from core.tools.base import ToolResult
from .base_collector import BaseCollector

class NewspaperCollector(BaseCollector):
    """Newspaper3k工具包装"""
    name = "newspaper"
    description = "新闻文章解析工具"

    async def execute(self, url: str) -> ToolResult:
        try:
            article = newspaper.Article(url)
            article.download()
            article.parse()
            article.nlp()

            return self._create_success_result({
                "title": article.title,
                "text": article.text,
                "summary": article.summary,
                "keywords": article.keywords,
                "authors": article.authors,
                "publish_date": article.publish_date,
                "top_image": article.top_image
            })
        except Exception as e:
            return self._create_error_result(str(e))

    async def _run(self, url: str) -> ToolResult:
        """CrewAI 所需的内部执行方法"""
        return await self.execute(url)
