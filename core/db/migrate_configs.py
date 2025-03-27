"""配置文件迁移工具

将已有的配置文件迁移到数据库中。
"""

import os
import json
import importlib
from typing import Dict, List, Any, Set
from loguru import logger

from core.db.session import get_db, init_db
from core.db.models import ContentType, ArticleStyle, Platform
from core.db.initialize import initialize_all

def migrate_content_types(sync_mode: bool = False):
    """迁移内容类型配置到数据库

    Args:
        sync_mode: 是否为同步模式。同步模式下会删除不在文件中的记录。
    """
    try:
        # 动态导入模块以避免循环引用
        content_type_module = importlib.import_module('.content_type', package='core.models')
        content_types = content_type_module.load_content_types()

        if not content_types:
            logger.warning("未找到内容类型配置")
            return

        logger.info(f"开始迁移 {len(content_types)} 个内容类型配置")

        with get_db() as db:
            # 如果是同步模式，先获取所有数据库中的ID
            if sync_mode:
                db_ids = {ct.id for ct in db.query(ContentType).all()}
                file_ids = set(content_types.keys())

                # 删除在数据库中存在但不在文件中的记录
                ids_to_delete = db_ids - file_ids
                if ids_to_delete:
                    for ct_id in ids_to_delete:
                        db.query(ContentType).filter(ContentType.id == ct_id).delete()
                        logger.info(f"删除不在文件中的内容类型: {ct_id}")

            # 更新或创建记录
            for ct_id, ct in content_types.items():
                # 转换为数据库对象
                ct_dict = {
                    "id": ct.id,
                    "name": ct.name,
                    "description": getattr(ct, "description", ""),
                    "default_word_count": getattr(ct, "default_word_count", "1000"),
                    "is_enabled": getattr(ct, "is_enabled", True),
                    "prompt_template": getattr(ct, "prompt_template", ""),
                    "output_format": getattr(ct, "output_format", {}),
                    "required_elements": getattr(ct, "required_elements", {}),
                    "optional_elements": getattr(ct, "optional_elements", {}),
                }

                # 检查是否已存在
                existing = db.query(ContentType).filter(ContentType.id == ct_id).first()
                if existing:
                    # 更新现有记录
                    for key, value in ct_dict.items():
                        if key != "id" and hasattr(existing, key):
                            setattr(existing, key, value)
                    logger.info(f"更新内容类型: {existing.id}")
                else:
                    # 创建新记录
                    new_content_type = ContentType(**ct_dict)
                    db.add(new_content_type)
                    logger.info(f"创建内容类型: {new_content_type.id}")

            # 提交更改
            db.commit()

        logger.info(f"内容类型配置迁移完成")

    except Exception as e:
        logger.error(f"内容类型配置迁移失败: {str(e)}")

def migrate_article_styles(sync_mode: bool = False):
    """迁移文章风格配置到数据库

    Args:
        sync_mode: 是否为同步模式。同步模式下会删除不在文件中的记录。
    """
    try:
        # 动态导入模块以避免循环引用
        article_style_module = importlib.import_module('.article_style', package='core.models')
        styles = article_style_module.load_article_styles()

        if not styles:
            logger.warning("未找到文章风格配置")
            return

        logger.info(f"开始迁移 {len(styles)} 个文章风格配置")

        with get_db() as db:
            # 如果是同步模式，先获取所有数据库中的ID
            if sync_mode:
                db_ids = {style.id for style in db.query(ArticleStyle).all()}
                file_ids = set(styles.keys())

                # 删除在数据库中存在但不在文件中的记录
                ids_to_delete = db_ids - file_ids
                if ids_to_delete:
                    for style_id in ids_to_delete:
                        db.query(ArticleStyle).filter(ArticleStyle.id == style_id).delete()
                        logger.info(f"删除不在文件中的文章风格: {style_id}")

            # 更新或创建记录
            for style_id, style in styles.items():
                # 处理内容类型兼容性
                content_types_ids = getattr(style, "content_types", [])

                # 转换为数据库对象
                style_dict = {
                    "id": style.id,
                    "name": style.name,
                    "description": getattr(style, "description", ""),
                    "is_enabled": getattr(style, "is_enabled", True),
                    "tone": getattr(style, "tone", ""),
                    "style_characteristics": getattr(style, "style_characteristics", {}),
                    "language_preference": getattr(style, "language_preference", {}),
                    "writing_format": getattr(style, "writing_format", {}),
                    "prompt_template": getattr(style, "prompt_template", ""),
                    "example": getattr(style, "example", ""),
                }

                # 检查是否已存在
                existing = db.query(ArticleStyle).filter(ArticleStyle.id == style_id).first()
                if existing:
                    # 更新现有记录
                    for key, value in style_dict.items():
                        if key != "id" and hasattr(existing, key):
                            setattr(existing, key, value)
                    style_obj = existing
                    logger.info(f"更新文章风格: {style_obj.id}")
                else:
                    # 创建新记录
                    style_obj = ArticleStyle(**style_dict)
                    db.add(style_obj)
                    logger.info(f"创建文章风格: {style_obj.id}")

                # 设置内容类型兼容性
                if content_types_ids:
                    # 清除现有关联
                    style_obj.compatible_content_types = []

                    # 添加新关联
                    for ct_id in content_types_ids:
                        ct = db.query(ContentType).filter(ContentType.id == ct_id).first()
                        if ct:
                            style_obj.compatible_content_types.append(ct)

            # 提交更改
            db.commit()

        logger.info(f"文章风格配置迁移完成")

    except Exception as e:
        logger.error(f"文章风格配置迁移失败: {str(e)}")

