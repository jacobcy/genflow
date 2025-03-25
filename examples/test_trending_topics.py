"""测试 TrendingTopics 工具的使用示例

展示如何在 AI Agent 中使用热点获取工具。
"""
import sys
import os
import asyncio
from typing import Dict, List, Set
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from core.tools.trending_tools import TrendingTopics
from core.tools.trending_tools.platform_categories import CATEGORY_TAGS, get_platforms_by_category
from core.tools.trending_tools.redis_storage import RedisStorage
from core.tools.trending_tools.config import get_config

def get_operation_mode() -> str:
    """获取操作模式

    Returns:
        str: 'read' 表示读取缓存，'fetch' 表示抓取新数据
    """
    while True:
        mode = input("\n请选择操作模式:\n1. 从缓存读取数据 [read]\n2. 从API抓取新数据 [fetch]\n请输入选择 (1/2): ")
        if mode in ['1', 'read']:
            print("\n已选择: 从缓存读取数据")
            return 'read'
        elif mode in ['2', 'fetch']:
            print("\n已选择: 从API抓取新数据")
            return 'fetch'
        print("无效的选择，请重试")

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

    # 统计每个平台的数据
    for platform in all_platforms:
        try:
            topics = await redis.get_platform_topics(platform)
            topic_count = len(topics)
            if topic_count > 0:
                platform_stats[platform] = topic_count
                total_topics += topic_count
                logger.info(f"平台 {platform}: {topic_count} 条话题")
        except Exception as e:
            logger.warning(f"获取平台 {platform} 数据失败: {e}")

    # 打印统计信息
    print(f"\n接口总数: {len(platform_stats)}")
    print(f"话题总数: {total_topics}")
    print("\n各平台数据统计:")
    for platform, count in sorted(platform_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"- {platform}: {count}条")

    # 获取最后更新时间
    latest_update = None
    for platform in platform_stats:
        try:
            update_time = await redis.get_platform_update_time(platform)
            if update_time and (latest_update is None or update_time > latest_update):
                latest_update = update_time
        except Exception as e:
            logger.warning(f"获取平台 {platform} 更新时间失败: {e}")

    if latest_update:
        update_time_str = datetime.fromtimestamp(latest_update).strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n最后更新时间: {update_time_str}")
    else:
        print("\n未找到更新时间信息")

    # 打印分类统计
    print("\n各分类平台统计:")
    for category in CATEGORY_TAGS:
        platforms = get_platforms_by_category(category)
        if platforms:
            platform_count = len(platforms)
            active_count = len([p for p in platforms if p in platform_stats])
            print(f"- {category}: {active_count}/{platform_count} 个平台有数据")

async def test_topics(mode: str = 'read'):
    """测试获取话题功能

    Args:
        mode: 'read' 表示读取缓存，'fetch' 表示抓取新数据
    """
    print("\n=== 测试获取话题功能 ===")

    tool = TrendingTopics()
    result = await tool.execute()  # 使用execute方法

    if "error" in result:
        print(f"获取话题失败: {result['message']}")
        return result

    # 显示详细信息
    print(f"\n获取到 {result['total']} 个'{result.get('category', '热点')}'类话题")
    if "summary" in result:
        print("\n话题摘要:")
        print(result["summary"])
        print(f"\n主要来源平台: {', '.join(result['top_platforms'])}")
    else:
        print("\n话题列表:")
        for topic in result["topics"][:10]:  # 只显示前10条
            print(f"\n标题: {topic['title']}")
            print(f"平台: {topic['platform']}")
            print(f"优先级分数: {topic['priority_score']}")
            if topic.get("description"):
                print(f"描述: {topic['description']}")

    return result

