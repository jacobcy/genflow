from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from loguru import logger

@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class BaseTool(ABC):
    """工具基类"""
    name: str
    description: str

    def __init__(self, config: Dict = None):
        self.config = config or {}
        logger.info(f"Initializing tool: {self.name}")

    @abstractmethod
    async def execute(self, *args, **kwargs) -> ToolResult:
        """执行工具功能"""
        pass

    def get_description(self) -> Dict:
        """获取工具描述"""
        return {
            "name": self.name,
            "description": self.description,
            "config": self.config
        }

    def _create_success_result(self, data: Any, metadata: Dict = None) -> ToolResult:
        """创建成功结果"""
        return ToolResult(success=True, data=data, metadata=metadata)

    def _create_error_result(self, error: str, metadata: Dict = None) -> ToolResult:
        """创建错误结果"""
        logger.error(f"Tool {self.name} error: {error}")
        return ToolResult(success=False, data=None, error=error, metadata=metadata)
