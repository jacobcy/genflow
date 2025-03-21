"""内容采集模块"""
from typing import List, Dict, Optional, Union
import logging
import time
from dataclasses import dataclass
from abc import ABC, abstractmethod
import asyncio
import requests
from newspaper import Article, Config as NewsConfig
from newspaper.article import ArticleException
from pytrends.request import TrendReq
from firecrawl.firecrawl import FirecrawlApp
from pydantic import BaseModel
from .base_collector import (
    ContentItem, ContentParser, ContentSource,
    register_parser, register_source, BaseCollector
)
from src.tools.base import BaseTool, ToolResult
from .newspaper_collector import NewspaperCollector
from .trafilatura_collector import TrafilaturaCollector
from .readability_collector import ReadabilityCollector

@dataclass
class ContentItem:
    """统一的内容数据结构"""
    title: str
    url: str
    content: str
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    publish_date: Optional[str] = None
    source_type: str = "web"  # web, news, social 等
    source_tool: str = "unknown"  # newspaper, firecrawl, custom 等

class ContentParser(ABC):
    """内容解析器抽象基类"""
    
    @abstractmethod
    async def parse(self, url: str) -> Optional[ContentItem]:
        """解析内容"""
        pass

@register_parser("newspaper")
class NewspaperParser(ContentParser):
    """基于 newspaper3k 的解析器"""
    
    def __init__(self, language: str = 'zh'):
        self.config = NewsConfig()
        self.config.language = language
        self.config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        self.config.request_timeout = 10
        self.config.fetch_images = False
        
    async def parse(self, url: str, retries: int = 3) -> Optional[ContentItem]:
        for i in range(retries):
            try:
                article = Article(url, config=self.config)
                article.download()
                article.parse()
                
                try:
                    article.nlp()
                except:
                    pass
                
                return ContentItem(
                    title=article.title,
                    url=url,
                    content=article.text,
                    summary=article.summary,
                    keywords=article.keywords,
                    authors=article.authors,
                    publish_date=str(article.publish_date) if article.publish_date else None,
                    source_tool="newspaper"
                )
                
            except ArticleException as e:
                if i == retries - 1:
                    logging.warning(f"Newspaper解析失败 {url}: {str(e)}")
                    return None
                time.sleep(1)
            except Exception as e:
                logging.error(f"Newspaper解析错误 {url}: {str(e)}")
                return None
        return None

class FirecrawlParser(ContentParser):
    """基于 Firecrawl 的解析器"""
    
    def __init__(self, api_key: str):
        self.client = FirecrawlApp(api_key=api_key)
        
    async def parse(self, url: str) -> Optional[ContentItem]:
        try:
            response = await self.client.scrape_url(
                url=url,
                params={
                    'formats': ['markdown', 'json']
                }
            )
            
            if not response or not response.get('success'):
                return None
                
            data = response.get('data', {})
            markdown_content = data.get('markdown', '')
            json_data = data.get('json', {})
            
            return ContentItem(
                title=json_data.get('title', ''),
                url=url,
                content=markdown_content,
                summary=json_data.get('description', ''),
                source_tool="firecrawl"
            )
            
        except Exception as e:
            logging.error(f"Firecrawl解析错误 {url}: {str(e)}")
            return None

@register_parser("trafilatura")
class TrafilaturaParser(ContentParser):
    """基于 Trafilatura 的解析器"""
    
    def __init__(self):
        import trafilatura
        self.trafilatura = trafilatura
        
    async def parse(self, url: str) -> Optional[ContentItem]:
        try:
            # 下载网页
            downloaded = self.trafilatura.fetch_url(url)
            if not downloaded:
                return None
                
            # 提取内容
            result = self.trafilatura.extract(
                downloaded,
                output_format='json',
                with_metadata=True,
                include_comments=False,
                include_tables=True
            )
            
            if not result:
                return None
                
            # 解析 JSON
            import json
            data = json.loads(result)
            
            return ContentItem(
                title=data.get('title', ''),
                url=url,
                content=data.get('text', ''),
                summary=data.get('description', ''),
                authors=data.get('author', '').split(',') if data.get('author') else None,
                publish_date=data.get('date', None),
                source_tool="trafilatura"
            )
            
        except Exception as e:
            logging.error(f"Trafilatura解析错误 {url}: {str(e)}")
            return None

