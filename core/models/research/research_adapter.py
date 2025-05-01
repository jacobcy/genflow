"""研究适配器

提供对研究临时存储的适配器，封装异常处理和日志记录。
"""

from typing import List, Optional, Dict, Any, Union
from loguru import logger

from .basic_research import BasicResearch
from .research_storage import ResearchStorage

class ResearchAdapter:
    """研究适配器

    封装对研究临时存储的操作，提供异常处理和日志记录。
    """

    @classmethod
    def initialize(cls) -> bool:
        """初始化适配器

        Returns:
            bool: 是否成功初始化
        """
        try:
            ResearchStorage.initialize()
            logger.info("研究适配器初始化成功")
            return True
        except Exception as e:
            logger.error(f"研究适配器初始化失败: {e}")
            return False

    @classmethod
    def get_research(cls, research_id: str) -> Optional[BasicResearch]:
        """获取临时研究

        Args:
            research_id: 研究ID

        Returns:
            Optional[BasicResearch]: 研究对象，不存在或发生错误则返回None
        """
        try:
            research = ResearchStorage.get_research(research_id)
            logger.debug(f"已获取研究: {research_id}")
            return research
        except Exception as e:
            logger.error(f"获取研究失败: {e}")
            return None

    @classmethod
    def save_research(cls, research: Union[BasicResearch, Dict[str, Any]], 
                     research_id: Optional[str] = None) -> str:
        """保存临时研究

        Args:
            research: 研究对象或字典
            research_id: 可选的研究ID，如不提供则自动生成

        Returns:
            str: 研究ID，发生错误则返回空字符串
        """
        try:
            result_id = ResearchStorage.save_research(research, research_id)
            logger.info(f"已保存研究: {result_id}")
            return result_id
        except Exception as e:
            logger.error(f"保存研究失败: {e}")
            # 如果提供了ID，则返回该ID，否则返回空字符串
            return research_id if research_id else ""

    @classmethod
    def update_research(cls, research_id: str, 
                       research: Union[BasicResearch, Dict[str, Any]]) -> bool:
        """更新临时研究

        Args:
            research_id: 研究ID
            research: 新的研究对象或字典

        Returns:
            bool: 是否成功更新
        """
        try:
            result = ResearchStorage.update_research(research_id, research)
            logger.info(f"已更新研究: {research_id}")
            return result
        except Exception as e:
            logger.error(f"更新研究失败: {e}")
            return False

    @classmethod
    def delete_research(cls, research_id: str) -> bool:
        """删除临时研究

        Args:
            research_id: 研究ID

        Returns:
            bool: 是否成功删除
        """
        try:
            result = ResearchStorage.delete_research(research_id)
            logger.info(f"已删除研究: {research_id}")
            return result
        except Exception as e:
            logger.error(f"删除研究失败: {e}")
            return False

    @classmethod
    def list_researches(cls) -> List[str]:
        """获取所有临时研究ID列表

        Returns:
            List[str]: 研究ID列表，发生错误则返回空列表
        """
        try:
            return ResearchStorage.list_researches()
        except Exception as e:
            logger.error(f"获取研究列表失败: {e}")
            return []