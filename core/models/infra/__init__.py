"""管理器模块初始化

导出所有管理器类，用于统一管理模型。
"""

from core.models.infra.base_manager import BaseManager
from config_service import ConfigService
from db_adapter import DBAdapter
from enums import *
from json_loader import JsonModelLoader
from temporary_storage import TemporaryStorage

__all__ = ['BaseManager', 'ConfigService', 'DBAdapter', 'JsonModelLoader', 'TemporaryStorage', 'ArticleSectionType', 'ContentCategory', 'CategoryType', 'ProductionStage', 'StageStatus']
