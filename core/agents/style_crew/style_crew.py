"""风格化团队的实现

该模块实现了风格化团队的核心逻辑，负责将内容按照不同平台的风格规范进行改写和适配。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from crewai import Crew, Agent, Task
from core.models.platform import Platform
from core.models.article import Article
from core.tools.style_tools.adapter import StyleAdapter
from .style_agents import PlatformAnalystAgent, StyleExpertAgent, ContentAdapterAgent, QualityCheckerAgent

logger = logging.getLogger(__name__)

@dataclass
class StyleWorkflowResult:
    """风格化工作流结果"""
    platform_analysis: Optional[Dict] = None
    style_recommendations: Optional[Dict] = None
    adapted_content: Optional[str] = None
    quality_check: Optional[Dict] = None
    final_article: Optional[Article] = None
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "platform_analysis": self.platform_analysis,
            "style_recommendations": self.style_recommendations,
            "adapted_content": self.adapted_content,
            "quality_check": self.quality_check,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'StyleWorkflowResult':
        """从字典创建实例"""
        result = cls(
            platform_analysis=data.get("platform_analysis"),
            style_recommendations=data.get("style_recommendations"),
            adapted_content=data.get("adapted_content"),
            quality_check=data.get("quality_check"),
            execution_time=data.get("execution_time", 0.0),
        )

        if "timestamp" in data:
            result.timestamp = datetime.fromisoformat(data["timestamp"])

        return result


class StyleCrew:
    """风格化团队

    负责将内容按照不同平台的风格规范进行改写和适配。
    """

    def __init__(self):
        """初始化风格化团队"""
        self.style_adapter = None
        self._init_complete = False

    def initialize(self, platform: Platform = None):
        """初始化风格化团队

        Args:
            platform: 目标平台，如果不提供则使用默认配置
        """
        if platform:
            self.platform = platform
            self.style_adapter = StyleAdapter.get_instance(platform)
        else:
            # 创建一个通用的风格适配器
            from core.models.platform import get_default_platform
            self.platform = get_default_platform()
            self.style_adapter = StyleAdapter.get_instance(self.platform)

        # 创建智能体
        self.platform_analyst = PlatformAnalystAgent(style_adapter=self.style_adapter)
        self.style_expert = StyleExpertAgent(style_adapter=self.style_adapter)
        self.content_adapter = ContentAdapterAgent(style_adapter=self.style_adapter)
        self.quality_checker = QualityCheckerAgent(style_adapter=self.style_adapter)

        # 标记初始化完成
        self._init_complete = True

    def _ensure_initialized(self):
        """确保团队已初始化"""
        if not self._init_complete:
            self.initialize()

    async def adapt_style(self, article: Article, platform: Optional[Platform] = None) -> StyleWorkflowResult:
        """执行风格适配工作流

        Args:
            article: 要进行风格适配的文章
            platform: 目标平台，如果提供则覆盖初始化时的平台

        Returns:
            StyleWorkflowResult: 风格化工作流结果
        """
        self._ensure_initialized()

        # 如果提供了新的平台，更新适配器
        if platform and (not self.platform or platform.id != self.platform.id):
            self.platform = platform
            self.style_adapter = StyleAdapter.get_instance(platform)

        start_time = datetime.now()

        # 创建工作流结果对象
        result = StyleWorkflowResult()

        try:
            # 步骤1: 平台分析
            platform_analysis = await self._analyze_platform(self.platform)
            result.platform_analysis = platform_analysis

            # 步骤2: 风格推荐
            style_recommendations = await self._generate_style_recommendations(
                platform_analysis,
                article
            )
            result.style_recommendations = style_recommendations

            # 步骤3: 内容适配
            adapted_content = await self._adapt_content(
                article,
                style_recommendations
            )
            result.adapted_content = adapted_content

            # 步骤4: 质量检查
            quality_check = await self._check_quality(
                adapted_content,
                self.platform
            )
            result.quality_check = quality_check

            # 创建最终文章
            final_article = article.copy()
            final_article.content = adapted_content
            result.final_article = final_article

            # 计算执行时间
            end_time = datetime.now()
            result.execution_time = (end_time - start_time).total_seconds()

            return result

        except Exception as e:
            logger.error(f"风格适配过程出错: {str(e)}")
            # 计算执行时间
            end_time = datetime.now()
            result.execution_time = (end_time - start_time).total_seconds()
            raise

    async def _analyze_platform(self, platform: Platform) -> Dict:
        """分析平台风格特点

        Args:
            platform: 目标平台

        Returns:
            Dict: 平台分析结果
        """
        # 创建平台分析任务
        agent = self.platform_analyst.get_agent()
        task = Task(
            description=f"分析平台 {platform.name} 的风格特点",
            expected_output="平台风格分析报告",
            agent=agent
        )

        # 执行任务
        platform_crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )

        result = await platform_crew.run_async(
            inputs={
                "platform_name": platform.name,
                "platform_description": platform.description,
                "target_audience": platform.target_audience,
                "content_types": platform.content_types,
                "style_rules": platform.style_rules.to_dict() if platform.style_rules else {}
            }
        )

        # 将结果转换为字典
        try:
            analysis_result = eval(result)
            if not isinstance(analysis_result, dict):
                analysis_result = {"raw_result": result}
        except:
            analysis_result = {"raw_result": result}

        return analysis_result

    async def _generate_style_recommendations(self, platform_analysis: Dict, article: Article) -> Dict:
        """生成风格建议

        Args:
            platform_analysis: 平台分析结果
            article: 原始文章

        Returns:
            Dict: 风格建议
        """
        # 创建风格专家任务
        agent = self.style_expert.get_agent()
        task = Task(
            description="根据平台特点生成风格改写建议",
            expected_output="风格建议报告",
            agent=agent
        )

        # 执行任务
        style_crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )

        result = await style_crew.run_async(
            inputs={
                "platform_analysis": str(platform_analysis),
                "article_title": article.title,
                "article_content": article.content[:1000] + "..." if len(article.content) > 1000 else article.content,
                "article_keywords": article.keywords,
                "article_type": article.article_type
            }
        )

        # 将结果转换为字典
        try:
            recommendations = eval(result)
            if not isinstance(recommendations, dict):
                recommendations = {"raw_result": result}
        except:
            recommendations = {"raw_result": result}

        return recommendations

    async def _adapt_content(self, article: Article, style_recommendations: Dict) -> str:
        """根据风格建议适配内容

        Args:
            article: 原始文章
            style_recommendations: 风格建议

        Returns:
            str: 适配后的内容
        """
        # 创建内容适配任务
        agent = self.content_adapter.get_agent()
        task = Task(
            description="按照风格建议改写文章内容",
            expected_output="改写后的文章内容",
            agent=agent
        )

        # 执行任务
        adapter_crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )

        result = await adapter_crew.run_async(
            inputs={
                "article_title": article.title,
                "article_content": article.content,
                "style_recommendations": str(style_recommendations)
            }
        )

        return result

    async def _check_quality(self, adapted_content: str, platform: Platform) -> Dict:
        """检查适配后内容的质量

        Args:
            adapted_content: 适配后的内容
            platform: 目标平台

        Returns:
            Dict: 质量检查结果
        """
        # 创建质量检查任务
        agent = self.quality_checker.get_agent()
        task = Task(
            description="检查适配后内容的质量和合规性",
            expected_output="质量检查报告",
            agent=agent
        )

        # 执行任务
        checker_crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )

        result = await checker_crew.run_async(
            inputs={
                "adapted_content": adapted_content[:1500] + "..." if len(adapted_content) > 1500 else adapted_content,
                "platform_name": platform.name,
                "platform_rules": str({
                    "style_rules": platform.style_rules.to_dict() if platform.style_rules else {},
                    "content_rules": platform.content_rules.to_dict() if platform.content_rules else {}
                })
            }
        )

        # 将结果转换为字典
        try:
            check_result = eval(result)
            if not isinstance(check_result, dict):
                check_result = {"raw_result": result}
        except:
            check_result = {"raw_result": result}

        return check_result
