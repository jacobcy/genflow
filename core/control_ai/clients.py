"""
专业团队客户端 - 与各专业团队API交互

该模块提供与各专业团队(选题、研究、写作、风格、审核)API交互的客户端类，
用于执行任务计划中的各种行动步骤。
"""

import json
import logging
import os
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union

# 配置日志
logger = logging.getLogger(__name__)

class TeamClient:
    """专业团队客户端基类

    提供与专业团队API交互的基础功能。
    """

    def __init__(self, base_url: Optional[str] = None):
        """初始化专业团队客户端

        Args:
            base_url: API基础URL，如果不提供则从环境变量获取
        """
        self.base_url = base_url or os.environ.get("TEAMS_API_BASE_URL", "http://localhost:8000")
        self.session = None

    async def _ensure_session(self):
        """确保存在有效的HTTP会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def _request(self,
                   method: str,
                   endpoint: str,
                   data: Optional[Dict[str, Any]] = None,
                   params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送HTTP请求

        Args:
            method: HTTP方法，如'GET'、'POST'等
            endpoint: API接口路径
            data: 请求数据
            params: 查询参数

        Returns:
            Dict[str, Any]: API响应

        Raises:
            Exception: 当请求失败时
        """
        await self._ensure_session()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            # 设置超时
            timeout = aiohttp.ClientTimeout(total=30)

            # 发送请求
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=timeout
            ) as response:
                # 解析响应
                result = await response.json()

                # 检查响应状态
                if response.status >= 400:
                    logger.error(f"API请求失败: {response.status} - {result}")
                    error_message = result.get("detail", str(result))
                    raise Exception(f"API错误: {error_message}")

                return result

        except aiohttp.ClientError as e:
            logger.error(f"HTTP请求异常: {str(e)}")
            raise Exception(f"网络错误: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析异常: {str(e)}")
            raise Exception(f"响应解析错误: {str(e)}")
        except Exception as e:
            logger.error(f"请求异常: {str(e)}")
            raise

    async def close(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None


class TopicClient(TeamClient):
    """选题团队客户端

    提供与选题团队API交互的功能。
    """

    async def get_trending_topics(self,
                             category: Optional[str] = None,
                             limit: int = 10) -> Dict[str, Any]:
        """获取热门话题

        Args:
            category: 可选的话题分类
            limit: 返回话题数量限制

        Returns:
            Dict[str, Any]: 热门话题列表
        """
        params = {"limit": limit}
        if category:
            params["category"] = category

        result = await self._request(
            method="GET",
            endpoint="/api/topics/trending",
            params=params
        )

        logger.info(f"获取到 {len(result.get('trending_topics', []))} 个热门话题")
        return result

    async def evaluate_topic(self, topic: str) -> Dict[str, Any]:
        """评估话题价值

        Args:
            topic: 要评估的话题

        Returns:
            Dict[str, Any]: 话题评估结果
        """
        data = {"topic": topic}

        result = await self._request(
            method="POST",
            endpoint="/api/topics/evaluate",
            data=data
        )

        logger.info(f"话题 '{topic}' 评估完成")
        return result


class ResearchClient(TeamClient):
    """研究团队客户端

    提供与研究团队API交互的功能。
    """

    async def research_topic(self,
                        topic: str,
                        depth: str = "medium",
                        focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """研究主题

        Args:
            topic: 研究主题
            depth: 研究深度，可选值为'light'、'medium'、'deep'
            focus_areas: 重点关注领域

        Returns:
            Dict[str, Any]: 研究结果
        """
        data = {
            "topic": topic,
            "depth": depth
        }

        if focus_areas:
            data["focus_areas"] = focus_areas

        result = await self._request(
            method="POST",
            endpoint="/api/research/topic",
            data=data
        )

        logger.info(f"主题 '{topic}' 研究完成")
        return result


class WritingClient(TeamClient):
    """写作团队客户端

    提供与写作团队API交互的功能。
    """

    async def create_content(self,
                        topic: str,
                        research_data: Optional[Dict[str, Any]] = None,
                        style: Optional[str] = None,
                        structure: Optional[str] = None) -> Dict[str, Any]:
        """创建内容

        Args:
            topic: 内容主题
            research_data: 研究数据
            style: 写作风格
            structure: 内容结构

        Returns:
            Dict[str, Any]: 创作结果
        """
        data = {
            "topic": topic
        }

        if research_data:
            data["research_data"] = research_data
        if style:
            data["style"] = style
        if structure:
            data["structure"] = structure

        result = await self._request(
            method="POST",
            endpoint="/api/writing/create",
            data=data
        )

        logger.info(f"主题 '{topic}' 内容创作完成")
        return result


class StyleClient(TeamClient):
    """风格团队客户端

    提供与风格团队API交互的功能。
    """

    async def adjust_style(self,
                      content: str,
                      style: str,
                      platform: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """调整内容风格

        Args:
            content: 原始内容
            style: 目标风格
            platform: 平台信息

        Returns:
            Dict[str, Any]: 风格调整结果
        """
        data = {
            "content": content,
            "style": style
        }

        if platform:
            data["platform"] = platform

        result = await self._request(
            method="POST",
            endpoint="/api/style/adjust",
            data=data
        )

        logger.info(f"内容风格调整为 '{style}' 完成")
        return result


class ReviewClient(TeamClient):
    """审核团队客户端

    提供与审核团队API交互的功能。
    """

    async def review_content(self,
                        topic: str,
                        content: str) -> Dict[str, Any]:
        """审核内容

        Args:
            topic: 内容主题
            content: 待审核内容

        Returns:
            Dict[str, Any]: 审核结果
        """
        data = {
            "topic": topic,
            "content": content
        }

        result = await self._request(
            method="POST",
            endpoint="/api/review/content",
            data=data
        )

        logger.info(f"主题 '{topic}' 内容审核完成")
        return result


class TeamClientFactory:
    """专业团队客户端工厂

    用于创建不同专业团队的客户端实例。
    """

    def __init__(self, base_url: Optional[str] = None):
        """初始化客户端工厂

        Args:
            base_url: API基础URL
        """
        self.base_url = base_url
        self._clients = {}

    def get_client(self, team_type: str) -> TeamClient:
        """获取指定类型的团队客户端

        Args:
            team_type: 团队类型，可选值为'topic'、'research'、'writing'、'style'、'review'

        Returns:
            TeamClient: 对应的团队客户端实例

        Raises:
            ValueError: 当指定的团队类型无效时
        """
        # 检查缓存
        if team_type in self._clients:
            return self._clients[team_type]

        # 创建新客户端
        client = None

        if team_type == "topic":
            client = TopicClient(self.base_url)
        elif team_type == "research":
            client = ResearchClient(self.base_url)
        elif team_type == "writing":
            client = WritingClient(self.base_url)
        elif team_type == "style":
            client = StyleClient(self.base_url)
        elif team_type == "review":
            client = ReviewClient(self.base_url)
        else:
            raise ValueError(f"无效的团队类型: {team_type}")

        # 缓存客户端
        self._clients[team_type] = client

        return client

    async def close_all(self):
        """关闭所有客户端"""
        for client in self._clients.values():
            await client.close()
        self._clients = {}
