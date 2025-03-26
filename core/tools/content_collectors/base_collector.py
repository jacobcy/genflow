from typing import Dict, List, Optional, ClassVar
from core.tools.base import BaseTool, ToolResult
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ContentItem:
    """内容数据结构"""
    title: str
    url: str
    content: str
    summary: Optional[str] = None
    keywords: List[str] = None
    authors: List[str] = None
    publish_date: Optional[datetime] = None
    source_type: str = "web"
    source_tool: str = "unknown"

class BaseCollector(BaseTool):
    """内容采集器基类"""

    @abstractmethod
    async def execute(self, url: str) -> ToolResult:
        """执行内容采集"""
        pass

class ContentParser(ABC):
    """内容解析器基类"""

    # 类级别缓存
    _instances: ClassVar[Dict[str, 'ContentParser']] = {}

    @classmethod
    def get_instance(cls, parser_type: str) -> 'ContentParser':
        """获取解析器实例"""
        if parser_type not in cls._instances:
            parser_class = PARSER_REGISTRY.get(parser_type)
            if not parser_class:
                raise ValueError(f"Unknown parser type: {parser_type}")
            cls._instances[parser_type] = parser_class()
        return cls._instances[parser_type]

    @classmethod
    def clear_cache(cls):
        """清除所有缓存的实例"""
        cls._instances.clear()

    @abstractmethod
    async def parse(self, url: str) -> ContentItem:
        """解析URL内容"""
        pass

    async def health_check(self) -> bool:
        """检查解析器健康状态"""
        try:
            return True
        except Exception:
            return False

class ContentSource(ABC):
    """内容源基类"""

    # 类级别缓存
    _instances: ClassVar[Dict[str, 'ContentSource']] = {}

    @classmethod
    def get_instance(cls, source_type: str) -> 'ContentSource':
        """获取内容源实例"""
        if source_type not in cls._instances:
            source_class = SOURCE_REGISTRY.get(source_type)
            if not source_class:
                raise ValueError(f"Unknown source type: {source_type}")
            cls._instances[source_type] = source_class()
        return cls._instances[source_type]

    @classmethod
    def clear_cache(cls):
        """清除所有缓存的实例"""
        cls._instances.clear()

    @abstractmethod
    async def search(self, keyword: str, **kwargs) -> List[ContentItem]:
        """搜索内容"""
        pass

    async def health_check(self) -> bool:
        """检查内容源健康状态"""
        try:
            return True
        except Exception:
            return False

# 注册表初始化
PARSER_REGISTRY = {}
SOURCE_REGISTRY = {}

def register_parser(parser_type: str):
    """注册解析器装饰器"""
    def wrapper(cls):
        PARSER_REGISTRY[parser_type] = cls
        return cls
    return wrapper

def register_source(source_type: str):
    """注册内容源装饰器"""
    def wrapper(cls):
        SOURCE_REGISTRY[source_type] = cls
        return cls
    return wrapper
