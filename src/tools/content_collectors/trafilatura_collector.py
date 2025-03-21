from trafilatura import extract, fetch_url
from src.tools.base import ToolResult
from .base_collector import BaseCollector

class TrafilaturaCollector(BaseCollector):
    """Trafilatura工具包装"""
    name = "trafilatura"
    description = "通用网页内容提取工具"
    
    async def execute(self, url: str) -> ToolResult:
        try:
            downloaded = fetch_url(url)
            if downloaded is None:
                return self._create_error_result("Failed to fetch URL")
            
            result = extract(downloaded, include_links=True, 
                           include_images=True, include_tables=True,
                           output_format="json")
            
            if result is None:
                return self._create_error_result("No content extracted")
                
            return self._create_success_result(result)
        except Exception as e:
            return self._create_error_result(str(e)) 