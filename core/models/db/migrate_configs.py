"""配置文件迁移工具

将已有的配置文件迁移到数据库中，支持增量同步和全量同步模式。
增量同步模式下只添加和更新记录，全量同步模式下会删除不在配置文件中的记录。
"""

import importlib
from typing import Dict, List, Any, Set, Type, Callable, Optional, Tuple, Union
from loguru import logger

# 显式导入数据库模型避免循环引用
from core.models.db.session import get_db, init_db
from core.models.db.initialize import initialize_all
try:
    from core.models.db import ContentType, ArticleStyle, Platform
except ImportError:
    # 如果无法导入，提供类型占位符
    logger.warning("无法直接导入数据库模型，使用类型占位符")
    ContentType = Any
    ArticleStyle = Any
    Platform = Any

def migrate_config(
    model_cls: Type,
    module_name: str,
    data_attr_or_func: Union[str, Callable],
    sync_mode: bool = False,
    id_field: str = "id",
    special_handlers: Optional[Dict[str, Callable]] = None
) -> bool:
    """通用配置迁移函数

    将配置数据同步到数据库，支持增量和全量同步模式

    Args:
        model_cls: 数据库模型类
        module_name: 配置模块路径，例如 '.content_type'
        data_attr_or_func: 数据源属性名或加载函数名
        sync_mode: 是否为同步模式。同步模式下会删除不在文件中的记录
        id_field: ID字段名，默认为"id"
        special_handlers: 特殊处理函数，用于处理特定模型的额外逻辑

    Returns:
        bool: 是否成功迁移
    """
    try:
        # 动态导入模块以避免循环引用
        module = importlib.import_module(module_name, package='core.models')

        # 获取数据
        if isinstance(data_attr_or_func, str):
            # 从模块属性获取数据
            items = getattr(module, data_attr_or_func)
        else:
            # 调用加载函数获取数据
            items = data_attr_or_func()

        if not items:
            logger.warning(f"未找到{model_cls.__name__}配置")
            return False

        logger.info(f"开始迁移 {len(items)} 个{model_cls.__name__}配置")

        with get_db() as db:
            # 如果是同步模式，先获取所有数据库中的ID并处理删除
            if sync_mode:
                db_ids = {getattr(item, id_field) for item in db.query(model_cls).all()}
                file_ids = set(items.keys())

                # 删除在数据库中存在但不在文件中的记录
                ids_to_delete = db_ids - file_ids
                if ids_to_delete:
                    for item_id in ids_to_delete:
                        db.query(model_cls).filter(getattr(model_cls, id_field) == item_id).delete()
                        logger.info(f"删除不在文件中的{model_cls.__name__}: {item_id}")

            # 更新或创建记录
            for item_id, item in items.items():
                # 转换为数据库对象字典
                item_dict = _create_item_dict(item, model_cls)

                # 检查是否已存在
                existing = db.query(model_cls).filter(getattr(model_cls, id_field) == item_id).first()

                if existing:
                    # 更新现有记录
                    for key, value in item_dict.items():
                        if key != id_field and hasattr(existing, key):
                            setattr(existing, key, value)
                    item_obj = existing
                    logger.info(f"更新{model_cls.__name__}: {getattr(existing, id_field)}")
                else:
                    # 创建新记录
                    item_obj = model_cls(**item_dict)
                    db.add(item_obj)
                    logger.info(f"创建{model_cls.__name__}: {item_dict.get(id_field)}")

                # 处理特殊逻辑
                if special_handlers:
                    for handler_name, handler_func in special_handlers.items():
                        handler_func(db, item_obj, item)

            # 提交更改
            db.commit()

        logger.info(f"{model_cls.__name__}配置迁移完成")
        return True

    except Exception as e:
        logger.error(f"{model_cls.__name__}配置迁移失败: {str(e)}")
        return False

