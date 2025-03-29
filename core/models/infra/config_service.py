"""配置服务模块

专注于加载和管理配置信息，不依赖其他高级组件。
负责从文件系统加载配置并提供简单的配置验证。
"""

from typing import Dict, Optional, Any, List
from loguru import logger
import os
import json
from pathlib import Path

class ConfigService:
    """配置服务类，处理应用配置的加载和管理

    专注于以下职责:
    1. 从文件加载配置
    2. 验证配置有效性
    3. 提供配置访问接口
    """

    _config_cache: Dict[str, Any] = {}
    _config_dir: str = ""  # 默认为空字符串，而不是None

    @classmethod
    def initialize(cls, config_dir: Optional[str] = None) -> bool:
        """初始化配置服务

        Args:
            config_dir: 配置文件目录路径，如果为None则使用默认路径

        Returns:
            bool: 是否成功初始化
        """
        if config_dir:
            cls._config_dir = config_dir
        else:
            # 默认配置目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            cls._config_dir = os.path.join(current_dir, "../../../config")

        # 确保目录存在
        os.makedirs(cls._config_dir, exist_ok=True)

        # 尝试加载核心配置
        try:
            cls.load_core_configs()
            logger.info(f"配置服务初始化成功，配置目录: {cls._config_dir}")
            return True
        except Exception as e:
            logger.error(f"配置服务初始化失败: {str(e)}")
            return False

    @classmethod
    def load_core_configs(cls) -> None:
        """加载核心配置文件"""
        # 加载应用配置
        app_config = cls.load_config_file("app_config.json")
        if app_config:
            cls._config_cache["app"] = app_config

        # 加载数据库配置
        db_config = cls.load_config_file("db_config.json")
        if db_config:
            cls._config_cache["database"] = db_config

    @classmethod
    def load_config_file(cls, filename: str) -> Optional[Dict[str, Any]]:
        """加载指定配置文件

        Args:
            filename: 配置文件名

        Returns:
            Optional[Dict[str, Any]]: 配置数据字典，加载失败则返回None
        """
        try:
            # _config_dir 现在确保不为 None
            file_path = os.path.join(cls._config_dir, filename)
            if not os.path.exists(file_path):
                logger.warning(f"配置文件不存在: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                logger.debug(f"已加载配置文件: {filename}")
                return config_data
        except Exception as e:
            logger.error(f"加载配置文件 {filename} 失败: {str(e)}")
            return None

    @classmethod
    def get_config(cls, config_key: str, default: Any = None) -> Any:
        """获取配置值

        Args:
            config_key: 配置键名，支持点号分隔的层级访问，如 "app.server.port"
            default: 默认值，当配置不存在时返回

        Returns:
            Any: 配置值或默认值
        """
        parts = config_key.split('.')
        config = cls._config_cache

        for part in parts:
            if not isinstance(config, dict) or part not in config:
                return default
            config = config[part]

        return config

    @classmethod
    def set_config(cls, config_key: str, value: Any) -> bool:
        """设置配置值（仅内存中）

        Args:
            config_key: 配置键名，支持点号分隔的层级访问
            value: 配置值

        Returns:
            bool: 是否成功设置
        """
        parts = config_key.split('.')
        config = cls._config_cache

        # 遍历到最后一级的父级
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            elif not isinstance(config[part], dict):
                config[part] = {}
            config = config[part]

        # 设置最后一级的值
        config[parts[-1]] = value
        return True

    @classmethod
    def save_config(cls, config_type: str) -> bool:
        """将内存中的配置保存到文件

        Args:
            config_type: 配置类型，例如 "app", "database"

        Returns:
            bool: 是否成功保存
        """
        if config_type not in cls._config_cache:
            logger.error(f"要保存的配置类型不存在: {config_type}")
            return False

        try:
            filename = f"{config_type}_config.json"
            # _config_dir 现在确保不为 None
            file_path = os.path.join(cls._config_dir, filename)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cls._config_cache[config_type], f, ensure_ascii=False, indent=2)

            logger.info(f"配置已保存到文件: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存配置到文件失败: {str(e)}")
            return False

    @classmethod
    def get_all_configs(cls) -> Dict[str, Any]:
        """获取所有配置

        Returns:
            Dict[str, Any]: 所有配置的副本
        """
        # 返回副本避免外部修改
        return dict(cls._config_cache)
