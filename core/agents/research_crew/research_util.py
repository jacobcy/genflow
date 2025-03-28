"""研究工具模块

提供研究团队使用的工具类和辅助函数，将工具逻辑与业务逻辑分离。
"""
import logging
from typing import Dict, List, Any, Optional, Union
from core.models.research import BasicResearch
from core.agents.research_crew.research_result import ResearchWorkflowResult

# 定义研究深度常量
RESEARCH_DEPTH_LIGHT = "light"
RESEARCH_DEPTH_MEDIUM = "medium"
RESEARCH_DEPTH_DEEP = "deep"

# 默认研究配置
DEFAULT_RESEARCH_CONFIG = {
    "content_type": "article",
    "depth": RESEARCH_DEPTH_MEDIUM,
    "needs_expert": True,
    "needs_data_analysis": True,
    "max_sources": 10
}

# 研究配置映射
RESEARCH_CONFIG = {
    "article": DEFAULT_RESEARCH_CONFIG,
    "blog": {
        "content_type": "blog",
        "depth": RESEARCH_DEPTH_MEDIUM,
        "needs_expert": True,
        "needs_data_analysis": False,
        "max_sources": 5
    },
    "news": {
        "content_type": "news",
        "depth": RESEARCH_DEPTH_LIGHT,
        "needs_expert": True,
        "needs_data_analysis": True,
        "max_sources": 3
    },
    "technical": {
        "content_type": "technical",
        "depth": RESEARCH_DEPTH_DEEP,
        "needs_expert": True,
        "needs_data_analysis": True,
        "max_sources": 15
    }
}

# 配置日志
logger = logging.getLogger("research_util")


def get_research_config(content_type=None):
    """获取指定内容类型的研究配置

    Args:
        content_type: 内容类型ID

    Returns:
        Dict: 研究配置
    """
    if not content_type:
        return DEFAULT_RESEARCH_CONFIG.copy()

    return RESEARCH_CONFIG.get(content_type, DEFAULT_RESEARCH_CONFIG).copy()


def extract_experts_from_insights(expert_insights_text: str) -> List:
    """从专家见解文本中提取专家信息

    Args:
        expert_insights_text: 专家见解文本

    Returns:
        List: 专家信息列表
    """
    # 简单实现，实际应用中可能需要更复杂的文本处理
    experts = []
    try:
        # 检查文本中是否包含专家部分
        if "专家" in expert_insights_text or "Expert" in expert_insights_text:
            # 简单的专家名称提取逻辑
            lines = expert_insights_text.split("\n")
            for i, line in enumerate(lines):
                if "专家概述" in line or "专家名称" in line or "Expert" in line:
                    # 在接下来的几行中寻找专家名称
                    for j in range(i+1, min(i+15, len(lines))):
                        if lines[j].strip() and (lines[j].strip().startswith("-") or lines[j].strip().startswith("*")):
                            expert_line = lines[j].strip().lstrip("-*").strip()
                            if ":" in expert_line or "：" in expert_line:
                                parts = expert_line.split(":") if ":" in expert_line else expert_line.split("：")
                                expert_name = parts[0].strip()
                                if expert_name:
                                    # 尝试提取专家领域和洞见
                                    field = ""
                                    insight = ""
                                    if len(parts) > 1:
                                        insight = parts[1].strip()

                                    # 添加专家
                                    experts.append({
                                        "name": expert_name,
                                        "field": field,
                                        "insight": insight,
                                        "credentials": ""
                                    })
    except Exception as e:
        logger.warning(f"提取专家信息时出错: {e}")

    return experts


def extract_key_findings(report: str) -> List[Dict[str, Any]]:
    """从研究报告中提取关键发现

    Args:
        report: 研究报告文本

    Returns:
        List[Dict[str, Any]]: 关键发现列表
    """
    findings = []
    try:
        # 检查报告中是否包含关键发现部分
        if "关键发现" in report or "主要发现" in report or "Key Findings" in report:
            # 提取关键发现部分
            parts = report.split("\n")
            in_findings_section = False
            findings_text = []

            for line in parts:
                if in_findings_section:
                    # 如果遇到下一个主要标题，结束关键发现部分
                    if line.startswith("# "):
                        break
                    # 收集关键发现文本
                    findings_text.append(line)
                elif "关键发现" in line or "主要发现" in line or "Key Findings" in line:
                    in_findings_section = True

            # 处理提取的文本
            if findings_text:
                finding_text = "\n".join(findings_text)
                bullet_points = [p for p in finding_text.split("\n") if p.strip().startswith("-") or p.strip().startswith("*")]

                for i, point in enumerate(bullet_points):
                    point_text = point.strip().lstrip("-").lstrip("*").strip()
                    if point_text:
                        findings.append({
                            "content": point_text,
                            "importance": 0.5 + (0.1 * (len(bullet_points) - i) / len(bullet_points))  # 根据顺序设置重要性
                        })
    except Exception as e:
        logger.warning(f"提取关键发现时出错: {e}")

    return findings


