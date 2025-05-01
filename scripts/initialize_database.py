#!/usr/bin/env python3
"""
数据库初始化脚本

该脚本用于执行完整的数据库初始化和同步，包括：
1. 创建数据库和表结构
2. 同步配置文件到数据库（删除不存在的配置记录）

用法：
    # 1. 激活虚拟环境
    # source .venv/bin/activate
    # 2. 运行脚本
    python initialize_database.py
"""

import os
import sys
from loguru import logger
from pathlib import Path

# --- 环境设置 开始 ---
# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent
backend_src_dir = project_root / "backend" / "src"
core_dir = project_root / "core"

# 将项目根目录、后端src目录和core目录添加到Python路径
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(backend_src_dir) not in sys.path:
    sys.path.insert(0, str(backend_src_dir))
if str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

# 检查是否在虚拟环境中运行 (可选但推荐)
try:
    import core # 尝试导入一个核心模块
except ImportError:
    logger.warning("警告：似乎没有在虚拟环境中运行，或者PYTHONPATH设置不完整。")
    logger.warning("请确保先激活虚拟环境: source .venv/bin/activate")
# --- 环境设置 结束 ---

print(f"DEBUG sys.path: {sys.path}")

def main():
    """执行数据库初始化和同步"""
    # 设置日志
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    logger.add(log_dir / "db_init.log", rotation="1 day", level="INFO")
    logger.info("开始执行数据库初始化和同步")

    try:
        # 1. 初始化数据库结构
        logger.info("开始初始化数据库结构...")
        from core.models.db.initialize import initialize_all
        initialize_all()
        logger.info("数据库结构初始化成功")

        # 2. 执行完整配置同步
        logger.info("开始执行完整配置同步...")
        from core.models.db.migrate_configs import migrate_all
        migrate_all(sync_mode=True) # sync_mode=True 表示完整同步
        logger.info("完整配置同步成功")

        return True
    except ImportError as e:
        logger.error(f"导入数据库或迁移模块失败: {str(e)}")
        logger.error("请确保在项目根目录激活了虚拟环境 (.venv) 并正确设置了PYTHONPATH")
        return False
    except Exception as e:
        logger.error(f"初始化或同步过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("数据库初始化和完整同步成功完成！")
        sys.exit(0)
    else:
        print("数据库初始化或同步过程中发生错误，详情请查看日志")
        sys.exit(1)
