"""研究工具包

提供研究报告处理的辅助功能和工具函数。
"""

# 需要创建相关文件后才能导入
from core.models.research.utils.research_formatter import format_research_as_markdown, format_research_as_json
from core.models.research.utils.research_validator import (
    validate_research_data,
    validate_source,
    get_research_completeness
)

__all__ = [
    'format_research_as_markdown',
    'format_research_as_json',
    'validate_research_data',
    'validate_source',
    'get_research_completeness',
]