async def test_search_topics(mode: str = 'read'):
    """测试搜索话题功能

    Args:
        mode: 'read' 表示读取缓存，'fetch' 表示抓取新数据
    """
    print("\n=== 测试搜索话题功能 ===")

    tool = TrendingTopics()
    search_category = "科技"
    search_keywords = "AI"

    result = await tool.execute(
        keywords=search_keywords,
        category=search_category
    )

    if "error" in result:
        print(f"搜索话题失败: {result['message']}")
        return result

    print(f"\n在'{result.get('category', search_category)}'分类中搜索'{search_keywords}'相关话题")

    if result['total'] == 0:
        print(f"未找到与'{search_keywords}'直接相关的话题")
        print(f"为您展示'{search_category}'分类下的热门话题：")
        # 重新获取分类数据
        category_result = await tool.execute(category=search_category)
        if category_result.get("topics"):
            print(f"\n获取到 {len(category_result['topics'])} 条{search_category}类话题")
            for topic in category_result["topics"][:5]:
                print(f"\n标题: {topic['title']}")
                print(f"平台: {topic['platform']}")
                print(f"优先级分数: {topic.get('priority_score', 'N/A')}")
                if topic.get("description"):
                    print(f"描述: {topic['description']}")
        return category_result

    print(f"找到 {result['total']} 个相关话题")
    if "summary" in result:
        print("\n话题摘要:")
        print(result["summary"])
        print(f"\n主要来源平台: {', '.join(result['top_platforms'])}")
    else:
        print("\n话题列表:")
        for topic in result["topics"][:5]:
            print(f"\n标题: {topic['title']}")
            print(f"平台: {topic['platform']}")
            print(f"优先级分数: {topic.get('priority_score', 'N/A')}")
            if topic.get("description"):
                print(f"描述: {topic['description']}")

    return result

async def test_invalid_category(mode: str = 'read'):
    """测试无效分类处理

    Args:
        mode: 'read' 表示读取缓存，'fetch' 表示抓取新数据
    """
    print("\n=== 测试无效分类处理 ===")

    tool = TrendingTopics()
    result = await tool.execute(
        category="不存在的分类"
    )

    if "error" in result:
        print(f"获取话题失败: {result['message']}")
        return result

    print(f"\n请求无效分类'不存在的分类'时自动使用'{result.get('category', '热点')}'分类")
    print(f"获取到 {result['total']} 个话题")

    if "summary" in result:
        print("\n话题摘要:")
        print(result["summary"])
    else:
        print("\n话题列表:")
        for topic in result["topics"][:3]:  # 只显示前3条
            print(f"\n标题: {topic['title']}")
            print(f"平台: {topic['platform']}")

    return result

async def test_all_categories(mode: str = 'read'):
    """测试所有有效分类

    Args:
        mode: 'read' 表示读取缓存，'fetch' 表示抓取新数据
    """
    print("\n=== 测试所有有效分类 ===")

    tool = TrendingTopics()
    results = {}
    total_topics = 0

    for category in CATEGORY_TAGS:
        print(f"\n--- 测试 {category} 分类 ---")
        result = await tool.execute(
            category=category
        )
        results[category] = result

        if "error" in result:
            print(f"获取{category}分类失败: {result['message']}")
            continue

        total_topics += result['total']
        print(f"获取到 {result['total']} 个话题")
        if "summary" in result:
            print(f"摘要: {result['summary'][:100]}...")
        else:
            for topic in result["topics"][:3]:
                print(f"- {topic['title']} (来自: {topic['platform']})")

    print(f"\n总计获取 {total_topics} 个话题")

    return results

async def test_crewai_tool():
    """测试 CrewAI 工具接口

    测试工具的主要功能：
    1. 默认获取热点分类数据
    2. 按分类获取数据
    3. 关键词搜索
    4. 结果数量限制
    """
    print("\n=== 测试 CrewAI 工具接口 ===")

    tool = TrendingTopics()

    # 测试默认参数
    print("\n1. 测试默认参数调用")
    result = await tool.execute()
    print(f"默认获取热点话题: 获取到 {result.get('total', 0)} 条数据")
    if result.get("topics"):
        print("示例话题:")
        for topic in result["topics"][:3]:
            print(f"- {topic['title']} (来自: {topic['platform']})")

    # 测试指定分类
    print("\n2. 测试指定分类")
    result = await tool.execute(category="科技")
    print(f"科技分类话题: 获取到 {result.get('total', 0)} 条数据")
    if result.get("topics"):
        print("示例话题:")
        for topic in result["topics"][:3]:
            print(f"- {topic['title']} (来自: {topic['platform']})")

    # 测试关键词搜索
    print("\n3. 测试关键词搜索")
    result = await tool.execute(keywords="AI")
    print(f"搜索'AI'相关话题: 获取到 {result.get('total', 0)} 条数据")
    if result.get("topics"):
        print("示例话题:")
        for topic in result["topics"][:3]:
            print(f"- {topic['title']} (来自: {topic['platform']})")

    # 测试结果数量限制
    print("\n4. 测试结果数量限制")
    result = await tool.execute(limit=5)
    print(f"限制返回5条数据: 获取到 {result.get('total', 0)} 条数据")
    if result.get("topics"):
        print("所有话题:")
        for topic in result["topics"]:
            print(f"- {topic['title']} (来自: {topic['platform']})")

