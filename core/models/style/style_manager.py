"""风格管理模块

继承自 BaseConfigManager，负责加载和管理静态的文章风格配置。
"""

from typing import Dict, List, Optional, Any, Type
from pathlib import Path
import os
from loguru import logger

# Internal dependencies
from core.models.infra.json_loader import load_json_config # Assuming this helper exists
from core.models.infra.base_manager import BaseManager # Corrected import path
# Remove unused DB imports causing errors for now
# from core.models.db.session import provide_session_initializer, SessionLocal
# from core.models.db.utils import get_db, get_or_create
# 使用正确的 Pydantic 模型
from .article_style import ArticleStyle
# 导入基类
from core.models.infra.base_manager import BaseManager

# Setup logger
logger = logger.bind(name="StyleManager")

# 移除文件内定义的 ArticleStyle 类


# 移除文件内定义的 StyleFactory 类


class StyleManager(BaseManager):
    """风格管理器

    管理从 collection/ 目录加载的文章风格配置。
    """

    # 配置目录相对于项目根目录
    CONFIG_DIR = Path("core/models/style/collection")
    # 配置对应的 Pydantic 模型
    MODEL_CLASS = ArticleStyle
    # 匹配配置文件的正则表达式
    FILENAME_REGEX = r".+\.json$"
    # 配置名称的属性字段 (Pydantic 模型中的哪个字段作为 key)
    CONFIG_NAME_FIELD = "name" # 假设 ArticleStyle Pydantic 模型有 'name' 字段作为唯一标识

    # Internal storage for loaded configurations
    _configs: Dict[str, ArticleStyle] = {}

    @classmethod
    def initialize(cls, use_db: bool = False, force_reload: bool = False) -> None:
        """Initializes the StyleManager by loading configurations.

        Args:
            use_db: Flag indicating database usage (currently unused here but kept for BaseManager compatibility).
            force_reload: If True, forces reloading even if already initialized.
        """
        if cls._initialized and not force_reload:
            logger.debug(f"{cls.__name__} 已初始化，跳过加载。")
            return

        logger.info(f"初始化 {cls.__name__}，从目录 {cls.CONFIG_DIR} 加载配置...")
        cls._configs = {}
        config_count = 0
        error_count = 0

        if not cls.CONFIG_DIR.is_dir():
            logger.error(f"配置目录不存在或不是一个目录: {cls.CONFIG_DIR.resolve()}")
            cls._initialized = True # Mark as initialized even if failed to load
            return

        logger.debug(f"开始扫描目录: {cls.CONFIG_DIR.resolve()}")
        found_files = list(cls.CONFIG_DIR.glob("*.json"))
        logger.debug(f"找到 {len(found_files)} 个 .json 文件: {found_files}")

        for filepath in found_files:
            if filepath.is_file():
                logger.debug(f"尝试加载文件: {filepath}")
                try:
                    # Step 1: Load raw dict data using the helper (assuming it takes only path)
                    raw_data = load_json_config(filepath) # Pass only filepath

                    if raw_data and isinstance(raw_data, dict):
                        # Step 2: Validate and create Pydantic model instance
                        try:
                            config_data = cls.MODEL_CLASS(**raw_data)
                            config_name = getattr(config_data, cls.CONFIG_NAME_FIELD, None)
                            if config_name:
                                cls._configs[str(config_name)] = config_data
                                config_count += 1
                                logger.debug(f"成功加载并验证配置 '{config_name}' 从 {filepath.name}")
                                # logger.debug(f"成功解析配置: {config_name}") # Keep one debug log
                            else:
                                logger.warning(f"配置文件 {filepath.name} JSON 数据有效，但缺少关键字段 '{cls.CONFIG_NAME_FIELD}'，已跳过。")
                                error_count += 1
                        except Exception as validation_error: # Catch Pydantic validation errors specifically if needed
                            logger.error(f"验证配置文件 {filepath.name} 数据时出错: {validation_error}")
                            error_count += 1
                    elif raw_data is None: # Handle case where loader returns None on error
                         logger.warning(f"load_json_config 为 {filepath.name} 返回 None")
                         error_count += 1
                    else: # Handle unexpected return type
                         logger.warning(f"load_json_config 为 {filepath.name} 返回了非字典类型: {type(raw_data)}")
                         error_count += 1

                except Exception as e:
                    # This will now primarily catch errors from load_json_config itself (e.g., file not found, JSON decode error if not handled inside)
                    logger.error(f"加载配置文件 {filepath.name} 时发生意外错误: {e}", exc_info=True) # <-- 添加 exc_info=True
                    error_count += 1
            else:
                logger.debug(f"路径 {filepath} 不是文件，跳过。")

        cls._initialized = True
        logger.info(f"{cls.__name__} 初始化完成。成功加载 {config_count} 个配置，遇到 {error_count} 个错误。")

    @classmethod
    def get_config_by_name(cls, name: str) -> Optional[ArticleStyle]:
        """Retrieves a specific configuration by its name (key)."""
        cls.ensure_initialized()
        return cls._configs.get(name)

    @classmethod
    def get_all_configs(cls) -> Dict[str, ArticleStyle]:
        """Retrieves all loaded configurations."""
        cls.ensure_initialized()
        # Return a copy to prevent external modification of the internal dict
        return cls._configs.copy()

    @classmethod
    def get_article_style(cls, style_name: str) -> Optional[ArticleStyle]:
        """获取指定名称的风格配置

        Args:
            style_name: 风格名称 (对应配置文件中的 'name' 字段值)

        Returns:
            Optional[ArticleStyle]: 风格配置对象或None
        """
        # 使用基类的 get_config_by_name 方法
        return cls.get_config_by_name(style_name)

    @classmethod
    def get_default_style(cls) -> Optional[ArticleStyle]:
        """获取默认风格配置

        尝试获取名称为 'default' 的风格配置。

        Returns:
            Optional[ArticleStyle]: 默认风格配置对象或None
        """
        # 假设默认风格的名称是 'default'
        cls.ensure_initialized() # Ensure configs are loaded
        default_style = cls.get_config_by_name("default")
        if default_style:
            return default_style
        else:
            # 如果没有名为 'default' 的风格，可以选择返回第一个加载的或 None/Error
            # 这里返回 None，并记录日志
            all_styles = cls.get_all_configs()
            if all_styles:
                first_style_name = next(iter(all_styles))
                logger.warning("未找到名为 'default' 的风格配置，返回第一个加载的风格: {}", first_style_name)
                return all_styles[first_style_name]
            else:
                logger.error("无法获取默认风格：没有加载任何风格配置。")
                return None

    @classmethod
    def get_all_styles(cls) -> Dict[str, ArticleStyle]:
        """获取所有已加载的风格配置

        Returns:
            Dict[str, ArticleStyle]: 所有风格配置的字典 {style_name: ArticleStyle}
        """
        # 使用实现的 get_all_configs 方法
        return cls.get_all_configs()

    @classmethod
    def find_style_by_type(cls, style_type: str) -> Optional[ArticleStyle]:
        """根据类型查找风格 (保留示例，根据需要调整)

        Args:
            style_type: 风格类型

        Returns:
            Optional[ArticleStyle]: 匹配的风格对象或None
        """
        cls.ensure_initialized() # 确保已加载配置
        for style in cls._configs.values():
            # 假设 ArticleStyle 模型有 'type' 字段
            if hasattr(style, 'type') and style.type.lower() == style_type.lower():
                return style
        return None

    @classmethod
    def save_style(cls, style: ArticleStyle) -> bool:
        """Saves an ArticleStyle object to a JSON file in the collection directory.

        Overwrites the file if it already exists.

        Args:
            style: The ArticleStyle object to save.

        Returns:
            bool: True if save was successful, False otherwise.
        """
        cls.ensure_initialized() # Ensure manager is aware of the directory
        if not hasattr(style, cls.CONFIG_NAME_FIELD):
            logger.error(f"无法保存风格：对象缺少关键字段 '{cls.CONFIG_NAME_FIELD}'")
            return False

        style_name = str(getattr(style, cls.CONFIG_NAME_FIELD))
        if not style_name: # Check for empty string
             logger.error(f"无法保存风格：关键字段 '{cls.CONFIG_NAME_FIELD}' 的值为空。")
             return False

        # Construct the full path for the JSON file
        # Use .json suffix
        filename = f"{style_name}.json"
        filepath = cls.CONFIG_DIR / filename

        try:
            # Ensure the directory exists (though it should from initialization)
            cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            # Use Pydantic's recommended way to serialize (handles complex types)
            # exclude_unset=True might be useful depending on desired output
            json_data = style.model_dump_json(indent=4)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_data)

            logger.info(f"成功保存风格 '{style_name}' 到 {filepath}")

            # Update the internal cache
            cls._configs[style_name] = style
            return True

        except IOError as e:
            logger.error(f"保存风格 '{style_name}' 到文件 {filepath} 时发生 IO 错误: {e}")
            return False
        except Exception as e:
            logger.error(f"保存风格 '{style_name}' 时发生意外错误: {e}")
            return False

# 可以选择性地实例化一个管理器实例供全局使用，如果需要的话
# style_manager = StyleManager()
# style_manager.load_configs() # 或者在应用启动时加载
