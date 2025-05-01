"""团队适配器基础模块

为各个专业团队提供统一的接口适配层基类，处理基本参数转换和错误处理。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from loguru import logger

from core.models.facade.content_manager import ContentManager

class BaseTeamAdapter(ABC):
    """团队适配器基类"""

    def __init__(self):
        """初始化适配器"""
        self._progress = 0
        self._initialized = False

    async def initialize(self, **kwargs) -> None:
        """初始化团队

        Args:
            **kwargs: 初始化参数
        """
        # 确保 ContentManager 已经初始化
        ContentManager.ensure_initialized()
        self._initialized = True

    def get_progress(self) -> float:
        """获取当前进度

        Returns:
            float: 0-1之间的进度值
        """
        return self._progress

    @property
    def initialized(self) -> bool:
        """是否已初始化"""
        return self._initialized