def migrate_platforms(sync_mode: bool = False):
    """迁移平台配置到数据库

    Args:
        sync_mode: 是否为同步模式。同步模式下会删除不在文件中的记录。
    """
    try:
        # 动态导入模块以避免循环引用
        platform_module = importlib.import_module('.platform', package='core.models')
        platforms = platform_module.PLATFORM_CONFIGS

        if not platforms:
            logger.warning("未找到平台配置")
            return

        logger.info(f"开始迁移 {len(platforms)} 个平台配置")

        with get_db() as db:
            # 如果是同步模式，先获取所有数据库中的ID
            if sync_mode:
                db_ids = {platform.id for platform in db.query(Platform).all()}
                file_ids = set(platforms.keys())

                # 删除在数据库中存在但不在文件中的记录
                ids_to_delete = db_ids - file_ids
                if ids_to_delete:
                    for platform_id in ids_to_delete:
                        db.query(Platform).filter(Platform.id == platform_id).delete()
                        logger.info(f"删除不在文件中的平台配置: {platform_id}")

            # 更新或创建记录
            for platform_id, platform in platforms.items():
                # 转换为数据库对象
                platform_dict = {
                    "id": platform.id,
                    "name": platform.name,
                    "description": getattr(platform, "description", ""),
                    "is_enabled": getattr(platform, "is_enabled", True),
                    "platform_type": getattr(platform, "platform_type", ""),
                    "url": getattr(platform, "url", ""),
                    "logo_url": getattr(platform, "logo_url", ""),
                    "max_title_length": getattr(platform, "max_title_length", {}),
                    "max_content_length": getattr(platform, "max_content_length", {}),
                    "allowed_media_types": getattr(platform, "allowed_media_types", {}),
                    "api_config": getattr(platform, "api_config", {}),
                }

                # 检查是否已存在
                existing = db.query(Platform).filter(Platform.id == platform_id).first()
                if existing:
                    # 更新现有记录
                    for key, value in platform_dict.items():
                        if key != "id" and hasattr(existing, key):
                            setattr(existing, key, value)
                    logger.info(f"更新平台配置: {existing.id}")
                else:
                    # 创建新记录
                    new_platform = Platform(**platform_dict)
                    db.add(new_platform)
                    logger.info(f"创建平台配置: {new_platform.id}")

            # 提交更改
            db.commit()

        logger.info(f"平台配置迁移完成")

    except Exception as e:
        logger.error(f"平台配置迁移失败: {str(e)}")

def migrate_all(sync_mode: bool = False):
    """迁移所有配置到数据库

    Args:
        sync_mode: 是否为同步模式。同步模式下会删除不在文件中的记录。
    """
    # 确保数据库已初始化
    initialize_all()

    # 迁移各类配置
    migrate_content_types(sync_mode)
    migrate_article_styles(sync_mode)
    migrate_platforms(sync_mode)

    logger.info("所有配置迁移完成")

if __name__ == "__main__":
    # 默认使用同步模式
    migrate_all(sync_mode=True)
