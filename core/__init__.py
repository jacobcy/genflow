"""
GenFlow Core Module

This package contains the core functionality of the GenFlow system,
including tools for content generation, data collection, and processing.
"""

__version__ = "0.1.0"

import os
import sys
import logging
from loguru import logger

# 初始化日志设置
if not logger._core.handlers:
    logger.add("logs/core.log", rotation="1 day", retention="7 days", level="INFO")

# 确保logs目录存在
os.makedirs("logs", exist_ok=True)

# 初始化数据库
try:
    # 使用数据库适配器初始化数据库
    from core.models.infra.db_adapter import DBAdapter

    # 初始化数据库并同步配置文件
    if DBAdapter.initialize():
        logger.info("数据库初始化完成")

        # 同步配置文件到数据库（非同步模式，不删除数据库中已存在的配置）
        if DBAdapter.sync_config_to_db(sync_mode=False):
            logger.info("配置文件同步到数据库完成（仅添加或更新）")
        else:
            logger.warning("配置文件同步到数据库失败")
    else:
        logger.warning("数据库初始化失败")
except ImportError as e:
    logger.warning(f"数据库模块导入失败: {str(e)}")
except Exception as e:
    logger.error(f"数据库初始化失败: {str(e)}")
