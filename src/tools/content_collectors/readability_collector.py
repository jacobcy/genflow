import requests
from readability import Document
from src.tools.base import ToolResult
from .base_collector import BaseCollector

class ReadabilityCollector(BaseCollector):
    """Readability工具包装"""
    name = "readability"
    description = "网页可读性优化工具"
    
    async def execute(self, url: str) -> ToolResult:
        try:
            response = requests.get(url)
            doc = Document(response.text)
            
            return self._create_success_result({
                "title": doc.title(),
                "content": doc.summary(),
                "short_title": doc.short_title(),
            })
        except Exception as e:
            return self._create_error_result(str(e)) 