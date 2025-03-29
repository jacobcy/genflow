"""审核团队工具模块

提供文章审核、内容检测和合规性评估所需的工具集合。
"""
import logging
from typing import Dict, List, Optional, Any
from crewai.tools import tool

from core.tools.nlp_tools import NLPAggregator
from core.tools.review_tools.reviewer import (
    PlagiarismChecker,
    StatisticalAIDetector,
    OpenAIDetector,
    SensitiveWordChecker
)
from core.models.platform.platform import Platform

# 配置日志
logger = logging.getLogger(__name__)

class ReviewTools:
    """审核团队工具类，按照CrewAI最佳实践组织工具"""

    def __init__(self, platform: Platform):
        """
        初始化审核工具集

        Args:
            platform: 发布平台信息，包含内容规范和合规要求
        """
        logger.info(f"初始化审核工具集，目标平台: {platform.name}")
        self.platform = platform

        # 初始化核心工具
        self.nlp_tools = NLPAggregator()
        self.plagiarism_checker = PlagiarismChecker.get_instance()
        self.statistical_ai_detector = StatisticalAIDetector.get_instance()
        self.openai_detector = OpenAIDetector.get_instance()
        self.sensitive_checker = SensitiveWordChecker.get_instance()

        logger.info("审核工具集初始化完成")

    @tool("原创性检测")
    def check_plagiarism(self, text: str, strict_mode: bool = False) -> Dict:
        """
        检测文章的原创性，识别重复内容和引用问题

        Args:
            text: 要检测的文章内容
            strict_mode: 是否启用严格模式

        Returns:
            Dict: 包含查重结果的字典
        """
        logger.info(f"执行原创性检测，严格模式: {strict_mode}")
        result = self.plagiarism_checker.execute(text=text, strict_mode=strict_mode)

        # 记录详细日志
        plagiarism_rate = result.data.get("plagiarism_rate", 0)
        logger.info(f"原创性检测完成，查重率: {plagiarism_rate}")

        return result.data

    @tool("AI内容检测")
    def detect_ai_content(self, text: str, detection_mode: str = "balanced") -> Dict:
        """
        检测文章是否由AI生成，分析语言特征

        Args:
            text: 要检测的文章内容
            detection_mode: 检测模式，可选值: "sensitive", "balanced", "relaxed"

        Returns:
            Dict: 包含AI检测结果的字典
        """
        logger.info(f"执行AI内容检测，模式: {detection_mode}")

        # 使用统计方法检测
        stat_result = self.statistical_ai_detector.execute(
            text=text,
            mode=detection_mode
        )

        # 使用OpenAI检测器检测
        openai_result = self.openai_detector.execute(
            text=text,
            mode=detection_mode
        )

        # 合并结果
        combined_result = {
            "statistical_score": stat_result.data.get("ai_score", 0),
            "openai_score": openai_result.data.get("ai_score", 0),
            "average_score": (
                stat_result.data.get("ai_score", 0) +
                openai_result.data.get("ai_score", 0)
            ) / 2,
            "is_likely_ai": stat_result.data.get("is_likely_ai", False) or
                           openai_result.data.get("is_likely_ai", False),
            "features": stat_result.data.get("features", {})
        }

        logger.info(f"AI内容检测完成，平均得分: {combined_result['average_score']}")
        return combined_result

    @tool("敏感内容检测")
    def check_sensitive_content(self, text: str, check_level: str = "normal") -> Dict:
        """
        检测文章中的敏感内容，评估合规性

        Args:
            text: 要检测的文章内容
            check_level: 检查级别，可选值: "relaxed", "normal", "strict"

        Returns:
            Dict: 包含敏感内容检测结果的字典
        """
        logger.info(f"执行敏感内容检测，级别: {check_level}")

        # 获取平台特定的敏感词列表
        platform_sensitive_words = self.platform.content_rules.get("sensitive_words", [])

        result = self.sensitive_checker.execute(
            text=text,
            level=check_level,
            additional_words=platform_sensitive_words
        )

        sensitive_count = len(result.data.get("sensitive_words", []))
        logger.info(f"敏感内容检测完成，发现敏感词: {sensitive_count}个")

        return result.data

    @tool("内容质量分析")
    def analyze_content_quality(self, text: str) -> Dict:
        """
        分析文章内容质量，包括语法、结构和专业性

        Args:
            text: 要分析的文章内容

        Returns:
            Dict: 包含内容质量分析结果的字典
        """
        logger.info("执行内容质量分析")
        result = self.nlp_tools.execute(text=text, analysis_type="quality")

        # 简化日志输出
        quality_score = result.data.get("overall_score", 0)
        logger.info(f"内容质量分析完成，总体得分: {quality_score}")

        return result.data

    @tool("合规性评估")
    def evaluate_compliance(self, text: str, platform_rules: Dict = None) -> Dict:
        """
        评估文章是否符合平台规范和法律要求

        Args:
            text: 要评估的文章内容
            platform_rules: 平台特定规则，默认使用初始化时指定的平台

        Returns:
            Dict: 包含合规性评估结果的字典
        """
        rules = platform_rules or self.platform.content_rules
        logger.info(f"执行合规性评估，平台: {self.platform.name}")

        # 组合多个工具的结果
        # 1. 敏感内容检测
        sensitive_result = self.check_sensitive_content(text)

        # 2. 内容长度检查
        min_words = rules.get("min_words", 0)
        max_words = rules.get("max_words", 10000)
        word_count = len(text.split())
        length_compliance = {
            "word_count": word_count,
            "min_required": min_words,
            "max_allowed": max_words,
            "is_compliant": min_words <= word_count <= max_words
        }

        # 3. 标签检查
        allowed_tags = rules.get("allowed_tags", [])
        # 这里应该有一个提取文章标签的逻辑，简化示例直接使用空列表
        article_tags = []
        tags_compliance = {
            "article_tags": article_tags,
            "allowed_tags": allowed_tags,
            "invalid_tags": [tag for tag in article_tags if tag not in allowed_tags],
            "is_compliant": all(tag in allowed_tags for tag in article_tags) if allowed_tags else True
        }

        # 合并结果
        compliance_result = {
            "sensitive_content": sensitive_result,
            "length_compliance": length_compliance,
            "tags_compliance": tags_compliance,
            "overall_compliance": (
                length_compliance["is_compliant"] and
                tags_compliance["is_compliant"] and
                len(sensitive_result.get("sensitive_words", [])) == 0
            ),
            "risk_level": self._determine_risk_level(sensitive_result, length_compliance, tags_compliance)
        }

        logger.info(f"合规性评估完成，风险等级: {compliance_result['risk_level']}")
        return compliance_result

    @tool("审核报告生成")
    def generate_review_report(self,
                              plagiarism_result: Dict,
                              ai_detection_result: Dict,
                              sensitive_result: Dict,
                              quality_result: Dict) -> Dict:
        """
        基于各项检测结果生成综合审核报告

        Args:
            plagiarism_result: 原创性检测结果
            ai_detection_result: AI内容检测结果
            sensitive_result: 敏感内容检测结果
            quality_result: 内容质量分析结果

        Returns:
            Dict: 综合审核报告
        """
        logger.info("生成综合审核报告")

        # 计算综合风险等级
        plagiarism_rate = plagiarism_result.get("plagiarism_rate", 0)
        ai_score = ai_detection_result.get("average_score", 0)
        sensitive_count = len(sensitive_result.get("sensitive_words", []))
        quality_score = quality_result.get("overall_score", 0)

        # 确定审核判断
        approval_status = "approved"
        if plagiarism_rate > 0.3 or sensitive_count > 0:
            approval_status = "rejected"
        elif plagiarism_rate > 0.15 or ai_score > 0.8 or quality_score < 0.6:
            approval_status = "needs_revision"

        # 风险等级
        risk_level = "low"
        if plagiarism_rate > 0.3 or sensitive_count > 5:
            risk_level = "high"
        elif plagiarism_rate > 0.15 or ai_score > 0.8 or sensitive_count > 0:
            risk_level = "medium"

        # 生成具体建议
        improvement_suggestions = []

        if plagiarism_rate > 0.15:
            improvement_suggestions.append({
                "aspect": "原创性",
                "issue": f"查重率达到{plagiarism_rate*100:.1f}%，超过建议水平",
                "suggestion": "增加原创内容，正确引用外部资料，避免直接复制"
            })

        if ai_score > 0.7:
            improvement_suggestions.append({
                "aspect": "AI生成内容",
                "issue": f"AI内容检测得分为{ai_score:.2f}，显示有明显AI特征",
                "suggestion": "增加个人见解和经验，调整句式结构，使内容更加人性化"
            })

        if sensitive_count > 0:
            improvement_suggestions.append({
                "aspect": "敏感内容",
                "issue": f"发现{sensitive_count}个敏感词或表述",
                "suggestion": "修改或删除敏感内容，确保符合平台规范和法律要求"
            })

        if quality_score < 0.7:
            improvement_suggestions.append({
                "aspect": "内容质量",
                "issue": f"内容质量评分为{quality_score:.2f}，低于期望水平",
                "suggestion": "提高内容深度，增加专业观点，完善论据支持"
            })

        # 汇总报告
        report = {
            "approval_status": approval_status,
            "risk_level": risk_level,
            "plagiarism_rate": plagiarism_rate,
            "ai_score": ai_score,
            "sensitive_content_count": sensitive_count,
            "quality_score": quality_score,
            "improvement_suggestions": improvement_suggestions,
            "platform_compliance": self._check_platform_compliance(
                plagiarism_rate,
                ai_score,
                sensitive_count,
                quality_score
            ),
            "review_timestamp": "current_timestamp",
            "revision_required": approval_status != "approved"
        }

        logger.info(f"审核报告生成完成，审核结果: {approval_status}")
        return report

    def _determine_risk_level(self, sensitive_result, length_compliance, tags_compliance) -> str:
        """内部方法：根据检测结果确定风险等级"""
        sensitive_count = len(sensitive_result.get("sensitive_words", []))

        if sensitive_count > 5 or not length_compliance["is_compliant"]:
            return "high"
        elif sensitive_count > 0 or not tags_compliance["is_compliant"]:
            return "medium"
        else:
            return "low"

    def _check_platform_compliance(self, plagiarism_rate, ai_score, sensitive_count, quality_score) -> Dict:
        """内部方法：检查平台特定合规性"""
        # 不同平台可能有不同规则
        platform_rules = {
            "zhihu": {
                "max_plagiarism": 0.2,
                "max_ai_score": 0.85,
                "allow_sensitive": False
            },
            "juejin": {
                "max_plagiarism": 0.25,
                "max_ai_score": 0.9,
                "allow_sensitive": False
            },
            "wechat": {
                "max_plagiarism": 0.15,
                "max_ai_score": 0.8,
                "allow_sensitive": False
            }
        }

        # 获取当前平台规则，默认使用最严格标准
        platform_name = self.platform.name.lower()
        rules = platform_rules.get(platform_name, {
            "max_plagiarism": 0.15,
            "max_ai_score": 0.8,
            "allow_sensitive": False
        })

        # 检查合规情况
        is_compliant = (
            plagiarism_rate <= rules["max_plagiarism"] and
            ai_score <= rules["max_ai_score"] and
            (sensitive_count == 0 or rules["allow_sensitive"])
        )

        return {
            "platform": self.platform.name,
            "is_compliant": is_compliant,
            "rules": rules,
            "violations": [
                f"查重率超过限制" if plagiarism_rate > rules["max_plagiarism"] else None,
                f"AI特征超过限制" if ai_score > rules["max_ai_score"] else None,
                f"包含敏感内容" if sensitive_count > 0 and not rules["allow_sensitive"] else None
            ]
        }
