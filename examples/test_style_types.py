"""风格类型模块测试脚本

本脚本用于测试style_types.py模块的功能，包括风格特征获取、平台配置加载等。
"""

import logging
import asyncio
from core.constants.style_types import (
    ALL_STYLE_TYPES,
    get_style_features,
    get_style_description,
    get_platform_style_type,
    get_similar_styles,
    get_style_config,
    StyleTypeConfig
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

async def test_style_types():
    """测试风格类型基本功能"""
    logger.info("开始测试风格类型基本功能...")

    # 测试所有风格类型
    logger.info(f"支持的风格类型: {ALL_STYLE_TYPES}")

    # 测试风格特征获取
    for style_type in ALL_STYLE_TYPES:
        features = get_style_features(style_type)
        logger.info(f"风格类型 '{style_type}' 的特征:")
        logger.info(f"  语调: {features.get('tone')}")
        logger.info(f"  正式程度: {features.get('formality')}")
        logger.info(f"  特点: {', '.join(features.get('characteristics', []))}")

    # 测试风格描述
    logger.info("\n风格描述:")
    for style_type in ALL_STYLE_TYPES:
        desc = get_style_description(style_type)
        logger.info(f"  {style_type}: {desc}")

    # 测试平台到风格的映射
    logger.info("\n平台ID到风格的映射:")
    platforms = ["zhihu", "xiaohongshu", "weibo", "bilibili", "wechat", "douyin", "csdn", "toutiao"]
    for platform_id in platforms:
        style_type = get_platform_style_type(platform_id)
        logger.info(f"  平台 '{platform_id}' -> 风格 '{style_type}'")

    # 测试相似风格查询
    logger.info("\n相似风格查询:")
    for style_type in ALL_STYLE_TYPES:
        similar = get_similar_styles(style_type, count=2)
        logger.info(f"  与 '{style_type}' 相似的风格: {similar}")

    logger.info("风格类型基本功能测试完成")

async def test_style_config():
    """测试StyleTypeConfig类的功能"""
    logger.info("\n开始测试StyleTypeConfig类...")

    # 获取配置实例
    config = get_style_config()

    # 测试平台配置加载
    platform_ids = config.get_all_platform_ids()
    logger.info(f"已加载的平台配置: {platform_ids}")

    # 测试获取特定平台配置
    for platform_id in platform_ids:
        style_guide = config.get_platform_style_guide(platform_id)
        if style_guide:
            logger.info(f"\n平台 '{platform_id}' 的风格指南:")
            logger.info(f"  写作风格: {style_guide.get('writing_style')}")
            logger.info(f"  目标受众: {style_guide.get('target_audience')}")

            # 获取推荐模式
            patterns = style_guide.get('recommended_patterns', [])
            if patterns:
                logger.info(f"  推荐模式:")
                for pattern in patterns[:3]:  # 只显示前3个
                    logger.info(f"    - {pattern}")

    logger.info("StyleTypeConfig类测试完成")

async def main():
    """主函数"""
    logger.info("开始测试风格类型模块...")

    await test_style_types()
    await test_style_config()

    logger.info("所有测试完成")

if __name__ == "__main__":
    asyncio.run(main())