def _create_item_dict(item: Any, model_cls: Type) -> Dict[str, Any]:
    """根据模型类型创建字典

    Args:
        item: 配置项对象
        model_cls: 模型类

    Returns:
        Dict[str, Any]: 属性字典
    """
    # 基础属性
    base_attrs = ["id", "name", "description", "is_enabled"]
    result = {}

    # 复制所有基础属性
    for attr in base_attrs:
        if hasattr(item, attr):
            result[attr] = getattr(item, attr)

    # 根据模型类型添加特定属性
    if model_cls.__name__ == "ContentType":
        content_type_attrs = [
            "default_word_count", "prompt_template", "output_format",
            "required_elements", "optional_elements"
        ]
        for attr in content_type_attrs:
            result[attr] = getattr(item, attr, None) if hasattr(item, attr) else None

    elif model_cls.__name__ == "ArticleStyle":
        style_attrs = [
            "tone", "style_characteristics", "language_preference",
            "writing_format", "prompt_template", "example"
        ]
        for attr in style_attrs:
            result[attr] = getattr(item, attr, None) if hasattr(item, attr) else None

    elif model_cls.__name__ == "Platform":
        platform_attrs = [
            "platform_type", "url", "logo_url", "max_title_length",
            "max_content_length", "allowed_media_types", "api_config"
        ]
        for attr in platform_attrs:
            result[attr] = getattr(item, attr, None) if hasattr(item, attr) else None

    return result

def _handle_article_style_compatibility(db, style_obj: Any, style_data: Any) -> None:
    """处理文章风格与内容类型的兼容性关系

    Args:
        db: 数据库会话
        style_obj: 文章风格对象
        style_data: 文章风格数据
    """
    try:
        # 动态导入ContentType模型
        from core.models.db import ContentType

        # 获取内容类型ID列表
        content_types_ids = getattr(style_data, "content_types", [])

        if content_types_ids:
            # 清除现有关联
            style_obj.compatible_content_types = []

            # 添加新关联
            for ct_id in content_types_ids:
                ct = db.query(ContentType).filter(ContentType.id == ct_id).first()
                if ct:
                    style_obj.compatible_content_types.append(ct)
    except ImportError:
        logger.warning("无法导入ContentType模型，跳过兼容性处理")
    except Exception as e:
        logger.error(f"处理文章风格兼容性关系失败: {str(e)}")

def migrate_content_types(sync_mode: bool = False) -> bool:
    """迁移内容类型配置到数据库

    Args:
        sync_mode: 是否为同步模式

    Returns:
        bool: 是否成功
    """
    return migrate_config(
        model_cls=ContentType,
        module_name='.content_type',
        data_attr_or_func='load_content_types',
        sync_mode=sync_mode
    )

def migrate_article_styles(sync_mode: bool = False) -> bool:
    """迁移文章风格配置到数据库

    Args:
        sync_mode: 是否为同步模式

    Returns:
        bool: 是否成功
    """
    return migrate_config(
        model_cls=ArticleStyle,
        module_name='.article_style',
        data_attr_or_func='load_article_styles',
        sync_mode=sync_mode,
        special_handlers={"compatibility": _handle_article_style_compatibility}
    )

def migrate_platforms(sync_mode: bool = False) -> bool:
    """迁移平台配置到数据库

    Args:
        sync_mode: 是否为同步模式

    Returns:
        bool: 是否成功
    """
    return migrate_config(
        model_cls=Platform,
        module_name='.platform',
        data_attr_or_func='PLATFORM_CONFIGS',
        sync_mode=sync_mode
    )

def migrate_all(sync_mode: bool = False) -> bool:
    """迁移所有配置到数据库

    Args:
        sync_mode: 是否为同步模式。同步模式下会删除不在文件中的记录。

    Returns:
        bool: 全部成功返回True，任一失败返回False
    """
    # 确保数据库已初始化
    initialize_all()

    # 迁移各类配置
    result_content = migrate_content_types(sync_mode)
    result_styles = migrate_article_styles(sync_mode)
    result_platforms = migrate_platforms(sync_mode)

    all_success = result_content and result_styles and result_platforms
    status = "成功" if all_success else "部分失败"
    logger.info(f"所有配置迁移{status}")

    return all_success

if __name__ == "__main__":
    # 默认使用同步模式
    migrate_all(sync_mode=True)
