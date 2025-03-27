"""
检查 Redis 数据库中的数据统计
"""
import sys
import os
import asyncio
from typing import Dict, List, Set
import logging
from datetime import datetime
import argparse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from core.tools.trending_tools import TrendingTopics
from core.tools.trending_tools.platform_categories import CATEGORY_TAGS, get_platforms_by_category
from core.tools.trending_tools.redis_storage import RedisStorage
from core.tools.trending_tools.config import get_config

async def test_redis_stats():
    """测试Redis数据统计"""
    print("\n=== Redis数据统计 ===")

    config = get_config()
    redis = RedisStorage(config["redis_url"])

    # 获取所有平台的数据
    platform_stats = {}
    total_topics = 0

    # 获取所有平台列表
    all_platforms = set()
    for category in CATEGORY_TAGS:
        platforms = get_platforms_by_category(category)
        if platforms:
            all_platforms.update(platforms)

    print("\n" + "="*50)
    print("【数据库统计】")
    print(f"总平台数: {len(all_platforms)}")

    # 统计每个平台的数据
    platforms_with_data = []
    for platform in sorted(all_platforms):
        try:
            topics = await redis.get_platform_topics(platform)
            topic_count = len(topics)
            if topic_count > 0:
                platform_stats[platform] = topic_count
                platforms_with_data.append(platform)
                total_topics += topic_count
                logger.info(f"平台 {platform}: {topic_count} 条话题")
        except Exception as e:
            logger.warning(f"获取平台 {platform} 数据失败: {e}")

    # 打印统计信息
    print(f"有数据的平台数: {len(platform_stats)}/{len(all_platforms)}")
    print(f"话题总数: {total_topics}")

    print("\n【各平台数据统计】")
    if platform_stats:
        for platform, count in sorted(platform_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"- {platform}: {count}条")
    else:
        print("无数据")

    # 获取最后更新时间
    latest_update = None
    for platform in platforms_with_data:
        try:
            update_time = await redis.get_platform_update_time(platform)
            if update_time and (latest_update is None or update_time > latest_update):
                latest_update = update_time
        except Exception as e:
            logger.warning(f"获取平台 {platform} 更新时间失败: {e}")

    print("\n【最后更新时间】")
    if latest_update:
        update_time_str = datetime.fromtimestamp(latest_update).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{update_time_str}")
    else:
        print("未找到更新时间信息")

    # 打印分类统计
    print("\n【各分类平台统计】")
    category_stats = {}

    for category in CATEGORY_TAGS:
        platforms = get_platforms_by_category(category)
        if platforms:
            platform_count = len(platforms)
            active_count = len([p for p in platforms if p in platform_stats])
            category_stats[category] = (active_count, platform_count)

    for category, (active, total) in sorted(category_stats.items(), key=lambda x: x[1][0]/max(x[1][1], 1), reverse=True):
        percentage = (active / total) * 100 if total > 0 else 0
        print(f"- {category}: {active}/{total} 个平台有数据 ({percentage:.1f}%)")

