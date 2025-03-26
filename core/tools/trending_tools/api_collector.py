"""数据收集模块

从API获取原始热点数据。
"""
import logging
import json
import time
from typing import Dict, List, Optional
import aiohttp
from functools import wraps
import asyncio
from datetime import datetime

from .config import get_config
from .redis_storage import RedisStorage

logger = logging.getLogger(__name__)

class APIError(Exception):
    """API调用异常"""
    pass

def async_retry(retries=3, delay=1.0):
    """异步重试装饰器

    Args:
        retries: 重试次数
        delay: 重试延迟（秒）
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < retries - 1:
                        logger.warning(
                            f"第{attempt + 1}次尝试失败: {e}, "
                            f"{delay}秒后重试..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"重试{retries}次后仍然失败: {e}")
                        raise last_error
        return wrapper
    return decorator

class PerformanceMetrics:
    """性能指标收集器"""

    def __init__(self):
        """初始化性能指标"""
        self.reset()

    def reset(self):
        """重置所有指标"""
        self.start_time = None
        self.end_time = None
        self.total_requests = 0
        self.failed_requests = 0
        self.total_topics = 0
        self.platform_stats = {}
        self.time_records = {}

    def start(self):
        """开始计时"""
        self.start_time = time.time()

    def stop(self):
        """停止计时"""
        self.end_time = time.time()

    def add_request(self, success: bool):
        """记录请求结果"""
        self.total_requests += 1
        if not success:
            self.failed_requests += 1

    def add_topics(self, platform: str, count: int):
        """记录话题数量"""
        self.total_topics += count
        self.platform_stats[platform] = count

    def record_time(self, key: str, duration: float = None):
        """记录特定操作的时间

        Args:
            key: 操作标识符
            duration: 如果提供，直接使用此持续时间，否则计算当前时间和开始时间的差值
        """
        if duration is None and self.start_time:
            duration = time.time() - self.start_time

        if key in self.time_records:
            self.time_records[key].append(duration)
        else:
            self.time_records[key] = [duration]

    def get_duration(self) -> float:
        """获取执行时长（秒）"""
        if not self.start_time or not self.end_time:
            return 0.0
        return self.end_time - self.start_time

    def get_summary(self) -> Dict:
        """获取性能统计摘要"""
        summary = {
            "duration": self.get_duration(),
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "total_topics": self.total_topics,
            "platform_stats": self.platform_stats
        }

        # 处理时间记录统计
        for key, times in self.time_records.items():
            if times:
                summary[key] = {
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "count": len(times)
                }

        return summary

class APICollector:
    """API数据收集器，专注于从API获取原始数据"""

    def __init__(self):
        """初始化收集器"""
        self.config = get_config()
        self.api_base_url = self.config["api_base_url"]
        self.update_interval = self.config["config_update_interval"]
        self.redis = RedisStorage(self.config["redis_url"])
        self.platforms_config = {}
        self.metrics = PerformanceMetrics()
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info(f"初始化API收集器: API地址={self.api_base_url}")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()

    def _validate_platform_config(self, config: Dict) -> bool:
        """验证平台配置有效性

        Args:
            config: 平台配置字典

        Returns:
            bool: 配置是否有效
        """
        return (
            isinstance(config, dict)
            and isinstance(config.get("data"), dict)
            and all(
                isinstance(p_config, dict) and "path" in p_config
                for p_config in config["data"].values()
            )
        )

    @async_retry(retries=3, delay=1.0)
    async def _update_platforms_config(self) -> bool:
        """更新平台配置

        从API获取最新的平台配置信息并存储到Redis。

        Returns:
            bool: 是否更新成功
        """
        try:
            # 构建API URL
            url = f"{self.api_base_url}/all"
            logger.info(f"开始获取平台配置: {url}")

            # 发送请求
            if not self.session:
                raise APIError("HTTP会话未初始化")

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise APIError(f"获取平台配置失败: HTTP {response.status}")

                data = await response.json()
                logger.debug(f"API返回原始数据: {json.dumps(data, ensure_ascii=False)}")

                if not isinstance(data, dict) or data.get("code") != 200:
                    raise APIError("API返回数据格式错误")

                routes = data.get("routes", [])
                if not isinstance(routes, list):
                    raise APIError("API返回的routes不是数组格式")

                # 处理平台配置
                self.platforms_config = {
                    route["name"]: {"path": route["path"]}
                    for route in routes
                    if isinstance(route, dict)
                    and route.get("name")
                    and route.get("path")
                    and route["name"] not in {"all", "config"}
                }

                logger.info(f"成功获取 {len(self.platforms_config)} 个平台配置")

                # 存储到Redis
                config_data = {
                    "data": self.platforms_config,
                    "update_time": time.time(),
                    "version": "1.0"
                }

                await self.redis.store_platform_config(config_data)

                return True

        except Exception as e:
            logger.error(f"更新平台配置失败: {e}")
            return False

    async def _load_platforms_config(self) -> bool:
        """从Redis加载平台配置

        如果Redis中的配置已过期或不存在，则从API获取新配置。

        Returns:
            bool: 是否加载成功
        """
        try:
            # 尝试从Redis获取配置
            config = await self.redis.get_platform_config()

            if config and isinstance(config, dict):
                data = config.get("data", {})
                update_time = config.get("update_time", 0)

                # 检查配置是否有效且未过期
                if (
                    self._validate_platform_config(config)
                    and time.time() - update_time < self.update_interval
                ):
                    self.platforms_config = data
                    logger.info(f"从Redis加载了 {len(self.platforms_config)} 个平台配置")
                    return True

            # 配置无效或已过期，从API获取新配置
            logger.info("Redis中的配置无效或已过期，从API获取新配置")
            return await self._update_platforms_config()

        except Exception as e:
            logger.error(f"加载平台配置失败: {e}")
            return False

    @async_retry(retries=3, delay=1.0)
    async def get_platform_data(self, platform: str) -> Dict:
        """获取单个平台的数据

        Args:
            platform: 平台名称

        Returns:
            Dict: 平台原始数据
        """
        start_time = time.time()
        try:
            if platform not in self.platforms_config:
                raise APIError(f"未知的平台: {platform}")

            path = self.platforms_config[platform]["path"]
            url = f"{self.api_base_url}{path}"

            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise APIError(f"获取平台 {platform} 数据失败: HTTP {response.status}")

                data = await response.json()
                if not isinstance(data, dict) or data.get("code") != 200:
                    raise APIError(f"平台 {platform} 返回数据格式错误")

                topics = data.get("data", [])
                if not isinstance(topics, list):
                    logger.warning(f"平台 {platform} 返回的 data 字段不是列表格式")
                    return {"data": []}

                # 打印成功获取的数据示例
                if topics:
                    logger.info(f"\n成功获取 {platform} 平台数据:")
                    logger.info(f"- 话题数量: {len(topics)}")
                    if topics:
                        sample = topics[0]
                        logger.info("- 数据示例:")
                        logger.info(f"  标题: {sample.get('title', 'N/A')}")
                        logger.info(f"  热度: {sample.get('hot', 'N/A')}")
                        logger.info(f"  链接: {sample.get('url', 'N/A')}")

                return {"data": topics}

        finally:
            self.metrics.record_time(f"get_platform_{platform}", start_time)

    async def get_all_topics(self) -> Dict[str, List]:
        """获取所有平台的原始数据

        Returns:
            Dict[str, List]: 平台名称到话题列表的映射
        """
        start_time = time.time()
        try:
            if not await self._load_platforms_config():
                logger.error("无法获取或更新平台配置")
                return {}

            all_data = {}
            total_topics = 0
            success_platforms = []
            failed_platforms = []

            logger.info(f"开始获取 {len(self.platforms_config)} 个平台的数据")

            # 并发获取所有平台数据
            tasks = [
                self.get_platform_data(platform)
                for platform in self.platforms_config
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for platform, result in zip(self.platforms_config.keys(), results):
                if isinstance(result, Exception):
                    logger.warning(f"获取平台 {platform} 数据失败: {result}")
                    failed_platforms.append(platform)
                    continue

                topics = result.get("data", [])
                if isinstance(topics, list) and topics:
                    all_data[platform] = topics
                    total_topics += len(topics)
                    success_platforms.append(platform)
                else:
                    logger.warning(f"平台 {platform} 返回空数据，跳过")
                    failed_platforms.append(platform)

            if not all_data:
                logger.error("未获取到任何有效数据")
                return {}

            # 记录详细的执行统计
            logger.info(f"\n数据获取总结:")
            logger.info(f"- 成功平台: {len(success_platforms)}/{len(self.platforms_config)}")
            logger.info(f"- 总话题数: {total_topics}")
            logger.info(f"- 成功平台列表: {', '.join(success_platforms)}")
            if failed_platforms:
                logger.warning(f"- 失败平台列表: {', '.join(failed_platforms)}")

            # 记录性能指标
            metrics_summary = self.metrics.get_summary()
            logger.info("\n性能指标总结:")
            for metric_name, metric_value in metrics_summary.items():
                if isinstance(metric_value, dict):
                    logger.info(f"- {metric_name}:")
                    for k, v in metric_value.items():
                        if isinstance(v, float):
                            logger.info(f"  {k}: {v:.3f}")
                        else:
                            logger.info(f"  {k}: {v}")
                elif isinstance(metric_value, float):
                    logger.info(f"- {metric_name}: {metric_value:.3f}秒")
                else:
                    logger.info(f"- {metric_name}: {metric_value}")

            return all_data

        finally:
            self.metrics.record_time("get_all_topics", time.time() - start_time)
            if self.session:
                await self.session.close()
                self.session = None