def extract_sources(report: str) -> List[Dict[str, Any]]:
    """从研究报告中提取信息来源

    Args:
        report: 研究报告文本

    Returns:
        List[Dict[str, Any]]: 信息来源列表
    """
    sources = []
    try:
        # 检查报告中是否包含参考资料部分
        if "参考资料" in report or "References" in report or "参考文献" in report:
            # 提取参考资料部分
            parts = report.split("\n")
            in_references_section = False
            references_text = []

            for line in parts:
                if in_references_section:
                    # 如果遇到空行后的主要标题，结束参考资料部分
                    if not line.strip() and len(references_text) > 0 and references_text[-1].strip() == "":
                        if parts.index(line) + 1 < len(parts) and parts[parts.index(line) + 1].startswith("# "):
                            break
                    # 收集参考资料文本
                    references_text.append(line)
                elif "参考资料" in line or "References" in line or "参考文献" in line:
                    in_references_section = True

            # 处理提取的文本
            if references_text:
                reference_text = "\n".join(references_text)
                # 简单分割参考资料
                refs = [r for r in reference_text.split("\n") if r.strip() and not r.startswith("#")]

                for ref in refs:
                    # 尝试提取URL
                    url = None
                    if "http" in ref:
                        url_start = ref.find("http")
                        url_end = ref.find(" ", url_start) if ref.find(" ", url_start) > 0 else len(ref)
                        url = ref[url_start:url_end].strip()

                    # 添加来源
                    sources.append({
                        "name": ref[:50] + "..." if len(ref) > 50 else ref,
                        "url": url,
                        "reliability": 0.7  # 默认可靠性
                    })
    except Exception as e:
        logger.warning(f"提取信息来源时出错: {e}")

    return sources


def format_expert(expert) -> Dict[str, Any]:
    """将专家信息转换为标准字典格式

    Args:
        expert: 专家信息字典或对象

    Returns:
        Dict[str, Any]: 标准格式的专家信息
    """
    if isinstance(expert, dict):
        return {
            "name": expert.get("name", "未知专家"),
            "insight": expert.get("insight", ""),
            "field": expert.get("field", ""),
            "credentials": expert.get("credentials", "")
        }
    # 如果不是字典，尝试转换为字典
    return {
        "name": getattr(expert, "name", "未知专家"),
        "insight": getattr(expert, "insight", ""),
        "field": getattr(expert, "field", ""),
        "credentials": getattr(expert, "credentials", "")
    }


def create_research_config_from_request(request) -> Dict[str, Any]:
    """根据研究请求创建研究配置

    Args:
        request: 研究请求对象，包含内容类型、深度等信息

    Returns:
        Dict[str, Any]: 完整的研究配置
    """
    # 获取基本参数
    content_type = request.content_type
    depth = request.depth
    options = request.options or {}
    metadata = request.metadata or {}

    # 基于内容类型获取基础配置
    config = get_research_config(content_type)

    # 根据请求中的深度设置研究深度
    if depth:
        if depth.lower() in ["shallow", "light"]:
            config["depth"] = RESEARCH_DEPTH_LIGHT
        elif depth.lower() in ["deep", "high"]:
            config["depth"] = RESEARCH_DEPTH_DEEP
        else:
            config["depth"] = RESEARCH_DEPTH_MEDIUM

    # 从元数据获取内容类型信息
    if "content_type_info" in metadata:
        config["content_type_info"] = metadata["content_type_info"]

    # 允许通过options覆盖配置
    for key, value in options.items():
        if key in ["needs_expert", "needs_data_analysis", "max_sources"]:
            config[key] = value

    return config


def map_research_depth(depth: str) -> str:
    """将研究深度映射为标准化的深度级别

    将各种可能的深度值映射为标准的"low"、"medium"、"high"三种级别，
    用于任务创建和配置调整。

    Args:
        depth: 研究深度标识符

    Returns:
        str: 标准化的深度级别 ("low", "medium", "high")
    """
    depth_map = {
        # 标准深度级别
        RESEARCH_DEPTH_LIGHT: "low",
        RESEARCH_DEPTH_MEDIUM: "medium",
        RESEARCH_DEPTH_DEEP: "high",

        # 兼容其他可能的描述
        "shallow": "low",
        "basic": "low",
        "simple": "low",
        "standard": "medium",
        "normal": "medium",
        "detailed": "high",
        "comprehensive": "high",
        "thorough": "high",

        # 数字映射
        "1": "low",
        "2": "medium",
        "3": "high",

        # 直接传入目标值
        "low": "low",
        "medium": "medium",
        "high": "high"
    }

    return depth_map.get(depth.lower(), "medium")


