"""通用研究工具模块

提供研究相关的通用工具函数，可供多个团队使用。
包含文本分析、关键信息提取和智能数据转换等功能。
"""

import logging
import re
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# 配置日志
logger = logging.getLogger("research_tools")


def extract_sections_from_text(text: str, section_markers: List[str] = None) -> Dict[str, str]:
    """从文本中提取特定部分

    Args:
        text: 要分析的文本
        section_markers: 部分标记列表，如["摘要", "引言", "结论"]

    Returns:
        Dict[str, str]: 部分名称与内容的映射
    """
    if not section_markers:
        section_markers = ["摘要", "介绍", "引言", "方法", "结果", "讨论", "结论", "参考文献"]

    sections = {}
    lines = text.split("\n")
    current_section = None
    current_content = []

    for line in lines:
        # 检查是否匹配任何部分标记
        found_section = False
        for marker in section_markers:
            pattern = re.compile(rf"^[#\s]*{marker}[\s:：]*", re.IGNORECASE)
            if pattern.search(line):
                # 保存之前的部分
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                # 开始新部分
                current_section = marker
                current_content = []
                found_section = True
                break

        if not found_section and current_section:
            current_content.append(line)

    # 添加最后一个部分
    if current_section and current_content:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def extract_bullet_points(text: str) -> List[str]:
    """从文本中提取项目符号列表项

    Args:
        text: 要分析的文本

    Returns:
        List[str]: 提取的项目符号列表
    """
    bullet_points = []
    lines = text.split("\n")

    for line in lines:
        stripped = line.strip()
        # 匹配常见的项目符号格式(-, *, 1., 等)
        if (stripped.startswith("-") or
            stripped.startswith("*") or
            re.match(r"^\d+\.", stripped) or
            stripped.startswith("•")):
            # 提取项目符号后的内容
            content = re.sub(r"^[-*•]|\d+\.\s*", "", stripped).strip()
            if content:
                bullet_points.append(content)

    return bullet_points


def extract_named_entities(text: str, entity_types: List[str] = None) -> Dict[str, List[str]]:
    """从文本中提取命名实体

    Args:
        text: 要分析的文本
        entity_types: 要提取的实体类型，如["person", "organization", "location"]

    Returns:
        Dict[str, List[str]]: 按类型分组的实体列表
    """
    # 这个函数需要在实际实现中使用NLP工具，这里仅作示例
    # 默认返回空结果
    if not entity_types:
        entity_types = ["person", "organization", "location"]

    result = {entity_type: [] for entity_type in entity_types}

    # 简单的模式匹配示例(不够准确，实际应使用NLP库)
    if "person" in entity_types:
        # 查找可能的人名(简单实现，不够准确)
        name_matches = re.findall(r"[A-Z][a-z]+ [A-Z][a-z]+", text)
        result["person"] = list(set(name_matches))

    if "organization" in entity_types:
        # 查找可能的组织名(简单实现，不够准确)
        org_matches = re.findall(r"[A-Z][A-Za-z]+ (Inc\.|Corp\.|Corporation|Company|Ltd\.)", text)
        result["organization"] = list(set(org_matches))

    return result


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """简单的情感分析

    Args:
        text: 要分析的文本

    Returns:
        Dict[str, Any]: 情感分析结果，包含积极性评分
    """
    # 这个函数需要在实际实现中使用NLP工具，这里仅作示例
    positive_words = ["好", "优秀", "出色", "杰出", "精彩", "卓越", "高效", "excellent", "good", "great"]
    negative_words = ["差", "糟糕", "失败", "劣质", "inefficient", "bad", "poor", "terrible"]

    # 计算积极和消极词的数量
    positive_count = sum(1 for word in positive_words if word in text.lower())
    negative_count = sum(1 for word in negative_words if word in text.lower())

    total = positive_count + negative_count
    if total == 0:
        sentiment_score = 0
    else:
        sentiment_score = (positive_count - negative_count) / total

    return {
        "score": sentiment_score,
        "assessment": "positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral",
        "confidence": min(abs(sentiment_score) + 0.5, 1.0)
    }


def extract_urls(text: str) -> List[Dict[str, str]]:
    """从文本中提取URL

    Args:
        text: 要分析的文本

    Returns:
        List[Dict[str, str]]: URL列表，包含URL和上下文
    """
    urls = []
    # 简单的URL匹配模式
    url_pattern = re.compile(r'https?://[^\s()<>"]+|www\.[^\s()<>"]+')

    # 查找所有URL
    for match in url_pattern.finditer(text):
        url = match.group(0)
        # 获取URL的上下文(前后50个字符)
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].strip()

        urls.append({
            "url": url,
            "context": context
        })

    return urls


def format_research_citation(source: Dict[str, Any]) -> str:
    """格式化研究引用

    Args:
        source: 源信息字典，包含标题、作者、日期等

    Returns:
        str: 格式化的引用字符串
    """
    # 检查必要的字段
    title = source.get("title", "未知标题")
    authors = source.get("authors", [])
    date = source.get("date", "")
    url = source.get("url", "")
    publisher = source.get("publisher", "")

    # 格式化作者列表
    if authors:
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} 和 {authors[1]}"
        else:
            author_str = f"{authors[0]} 等人"
    else:
        author_str = "未知作者"

    # 格式化日期
    if date:
        try:
            if isinstance(date, str):
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%Y年%m月%d日")
            else:
                formatted_date = date.strftime("%Y年%m月%d日")
        except (ValueError, AttributeError):
            formatted_date = date
    else:
        formatted_date = "无日期"

    # 构建引用字符串
    citation = f"{author_str}. ({formatted_date}). {title}"

    if publisher:
        citation += f". {publisher}"

    if url:
        citation += f". 链接: {url}"

    return citation
