"""数据库初始化脚本

提供初始化数据库和导入默认数据的功能。
"""

import os
from typing import List, Dict, Any
import json
from loguru import logger

from core.db.session import init_db, get_db
from core.db.models import (
    ContentType, ArticleStyle, Platform, Topic, Article,
    get_default_content_type, get_default_article_style, get_default_platform
)

def init_database():
    """初始化数据库并导入默认数据"""
    # 创建数据库表
    init_db()

    # 导入默认数据
    with get_db() as db:
        # 检查是否已有内容类型
        count = db.query(ContentType).count()
        if count == 0:
            logger.info("导入默认内容类型...")
            default_content_type = get_default_content_type()
            db.add(default_content_type)

        # 检查是否已有文章风格
        count = db.query(ArticleStyle).count()
        if count == 0:
            logger.info("导入默认文章风格...")
            default_style = get_default_article_style()
            db.add(default_style)

        # 检查是否已有平台配置
        count = db.query(Platform).count()
        if count == 0:
            logger.info("导入默认平台配置...")
            default_platform = get_default_platform()
            db.add(default_platform)

        # 提交更改
        db.commit()

    logger.info("数据库初始化完成")

def import_content_types_from_file():
    """从文件导入内容类型数据"""
    # 获取内容类型配置目录
    content_types_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "models", "content_types"
    )

    if not os.path.exists(content_types_dir):
        logger.warning(f"内容类型目录不存在: {content_types_dir}")
        return

    # 读取配置文件
    config_file = os.path.join(content_types_dir, "content_types.json")
    if not os.path.exists(config_file):
        logger.warning(f"内容类型配置文件不存在: {config_file}")
        return

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            content_types_data = json.load(f)

        content_types = content_types_data.get("content_types", [])
        if not content_types:
            logger.warning("内容类型配置文件中没有数据")
            return

        # 导入内容类型
        with get_db() as db:
            for ct_data in content_types:
                # 检查是否已存在
                existing = db.query(ContentType).filter(ContentType.id == ct_data["id"]).first()

                if existing:
                    # 更新现有记录
                    for key, value in ct_data.items():
                        if key != "id" and hasattr(existing, key):
                            setattr(existing, key, value)
                    logger.info(f"更新内容类型: {existing.id}")
                else:
                    # 创建新记录
                    new_content_type = ContentType(**ct_data)
                    db.add(new_content_type)
                    logger.info(f"创建内容类型: {new_content_type.id}")

            # 提交更改
            db.commit()

        logger.info(f"已从配置文件导入 {len(content_types)} 个内容类型")

    except Exception as e:
        logger.error(f"导入内容类型失败: {str(e)}")

def import_article_styles_from_file():
    """从文件导入文章风格数据"""
    # 获取文章风格配置目录
    styles_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "models", "styles"
    )

    if not os.path.exists(styles_dir):
        logger.warning(f"文章风格目录不存在: {styles_dir}")
        return

    # 读取配置文件
    config_file = os.path.join(styles_dir, "article_styles.json")
    if not os.path.exists(config_file):
        logger.warning(f"文章风格配置文件不存在: {config_file}")
        return

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            styles_data = json.load(f)

        styles = styles_data.get("article_styles", [])
        if not styles:
            logger.warning("文章风格配置文件中没有数据")
            return

        # 导入文章风格
        with get_db() as db:
            for style_data in styles:
                # 处理内容类型兼容性
                content_types_ids = style_data.pop("content_types", [])

                # 检查是否已存在
                existing = db.query(ArticleStyle).filter(ArticleStyle.id == style_data["id"]).first()

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

                # 设置内容类型兼容性
                if content_types_ids:
                    # 清除现有关联
                    style.compatible_content_types = []

                    # 添加新关联
                    for ct_id in content_types_ids:
                        ct = db.query(ContentType).filter(ContentType.id == ct_id).first()
                        if ct:
                            style.compatible_content_types.append(ct)

            # 提交更改
            db.commit()

        logger.info(f"已从配置文件导入 {len(styles)} 个文章风格")

    except Exception as e:
        logger.error(f"导入文章风格失败: {str(e)}")

def import_platforms_from_file():
    """从文件导入平台数据"""
    # 获取平台配置目录
    platforms_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "models", "platforms"
    )

    if not os.path.exists(platforms_dir):
        logger.warning(f"平台配置目录不存在: {platforms_dir}")
        return

    # 读取配置文件
    config_file = os.path.join(platforms_dir, "platforms.json")
    if not os.path.exists(config_file):
        logger.warning(f"平台配置文件不存在: {config_file}")
        return

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            platforms_data = json.load(f)

        platforms = platforms_data.get("platforms", [])
        if not platforms:
            logger.warning("平台配置文件中没有数据")
            return

        # 导入平台配置
        with get_db() as db:
            for platform_data in platforms:
                # 检查是否已存在
                existing = db.query(Platform).filter(Platform.id == platform_data["id"]).first()

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

            # 提交更改
            db.commit()

        logger.info(f"已从配置文件导入 {len(platforms)} 个平台配置")

    except Exception as e:
        logger.error(f"导入平台配置失败: {str(e)}")

def import_all_from_files():
    """从所有配置文件导入数据"""
    import_content_types_from_file()
    import_article_styles_from_file()
    import_platforms_from_file()
    logger.info("所有配置数据导入完成")

# 主函数
def initialize_all():
    """初始化数据库并导入所有配置数据"""
    # 初始化数据库
    init_database()

    # 导入配置文件数据
    import_all_from_files()

    logger.info("初始化完成")

if __name__ == "__main__":
    initialize_all()
