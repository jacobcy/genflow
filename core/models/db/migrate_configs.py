"""配置文件迁移工具

将已有的配置文件迁移到数据库中，支持增量同步和全量同步模式。
增量同步模式下只添加和更新记录，全量同步模式下会删除不在配置文件中的记录。
"""

import importlib
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Set, Type, Callable, Optional, Tuple, Union
from loguru import logger

# Import session and moved config loading functions
from .session import get_db
from core.models.infra.json_loader import get_config_file_path, load_json_config
# Remove incorrect import of initialize_all from initialize
# from core.models.db.initialize import initialize_all

# Keep try-except for model imports for now, or move imports inside functions
try:
    # Try importing necessary DB models directly
    from core.models.content_type.content_type_db import ContentType
    from core.models.style.style_db import ArticleStyle
    from core.models.platform.platform_db import Platform
except ImportError:
    # Fallback placeholder if models cannot be imported at top level
    logger.warning("无法在顶层导入数据库模型，将在函数内尝试导入")
    ContentType = Any
    ArticleStyle = Any
    Platform = Any

def migrate_config(
    model_cls: Type,
    items: Dict[str, Any],
    sync_mode: bool = False,
    id_field: str = "id",
    special_handlers: Optional[Dict[str, Callable]] = None
) -> bool:
    """通用配置迁移函数

    将配置数据同步到数据库，支持增量和全量同步模式

    Args:
        model_cls: 数据库模型类
        items: 从文件加载的配置项字典 {item_id: item_data}
        sync_mode: 是否为同步模式。同步模式下会删除不在文件中的记录
        id_field: ID字段名，默认为"id"
        special_handlers: 特殊处理函数，用于处理特定模型的额外逻辑

    Returns:
        bool: 是否成功迁移
    """
    try:
        # 检查数据是否为空
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
            for item_id, item_data in items.items():
                # 检查是否已存在
                existing = db.query(model_cls).filter(getattr(model_cls, id_field) == item_id).first()

                if existing:
                    # 更新现有记录
                    for key, value in item_data.items():
                        # 确保字段存在且不是主键
                        if key != id_field and hasattr(existing, key):
                            setattr(existing, key, value)
                    item_obj = existing
                    logger.info(f"更新{model_cls.__name__}: {getattr(existing, id_field)}")
                else:
                    # 创建新记录
                    # 确保提供了ID
                    if id_field not in item_data:
                       item_data[id_field] = item_id 
                    item_obj = model_cls(**item_data)
                    db.add(item_obj)
                    logger.info(f"创建{model_cls.__name__}: {item_data.get(id_field)}")

                # 处理特殊逻辑
                if special_handlers:
                    for handler_name, handler_func in special_handlers.items():
                        handler_func(db, item_obj, item_data) # 传入 item_data 而非 item 对象

            # 提交更改
            db.commit()

        logger.info(f"{model_cls.__name__}配置迁移完成")
        return True

    except Exception as e:
        logger.error(f"{model_cls.__name__}配置迁移失败: {str(e)}", exc_info=True)
        return False

def _handle_article_style_compatibility(db, style_obj: Any, style_data: Dict[str, Any]) -> None:
    """处理文章风格与内容类型的兼容性关系

    Args:
        db: 数据库会话
        style_obj: 文章风格数据库对象 (ArticleStyle DB model instance)
        style_data: 从 Manager 加载的风格配置字典 (来自 Pydantic model.dict())
    """
    try:
        # Correctly import ContentTypeName model
        try:
            from core.models.content_type.content_type_db import ContentTypeName as ContentTypeNameModel
        except ImportError:
            logger.warning("无法导入 ContentTypeName 模型，跳过兼容性处理")
            return

        # Get compatible content type names from the Pydantic object's data
        # Use 'content_types' field from the Pydantic model data (now in style_data dict)
        content_type_names_from_config = style_data.get("content_types", [])
        if not isinstance(content_type_names_from_config, list):
             logger.warning(f"风格 {style_obj.name} 的 'content_types' 字段不是列表，跳过兼容性处理。 Found: {content_type_names_from_config}")
             content_type_names_from_config = [] # Treat as empty

        if not content_type_names_from_config:
            # If config specifies no compatible types, clear the relationship
            logger.debug(f"风格 {style_obj.name} 在配置中未指定兼容的内容类型，清空关联。")
            style_obj.compatible_content_types = []
            return

        # Efficiently query all needed content type objects at once
        compatible_ct_objects = db.query(ContentTypeNameModel).filter(ContentTypeNameModel.name.in_(content_type_names_from_config)).all()

        # Check if all requested names were found in the database
        found_names = {ct.name for ct in compatible_ct_objects}
        missing_names = set(content_type_names_from_config) - found_names
        if missing_names:
            logger.warning(f"为风格 {style_obj.name} 处理兼容性时，未在数据库中找到以下内容类型: {missing_names}。只会关联找到的类型。")

        # Assign the list of fetched DB objects to the relationship attribute
        # SQLAlchemy will automatically manage the association table based on this assignment
        style_obj.compatible_content_types = compatible_ct_objects
        logger.debug(f"已更新风格 {style_obj.name} 的兼容内容类型关联，关联了 {len(compatible_ct_objects)} 个类型。")

    except Exception as e:
        # Use the correct ID field 'name' in the error message
        logger.error(f"处理文章风格 {getattr(style_obj, 'name', '未知')} 兼容性关系失败: {str(e)}", exc_info=True)