async def test_core_functions():
    """测试核心功能"""
    print("\n=== 核心功能测试 ===")
    tool = TrendingTopics()

    # 1. 测试默认获取热点话题
    print("\n1. 测试默认获取热点话题")
    result = await tool.execute()
    print("\n完整返回数据:")
    print(f"- total: {result.get('total')}")
    print(f"- category: {result.get('category')}")
    print(f"- message: {result.get('message')}")
    print(f"- platforms: {result.get('platforms')}")
    print("\n话题列表:")
    for topic in result.get('topics', []):
        print(f"\n标题: {topic.get('title')}")
        print(f"平台: {topic.get('platform')}")
        print(f"热度: {topic.get('hot')}")
        print(f"优先级分数: {topic.get('priority_score')}")
        if topic.get('description'):
            print(f"描述: {topic.get('description')}")
        print(f"时间戳: {topic.get('timestamp')}")
        print(f"抓取时间: {topic.get('fetch_time')}")
        print(f"过期时间: {topic.get('expire_time')}")
        print("-" * 50)

    # 2. 测试指定分类获取
    print("\n2. 测试指定分类获取(科技类)")
    result = await tool.execute(category="科技")
    topics = result.get('topics', [])
    print(f"获取到 {len(topics)} 条科技类话题")
    if topics:
        topic = topics[0]
        print(f"示例话题: {topic.get('title')} (来自: {topic.get('platform')})")

    # 3. 测试关键词搜索
    print("\n3. 测试关键词搜索(关键词: AI)")
    result = await tool.execute(keywords="AI")
    topics = result.get('topics', [])
    print(f"搜索到 {len(topics)} 条相关话题")
    if topics:
        topic = topics[0]
        print(f"示例话题: {topic.get('title')} (来自: {topic.get('platform')})")

    # 4. 测试数量限制(限制5条)并展示完整的CrewAI工具状态
    print("\n4. 测试数量限制(限制5条)")
    result = await tool.execute(limit=5)
    print("\nCrewAI工具完整状态:")
    print(f"工具名称: {tool.name}")
    print(f"工具描述: {tool.description}")
    print("\n参数配置:")
    for param, config in tool.parameters["properties"].items():
        print(f"- {param}: {config}")

    print("\n执行结果:")
    print(f"- total: {result.get('total')}")
    print(f"- category: {result.get('category')}")
    print(f"- message: {result.get('message')}")
    print(f"- platforms: {result.get('platforms')}")

    print("\n话题列表:")
    for topic in result.get('topics', []):
        print(f"\n标题: {topic.get('title')}")
        print(f"平台: {topic.get('platform')}")
        print(f"热度: {topic.get('hot')}")
        print(f"优先级分数: {topic.get('priority_score')}")
        if topic.get('description'):
            print(f"描述: {topic.get('description')}")
        print(f"时间戳: {topic.get('timestamp')}")
        print(f"抓取时间: {topic.get('fetch_time')}")
        print(f"过期时间: {topic.get('expire_time')}")
        print("-" * 50)

async def main():
    """主函数"""
    # 1. 数据统计
    await test_redis_stats()

    # 2. 功能测试
    await test_core_functions()

if __name__ == "__main__":
    asyncio.run(main())
