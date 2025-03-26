"""测试 TrendingTopics 工具的使用示例

展示如何在 AI Agent 中使用热点获取工具。
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

async def test_keyword_supplement():
    """测试关键词搜索结果不足时自动补充数据的功能"""
    print("\n" + "="*50)
    print("【测试数据自动补充】")
    
    tool = TrendingTopics()
    
    # 1. 使用非常稀少的关键词，确保结果少于limit
    rare_keyword = "量子计算"  # 或其他非常稀有的关键词
    limit = 10  # 设置一个合理的数量限制
    
    print(f"\n【发送请求】keywords='{rare_keyword}', limit={limit}")
    result = await tool.execute(keywords=rare_keyword, limit=limit)
    
    print("\n【响应数据】")
    if "error" in result:
        print(f"- 错误: {result.get('error')}")
        print(f"- 消息: {result.get('message')}")
    else:
        print(f"- 状态: 成功")
        print(f"- 消息: {result.get('message')}")
        print(f"- 总数: {result.get('total')}")
        print(f"- 关键词: {result.get('keywords')}")
        if "is_supplemented" in result:
            print(f"- 是否补充: 是")
            if "matched_count" in result:
                print(f"- 匹配结果数: {result.get('matched_count')}")
            if "supplemented_count" in result:
                print(f"- 补充数量: {result.get('supplemented_count')}")
        
        topics = result.get("topics", [])
        print(f"\n获取到 {len(topics)} 条话题:")
        
        # 打印前几条结果
        for i, topic in enumerate(topics[:3]):
            print(f"\n话题 {i+1}:")
            print(f"  标题: {topic.get('title')}")
            print(f"  平台: {topic.get('platform')}")
            print(f"  热度: {topic.get('hot')}")
        
        if len(topics) > 3:
            print(f"\n... 还有 {len(topics) - 3} 条话题 ...")
    
    # 2. 使用关键词+分类，结果不足时补充
    print("\n" + "="*50)
    print("【测试分类内关键词不足补充】")
    
    category = "科技"
    rare_keyword = "低代码"  # 或其他在科技分类中稀有的关键词
    
    print(f"\n【发送请求】category='{category}', keywords='{rare_keyword}', limit={limit}")
    result = await tool.execute(category=category, keywords=rare_keyword, limit=limit)
    
    print("\n【响应数据】")
    if "error" in result:
        print(f"- 错误: {result.get('error')}")
        print(f"- 消息: {result.get('message')}")
    else:
        print(f"- 状态: 成功")
        print(f"- 消息: {result.get('message')}")
        print(f"- 总数: {result.get('total')}")
        print(f"- 分类: {result.get('category')}")
        print(f"- 关键词: {result.get('keywords')}")
        if "is_supplemented" in result:
            print(f"- 是否补充: 是")
            if "matched_count" in result:
                print(f"- 匹配结果数: {result.get('matched_count')}")
            if "supplemented_count" in result:
                print(f"- 补充数量: {result.get('supplemented_count')}")
        
        topics = result.get("topics", [])
        print(f"\n获取到 {len(topics)} 条话题:")
        
        # 打印前几条结果
        for i, topic in enumerate(topics[:3]):
            print(f"\n话题 {i+1}:")
            print(f"  标题: {topic.get('title')}")
            print(f"  平台: {topic.get('platform')}")
            print(f"  热度: {topic.get('hot')}")
        
        if len(topics) > 3:
            print(f"\n... 还有 {len(topics) - 3} 条话题 ...")

async def test_execute_with_params(param_string: str):
    """测试特定参数的执行结果
    
    Args:
        param_string: 参数字符串，格式如：category=科技&keywords=AI&limit=10
    """
    print("\n" + "="*50)
    print(f"【测试特定参数】: {param_string}")
    
    # 解析参数
    param_dict = {}
    parts = param_string.split("&")
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            # 处理特殊参数类型
            if key == "limit" and value.isdigit():
                param_dict[key] = int(value)
            else:
                param_dict[key] = value
    
    tool = TrendingTopics()
    print(f"\n【发送请求】{param_dict}")
    result = await tool.execute(**param_dict)
    
    print("\n【响应数据】")
    if "error" in result:
        print(f"- 错误: {result.get('error')}")
        print(f"- 消息: {result.get('message')}")
    else:
        print(f"- 状态: 成功")
        print(f"- 消息: {result.get('message')}")
        print(f"- 总数: {result.get('total')}")
        
        if "category" in result:
            print(f"- 分类: {result.get('category')}")
        if "keywords" in result:
            print(f"- 关键词: {result.get('keywords')}")
        if "platforms" in result and result["platforms"]:
            print(f"- 平台: {', '.join(result['platforms'])}")
            
        if "is_supplemented" in result:
            print(f"- 是否补充: 是")
            if "matched_count" in result:
                print(f"- 匹配结果数: {result.get('matched_count')}")
            if "supplemented_count" in result:
                print(f"- 补充数量: {result.get('supplemented_count')}")
        
        topics = result.get("topics", [])
        print(f"\n获取到 {len(topics)} 条话题:")
        
        # 打印前几条结果
        for i, topic in enumerate(topics[:3]):
            print(f"\n话题 {i+1}:")
            print(f"  标题: {topic.get('title')}")
            print(f"  平台: {topic.get('platform')}")
            print(f"  热度: {topic.get('hot')}")
        
        if len(topics) > 3:
            print(f"\n... 还有 {len(topics) - 3} 条话题 ...")

async def test_summary_feature():
    """测试话题摘要功能"""
    print("\n" + "="*50)
    print("【测试话题摘要功能】")
    
    tool = TrendingTopics()
    
    # 测试1: 强制使用摘要
    print("\n" + "-"*40)
    print("测试1: 强制使用摘要模式 (热点分类)")
    print("-"*40)
    result = await tool.execute(
        category="热点",
        limit=20,
        force_summarize=True
    )
    
    if "summary" in result:
        print("\n📊 话题摘要:")
        print(f"➤ {result['summary']}")
        
        # 展示统计信息
        if "stats" in result:
            stats = result["stats"]
            print("\n📈 统计信息:")
            print(f"➤ 话题总数: {stats['total_topics']}")
            print(f"➤ 平台数量: {stats['platform_count']}")
            print(f"➤ 平均热度: {stats['avg_hot']}")
            
            print("\n主要平台:")
            for platform in stats['top_platforms'][:3]:
                print(f"- {platform['name']}: {platform['count']}条")
            
            print("\n热门关键词:")
            for keyword in stats['hot_keywords'][:5]:
                print(f"- {keyword['word']}: 出现{keyword['freq']}次")
        
        print(f"\n包含 {len(result.get('topics', []))} 条热门话题示例:")
        for i, topic in enumerate(result.get("topics", [])[:3], 1):
            print(f"{i}. {topic.get('title')} - {topic.get('platform')} (热度: {topic.get('hot')})")
    else:
        print("获取摘要失败")
    
    # 测试2: 使用关键词并强制摘要
    print("\n" + "-"*40)
    print("测试2: 使用关键词搜索并强制摘要 (关键词: 游戏)")
    print("-"*40)
    result = await tool.execute(
        keywords="游戏",
        limit=20,
        force_summarize=True
    )
    
    if "summary" in result:
        print("\n📊 话题摘要:")
        print(f"➤ {result['summary']}")
        
        # 展示统计信息
        if "stats" in result:
            stats = result["stats"]
            print("\n📈 统计信息:")
            print(f"➤ 话题总数: {stats['total_topics']}")
            print(f"➤ 平台数量: {stats['platform_count']}")
            print(f"➤ 平均热度: {stats['avg_hot']}")
            
            print("\n主要平台:")
            for platform in stats['top_platforms'][:3]:
                print(f"- {platform['name']}: {platform['count']}条")
            
            print("\n热门关键词:")
            for keyword in stats['hot_keywords'][:5]:
                print(f"- {keyword['word']}: 出现{keyword['freq']}次")
        
        print(f"\n包含 {len(result.get('topics', []))} 条关键词相关话题示例:")
        for i, topic in enumerate(result.get("topics", [])[:3], 1):
            print(f"{i}. {topic.get('title')} - {topic.get('platform')} (热度: {topic.get('hot')})")
    else:
        print("获取摘要失败")
    
    # 测试3: 调整字数限制
    print("\n" + "-"*40)
    print("测试3: 调整字数限制 (科技分类, 200字限制)")
    print("-"*40)
    result = await tool.execute(
        category="科技",
        limit=30,
        word_limit=200  # 降低字数限制，更容易触发摘要
    )
    
    if "summary" in result:
        print("\n自动摘要模式 (数据量超过200字限制):")
        print(f"\n📊 话题摘要:")
        print(f"➤ {result['summary']}")
        
        # 展示统计信息
        if "stats" in result:
            stats = result["stats"]
            print("\n📈 统计信息:")
            print(f"➤ 话题总数: {stats['total_topics']}")
            print(f"➤ 平台数量: {stats['platform_count']}")
            print(f"➤ 平均热度: {stats['avg_hot']}")
            
            print("\n主要平台:")
            for platform in stats['top_platforms'][:3]:
                print(f"- {platform['name']}: {platform['count']}条")
            
            print("\n热门关键词:")
            for keyword in stats['hot_keywords'][:5]:
                print(f"- {keyword['word']}: 出现{keyword['freq']}次")
            
        # 计算压缩率
        total_topics = len(result.get("topics", []))
        if total_topics > 0:
            original_data_size = 30  # 原始请求的数据量
            compression_ratio = (total_topics / original_data_size) * 100
            print(f"\n📉 数据压缩率: {compression_ratio:.1f}% (返回{total_topics}条/原始30条)")
    else:
        print("\n未触发摘要功能，返回完整数据")
        total_topics = len(result.get("topics", []))
        print(f"共获取 {total_topics} 条话题，数据量未超过字数限制")
        # 显示部分数据示例
        print("\n话题示例:")
        for i, topic in enumerate(result.get("topics", [])[:3], 1):
            print(f"{i}. {topic.get('title')} - {topic.get('platform')} (热度: {topic.get('hot')})")
    
    # 测试4: 对比原始数据与摘要数据
    print("\n" + "-"*40)
    print("测试4: 原始数据与摘要数据对比")
    print("-"*40)
    
    # 获取原始数据
    print("\n获取原始数据...")
    original_result = await tool.execute(
        category="热点",
        limit=20,
        force_summarize=False
    )
    
    # 获取摘要数据
    print("获取摘要数据...")
    summary_result = await tool.execute(
        category="热点",
        limit=20,
        force_summarize=True
    )
    
    original_topics = original_result.get("topics", [])
    summary_topics = summary_result.get("topics", [])
    
    print(f"\n原始数据: {len(original_topics)}条话题")
    print(f"摘要数据: {len(summary_topics)}条话题 + 摘要文本")
    
    if "summary" in summary_result:
        print("\n📊 摘要文本:")
        print(f"➤ {summary_result['summary']}")
        
        if "stats" in summary_result:
            stats = summary_result["stats"]
            print("\n摘要统计了以下信息:")
            print(f"- 涵盖了{stats['total_topics']}条话题的内容")
            print(f"- 从{stats['platform_count']}个平台获取数据")
            print(f"- 提取了{len(stats['hot_keywords'])}个热门关键词")
            print(f"- 筛选出{len(summary_topics)}条最具代表性的话题")
    
    # 测试5: 调整摘要压缩率
    print("\n" + "-"*40)
    print("测试5: 调整摘要压缩率")
    print("-"*40)

    # 测试不同压缩率
    compression_ratios = [0.1, 0.25, 0.5]
    results = {}
    
    # 首先获取完整数据作为参考
    print("\n获取完整数据作为参考...")
    full_result = await tool.execute(
        category="科技", 
        limit=30,
        force_summarize=False
    )
    full_topics = full_result.get("topics", [])
    print(f"完整数据: {len(full_topics)}条话题")
    
    # 测试不同压缩率
    for ratio in compression_ratios:
        print(f"\n" + "="*30)
        print(f"压缩率 {ratio*100:.0f}% 的效果:")
        print("="*30)
        
        result = await tool.execute(
            category="科技",
            limit=30,
            force_summarize=True,
            compression_ratio=ratio
        )
        results[ratio] = result
        
        if "stats" in result:
            stats = result["stats"]
            summary_count = len(result.get("topics", []))
            total = stats["total_topics"]
            actual_ratio = summary_count / total if total > 0 else 0
            
            print(f"\n【摘要统计】")
            print(f"- 原始数据量: {total}条话题")
            print(f"- 摘要后数据量: {summary_count}条话题")
            print(f"- 实际压缩率: {actual_ratio*100:.1f}%")
            print(f"- 摘要文本长度: {len(result['summary'])}字符")
            
            # 显示摘要的详细信息
            print(f"\n【摘要文本】")
            print(f"➤ {result['summary']}")
            
            # 显示关键词统计差异
            print(f"\n【热门关键词】({len(stats['hot_keywords'])}个)")
            for kw in stats['hot_keywords']:
                print(f"- {kw['word']}: 出现{kw['freq']}次")
            
            # 显示代表性话题
            print(f"\n【代表性话题】({summary_count}条)")
            for i, topic in enumerate(result.get("topics", [])[:min(5, summary_count)], 1):
                print(f"{i}. {topic.get('title')} - {topic.get('platform')} (热度: {topic.get('hot')})")
            
            # 如果话题太多，只显示部分
            if summary_count > 5:
                print(f"... 还有 {summary_count - 5} 条话题 ...")
    
    # 比较不同压缩率的摘要差异
    if len(results) == 3:
        print("\n" + "="*40)
        print("【不同压缩率摘要对比】")
        print("="*40)
        
        print("\n1. 返回话题数量对比")
        for ratio, result in sorted(results.items()):
            topics = result.get("topics", [])
            print(f"- 压缩率 {ratio*100:.0f}%: {len(topics)}条话题 ({len(topics)/len(full_topics)*100:.1f}%的原始数据)")
            
        print("\n2. 摘要文本长度对比")
        for ratio, result in sorted(results.items()):
            summary = result.get("summary", "")
            print(f"- 压缩率 {ratio*100:.0f}%: {len(summary)}字符")
        
        print("\n3. 关键词覆盖对比")
        for ratio, result in sorted(results.items()):
            if "stats" in result:
                keywords = result["stats"].get("hot_keywords", [])
                keyword_str = ", ".join([k["word"] for k in keywords])
                print(f"- 压缩率 {ratio*100:.0f}%: {len(keywords)}个关键词 ({keyword_str})")
                
        print("\n4. 话题热度分布对比")
        for ratio, result in sorted(results.items()):
            topics = result.get("topics", [])
            if topics:
                hot_values = [t.get("hot", 0) for t in topics]
                avg_hot = sum(hot_values) / len(hot_values) if hot_values else 0
                max_hot = max(hot_values) if hot_values else 0
                min_hot = min(hot_values) if hot_values else 0
                print(f"- 压缩率 {ratio*100:.0f}%: 平均热度 {avg_hot:.0f}, 最高热度 {max_hot}, 最低热度 {min_hot}")
    
    return results

async def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(description='测试热点话题工具')
    parser.add_argument('--skip-redis', action='store_true', help='跳过Redis统计测试')
    parser.add_argument('--skip-core', action='store_true', help='跳过核心功能测试')
    parser.add_argument('--test-execute', action='store_true', help='测试execute方法')
    parser.add_argument('--test-execute-case', type=str, help='测试execute方法的特定案例，格式如：category=科技&keywords=AI&limit=10')
    parser.add_argument('--test-supplement', action='store_true', help='测试数据自动补充功能')
    parser.add_argument('--test-summary', action='store_true', help='测试摘要功能')
    
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print("《热点话题工具测试》")
    
    if args.test_execute_case:
        await test_execute_with_params(args.test_execute_case)
    elif args.test_summary:
        await test_summary_feature()
    elif args.test_supplement:
        await test_keyword_supplement()
    elif args.test_execute:
        await test_topics()
    else:
        if not args.skip_redis:
            # 1. 数据统计
            await test_redis_stats()
        
        if not args.skip_core:
            # 2. 核心功能测试
            await test_core_functions()
    
    print("\n" + "="*50)
    print("测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 
