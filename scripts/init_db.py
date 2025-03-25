#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加项目根目录和后端源码目录到 Python 路径
project_root = Path(__file__).parent.parent.absolute()
backend_src = project_root / "backend" / "src"
sys.path.insert(0, str(project_root))  # 添加项目根目录
sys.path.insert(0, str(backend_src))   # 确保后端源码目录优先

# 导入测试
try:
    from core.security import get_password_hash
    from core.config import settings
    from db.session import async_engine
    from db.init_db import init_database, create_first_admin
    print("成功导入所有必要模块")
except ImportError as e:
    print(f"导入错误: {e}")
    print(f"Python 路径: {sys.path}")
    sys.exit(1)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        await init_database()
        await create_first_admin()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
