"""内容采集工具包"""
from .base_collector import BaseCollector
from .collector import ContentCollector
from .newspaper_collector import NewspaperCollector
from .trafilatura_collector import TrafilaturaCollector
from .readability_collector import ReadabilityCollector

__all__ = [
    'BaseCollector',
    'ContentCollector',
    'NewspaperCollector',
    'TrafilaturaCollector',
    'ReadabilityCollector'
]
