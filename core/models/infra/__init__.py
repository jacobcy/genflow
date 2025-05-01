"""管理器模块初始化

导出所有管理器类，用于统一管理模型。
"""

from core.models.infra.base_manager import BaseManager
# Remove the following commented-out lines:
# # from config_service import ConfigService # 移除错误的导入
# # from .db_adapter import DBAdapter # 移除 DBAdapter 导入
from .enums import * # 使用相对导入
from .json_loader import JsonModelLoader # 使用相对导入
from .temporary_storage import TemporaryStorage # 使用相对导入

__all__ = ['BaseManager', 'JsonModelLoader', 'TemporaryStorage', 'ArticleSectionType', 'ContentCategory', 'CategoryType', 'ProductionStage', 'StageStatus'] # 移除 DBAdapter
