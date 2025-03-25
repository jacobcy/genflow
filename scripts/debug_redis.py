import sys
import os
import asyncio
from pprint import pprint

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from core.tools.trending_tools.redis_storage import RedisStorage
from core.tools.trending_tools.config import get_config
from core.tools.trending_tools.tasks import update_trending_data

async def debug_redis():
    """逐层调试 Redis 数据"""
    print("\n=== 开始更新热点数据 ===")
    success = await update_trending_data()
    if not success:
        print("更新热点数据失败")
        return

    print("\n=== 更新完成，检查数据状态 ===")

    # 初始化 Redis 连接
    config = get_config()
    redis = RedisStorage(config["redis_url"])

    # 检查 Redis 键
    print("\n=== Redis 键列表 ===")
    for key_type in ["topic", "platform", "stats"]:
        keys = await redis.get_keys(key_type)
        print(f"\n{key_type} 类型的键:")
        for key in keys:
            print(f"- {key.decode('utf-8')}")

    # 检查平台索引
    print("\n=== 平台索引数据 ===")
    platform = "bilibili"  # 可以换成其他平台
    index_key = f"{redis.KEY_PREFIX['platform']}{platform}:topics"
    index_data = redis.redis.get(index_key)
    if index_data:
        print(f"\n{platform} 平台索引:")
        pprint(index_data)
    else:
        print(f"\n{platform} 平台无索引数据")

    # 获取平台话题
    print("\n=== 平台话题数据 ===")
    topics = await redis.get_platform_topics(platform)
    print(f"\n{platform} 平台话题数量: {len(topics)}")
    if topics:
        print("\n示例话题:")
        pprint(topics[0])

if __name__ == "__main__":
    asyncio.run(debug_redis())
