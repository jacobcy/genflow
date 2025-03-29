"""数据库初始化脚本

提供初始化数据库和导入默认数据的功能。
"""

import os
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from loguru import logger

from core.models.db.session import init_db, get_db
from core.models.db import ArticleStyle, Platform, Topic, Article
from core.models.content_type.content_type_db import ContentTypeName, ensure_default_content_types
from core.models.db.model_manager import (
    create_default_article_style, create_default_platform
)

# 配置目录路径
CONFIG_DIR = os.environ.get(
    "GENFLOW_CONFIG_DIR",
    os.path.join(Path(__file__).parent.parent.parent.parent, "config")
)

def init_database():
    """初始化数据库并导入默认数据"""
    try:
        # 创建数据库表
        init_db()

        # 导入默认数据
        with get_db() as db:
            # 导入默认内容类型名称
            logger.info("导入默认内容类型名称...")
            ensure_default_content_types(db)

            # 检查是否已有文章风格
            count = db.query(ArticleStyle).count()
            if count == 0:
                logger.info("导入默认文章风格...")
                default_style_dict = create_default_article_style()
                default_style = ArticleStyle(**default_style_dict)
                db.add(default_style)

            # 检查是否已有平台配置
            count = db.query(Platform).count()
            if count == 0:
                logger.info("导入默认平台配置...")
                default_platform_dict = create_default_platform()
                default_platform = Platform(**default_platform_dict)
                db.add(default_platform)

            # 提交更改
            db.commit()

        logger.info("数据库初始化完成")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        return False

def get_config_file_path(config_type: str, filename: str) -> Path:
    """获取配置文件路径

    Args:
        config_type: 配置类型目录（如styles, platforms）
        filename: 文件名

    Returns:
        Path: 配置文件路径
    """
    return Path(CONFIG_DIR) / config_type / filename

def load_json_config(config_path: Path) -> Optional[Dict[str, Any]]:
    """加载JSON配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        Optional[Dict[str, Any]]: 配置数据，失败返回None
    """
    try:
        if not config_path.exists():
            logger.warning(f"配置文件不存在: {config_path}")
            return None

        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {config_path}, 错误: {str(e)}")
        return None

def import_article_styles_from_file():
    """从文件导入文章风格数据"""
    # 获取配置文件路径
    config_path = get_config_file_path("styles", "article_styles.json")
    config_data = load_json_config(config_path)

    if not config_data:
        return False

    styles = config_data.get("article_styles", [])
    if not styles:
        logger.warning("文章风格配置文件中没有数据")
        return False

    try:
        # 导入文章风格
        with get_db() as db:
            success_count = 0
            for style_data in styles:
                # 处理内容类型兼容性
                content_type_names = style_data.pop("content_types", [])

                # 检查是否已存在
                existing = db.query(ArticleStyle).filter(ArticleStyle.id == style_data.get("id")).first()

                if existing:
                    # 更新现有记录
                    for key, value in style_data.items():
                        if key != "id" and hasattr(existing, key):
                            setattr(existing, key, value)
                    style = existing
                    logger.info(f"更新文章风格: {style.id}")
                else:
                    # 创建新记录
                    style = ArticleStyle(**style_data)
                    db.add(style)
                    logger.info(f"创建文章风格: {style.id}")

                success_count += 1

            # 提交更改
            db.commit()

        logger.info(f"已从配置文件导入 {success_count} 个文章风格")
        return True
    except Exception as e:
        logger.error(f"导入文章风格失败: {str(e)}")
        return False

def import_platforms_from_file():
    """从文件导入平台数据"""
    # 获取配置文件路径
    config_path = get_config_file_path("platforms", "platforms.json")
    config_data = load_json_config(config_path)

    if not config_data:
        return False

    platforms = config_data.get("platforms", [])
    if not platforms:
        logger.warning("平台配置文件中没有数据")
        return False

    try:
        # 导入平台配置
        with get_db() as db:
            success_count = 0
            for platform_data in platforms:
                # 检查是否已存在
                existing = db.query(Platform).filter(Platform.id == platform_data.get("id")).first()

                if existing:
                    # 更新现有记录
                    for key, value in platform_data.items():
                        if key != "id" and hasattr(existing, key):
                            setattr(existing, key, value)
                    logger.info(f"更新平台配置: {existing.id}")
                else:
                    # 创建新记录
                    new_platform = Platform(**platform_data)
                    db.add(new_platform)
                    logger.info(f"创建平台配置: {new_platform.id}")

                success_count += 1

            # 提交更改
            db.commit()

        logger.info(f"已从配置文件导入 {success_count} 个平台配置")
        return True
    except Exception as e:
        logger.error(f"导入平台配置失败: {str(e)}")
        return False

def import_all_from_files() -> bool:
    """从文件导入所有配置数据

    Returns:
        bool: 导入是否全部成功
    """
    styles_result = import_article_styles_from_file()
    platforms_result = import_platforms_from_file()

    return styles_result and platforms_result

def initialize_all() -> bool:
    """初始化所有数据

    Returns:
        bool: 初始化是否成功
    """
    db_result = init_database()
    import_result = import_all_from_files()

    return db_result and import_result

# 本地测试
if __name__ == "__main__":
    success = initialize_all()
    exit_code = 0 if success else 1
    exit(exit_code)
