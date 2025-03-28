"""风格化团队的实现

该模块实现了风格化团队的核心逻辑，负责将内容按照不同风格规范进行改写和适配。
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json

from crewai import Crew, Agent, Task, Process
from core.models.basic_article import BasicArticle
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
    final_article: Optional[BasicArticle] = None
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            "platform_analysis": self.platform_analysis,
            "style_recommendations": self.style_recommendations,
            "adapted_content": self.adapted_content,
            "quality_check": self.quality_check,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat()
        }

        # 添加文章信息
        if self.final_article:
            result["article"] = {
                "id": self.final_article.id,
                "title": self.final_article.title,
                "content": self.adapted_content
            }

        return result

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

    def to_article(self, content_id=None) -> BasicArticle:
        """将结果转换为BasicArticle对象

        Args:
            content_id: 可选的内容ID

        Returns:
            BasicArticle: 文章对象
        """
        if self.final_article:
            article = self.final_article
            if content_id and not article.id:
                article.id = content_id
            return article

        # 创建新文章
        return BasicArticle(
            id=content_id,
            title="风格化后的内容",
            content=self.adapted_content or ""
        )


class StyleCrew:
    """风格化团队

    负责将内容按照不同风格规范进行改写和适配。
    专注于风格转换的核心实现，不处理任何解析工作。
    """

    def __init__(self, verbose: bool = True):
        """初始化风格化团队

        Args:
            verbose: 是否启用详细日志输出
        """
        logger.info("初始化风格化团队")
        self.verbose = verbose
        self._init_complete = False

        # 创建智能体
        self.platform_analyst = None
        self.style_expert = None
        self.content_adapter = None
        self.quality_checker = None

        # 当前配置
        self.default_style_config = {
            "style_name": "默认风格",
            "style": "formal",
            "tone": "professional",
            "formality": 3,
            "emotion": False,
            "emoji": False,
            "description": "通用的文章风格，适合大多数场景",
            "target_audience": "通用受众",
            "writing_style": "standard",
            "language_level": "normal",
            "min_length": 800,
            "max_length": 8000,
            "min_paragraph_length": 50,
            "max_paragraph_length": 300,
            "paragraph_count_min": 5,
            "paragraph_count_max": 30,
            "code_block": True,
            "allowed_formats": ["text", "image", "code"],
            "recommended_patterns": ["清晰的结构", "逻辑性强", "易于理解", "重点突出"],
            "examples": ["标准文章结构示例", "通用写作风格指南"]
        }

        logger.info("风格化团队初始化完成")

    def _ensure_initialized(self):
        """确保团队已初始化"""
        if not self._init_complete:
            self._init_agents()
            self._init_complete = True

    def _init_agents(self):
        """初始化智能体"""
        # 创建StyleAdapter实例
        style_adapter = StyleAdapter.get_instance()

        # 创建智能体
        self.platform_analyst = PlatformAnalystAgent(style_adapter=style_adapter)
        self.style_expert = StyleExpertAgent(style_adapter=style_adapter)
        self.content_adapter = ContentAdapterAgent(style_adapter=style_adapter)
        self.quality_checker = QualityCheckerAgent(style_adapter=style_adapter)

        self._init_complete = True
        logger.info("风格化团队智能体初始化完成")

    async def style_text(
        self,
        article: BasicArticle,
        style_config: Dict[str, Any],
        platform_info: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> StyleWorkflowResult:
        """对输入文章进行风格适配

        直接对文章对象进行风格化处理，核心方法。

        Args:
            article: 要进行风格适配的文章对象
            style_config: 风格配置，包含风格参数
            platform_info: 平台信息，包含platform_id, platform_name等
            options: 其他选项

        Returns:
            StyleWorkflowResult: 风格化工作流结果
        """
        self._ensure_initialized()

        # 合并选项
        merged_options = options or {}

        # 调用内部方法执行风格适配
        return await self._run_style_workflow(article, style_config, platform_info)

    async def analyze_platform(
        self,
        platform_info: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """分析平台风格特点

        Args:
            platform_info: 平台信息，包含platform_id, platform_name等
            options: 其他选项

        Returns:
            Dict: 平台分析结果
        """
        self._ensure_initialized()

        # 创建平台分析任务
        agent = self.platform_analyst.get_agent()
        task = Task(
            description=f"""分析平台 {platform_info.get('platform_name', '未知平台')} 的风格特点。

            平台描述：{platform_info.get('platform_description', '无描述')}
            目标受众：{platform_info.get('target_audience', '未指定')}
            平台规则：{json.dumps(platform_info.get('style_rules', {}))}

            请提供详细的平台风格分析，包括：
            1. 语言风格特点
            2. 内容结构偏好
            3. 媒体使用建议
            4. 受众特征与偏好
            5. 适合的表达方式
            """,
            expected_output="""详细的平台风格分析报告，JSON格式：
            {
                "language_style": "语言风格描述",
                "content_structure": "内容结构描述",
                "media_usage": "媒体使用建议",
                "audience_preferences": "受众偏好描述",
                "expression_style": "表达方式建议"
            }
            """,
            agent=agent
        )

        # 执行任务
        platform_crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=self.verbose,
            process=Process.sequential
        )

        result = await platform_crew.run_async(inputs=platform_info)

        # 解析结果为字典
        return self._parse_json_result(result)

    async def _run_style_workflow(
        self,
        article: BasicArticle,
        style_config: Dict[str, Any],
        platform_info: Dict[str, Any]
    ) -> StyleWorkflowResult:
        """执行风格适配工作流

        核心风格适配流程，不处理ID解析等逻辑

        Args:
            article: 要进行风格适配的文章
            style_config: 风格配置
            platform_info: 平台信息

        Returns:
            StyleWorkflowResult: 风格化工作流结果
        """
        self._ensure_initialized()
        start_time = datetime.now()

        # 创建工作流结果对象
        result = StyleWorkflowResult()

        try:
            # 步骤1: 平台分析
            platform_analysis = await self._analyze_platform_internal(platform_info)
            result.platform_analysis = platform_analysis

            # 步骤2: 风格推荐
            style_recommendations = await self._generate_style_recommendations(
                platform_analysis,
                article,
                style_config
            )
            result.style_recommendations = style_recommendations

            # 步骤3: 内容适配
            adapted_content = await self._adapt_content(
                article,
                style_recommendations,
                style_config
            )
            result.adapted_content = adapted_content

            # 步骤4: 质量检查
            quality_check = await self._check_quality(
                adapted_content,
                platform_info,
                style_config
            )
            result.quality_check = quality_check

            # 创建最终文章
            final_article = BasicArticle(
                title=article.title,
                content=adapted_content
            )
            result.final_article = final_article

            # 计算执行时间
            end_time = datetime.now()
            result.execution_time = (end_time - start_time).total_seconds()

            logger.info(f"风格适配完成，耗时: {result.execution_time:.2f}秒")
            return result

        except Exception as e:
            logger.error(f"风格适配过程出错: {str(e)}")
            # 计算执行时间
            end_time = datetime.now()
            result.execution_time = (end_time - start_time).total_seconds()
            raise

    async def _analyze_platform_internal(self, platform_info: Dict[str, Any]) -> Dict:
        """内部使用的平台分析方法

        Args:
            platform_info: 平台信息

        Returns:
            Dict: 平台分析结果
        """
        # 创建平台分析任务
        agent = self.platform_analyst.get_agent()
        task = Task(
            description=f"""分析平台 {platform_info.get('platform_name', '未知平台')} 的风格特点。

            平台描述：{platform_info.get('platform_description', '无描述')}
            目标受众：{platform_info.get('target_audience', '未指定')}
            平台规则：{json.dumps(platform_info.get('style_rules', {}))}

            请提供详细的平台风格分析，包括：
            1. 语言风格特点
            2. 内容结构偏好
            3. 媒体使用建议
            4. 受众特征与偏好
            5. 适合的表达方式
            """,
            expected_output="""详细的平台风格分析报告，JSON格式：
            {
                "language_style": "语言风格描述",
                "content_structure": "内容结构描述",
                "media_usage": "媒体使用建议",
                "audience_preferences": "受众偏好描述",
                "expression_style": "表达方式建议"
            }
            """,
            agent=agent
        )

        # 执行任务
        platform_crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=self.verbose,
            process=Process.sequential
        )

        result = await platform_crew.run_async(inputs=platform_info)

        # 解析结果为字典
        return self._parse_json_result(result)

    async def _generate_style_recommendations(
        self,
        platform_analysis: Dict,
        article: BasicArticle,
        style_config: Dict[str, Any]
    ) -> Dict:
        """生成风格建议

        Args:
            platform_analysis: 平台分析结果
            article: 原始文章
            style_config: 风格配置

        Returns:
            Dict: 风格建议
        """
        # 创建风格专家任务
        agent = self.style_expert.get_agent()
        task = Task(
            description=f"""
            基于平台分析结果，为文章《{article.title}》提供风格改写建议。

            平台分析结果：{json.dumps(platform_analysis)}
            文章内容：{article.content[:1000]}{"..." if len(article.content) > 1000 else ""}

            当前风格配置：
            - 风格名称: {style_config.get("style_name", "默认风格")}
            - 风格类型: {style_config.get("style", "formal")}
            - 语气: {style_config.get("tone", "professional")}
            - 正式程度: {style_config.get("formality", 3)}
            - 情感表达: {"启用" if style_config.get("emotion", False) else "禁用"}
            - 表情符号: {"启用" if style_config.get("emoji", False) else "禁用"}
            - 目标受众: {style_config.get("target_audience", "通用受众")}
            - 写作风格: {style_config.get("writing_style", "standard")}
            - 语言水平: {style_config.get("language_level", "normal")}
            - 内容长度范围: {style_config.get("min_length", 800)}-{style_config.get("max_length", 8000)}字
            - 段落长度范围: {style_config.get("min_paragraph_length", 50)}-{style_config.get("max_paragraph_length", 300)}字
            - 段落数量范围: {style_config.get("paragraph_count_min", 5)}-{style_config.get("paragraph_count_max", 30)}段
            - 代码块支持: {"支持" if style_config.get("code_block", True) else "不支持"}
            - 允许的格式: {", ".join(style_config.get("allowed_formats", ["text", "image", "code"]))}

            请提供详细的风格改写建议，包括：
            1. 语言风格调整（词汇选择、句式结构）
            2. 表达方式建议（直接/间接、正式/非正式）
            3. 结构优化建议
            4. 特定元素处理（如专业术语、引用等）
            5. 风格示例
            """,
            expected_output="""详细的风格建议，JSON格式：
            {
                "language_style": {
                    "vocabulary": "词汇建议",
                    "sentence_structure": "句式建议",
                    "tone_adjustments": "语气调整"
                },
                "expression_style": {
                    "directness": "直接/间接表达建议",
                    "formality": "正式程度建议"
                },
                "structure_suggestions": "结构优化建议",
                "special_elements": "特定元素处理建议",
                "examples": ["示例1", "示例2"]
            }
            """,
            agent=agent
        )

        # 执行任务
        style_crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=self.verbose,
            process=Process.sequential
        )

        # 准备输入
        inputs = {
            "platform_analysis": platform_analysis,
            "article_title": article.title,
            "article_excerpt": article.content[:1000] + ("..." if len(article.content) > 1000 else ""),
            "article_content": article.content,
            "style_config": style_config
        }

        result = await style_crew.run_async(inputs=inputs)

        # 解析结果为字典
        return self._parse_json_result(result)

    async def _adapt_content(
        self,
        article: BasicArticle,
        style_recommendations: Dict,
        style_config: Dict[str, Any]
    ) -> str:
        """适配内容风格

        Args:
            article: 原始文章
            style_recommendations: 风格建议
            style_config: 风格配置

        Returns:
            str: 适配后的内容
        """
        # 创建内容适配任务
        agent = self.content_adapter.get_agent()
        task = Task(
            description=f"""
            根据风格建议，改写文章《{article.title}》的内容，使其符合目标风格要求。

            原始内容：{article.content}

            风格建议：{json.dumps(style_recommendations)}

            当前风格配置：
            - 风格名称: {style_config.get("style_name", "默认风格")}
            - 风格类型: {style_config.get("style", "formal")}
            - 语气: {style_config.get("tone", "professional")}
            - 正式程度: {style_config.get("formality", 3)}
            - 情感表达: {"启用" if style_config.get("emotion", False) else "禁用"}
            - 表情符号: {"启用" if style_config.get("emoji", False) else "禁用"}
            - 目标受众: {style_config.get("target_audience", "通用受众")}
            - 写作风格: {style_config.get("writing_style", "standard")}
            - 语言水平: {style_config.get("language_level", "normal")}

            内容长度要求:
            - 最小长度: {style_config.get("min_length", 800)}字
            - 最大长度: {style_config.get("max_length", 8000)}字

            段落要求:
            - 段落最小长度: {style_config.get("min_paragraph_length", 50)}字
            - 段落最大长度: {style_config.get("max_paragraph_length", 300)}字
            - 推荐段落数量: {style_config.get("paragraph_count_min", 5)}-{style_config.get("paragraph_count_max", 30)}段

            格式要求:
            - 代码块支持: {"支持" if style_config.get("code_block", True) else "不支持"}
            - 允许的格式: {", ".join(style_config.get("allowed_formats", ["text", "image", "code"]))}

            风格模式:
            {", ".join(style_config.get("recommended_patterns", ["清晰的结构", "逻辑性强"]))}

            请按照风格建议改写文章内容，确保：
            1. 保持原始内容的核心信息和主旨
            2. 调整语言风格和表达方式以符合风格建议
            3. 优化结构以符合平台偏好
            4. 适当处理特殊元素（如专业术语、引用等）
            5. 整体风格一致性
            6. 符合长度和段落限制
            7. 遵循推荐的风格模式
            """,
            expected_output="按照风格建议改写后的完整文章内容",
            agent=agent
        )

        # 执行任务
        adapter_crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=self.verbose,
            process=Process.sequential
        )

        # 准备输入
        inputs = {
            "article_title": article.title,
            "article_content": article.content,
            "style_recommendations": style_recommendations,
            "style_config": style_config
        }

        adapted_content = await adapter_crew.run_async(inputs=inputs)
        return adapted_content

    async def _check_quality(
        self,
        adapted_content: str,
        platform_info: Dict[str, Any],
        style_config: Dict[str, Any]
    ) -> Dict:
        """检查适配后内容的质量

        Args:
            adapted_content: 适配后的内容
            platform_info: 平台信息
            style_config: 风格配置

        Returns:
            Dict: 质量检查结果
        """
        # 创建质量检查任务
        agent = self.quality_checker.get_agent()
        task = Task(
            description=f"""
            检查经过风格适配后的内容质量和合规性。

            适配后的内容：{adapted_content[:1000]}{"..." if len(adapted_content) > 1000 else ""}

            平台名称：{platform_info.get("platform_name", "通用平台")}
            平台描述：{platform_info.get("platform_description", "无描述")}

            风格配置：
            - 风格名称: {style_config.get("style_name", "默认风格")}
            - 风格类型: {style_config.get("style", "formal")}
            - 语气: {style_config.get("tone", "professional")}
            - 正式程度: {style_config.get("formality", 3)}
            - 目标受众: {style_config.get("target_audience", "通用受众")}

            内容长度要求:
            - 最小长度: {style_config.get("min_length", 800)}字
            - 最大长度: {style_config.get("max_length", 8000)}字

            段落要求:
            - 段落最小长度: {style_config.get("min_paragraph_length", 50)}字
            - 段落最大长度: {style_config.get("max_paragraph_length", 300)}字
            - 推荐段落数量: {style_config.get("paragraph_count_min", 5)}-{style_config.get("paragraph_count_max", 30)}段

            请对内容进行全面评估，包括：
            1. 风格一致性（与平台风格的匹配度）
            2. 内容质量（清晰度、连贯性、可读性）
            3. 语法和拼写
            4. 平台规则合规性
            5. 内容完整性
            6. 长度和结构符合度（是否符合字数和段落要求）

            请提供详细评估报告和改进建议。
            """,
            expected_output="""质量检查报告，JSON格式：
            {
                "style_consistency": {
                    "score": 8.5,
                    "comments": "风格一致性评价"
                },
                "content_quality": {
                    "clarity": 8.0,
                    "coherence": 7.5,
                    "readability": 8.0,
                    "comments": "内容质量评价"
                },
                "grammar_spelling": {
                    "score": 9.0,
                    "issues": ["问题1", "问题2"]
                },
                "compliance": {
                    "score": 8.0,
                    "comments": "合规性评价"
                },
                "completeness": {
                    "score": 7.5,
                    "comments": "完整性评价"
                },
                "structure_compliance": {
                    "length_check": "是否符合字数要求",
                    "paragraph_check": "是否符合段落要求",
                    "score": 8.0
                },
                "overall_score": 8.0,
                "improvement_suggestions": ["建议1", "建议2"]
            }
            """,
            agent=agent
        )

        # 执行任务
        checker_crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=self.verbose,
            process=Process.sequential
        )

        # 准备输入
        inputs = {
            "adapted_content_excerpt": adapted_content[:1000] + ("..." if len(adapted_content) > 1000 else ""),
            "adapted_content_full": adapted_content,
            "platform_name": platform_info.get("platform_name", "通用平台"),
            "platform_description": platform_info.get("platform_description", "无描述"),
            "style_config": style_config
        }

        result = await checker_crew.run_async(inputs=inputs)

        # 解析结果为字典
        return self._parse_json_result(result)

    def _parse_json_result(self, result: str) -> Dict:
        """解析任务结果为字典

        Args:
            result: 任务结果字符串

        Returns:
            Dict: 解析后的字典
        """
        try:
            import json
            from json_repair import repair_json  # 如果可用，导入json修复库

            try:
                # 首先尝试直接解析
                parsed_result = json.loads(result)
            except json.JSONDecodeError:
                try:
                    # 尝试修复和解析
                    repaired = repair_json(result)
                    parsed_result = json.loads(repaired)
                except:
                    # 如果仍然失败，作为原始文本处理
                    parsed_result = {"raw_result": result}

            if not isinstance(parsed_result, dict):
                parsed_result = {"raw_result": result}
        except:
            parsed_result = {"raw_result": result}

        return parsed_result