class ContentSource(ABC):
    """内容源抽象基类"""
    
    def __init__(self, parsers: List[ContentParser]):
        self.parsers = parsers
    
    @abstractmethod
    async def search(self, keyword: str) -> List[Dict]:
        """搜索内容"""
        pass
        
    async def get_content(self, url: str) -> Optional[ContentItem]:
        """获取内容，尝试所有可用的解析器
        
        Args:
            url: 文章URL
            
        Returns:
            Optional[ContentItem]: 解析结果
        """
        for parser in self.parsers:
            try:
                content = await parser.parse(url)
                if content and content.content:
                    return content
            except:
                continue
        return None

@register_source("google_trends")
class GoogleTrendsSource(ContentSource):
    """Google趋势源"""
    
    def __init__(self, config, parsers: List[ContentParser]):
        super().__init__(parsers)
        self.pytrends = TrendReq(hl=config.LANGUAGE)
        self.serp_api_key = getattr(config, 'SERP_API_KEY', None)
        
    async def search(self, keyword: str) -> List[Dict]:
        try:
            # 使用 Google Trends
            self.pytrends.build_payload(kw_list=[keyword])
            results = []
            
            # 获取相关话题
            related_topics = self.pytrends.related_topics()
            if related_topics and keyword in related_topics:
                for topic_type in ['top', 'rising']:
                    if topic_type in related_topics[keyword]:
                        df = related_topics[keyword][topic_type]
                        for _, row in df.iterrows():
                            results.append({
                                'title': row.get('topic_title', ''),
                                'url': f"https://trends.google.com/trends/explore?q={row.get('topic_title', '')}",
                                'summary': row.get('topic_type', '')
                            })
            
            # 获取相关查询
            related_queries = self.pytrends.related_queries()
            if keyword in related_queries:
                for query_type in ['top', 'rising']:
                    if query_type in related_queries[keyword]:
                        df = related_queries[keyword][query_type]
                        for _, row in df.iterrows():
                            query = row.get('query', '')
                            if query:
                                results.append({
                                    'title': query,
                                    'url': f"https://www.google.com/search?q={query}",
                                    'summary': f"{query_type.title()} related query"
                                })
            
            return results
            
        except Exception as e:
            logging.error(f"Google Trends 搜索失败: {str(e)}")
            return []

class FirecrawlSource(ContentSource):
    """Firecrawl搜索源"""
    
    def __init__(self, config, parsers: List[ContentParser]):
        super().__init__(parsers)
        self.client = FirecrawlApp(api_key=config.FIRECRAWL_API_KEY)
        
    async def search(self, keyword: str) -> List[Dict]:
        try:
            response = await self.client.search(
                query=keyword,
                params={
                    'scrapeOptions': {
                        'formats': ['markdown']
                    }
                }
            )
            
            if not response or not response.get('success'):
                return []
                
            results = []
            for item in response.get('data', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'summary': item.get('description', '')
                })
            return results
            
        except Exception as e:
            logging.error(f"Firecrawl 搜索失败: {str(e)}")
            return []

class ContentCollector(BaseTool):
    """内容采集聚合工具"""
    name = "content_collector"
    description = "多源内容采集工具"
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.tools = [
            NewspaperCollector(config),
            TrafilaturaCollector(config),
            ReadabilityCollector(config)
        ]
    
    async def execute(self, url: str) -> ToolResult:
        """尝试使用所有工具采集内容，返回最佳结果"""
        results = []
        for tool in self.tools:
            result = await tool.execute(url)
            if result.success:
                results.append((tool.name, result))
        
        if not results:
            return self._create_error_result("All tools failed to extract content")
        
        # 选择最佳结果（这里可以实现更复杂的选择逻辑）
        best_result = max(results, key=lambda x: len(str(x[1].data)))
        return self._create_success_result(
            best_result[1].data,
            {"tool_used": best_result[0]}
        ) 