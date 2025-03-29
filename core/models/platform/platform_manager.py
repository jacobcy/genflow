"""平台管理器

负责管理发布平台的获取、保存等操作
"""

from typing import Dict, List, Optional, Any, ClassVar
from loguru import logger
import os
import json
from pathlib import Path

from core.models.article.article import Article
from core.models.platform.platform import Platform, get_default_platform
from core.models.infra.json_loader import JsonModelLoader
from core.models.platform.platform_validator import validate_article_against_platform
from ..infra.base_manager import BaseManager


class PlatformManager(BaseManager):
    """平台管理器

    提供平台相关的操作，包括获取、保存平台
    """

    _platforms: ClassVar[Dict[str, Platform]] = {}
    _initialized: ClassVar[bool] = False

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化"""
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def initialize(cls) -> None:
        """初始化平台管理器"""
        if cls._initialized:
            return

        # 加载平台数据
        cls._load_platforms()

        cls._initialized = True
        logger.info("平台管理器初始化完成")

    @classmethod
    def _load_platforms(cls) -> None:
        """从文件目录加载平台数据"""
        # 从platforms目录加载平台数据
        platforms_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'platforms')
        platforms: List[Platform] = []

        try:
            # 加载目录中的所有平台JSON文件
            if os.path.exists(platforms_dir):
                for file_path in Path(platforms_dir).glob("*.json"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            platform_data = json.load(f)
                            platform = Platform(**platform_data)
                            platforms.append(platform)
                    except Exception as file_e:
                        logger.error(f"加载平台文件失败 {file_path}: {str(file_e)}")
        except Exception as e:
            logger.error(f"从目录加载平台失败: {str(e)}")

        # 保存到缓存中
        for platform in platforms:
            cls._platforms[platform.name] = platform

        logger.info(f"已加载 {len(platforms)} 个平台")

    @classmethod
    def get_platform(cls, platform_id: str) -> Optional[Platform]:
        """获取指定ID的平台

        Args:
            platform_id: 平台ID

        Returns:
            Optional[Platform]: 平台对象，不存在则返回None
        """
        cls.ensure_initialized()
        return cls._platforms.get(platform_id)

    @classmethod
    def get_platform_by_name(cls, name: str) -> Optional[Platform]:
        """根据名称获取平台

        Args:
            name: 平台名称

        Returns:
            Optional[Platform]: 平台对象，不存在则返回None
        """
        cls.ensure_initialized()

        # 直接匹配名称
        if name in cls._platforms:
            return cls._platforms[name]

        # 不区分大小写匹配
        for platform in cls._platforms.values():
            if platform.name.lower() == name.lower():
                return platform

        return None

    @classmethod
    def get_all_platforms(cls) -> List[Platform]:
        """获取所有平台

        Returns:
            List[Platform]: 平台列表
        """
        cls.ensure_initialized()
        return list(cls._platforms.values())

    @classmethod
    def save_platform(cls, platform: Platform) -> bool:
        """保存平台

        Args:
            platform: 平台对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()

        # 保存到缓存
        cls._platforms[platform.name] = platform

        # 尝试保存到文件
        try:
            platforms_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'platforms')
            os.makedirs(platforms_dir, exist_ok=True)

            file_path = os.path.join(platforms_dir, f"{platform.name}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                # 将Platform对象转换为字典
                platform_dict = platform.dict()
                json.dump(platform_dict, f, ensure_ascii=False, indent=2)

            logger.info(f"平台保存成功: {platform.name}")
            return True
        except Exception as e:
            logger.error(f"保存平台到文件失败: {str(e)}")
            return False

    @classmethod
    def validate_article(cls, article: Article, platform_name: str) -> Dict[str, Any]:
        """验证文章是否符合平台要求

        Args:
            article: 文章对象
            platform_name: 平台名称

        Returns:
            Dict[str, Any]: 验证结果，包含是否通过验证和详细信息
        """
        cls.ensure_initialized()

        # 获取平台对象
        platform = cls.get_platform_by_name(platform_name)
        if not platform:
            return {
                "valid": False,
                "message": f"找不到平台: {platform_name}",
                "details": []
            }

        # 使用平台验证工具验证文章
        return validate_article_against_platform(article, platform)

    @classmethod
    def get_platform_constraints(cls, platform_name: str) -> Dict[str, Any]:
        """获取平台的内容约束

        Args:
            platform_name: 平台名称

        Returns:
            Dict[str, Any]: 平台约束配置
        """
        cls.ensure_initialized()

        platform = cls.get_platform_by_name(platform_name)
        if not platform:
            return {}

        # 使用Platform模型中的方法获取约束
        return platform.get_platform_constraints()
