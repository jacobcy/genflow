"""研究报告格式化工具

提供将研究报告转换为各种格式的工具函数。
"""

from typing import Dict, Any, Optional, List, Union
from ..basic_research import BasicResearch
from ..research import TopicResearch


def format_research_as_markdown(research: Union[BasicResearch, TopicResearch, Dict[str, Any]]) -> str:
    """将研究报告格式化为Markdown格式

    将研究报告对象或研究报告字典转换为Markdown格式的文本，便于导出或展示。

    Args:
        research: 研究报告对象或字典

    Returns:
        str: Markdown格式的研究报告文本
    """
    # 如果是字典，先转换为对象
    if isinstance(research, dict):
        try:
            research = TopicResearch(**research)
        except:
            research = BasicResearch(**research)

    # 提取标题
    title = research.title
    research_type = research.content_type

    # 构建Markdown文本
    markdown = f"# {title}\n\n"

    # 添加基本信息
    markdown += f"**内容类型**: {research_type}\n\n"

    # 添加研究时间
    if hasattr(research, "research_timestamp"):
        research_time = research.research_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        markdown += f"**研究时间**: {research_time}\n\n"

    # 添加话题ID (如果是TopicResearch)
    if isinstance(research, TopicResearch) and research.topic_id:
        markdown += f"**关联话题**: {research.topic_id}\n\n"

    # 添加背景信息
    if research.background:
        markdown += f"## 研究背景\n\n{research.background}\n\n"

    # 添加关键发现
    if research.key_findings:
        markdown += "## 关键发现\n\n"
        for i, finding in enumerate(research.key_findings, 1):
            importance = int(finding.importance * 100)
            markdown += f"### {i}. {finding.content}\n\n"
            markdown += f"**重要性**: {importance}%\n\n"

            # 添加来源信息
            if finding.sources:
                markdown += "**来源**:\n\n"
                for source in finding.sources:
                    markdown += f"- {source.name}"
                    if source.url:
                        markdown += f" ([链接]({source.url}))"
                    markdown += "\n"
                markdown += "\n"

    # 添加专家见解
    if research.expert_insights:
        markdown += "## 专家见解\n\n"
        for i, insight in enumerate(research.expert_insights, 1):
            markdown += f"### {insight.expert_name}"
            if insight.field:
                markdown += f" ({insight.field})"
            markdown += "\n\n"

            if insight.credentials:
                markdown += f"**资质**: {insight.credentials}\n\n"

            markdown += f"{insight.content}\n\n"

    # 添加数据分析
    if research.data_analysis:
        markdown += f"## 数据分析\n\n{research.data_analysis}\n\n"

    # 添加摘要
    if research.summary:
        markdown += f"## 研究摘要\n\n{research.summary}\n\n"

    # 添加完整报告
    if research.report:
        markdown += f"## 完整研究报告\n\n{research.report}\n\n"

    # 添加参考来源
    if research.sources:
        markdown += "## 参考来源\n\n"
        for i, source in enumerate(research.sources, 1):
            markdown += f"{i}. **{source.name}**"
            if source.url:
                markdown += f" - [链接]({source.url})"
            if source.author:
                markdown += f" - 作者: {source.author}"
            if hasattr(source, "publish_date") and source.publish_date:
                markdown += f" - 日期: {source.publish_date}"
            markdown += "\n\n"
            if hasattr(source, "content_snippet") and source.content_snippet:
                markdown += f"   {source.content_snippet}\n\n"

    return markdown


def format_research_as_json(research: Union[BasicResearch, TopicResearch]) -> Dict[str, Any]:
    """将研究报告格式化为JSON格式

    将研究报告对象转换为字典，便于序列化为JSON。

    Args:
        research: 研究报告对象

    Returns:
        Dict[str, Any]: 字典格式的研究报告
    """
    if isinstance(research, (BasicResearch, TopicResearch)):
        return research.to_dict()
    return research
