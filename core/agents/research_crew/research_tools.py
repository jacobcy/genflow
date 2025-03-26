"""研究团队工具模块

这个模块定义了研究团队使用的工具集，包括内容收集、专家观点搜索、数据分析和报告生成等功能。
所有工具都按照CrewAI最佳实践组织，便于智能体调用和使用。
"""
import logging
from typing import List, Dict, Optional, Any
from crewai.tools import tool

from core.tools.content_collectors import ContentCollector
from core.tools.search_tools import SearchAggregator
from core.tools.nlp_tools import NLPAggregator
from core.config import Config

# 配置日志
logger = logging.getLogger("research_tools")

class ResearchTools:
    """研究团队工具集

    该类集中管理研究团队使用的各种工具，包括内容收集、搜索和NLP工具。
    工具方法使用@tool装饰器注册，便于智能体调用。
    """

    def __init__(self, config: Optional[Config] = None):
        """初始化工具集

        Args:
            config: 可选的配置对象，如果为None则使用默认配置
        """
        # 加载配置
        self.config = config or Config()

        # 初始化核心工具实例
        logger.info("初始化研究工具集...")
        self.content_collector = ContentCollector()
        self.search_tools = SearchAggregator()
        self.nlp_tools = NLPAggregator()
        logger.info("核心工具实例初始化完成")

    @tool("内容收集工具")
    def collect_content(self, query: str, source_type: str = "web", limit: int = 5) -> str:
        """收集与特定查询相关的内容

        这个工具可以从各种来源收集信息，包括网页、新闻文章、学术文献等。

        Args:
            query: 搜索查询词
            source_type: 内容来源类型，可选值包括 "web"、"news"、"academic"、"social"
            limit: 返回结果数量限制

        Returns:
            str: 收集到的内容汇总
        """
        logger.info(f"执行内容收集: 查询={query}, 来源={source_type}, 数量={limit}")
        return self.content_collector.execute(query=query, source_type=source_type, limit=limit)

    @tool("专家观点搜索")
    def search_expert_opinions(self, topic: str, expert_count: int = 3) -> str:
        """搜索特定话题的专家观点

        这个工具专注于寻找和收集领域专家对特定话题的观点和见解。

        Args:
            topic: 话题关键词
            expert_count: 需要收集的专家数量

        Returns:
            str: 专家观点汇总
        """
        logger.info(f"搜索专家观点: 话题={topic}, 专家数量={expert_count}")
        return self.search_tools.execute(
            query=f"{topic} expert opinions",
            filter="credible_sources",
            limit=expert_count
        )

    @tool("数据分析工具")
    def analyze_data(self, content: str, analysis_type: str = "key_insights") -> str:
        """分析文本内容，提取关键见解

        这个工具可以分析大量文本内容，提取关键见解、趋势、模式等。

        Args:
            content: 需要分析的文本内容
            analysis_type: 分析类型，可选值包括 "key_insights"、"trends"、"sentiment"、"summary"

        Returns:
            str: 分析结果
        """
        logger.info(f"执行数据分析: 分析类型={analysis_type}, 内容长度={len(content)}")
        return self.nlp_tools.execute(text=content, action=analysis_type)

    @tool("研究报告生成")
    def generate_research_report(self, background: str, expert_insights: str, data_analysis: str) -> str:
        """生成结构化的研究报告

        这个工具可以将各类研究素材整合为一份条理清晰的研究报告。

        Args:
            background: 背景研究内容
            expert_insights: 专家观点内容
            data_analysis: 数据分析结果

        Returns:
            str: 生成的研究报告
        """
        logger.info("生成研究报告: 整合背景、专家观点和数据分析")
        report_prompt = f"""
        基于以下研究材料生成一份结构化研究报告:

        ## 背景材料:
        {background}

        ## 专家观点:
        {expert_insights}

        ## 数据分析:
        {data_analysis}

        报告应包括以下部分:
        1. 概述
        2. 背景分析
        3. 专家观点总结
        4. 数据支持的发现
        5. 结论与建议
        6. 参考资料
        """
        return self.nlp_tools.execute(text=report_prompt, action="generation")

    @tool("关键发现提取工具")
    def extract_key_findings(self, content: str, max_findings: int = 5) -> str:
        """从长文本中提取关键发现

        这个工具可以从研究报告或论文中提取出最重要的发现。

        Args:
            content: 需要分析的文本内容
            max_findings: 提取的最大发现数量

        Returns:
            str: 提取的关键发现列表
        """
        logger.info(f"提取关键发现: 最大数量={max_findings}")
        return self.nlp_tools.execute(
            text=content,
            action="extract_findings",
            params={"max_findings": max_findings}
        )

    @tool("事实验证工具")
    def validate_facts(self, content: str, fact_list: List[str]) -> str:
        """验证研究内容中的事实准确性

        这个工具可以通过查找多个来源来验证研究中的事实性陈述。

        Args:
            content: 需要验证的研究内容
            fact_list: 需要特别验证的事实陈述列表

        Returns:
            str: 验证结果
        """
        logger.info(f"执行事实验证: 验证 {len(fact_list)} 个事实陈述")
        # 组合使用搜索和内容收集工具来验证事实
        results = []
        for fact in fact_list:
            search_result = self.search_tools.execute(
                query=f"verify {fact}",
                filter="reliable_sources",
                limit=3
            )
            results.append(f"事实: {fact}\n验证结果: {search_result}\n")

        return "\n".join(results)

    @tool("相关资源搜索")
    def search_related_resources(self, topic: str, resource_type: str = "all", limit: int = 5) -> str:
        """搜索与话题相关的各类资源

        这个工具可以查找与特定话题相关的书籍、论文、网站等资源。

        Args:
            topic: 话题关键词
            resource_type: 资源类型，可选值包括 "all"、"books"、"papers"、"websites"
            limit: 返回结果数量限制

        Returns:
            str: 相关资源列表
        """
        logger.info(f"搜索相关资源: 话题={topic}, 类型={resource_type}, 数量={limit}")

        # 构建搜索查询
        query = f"{topic} resources"
        if resource_type == "books":
            query = f"{topic} books recommendations"
        elif resource_type == "papers":
            query = f"{topic} academic papers research"
        elif resource_type == "websites":
            query = f"{topic} reliable websites resources"

        return self.search_tools.execute(query=query, limit=limit)

    @tool("观点对比分析")
    def compare_perspectives(self, topic: str, perspective_a: str, perspective_b: str) -> str:
        """对比分析同一话题的不同观点

        这个工具用于对比分析同一话题下的不同立场或观点，找出共识和分歧。

        Args:
            topic: 话题关键词
            perspective_a: 第一个观点或立场
            perspective_b: 第二个观点或立场

        Returns:
            str: 观点对比分析结果
        """
        logger.info(f"执行观点对比分析: 话题={topic}, 观点对比={perspective_a} vs {perspective_b}")

        # 构建对比分析提示
        analysis_prompt = f"""
        对比分析以下关于"{topic}"的两种观点:

        观点A: {perspective_a}
        观点B: {perspective_b}

        请从以下方面进行分析:
        1. 两种观点的核心论点
        2. 支持各自观点的主要证据
        3. 观点之间的共识点
        4. 观点之间的显著差异
        5. 分析差异产生的潜在原因
        6. 客观评估各自观点的优势和局限性
        """

        return self.nlp_tools.execute(text=analysis_prompt, action="analysis")

    @tool("定量统计分析")
    def analyze_statistics(self, data_text: str, analysis_focus: str = "trends") -> str:
        """分析文本中的定量数据和统计信息

        这个工具专注于从文本中提取和分析数字数据、统计信息和趋势。

        Args:
            data_text: 包含数据的文本
            analysis_focus: 分析焦点，可选值包括 "trends"、"comparisons"、"correlations"

        Returns:
            str: 统计分析结果
        """
        logger.info(f"执行定量统计分析: 焦点={analysis_focus}, 数据长度={len(data_text)}")

        analysis_prompt = f"""
        从以下文本中提取和分析定量数据:

        {data_text}

        分析焦点: {analysis_focus}

        请提供:
        1. 提取的关键数据点和统计信息
        2. 数据显示的主要趋势或模式
        3. 数据之间的关系或对比
        4. 基于数据的主要发现和结论
        5. 数据的局限性和可能的偏差
        """

        return self.nlp_tools.execute(text=analysis_prompt, action="data_analysis")