def _format_expert(self, expert) -> Dict[str, Any]:
    """将专家信息转换为标准字典格式

    Args:
        expert: 专家信息字典或对象

    Returns:
        Dict[str, Any]: 标准格式的专家信息
    """
    if isinstance(expert, dict):
        return {
            "name": expert.get("name", "未知专家"),
            "insight": expert.get("insight", ""),
            "field": expert.get("field", ""),
            "credentials": expert.get("credentials", "")
        }
    # 如果不是字典，尝试转换为字典
    return {
        "name": getattr(expert, "name", "未知专家"),
        "insight": getattr(expert, "insight", ""),
        "field": getattr(expert, "field", ""),
        "credentials": getattr(expert, "credentials", "")
    }

def _extract_key_findings(self, report: str) -> List[Dict[str, Any]]:
    """从研究报告中提取关键发现

    Args:
        report: 研究报告文本

    Returns:
        List[Dict[str, Any]]: 关键发现列表
    """
    # 简单实现，实际应用中可以使用更复杂的提取逻辑
    findings = []
    try:
        # 检查报告中是否包含关键发现部分
        if "关键发现" in report or "主要发现" in report or "Key Findings" in report:
            # 提取关键发现部分
            parts = report.split("\n")
            in_findings_section = False
            findings_text = []

            for line in parts:
                if in_findings_section:
                    # 如果遇到下一个主要标题，结束关键发现部分
                    if line.startswith("# "):
                        break
                    # 收集关键发现文本
                    findings_text.append(line)
                elif "关键发现" in line or "主要发现" in line or "Key Findings" in line:
                    in_findings_section = True

            # 处理提取的文本
            if findings_text:
                finding_text = "\n".join(findings_text)
                bullet_points = [p for p in finding_text.split("\n") if p.strip().startswith("-") or p.strip().startswith("*")]

                for i, point in enumerate(bullet_points):
                    point_text = point.strip().lstrip("-").lstrip("*").strip()
                    if point_text:
                        findings.append({
                            "content": point_text,
                            "importance": 0.5 + (0.1 * (len(bullet_points) - i) / len(bullet_points))  # 根据顺序设置重要性
                        })
    except Exception as e:
        logger.warning(f"提取关键发现时出错: {e}")

    return findings

def _extract_sources(self, report: str) -> List[Dict[str, Any]]:
    """从研究报告中提取信息来源

    Args:
        report: 研究报告文本

    Returns:
        List[Dict[str, Any]]: 信息来源列表
    """
    # 简单实现，实际应用中可以使用更复杂的提取逻辑
    sources = []
    try:
        # 检查报告中是否包含参考资料部分
        if "参考资料" in report or "References" in report or "参考文献" in report:
            # 提取参考资料部分
            parts = report.split("\n")
            in_references_section = False
            references_text = []

            for line in parts:
                if in_references_section:
                    # 如果遇到空行后的主要标题，结束参考资料部分
                    if not line.strip() and len(references_text) > 0 and references_text[-1].strip() == "":
                        if parts.index(line) + 1 < len(parts) and parts[parts.index(line) + 1].startswith("# "):
                            break
                    # 收集参考资料文本
                    references_text.append(line)
                elif "参考资料" in line or "References" in line or "参考文献" in line:
                    in_references_section = True

            # 处理提取的文本
            if references_text:
                reference_text = "\n".join(references_text)
                # 简单分割参考资料
                refs = [r for r in reference_text.split("\n") if r.strip() and not r.startswith("#")]

                for ref in refs:
                    # 尝试提取URL
                    url = None
                    if "http" in ref:
                        url_start = ref.find("http")
                        url_end = ref.find(" ", url_start) if ref.find(" ", url_start) > 0 else len(ref)
                        url = ref[url_start:url_end].strip()

                    # 添加来源
                    sources.append({
                        "name": ref[:50] + "..." if len(ref) > 50 else ref,
                        "url": url,
                        "reliability": 0.7  # 默认可靠性
                    })
    except Exception as e:
        logger.warning(f"提取信息来源时出错: {e}")

    return sources

def _workflow_result_to_basic_research(self, result: ResearchWorkflowResult) -> BasicResearch:
    """将ResearchWorkflowResult转换为BasicResearch

    Args:
        result: 研究工作流结果

    Returns:
        BasicResearch: 基础研究结果
    """
    # 创建BasicResearch对象
    research = BasicResearch(
        title=result.topic,
        content_type="article",  # 默认使用article
        background=str(result.background_research) if result.background_research else None,
        expert_insights=[],
        key_findings=[],
        sources=[],
        data_analysis=str(result.data_analysis) if result.data_analysis else None,
        report=result.research_results,
        metadata=result.metadata.copy()
    )

    return research
