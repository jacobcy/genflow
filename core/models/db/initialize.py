"""数据库初始化脚本

提供初始化数据库和导入默认配置数据的功能。
"""

import os
import sys # Import sys for argument parsing
import argparse # Import argparse
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from loguru import logger

# Use relative import for session and migrate_configs
from .session import init_db as create_tables, get_db
from .migrate_configs import migrate_all

# Import DB models directly (assuming they are in the correct path)
# If __init__.py doesn't export them, this needs adjustment
# For now, assume they might be accessible via module path
# Let's try importing within functions to mitigate potential issues

def _ensure_default_style(db_session):
    """确保默认文章风格存在"""
    from . import ArticleStyle # Import inside function
    count = db_session.query(ArticleStyle).count()
    if count == 0:
        logger.info("导入默认文章风格...")
        # Logic from removed model_manager.create_default_article_style
        default_style_dict = {
            "id": "default",
            "name": "默认风格",
            "description": "通用默认风格",
            "tone": "neutral",
            "formality": 3,
            "language": "zh",
            "target_audience": "general",
            "constraints": [],
            "examples": [],
            "compatible_content_types": [] # Assuming relation handled by migrate_configs
        }
        default_style = ArticleStyle(**default_style_dict)
        db_session.add(default_style)
        logger.info("默认文章风格已添加")
        return True
    return False

def _ensure_default_platform(db_session):
    """确保默认平台存在"""
    from . import Platform # Import inside function
    count = db_session.query(Platform).count()
    if count == 0:
        logger.info("导入默认平台配置...")
        # Logic from removed model_manager.create_default_platform
        default_platform_dict = {
            "id": "default",
            "name": "默认平台",
            "description": "通用默认平台配置",
            "url_structure": "",
            "content_restrictions": {},
            "api_details": {},
            "audience_profile": {},
            "posting_guidelines": []
        }
        default_platform = Platform(**default_platform_dict)
        db_session.add(default_platform)
        logger.info("默认平台配置已添加")
        return True
    return False

def init_database_structure_and_defaults():
    """初始化数据库结构并导入默认数据（如内容类型名、默认风格/平台）"""
    try:
        # 1. 创建数据库表
        logger.info("正在创建数据库表...")
        create_tables() # Renamed import from session
        logger.info("数据库表创建完成")

        # 2. 导入默认数据
        with get_db() as db:
            logger.info("开始导入默认数据...")
            # 导入默认内容类型名称
            from core.models.content_type.content_type_db import ensure_default_content_types # Keep this specific import
            logger.info("导入默认内容类型名称...")
            content_type_added = ensure_default_content_types(db)

            # 确保默认文章风格存在
            style_added = _ensure_default_style(db)

            # 确保默认平台配置存在
            platform_added = _ensure_default_platform(db)

            # 提交默认数据更改
            if content_type_added or style_added or platform_added:
                db.commit()
                logger.info("默认数据导入完成")
            else:
                logger.info("默认数据已存在，无需导入")

        return True
    except Exception as e:
        logger.error(f"数据库结构和默认数据初始化失败: {str(e)}", exc_info=True)
        return False

# Remove get_config_file_path and load_json_config (moved to json_loader)
# Remove import_*_from_file functions (handled by migrate_configs)
# Remove import_all_from_files function

def initialize_all(sync_mode: bool = False) -> bool:
    """完整初始化流程：创建结构、导入默认值、迁移配置

    Args:
        sync_mode: 是否在配置迁移时使用完整同步模式。

    Returns:
        bool: 初始化是否成功
    """
    logger.info(f"开始完整数据库初始化流程 (sync_mode={sync_mode})...")
    # 步骤 1 & 2: 创建表结构并确保默认数据存在
    db_result = init_database_structure_and_defaults()
    if not db_result:
        logger.error("数据库结构和默认数据初始化失败，中止初始化流程")
        return False

    # 步骤 3: 迁移配置文件
    logger.info("开始迁移配置文件到数据库...")
    # Note: migrate_all might need adjustment if models aren't exported from db.__init__
    migrate_result = migrate_all(sync_mode=sync_mode)
    if not migrate_result:
        logger.error("配置文件迁移失败")
        # Decide if this is a fatal error for initialization
        # return False

    final_success = db_result and migrate_result
    if final_success:
        logger.info("数据库完整初始化流程成功完成")
    else:
        logger.warning("数据库完整初始化流程完成，但存在部分失败 (请检查日志)")

    return final_success

# 更新 main block 以支持命令行参数
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize GenFlow Database")
    parser.add_argument(
        "--sync-mode",
        action="store_true",
        help="Enable full sync mode for config migration (deletes extra DB entries)"
    )
    args = parser.parse_args()

    logger.info(f"从命令行运行初始化 (sync_mode={args.sync_mode})...")
    success = initialize_all(sync_mode=args.sync_mode)
    exit_code = 0 if success else 1
    logger.info(f"初始化脚本执行完毕，退出码: {exit_code}")
    sys.exit(exit_code)