def migrate_content_types(sync_mode: bool = False) -> bool:
    """迁移内容类型配置到数据库

    Args:
        sync_mode: 是否为同步模式

    Returns:
        bool: 是否成功
    """
    # Correctly import ContentTypeName model
    try:
        from core.models.content_type.content_type_db import ContentTypeName as ContentTypeNameModel
    except ImportError:
        logger.error("无法导入 ContentTypeName 模型，无法迁移")
        return False

    # Provide both the config key and the filename to get_config_file_path
    config_path = get_config_file_path("content_types", "content_types.json") # Restored filename argument
    if not config_path:
        # Assuming get_config_file_path returns None or raises error if not found
        logger.error("找不到 content_types.json 配置文件路径")
        return False

    config_data = load_json_config(config_path)
    # Check if config_data itself is None or the key 'content_types' is missing/empty
    if not config_data or not config_data.get("content_types"):
        logger.error(f"无法加载或解析 {config_path}，或者 'content_types' 列表为空或不存在")
        return False

    # Extract the list of content type dicts
    content_type_list = config_data["content_types"]

    # Convert list to a dict keyed by the 'name' field
    items_dict = {item['name']: item for item in content_type_list if 'name' in item}
    if len(items_dict) != len(content_type_list):
        logger.warning("content_types.json 中部分条目缺少 'name' 字段")

    # Call migrate_config with ContentTypeName model and 'name' as the unique key
    return migrate_config(
        model_cls=ContentTypeNameModel,
        items=items_dict,
        sync_mode=sync_mode,
        id_field='name' # Specify 'name' as the ID field for ContentTypeName
    )

def migrate_article_styles(sync_mode: bool = False) -> bool:
    """迁移文章风格配置到数据库

    Args:
        sync_mode: 是否为同步模式

    Returns:
        bool: 是否成功
    """
    try:
        from core.models.style.style_db import ArticleStyle as StyleModel
        # Import the Pydantic model and StyleManager
        from core.models.style import StyleManager, ArticleStyle as StylePydanticModel
    except ImportError as e:
        logger.error(f"无法导入 ArticleStyle 模型或 StyleManager: {e}", exc_info=True)
        return False

    # Load configurations using StyleManager
    try:
        # Ensure manager is initialized and load configs
        StyleManager.ensure_initialized()
        all_styles_pydantic: Dict[str, StylePydanticModel] = StyleManager.get_all_configs()
        if not all_styles_pydantic:
            logger.warning("StyleManager 未加载任何风格配置，跳过迁移。")
            return True # Nothing to migrate, not an error

    except Exception as e:
        logger.error(f"使用 StyleManager 加载风格配置失败: {e}", exc_info=True)
        return False

    # Convert Pydantic objects to dicts, using 'name' as the key
    # Use model_dump (or dict) for Pydantic v2 (or v1)
    items_dict: Dict[str, Dict[str, Any]] = {}
    for style_name, style_pydantic in all_styles_pydantic.items():
        try:
            # Ensure the key matches the object's name field
            if style_name != style_pydantic.name:
                logger.warning(f"Style key '{style_name}' 与对象 name '{style_pydantic.name}' 不匹配，跳过此风格。")
                continue
            # Use model_dump for Pydantic v2+, dict() for v1
            if hasattr(style_pydantic, 'model_dump'):
                items_dict[style_name] = style_pydantic.model_dump()
            else:
                items_dict[style_name] = style_pydantic.dict()
        except Exception as e:
             logger.error(f"转换 Pydantic 风格对象 '{style_name}' 为字典失败: {e}", exc_info=True)
             # Decide if one failure should stop the whole migration
             continue # Skip this item

    if not items_dict:
         logger.warning("没有成功转换任何风格配置为字典，迁移中止。")
         return False

    # Call migrate_config with the correct model, items, id_field, and handlers
    return migrate_config(
        model_cls=StyleModel, # SQLAlchemy model
        items=items_dict,
        sync_mode=sync_mode,
        id_field='name', # Use 'name' as the primary key field
        special_handlers={"compatibility": _handle_article_style_compatibility}
    )

def migrate_platforms(sync_mode: bool = False) -> bool:
    """迁移平台配置到数据库

    Args:
        sync_mode: 是否为同步模式

    Returns:
        bool: 是否成功
    """
    try:
        from core.models.platform.platform_db import Platform as PlatformModel
    except ImportError:
        logger.error("无法导入 Platform 模型，无法迁移")
        return False

    config_path = get_config_file_path("platforms", "platforms.json")
    config_data = load_json_config(config_path)
    if not config_data or "platforms" not in config_data:
        logger.error("无法加载或解析 platforms.json")
        return False

    # 将列表转换为ID为键的字典
    items_dict = {item['id']: item for item in config_data["platforms"]}

    return migrate_config(
        model_cls=PlatformModel,
        items=items_dict,
        sync_mode=sync_mode
    )

def migrate_all(sync_mode: bool = False) -> bool:
    """迁移所有配置到数据库

    Args:
        sync_mode: 是否为同步模式。同步模式下会删除不在文件中的记录。

    Returns:
        bool: 全部成功返回True，任一失败返回False
    """
    logger.info(f"开始执行配置迁移 (sync_mode={sync_mode})...")
    # Remove the call to initialize_all()
    # initialize_all()

    # 迁移各类配置
    result_content = migrate_content_types(sync_mode)
    result_style = migrate_article_styles(sync_mode)
    result_platform = migrate_platforms(sync_mode)

    # 检查所有迁移结果
    if result_content and result_style and result_platform:
        logger.info("所有配置成功迁移到数据库")
        return True
    else:
        logger.error("部分配置迁移失败")
        return False

# 本地测试
if __name__ == "__main__":
    # 执行完整同步
    logger.info("执行完整配置同步测试...")
    # It might be better to call initialize_all from the main script or test setup
    # For standalone testing, ensure tables exist first
    # from .session import init_db as create_tables
    # create_tables()
    success = migrate_all(sync_mode=True)
    exit_code = 0 if success else 1
    exit(exit_code)
