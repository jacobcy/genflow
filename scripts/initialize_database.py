#!/usr/bin/env python3
"""
数据库初始化脚本

该脚本用于执行完整的数据库初始化和同步，包括：
1. 创建数据库和表结构
2. 同步配置文件到数据库（删除不存在的配置记录）

用法：
    python initialize_database.py
"""

import os
import sys
from loguru import logger

def main():
    """执行数据库初始化和同步"""
    # 设置日志
    logger.add("logs/db_init.log", rotation="1 day", level="INFO")
    logger.info("开始执行数据库初始化和同步")

    # 确保logs目录存在
    os.makedirs("logs", exist_ok=True)

    try:
        # 导入ContentManager
        from core.models.content_manager import ContentManager

        # 使用数据库模式初始化ContentManager
        ContentManager.initialize(use_db=True)
        logger.info("内容管理器初始化成功")

        # 执行完整同步（包括删除不存在的配置）
        if not ContentManager.sync_configs_to_db_full():
            logger.error("完整同步配置到数据库失败")
            return False

        logger.info("完整同步成功：配置文件已同步到数据库（包括删除不存在的配置）")
        return True
    except ImportError as e:
        logger.error(f"导入数据库模块失败: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"初始化过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("数据库初始化和完整同步成功完成！")
        sys.exit(0)
    else:
        print("数据库初始化或同步过程中发生错误，详情请查看日志")
        sys.exit(1)
