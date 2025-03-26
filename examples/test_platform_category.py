"""测试平台分类与内容类型的映射功能

测试根据平台分类自动确定内容类型的功能是否正常工作。
"""
import asyncio
import logging
from core.constants.platform_categories import get_platform_categories, PLATFORM_CATEGORIES
from core.constants.content_types import get_content_type_from_categories, ALL_CONTENT_TYPES

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_platform_to_content_type():
    """测试平台分类到内容类型的映射"""
    logger.info("开始测试平台分类到内容类型的映射...")

    # 测试所有平台
    for platform_name, categories in PLATFORM_CATEGORIES.items():
        content_type = get_content_type_from_categories(categories)
        logger.info(f"平台: {platform_name}, 分类: {categories}, 推荐内容类型: {content_type}")

    logger.info("平台分类到内容类型的映射测试完成")

if __name__ == "__main__":
    asyncio.run(test_platform_to_content_type())
    logger.info("所有测试完成")
