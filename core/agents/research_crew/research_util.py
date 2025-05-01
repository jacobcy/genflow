"""研究工具模块

提供研究团队使用的工具类和辅助函数，将工具逻辑与业务逻辑分离。
"""
import logging
from typing import Dict, List, Any, Optional, Union
import re
from core.models.research.research import BasicResearch
from core.agents.research_crew.research_result import ResearchWorkflowResult
from core.models.facade.content_manager import ContentManager

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

# 研究配置映射 - 仅作为后备使用，应优先使用ContentManager获取的配置
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

    从ContentManager获取内容类型对象，提取其配置信息。
    这是唯一的研究配置来源，确保配置统一。

    Args:
        content_type: 内容类型ID

    Returns:
        Dict: 研究配置
    """
    if not content_type:
        content_type = "article"
        logger.info(f"未指定content_type，使用默认内容类型: {content_type}")

    # 从ContentManager获取内容类型配置
    try:
        content_type_obj = ContentManager.get_content_type(content_type)
        if content_type_obj:
            # 使用content_type对象的配置创建研究配置
            config = {
                "content_type": content_type_obj.name,
                "depth": content_type_obj.depth,
                "needs_expert": content_type_obj.needs_expert,
                "needs_data_analysis": content_type_obj.needs_data_analysis,
                "max_sources": 10  # 默认值，可以根据内容类型调整
            }

            # 获取内容类型摘要
            content_type_info = content_type_obj.get_type_summary()
            if content_type_info:
                config["content_type_info"] = content_type_info

                # 如果摘要中有研究需求信息，进一步细化配置
                research_needs = content_type_info.get("research_needs", {})
                if research_needs:
                    if "max_sources" in research_needs:
                        config["max_sources"] = research_needs.get("max_sources")

            logger.info(f"从ContentManager获取研究配置: {content_type}")
            return config
    except Exception as e:
        logger.warning(f"从ContentManager获取内容类型配置失败: {e}，使用默认配置")

    # 如果无法获取内容类型配置，使用默认配置
    default_config = {
        "content_type": content_type,
        "depth": "medium",
        "needs_expert": True,
        "needs_data_analysis": False,
        "max_sources": 10
    }

    logger.warning(f"使用默认研究配置: {default_config}")
    return default_config


def extract_experts_from_insights(expert_insights_text: str) -> List:
    """从专家见解文本中提取专家信息

    Args:
        expert_insights_text: 专家见解文本

    Returns:
        List: 专家信息列表
    """
    experts = []

    try:
        # 如果没有内容，返回空列表
        if not expert_insights_text:
            return []

        # 查找可能的专家段落
        expert_sections = []
        lines = expert_insights_text.split("\n")
        current_expert = []
        in_expert_section = False

        # 查找专家部分的标记
        for line in lines:
            if re.search(r"^#+ (.+专家|Expert .+)$", line) or "专家观点" in line or "Expert Insights" in line:
                in_expert_section = True
                if current_expert:
                    expert_sections.append("\n".join(current_expert))
                    current_expert = []
                continue

            if in_expert_section:
                if re.match(r"^#+ ", line) and "专家" not in line.lower() and "expert" not in line.lower():
                    # 遇到新的非专家章节标题，结束专家部分
                    in_expert_section = False
                    if current_expert:
                        expert_sections.append("\n".join(current_expert))
                        current_expert = []
                    continue

                # 在专家部分内
                if re.match(r"^[1-9]\.", line) or re.match(r"^- ", line) or re.match(r"^\* ", line):
                    # 新的专家条目
                    if current_expert:
                        expert_sections.append("\n".join(current_expert))
                        current_expert = []
                current_expert.append(line)

        # 添加最后一个专家
        if current_expert:
            expert_sections.append("\n".join(current_expert))

        # 如果没有找到专家部分，尝试按段落分割
        if not expert_sections and expert_insights_text:
            paragraphs = re.split(r"\n\n+", expert_insights_text)
            for p in paragraphs:
                if "专家" in p or "expert" in p.lower() or "教授" in p or "professor" in p.lower() or "博士" in p or "dr." in p.lower():
                    expert_sections.append(p)

        # 处理每个专家部分
        for section in expert_sections:
            # 提取专家姓名
            name_match = re.search(r"([\w\s·\.]+)(?:，|\(|（|,|\s+是|，|:|：)", section)
            name = name_match.group(1).strip() if name_match else "未知专家"

            # 提取专家领域
            field_match = re.search(r"(专注于|专业是|领域是|field is|专业领域|field of|field in)[\s:：]*([\w\s\d]+)", section, re.IGNORECASE)
            field = field_match.group(2).strip() if field_match else None

            # 提取专家证书/资质
            cred_match = re.search(r"(教授|professor|博士|Ph\.D|Dr\.|院士|研究员|科学家|专家|expert)[\s:：]*", section, re.IGNORECASE)
            credentials = cred_match.group(1).strip() if cred_match else None

            # 专家观点
            insight = section

            # 创建专家对象
            expert = {
                "name": name,
                "field": field,
                "credentials": credentials,
                "insight": insight
            }
            experts.append(expert)

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
                # 合并文本
                refs_text = "\n".join(references_text)

                # 查找引用形式的参考文献
                refs = re.findall(r"\[\d+\]\s+(.*?)(?=\[\d+\]|\Z)", refs_text + "\n[0]", re.DOTALL)
                if not refs:
                    # 尝试按列表形式查找
                    refs = [line.strip() for line in refs_text.split("\n") if
                            (line.strip().startswith("-") or line.strip().startswith("*") or
                            re.match(r"^\d+\.", line.strip())) and len(line.strip()) > 3]

                # 处理每个引用
                for ref in refs:
                    # 提取URL
                    url_match = re.search(r"(https?://[^\s]+)", ref)
                    url = url_match.group(1) if url_match else None

                    # 提取作者
                    author_match = re.search(r"^([^,.]+)[,.]", ref)
                    author = author_match.group(1).strip() if author_match else None

                    # 提取日期
                    date_match = re.search(r"(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}|\d{4}年\d{1,2}月\d{1,2}日|\d{4}年)", ref)
                    date = date_match.group(0) if date_match else None

                    # 提取片段
                    snippet = ref.strip()

                    # 添加来源
                    source = {
                        "name": snippet[:50] + "..." if len(snippet) > 50 else snippet,
                        "url": url,
                        "author": author,
                        "date": date,
                        "snippet": snippet,
                        "reliability": 0.7  # 默认可靠性
                    }
                    sources.append(source)
    except Exception as e:
        logger.warning(f"提取信息来源时出错: {e}")

    return sources


def extract_verification_results(result_text: str) -> List[Dict[str, Any]]:
    """从事实验证结果文本中提取结构化的验证结果

    Args:
        result_text: 验证结果文本，通常包含多个陈述的验证信息

    Returns:
        List[Dict[str, Any]]: 结构化的验证结果列表
    """
    verification_results = []

    try:
        # 处理空结果
        if not result_text or result_text.strip() == "":
            return []

        # 尝试找到验证结果的各个部分
        statements = []

        # 方法1: 基于常见的分隔符划分结果
        if "验证结果" in result_text or "Verification Results" in result_text:
            # 找到结果部分
            result_section = re.split(r"验证结果|Verification Results", result_text, 1)[-1]

            # 尝试按陈述编号分割
            numbered_statements = re.split(r"\n\s*(\d+[\.\)、]|陈述\s*\d+|Statement\s*\d+)", result_section)

            # 如果成功分割，处理每个部分
            if len(numbered_statements) > 1:
                # 跳过第一个元素（它是分隔符之前的文本）
                for i in range(1, len(numbered_statements), 2):
                    if i+1 < len(numbered_statements):
                        statement_num = numbered_statements[i].strip()
                        statement_text = numbered_statements[i+1].strip()
                        statements.append(statement_text)

        # 如果方法1未找到结果，尝试方法2: 按段落分割
        if not statements:
            # 按空行分割成段落
            paragraphs = re.split(r"\n\s*\n", result_text)

            # 筛选可能包含验证结果的段落
            for para in paragraphs:
                if (":" in para or "：" in para) and ("真实" in para or "错误" in para or
                                                    "正确" in para or "不正确" in para or
                                                    "true" in para.lower() or "false" in para.lower() or
                                                    "correct" in para.lower() or "incorrect" in para.lower()):
                    statements.append(para)

        # 如果方法2也未找到结果，按验证/未验证关键词拆分
        if not statements:
            possible_statements = re.split(r"(验证|未验证|verified|not verified|true|false|正确|不正确)", result_text, flags=re.IGNORECASE)
            if len(possible_statements) > 1:
                assembled_statements = []
                current_statement = ""

                for i, part in enumerate(possible_statements):
                    current_statement += part
                    if i % 2 == 1:  # 奇数索引是我们的分隔关键词
                        assembled_statements.append(current_statement)
                        current_statement = ""

                if current_statement:
                    assembled_statements.append(current_statement)

                statements = assembled_statements

        # 处理识别出的每个陈述
        for statement_text in statements:
            # 提取原始陈述内容
            original_statement_match = re.search(r"(陈述|statement)[：:]\s*(.+?)(?=\n|$)", statement_text, re.IGNORECASE)
            original_statement = original_statement_match.group(2).strip() if original_statement_match else ""

            if not original_statement:
                # 尝试查找冒号之前的文本作为陈述
                colon_split = re.split(r"[:：]", statement_text, 1)
                if len(colon_split) > 1:
                    original_statement = colon_split[0].strip()

            # 如果仍然没有找到陈述，使用整个文本的前部分
            if not original_statement:
                words = statement_text.split()
                original_statement = " ".join(words[:min(20, len(words))])  # 取前20个词

            # 确定验证结果
            is_verified = False

            if re.search(r"(正确|真实|验证|verified|true|correct)", statement_text, re.IGNORECASE):
                is_verified = True
            elif re.search(r"(错误|不正确|未验证|not verified|false|incorrect)", statement_text, re.IGNORECASE):
                is_verified = False

            # 提取置信度
            confidence_match = re.search(r"(置信度|confidence)[：:]\s*(\d+\.?\d*|\.\d+)", statement_text, re.IGNORECASE)
            confidence = float(confidence_match.group(2)) if confidence_match else 0.5

            # 限制置信度在0-1之间
            confidence = max(0.0, min(1.0, confidence))

            # 提取解释
            explanation_match = re.search(r"(解释|explanation)[：:]\s*(.+?)(?=\n\n|\n[^\n]|$)", statement_text, re.IGNORECASE | re.DOTALL)
            explanation = explanation_match.group(2).strip() if explanation_match else ""

            if not explanation:
                # 如果没有明确的解释部分，使用整个陈述文本减去已识别的部分作为解释
                explanation = statement_text
                # 移除原始陈述部分
                if original_statement:
                    explanation = explanation.replace(original_statement, "")
                # 移除验证状态部分
                for term in ["正确", "真实", "验证", "verified", "true", "correct",
                            "错误", "不正确", "未验证", "not verified", "false", "incorrect"]:
                    explanation = explanation.replace(term, "")
                explanation = explanation.strip()

            # 提取来源
            sources = []
            source_section_match = re.search(r"(来源|sources)[：:]\s*(.+?)(?=\n\n|\n[^\n]|$)", statement_text, re.IGNORECASE | re.DOTALL)

            if source_section_match:
                source_text = source_section_match.group(2)
                source_lines = source_text.split("\n")

                for line in source_lines:
                    if line.strip():
                        # 尝试提取URL
                        url_match = re.search(r"(https?://[^\s]+)", line)
                        url = url_match.group(1) if url_match else None

                        # 创建来源对象
                        source = {
                            "name": line.strip(),
                            "url": url
                        }
                        sources.append(source)

            # 创建验证结果对象
            verification_result = {
                "statement": original_statement,
                "verified": is_verified,
                "confidence": confidence,
                "explanation": explanation,
                "sources": sources
            }

            verification_results.append(verification_result)

    except Exception as e:
        logger.warning(f"提取验证结果时出错: {e}")
        # 在出错的情况下，尝试返回简单解析的结果
        simple_result = {
            "statement": result_text[:100] + "..." if len(result_text) > 100 else result_text,
            "verified": "正确" in result_text or "true" in result_text.lower(),
            "confidence": 0.5,
            "explanation": "解析验证结果时出错",
            "sources": []
        }
        verification_results = [simple_result]

    # 如果没有有效结果，返回一个默认结果
    if not verification_results:
        default_result = {
            "statement": "无法解析的陈述",
            "verified": False,
            "confidence": 0.5,
            "explanation": "无法从结果文本中提取结构化的验证信息",
            "sources": []
        }
        verification_results = [default_result]

    return verification_results


def format_expert(expert: Dict[str, Any]) -> Dict[str, Any]:
    """格式化专家信息，确保具有统一的结构

    Args:
        expert: 专家信息字典

    Returns:
        Dict[str, Any]: 格式化后的专家信息
    """
    return {
        "name": expert.get("name", "未知专家"),
        "field": expert.get("field"),
        "credentials": expert.get("credentials"),
        "insight": expert.get("insight", "")
    }


def create_research_config_from_request(request):
    """根据研究请求创建研究配置

    从请求对象中提取基本配置参数，并返回标准化的研究配置。

    主要配置来源:
    1. content_type_obj对象中的配置参数
    2. research_instruct文本中描述的研究要求
    3. metadata中的附加信息
    4. 选项参数中的覆盖设置

    Args:
        request: ResearchRequest对象

    Returns:
        Dict: 研究配置
    """
    # 初始化默认配置
    config = {
        "depth": "medium",
        "needs_expert": True,
        "needs_data_analysis": False,
        "max_sources": 10
    }

    # 1. 如果有内容类型对象，从中提取配置
    content_type_obj = request.content_type_obj
    if content_type_obj:
        logger.info(f"从内容类型对象提取研究配置")

        # 获取内容类型名称
        if hasattr(content_type_obj, 'name'):
            config["content_type"] = content_type_obj.name
        elif hasattr(content_type_obj, 'id'):
            config["content_type"] = content_type_obj.id

        # 获取研究深度
        if hasattr(content_type_obj, 'depth'):
            config["depth"] = content_type_obj.depth

        # 获取是否需要专家见解
        if hasattr(content_type_obj, 'needs_expert'):
            config["needs_expert"] = content_type_obj.needs_expert

        # 获取是否需要数据分析
        if hasattr(content_type_obj, 'needs_data_analysis'):
            config["needs_data_analysis"] = content_type_obj.needs_data_analysis

        # 获取内容类型摘要并添加到配置中
        if hasattr(content_type_obj, 'get_type_summary'):
            try:
                type_summary = content_type_obj.get_type_summary()
                if type_summary:
                    config["content_type_info"] = type_summary
            except Exception as e:
                logger.warning(f"获取内容类型摘要时出错: {e}")

    # 2. 如果有研究指导，根据指导调整配置
    if hasattr(request, 'research_instruct') and request.research_instruct:
        logger.info(f"根据研究指导调整配置")
        research_instruct = request.research_instruct

        # 简单示例：根据关键词调整研究深度
        if any(term in research_instruct.lower() for term in ["深入", "深度", "详细", "comprehensive", "deep", "thorough"]):
            config["depth"] = "deep"
            logger.info(f"根据研究指导，调整研究深度为: {config['depth']}")
        elif any(term in research_instruct.lower() for term in ["轻量", "简要", "概述", "brief", "light", "overview"]):
            config["depth"] = "light"
            logger.info(f"根据研究指导，调整研究深度为: {config['depth']}")

        # 添加研究指导到配置中
        config["research_instruct"] = research_instruct

    # 3. 合并元数据
    if request.metadata:
        # 只合并基本配置参数，避免覆盖已经处理的内容类型对象
        for key in ["depth", "needs_expert", "needs_data_analysis", "max_sources"]:
            if key in request.metadata:
                config[key] = request.metadata[key]

    # 4. 合并选项参数（最高优先级）
    if request.options:
        for key, value in request.options.items():
            config[key] = value

    return config


def workflow_result_to_basic_research(workflow_result):
    """将工作流结果转换为BasicResearch对象

    Args:
        workflow_result: 工作流结果

    Returns:
        BasicResearch: 基础研究结果
    """
    from core.models.research.research import BasicResearch, ExpertInsight, KeyFinding, Source

    # 提取专家见解
    expert_insights = []
    for expert in workflow_result.experts:
        insight = ExpertInsight(
            expert_name=expert.get("name", "未知专家"),
            content=expert.get("insight", ""),
            field=expert.get("field", None),
            credentials=expert.get("credentials", None)
        )
        expert_insights.append(insight)

    # 从研究报告中提取关键发现
    key_findings = []
    key_findings_data = extract_key_findings(workflow_result.research_results)
    for finding in key_findings_data:
        kf = KeyFinding(
            content=finding.get("content", ""),
            importance=finding.get("importance", 0.5),
            sources=[]  # 暂不关联来源
        )
        key_findings.append(kf)

    # 从研究报告中提取信息来源
    sources = []
    sources_data = extract_sources(workflow_result.research_results)
    for source_data in sources_data:
        src = Source(
            name=source_data.get("name", "未知来源"),
            url=source_data.get("url", None),
            author=source_data.get("author", None),
            publish_date=source_data.get("date", None),
            content_snippet=source_data.get("snippet", None),
            reliability_score=source_data.get("reliability", 0.5)
        )
        sources.append(src)

    # 创建BasicResearch对象
    return BasicResearch(
        title=workflow_result.topic,
        content_type=workflow_result.metadata.get("content_type", "article"),
        background=str(workflow_result.background_research) if workflow_result.background_research else None,
        expert_insights=expert_insights,
        key_findings=key_findings,
        sources=sources,
        data_analysis=str(workflow_result.data_analysis) if workflow_result.data_analysis else None,
        report=workflow_result.research_results,
        metadata=workflow_result.metadata
    )
