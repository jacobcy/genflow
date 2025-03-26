"""数据爬虫脚本

用于抓取各平台热点数据并更新Redis缓存。
"""
import os
import sys
import asyncio
import logging
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from core.tools.trending_tools.tasks import update_trending_data
from core.tools.trending_tools.redis_storage import RedisStorage
from core.tools.trending_tools.config import get_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """主函数"""
    start_time = datetime.now()
    logger.info(f"开始抓取数据: {start_time}")
    
    try:
        # 获取配置
        config = get_config()
        logger.info(f"已加载配置: {config}")
        
        # 更新数据
        logger.info("开始更新热点数据...")
        success = await update_trending_data()
        
        # 验证数据
        if success:
            logger.info("数据更新成功，开始验证数据...")
            storage = RedisStorage(config["redis_url"])
            platforms = await storage.get_all_platforms()
            
            if not platforms:
                logger.warning("未找到任何平台数据")
            else:
                total_topics = 0
                for platform in platforms:
                    topics = await storage.get_platform_topics(platform)
                    topic_count = len(topics)
                    total_topics += topic_count
                    logger.info(f"平台 {platform}: {topic_count} 条话题")
                
                logger.info(f"总计: {len(platforms)} 个平台, {total_topics} 条话题")
        else:
            logger.error("数据更新失败")
    
    except Exception as e:
        logger.error(f"数据更新失败: {e}", exc_info=True)
        return False
    
    finally:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"抓取完成: 耗时 {duration:.2f} 秒")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1) 