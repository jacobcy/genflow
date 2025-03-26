"""Redis存储模块

专注于热点数据的Redis存储和缓存管理。
提供数据的存取、缓存更新和过期处理等基础功能。
"""
import json
import logging
import hashlib
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import redis

from .platform_weights import get_platform_weight

logger = logging.getLogger(__name__)

class RedisStorage:
    """Redis存储管理器

    核心功能:
    1. 数据存储与获取
    2. 缓存过期管理
    3. 数据版本控制
    4. 批量操作支持
    5. 话题数据去重和权重处理
    """

    def __init__(self, redis_url: str):
        """初始化Redis存储器

        Args:
            redis_url: Redis连接URL
        """
        self.redis = redis.from_url(redis_url)
        self._init_storage()

    def _init_storage(self):
        """初始化存储配置"""
        # 键前缀定义
        self.KEY_PREFIX = {
            "topic": "genflow:trending:topic:",      # 话题数据
            "platform": "genflow:trending:platform:", # 平台索引
            "stats": "genflow:trending:stats:"       # 统计数据
        }

        # 过期时间配置（秒）
        self.EXPIRATION = {
            "topic": 7 * 24 * 60 * 60,    # 话题数据7天过期
            "platform": 3 * 60 * 60,       # 平台索引3小时过期
            "stats": 24 * 60 * 60         # 统计数据24小时过期
        }

    def _generate_title_hash(self, title: str) -> str:
        """生成标题的哈希值作为键"""
        return hashlib.md5(title.encode('utf-8')).hexdigest()

    async def store_topics(self, topics: List[Dict]) -> bool:
        """存储话题数据

        Args:
            topics: 话题列表

        Returns:
            bool: 是否存储成功
        """
        if not topics:
            logger.error("没有数据需要存储")
            return False

        try:
            logger.info(f"开始存储 {len(topics)} 条话题数据")
            current_time = datetime.now().timestamp()

            # 按平台分组话题
            platform_topics = {}
            for topic in topics:
                platform = topic.get("platform")
                if not platform:
                    continue
                if platform not in platform_topics:
                    platform_topics[platform] = []
                platform_topics[platform].append(topic)

            # 处理每个平台的话题
            pipe = self.redis.pipeline()
            platform_stats = {}  # 平台话题计数
            stored_hashes = {}

            # 先获取所有已存在的话题哈希
            existing_hashes = set()
            for key in self.redis.scan_iter(f"{self.KEY_PREFIX['topic']}*"):
                hash_part = key.decode('utf-8').split(':')[-1]
                existing_hashes.add(hash_part)

            for platform, platform_data in platform_topics.items():
                platform_stats[platform] = 0
                stored_hashes[platform] = []

                for topic in platform_data:
                    title = topic.get("title")
                    if not title:
                        continue

                    # 生成话题键
                    topic_hash = self._generate_title_hash(title)

                    # 如果话题已存在，跳过
                    if topic_hash in existing_hashes:
                        logger.debug(f"话题已存在，跳过: {title}")
                        continue

                    topic_key = f"{self.KEY_PREFIX['topic']}{topic_hash}"

                    # 准备存储数据
                    storage_data = {
                        "title": title,
                        "platform": platform,
                        "url": topic.get("url", ""),
                        "mobile_url": topic.get("mobile_url", ""),
                        "hot": topic.get("hot", 0),
                        "description": topic.get("description", ""),
                        "cover": topic.get("cover", ""),
                        "timestamp": topic.get("timestamp", int(current_time)),
                        "fetch_time": int(current_time),
                        "expire_time": int((datetime.now() + timedelta(days=7)).timestamp())
                    }

                    # 添加到管道
                    pipe.set(
                        topic_key,
                        json.dumps(storage_data),
                        ex=self.EXPIRATION["topic"]
                    )

                    stored_hashes[platform].append(topic_hash)
                    platform_stats[platform] += 1

            # 更新平台索引
            for platform, hashes in stored_hashes.items():
                if not hashes:
                    continue

                # 存储平台话题索引
                platform_index_key = f"{self.KEY_PREFIX['platform']}{platform}:topics"
                index_data = {
                    "topic_hashes": hashes,
                    "update_time": current_time
                }
                pipe.set(
                    platform_index_key,
                    json.dumps(index_data),
                    ex=self.EXPIRATION["platform"]
                )

            # 执行存储
            pipe.execute()

            # 更新统计数据
            stats_key = f"{self.KEY_PREFIX['stats']}platforms"
            stats_data = {
                "platform_topics": platform_stats,
                "total_topics": sum(platform_stats.values()),
                "update_time": current_time
            }
            self.redis.set(
                stats_key,
                json.dumps(stats_data),
                ex=self.EXPIRATION["stats"]
            )

            logger.info("\n存储统计:")
            for platform, count in platform_stats.items():
                logger.info(f"- 平台 {platform}: {count}条话题")
            logger.info(f"总计: {sum(platform_stats.values())}条话题")

            return True

        except Exception as e:
            logger.error(f"存储话题数据失败: {e}")
            return False

    async def get_platform_topics(self, platform: str) -> List[Dict]:
        """获取平台的所有话题数据

        Args:
            platform: 平台名称

        Returns:
            List[Dict]: 话题列表
        """
        try:
            # 获取平台索引
            index_key = f"{self.KEY_PREFIX['platform']}{platform}:topics"
            index_data = self.redis.get(index_key)

            if not index_data:
                logger.warning(f"平台 {platform} 无索引数据")
                return []

            index = json.loads(index_data)
            if not isinstance(index, dict) or "topic_hashes" not in index:
                logger.warning(f"平台 {platform} 索引数据格式错误")
                return []

            # 获取所有话题数据
            topics = []
            pipe = self.redis.pipeline()
            seen_hashes = set()  # 用于记录已处理的哈希值

            for topic_hash in index["topic_hashes"]:
                # 跳过已处理的哈希值
                if topic_hash in seen_hashes:
                    continue
                seen_hashes.add(topic_hash)

                topic_key = f"{self.KEY_PREFIX['topic']}{topic_hash}"
                pipe.get(topic_key)

            results = pipe.execute()

            for result in results:
                if result:
                    try:
                        topic_data = json.loads(result)
                        # 确保话题属于当前平台
                        if topic_data.get("platform") == platform:
                            topics.append(topic_data)
                    except json.JSONDecodeError:
                        continue

            return topics

        except Exception as e:
            logger.error(f"获取平台 {platform} 话题数据失败: {e}")
            return []

    async def get_platform_config(self) -> Optional[Dict]:
        """获取平台配置数据

        Returns:
            Optional[Dict]: 平台配置数据，如果不存在则返回None
        """
        try:
            config_key = f"{self.KEY_PREFIX['platform']}config"
            data = self.redis.get(config_key)

            if not data:
                return None

            return json.loads(data)

        except Exception as e:
            logger.error(f"获取平台配置失败: {e}")
            return None

    async def store_platform_config(self, config: Dict) -> bool:
        """存储平台配置数据

        Args:
            config: 平台配置数据

        Returns:
            bool: 是否存储成功
        """
        try:
            config_key = f"{self.KEY_PREFIX['platform']}config"
            self.redis.set(
                config_key,
                json.dumps(config),
                ex=self.EXPIRATION["platform"]
            )

            # 存储备份
            backup_key = f"{self.KEY_PREFIX['platform']}config_backup"
            self.redis.set(
                backup_key,
                json.dumps(config),
                ex=self.EXPIRATION["platform"]
            )

            logger.info("平台配置数据存储成功")
            return True

        except Exception as e:
            logger.error(f"存储平台配置失败: {e}")
            return False

    async def get_platform_update_time(self, platform: str) -> Optional[float]:
        """获取平台数据的最后更新时间

        Args:
            platform: 平台名称

        Returns:
            Optional[float]: 最后更新时间戳，如果不存在则返回None
        """
        try:
            index_key = f"{self.KEY_PREFIX['platform']}{platform}:topics"
            index_data = self.redis.get(index_key)

            if not index_data:
                return None

            index = json.loads(index_data)
            return index.get("update_time")

        except Exception as e:
            logger.error(f"获取平台 {platform} 更新时间失败: {e}")
            return None

    async def delete_data(self, key_type: str,
                         sub_key: Optional[str] = None) -> bool:
        """删除数据

        Args:
            key_type: 键类型
            sub_key: 子键名（可选）

        Returns:
            bool: 是否删除成功
        """
        try:
            key = self._build_key(key_type, sub_key)
            self.redis.delete(key)
            logger.info(f"数据删除成功: {key}")
            return True

        except Exception as e:
            logger.error(f"数据删除失败: {e}")
            return False

    async def clear_expired(self, key_type: str) -> bool:
        """清理过期数据

        Args:
            key_type: 键类型

        Returns:
            bool: 是否清理成功
        """
        try:
            pattern = f"{self.KEY_PREFIX[key_type]}*"
            keys = self.redis.keys(pattern)

            if not keys:
                logger.info(f"没有找到需要清理的 {key_type} 类型数据")
                return True

            current_time = datetime.now().timestamp()
            cleared_count = 0

            for key in keys:
                try:
                    data = self.redis.get(key)
                    if not data:
                        continue

                    storage_data = json.loads(data)
                    if isinstance(storage_data, dict):
                        expire_time = storage_data.get("expire_time")
                        if expire_time and expire_time < current_time:
                            self.redis.delete(key)
                            cleared_count += 1

                except Exception as e:
                    logger.warning(f"处理键 {key} 时出错: {e}")
                    continue

            logger.info(f"清理了 {cleared_count} 条过期的 {key_type} 数据")
            return True

        except Exception as e:
            logger.error(f"清理过期数据失败: {e}")
            return False

    def _build_key(self, key_type: str, sub_key: Optional[str] = None) -> str:
        """构建完整的Redis键名

        Args:
            key_type: 键类型
            sub_key: 子键名（可选）

        Returns:
            str: 完整的键名
        """
        base_key = self.KEY_PREFIX.get(key_type, "")
        if not base_key:
            raise ValueError(f"未知的键类型: {key_type}")

        return f"{base_key}{sub_key}" if sub_key else base_key

    async def get_keys(self, key_type: str) -> List[str]:
        """获取指定类型的所有键

        Args:
            key_type: 键类型

        Returns:
            List[str]: 键名列表
        """
        try:
            pattern = f"{self.KEY_PREFIX[key_type]}*"
            return self.redis.keys(pattern)

        except Exception as e:
            logger.error(f"获取键列表失败: {e}")
            return []

    async def get_all_platforms(self) -> List[str]:
        """获取所有有数据的平台名称列表

        Returns:
            List[str]: 平台名称列表
        """
        try:
            platforms = []
            # 查找所有平台索引键
            pattern = f"{self.KEY_PREFIX['platform']}*:topics"
            for key in self.redis.scan_iter(pattern):
                key_str = key.decode('utf-8')
                # 从键名提取平台名称
                platform = key_str.split(':')[-2]
                if platform:
                    platforms.append(platform)
            
            logger.info(f"找到 {len(platforms)} 个平台")
            return platforms
            
        except Exception as e:
            logger.error(f"获取平台列表失败: {e}")
            return []