async def test_core_functions():
    """测试核心功能"""
    print("\n=== 核心功能测试 ===")
    tool = TrendingTopics()

    print("\n" + "="*50)
    print("【工具元数据】")
    print("工具名称:", tool.name)
    print("工具描述:")
    print("-"*50)
    print(tool.description)
    print("-"*50)
    print("\n【参数说明】")
    for param, config in tool.parameters["properties"].items():
        print(f"- {param}: {config.get('description')}")
        print(f"  类型: {config.get('type')}")
        if 'default' in config:
            print(f"  默认值: {config.get('default')}")
        if 'minimum' in config:
            print(f"  最小值: {config.get('minimum')}")
        if 'maximum' in config:
            print(f"  最大值: {config.get('maximum')}")
        print()
    print("="*50)

    # 1. 测试默认获取热点话题
    print("\n1. 测试默认获取热点话题")
    print("\n【发送请求】默认参数")
    result = await tool.execute()

    print("\n【响应数据】")
    print(f"- 状态: {'成功' if not result.get('error') else '失败'}")
    print(f"- 消息: {result.get('message')}")
    print(f"- 总数: {result.get('total')}")
    print(f"- 分类: {result.get('category')}")

    topics = result.get('topics', [])
    print(f"\n获取到 {len(topics)} 条话题：")

    for i, topic in enumerate(topics[:3], 1):
        print(f"\n话题 {i}:")
        print(f"  标题: {topic.get('title')}")
        print(f"  平台: {topic.get('platform')}")
        print(f"  热度: {topic.get('hot')}")
        print(f"  优先级: {topic.get('priority_score')}")
        print(f"  时间戳: {topic.get('timestamp')}")

    if len(topics) > 3:
        print(f"\n... 还有 {len(topics) - 3} 条话题 ...")

    # 2. 测试指定分类获取
    print("\n" + "="*50)
    print("\n2. 测试指定分类获取(科技类)")
    print("\n【发送请求】category='科技'")
    result = await tool.execute(category="科技")

    print("\n【响应数据】")
    print(f"- 状态: {'成功' if not result.get('error') else '失败'}")
    print(f"- 消息: {result.get('message')}")
    print(f"- 总数: {result.get('total')}")
    print(f"- 分类: {result.get('category')}")

    topics = result.get('topics', [])
    print(f"\n获取到 {len(topics)} 条科技类话题")

    for i, topic in enumerate(topics[:3], 1):
        print(f"\n话题 {i}:")
        print(f"  标题: {topic.get('title')}")
        print(f"  平台: {topic.get('platform')}")
        print(f"  热度: {topic.get('hot')}")

    if len(topics) > 3:
        print(f"\n... 还有 {len(topics) - 3} 条话题 ...")

    # 3. 测试关键词搜索
    print("\n" + "="*50)
    print("\n3. 测试关键词搜索(关键词: AI)")
    print("\n【发送请求】keywords='AI'")
    result = await tool.execute(keywords="AI")

    print("\n【响应数据】")
    print(f"- 状态: {'成功' if not result.get('error') else '失败'}")
    print(f"- 消息: {result.get('message')}")
    print(f"- 总数: {result.get('total')}")
    print(f"- 分类: {result.get('category')}")
    print(f"- 平台: {', '.join(result.get('platforms', []))}")

    topics = result.get('topics', [])
    print(f"\n搜索到 {len(topics)} 条相关话题")

    for i, topic in enumerate(topics[:3], 1):
        print(f"\n话题 {i}:")
        print(f"  标题: {topic.get('title')}")
        print(f"  平台: {topic.get('platform')}")
        print(f"  热度: {topic.get('hot')}")

    if len(topics) > 3:
        print(f"\n... 还有 {len(topics) - 3} 条话题 ...")

    # 4. 测试数量限制
    print("\n" + "="*50)
    print("\n4. 测试数量限制(限制5条)")
    print("\n【发送请求】limit=5")
    result = await tool.execute(limit=5)

    print("\n【响应数据】")
    print(f"- 状态: {'成功' if not result.get('error') else '失败'}")
    print(f"- 消息: {result.get('message')}")
    print(f"- 总数: {result.get('total')}")
    print(f"- 分类: {result.get('category')}")
    print(f"- 平台: {', '.join(result.get('platforms', []))}")

    topics = result.get('topics', [])
    if topics:
        print(f"\n限制返回 {len(topics)} 条话题:")
        for i, topic in enumerate(topics, 1):
            print(f"\n话题 {i}:")
            print(f"  标题: {topic.get('title')}")
            print(f"  平台: {topic.get('platform')}")
            print(f"  热度: {topic.get('hot')}")
    else:
        print("\n未找到任何话题")

if __name__ == "__main__":
    asyncio.run(test_redis_stats())
    asyncio.run(test_core_functions())
