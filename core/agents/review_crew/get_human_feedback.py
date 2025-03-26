"""人工反馈模块

提供从人类编辑获取文章审核反馈的功能。
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from .review_crew import ReviewResult

# 配置日志
logger = logging.getLogger(__name__)

def get_human_feedback(review_result: ReviewResult) -> ReviewResult:
    """获取人工反馈

    提供交互式界面让人类编辑者评估审核报告并提供反馈。

    Args:
        review_result: 审核过程的结果对象

    Returns:
        ReviewResult: 包含人工反馈的更新结果对象
    """
    logger.info(f"开始收集人工反馈，文章: {review_result.article.title}")

    try:
        print("\n" + "="*50)
        print(f" 审核报告评估: {review_result.article.title} ".center(50, "="))
        print("="*50 + "\n")

        # 收集评分反馈
        print("\n1. 查重报告质量 (0-10分):")
        print("   - 问题定位准确性")
        print("   - 分析深度")
        print("   - 建议可行性")

        while True:
            try:
                plagiarism_score = float(input("\n请评分 (0-10): "))
                if 0 <= plagiarism_score <= 10:
                    break
                print("评分必须在0到10之间，请重新输入")
            except ValueError:
                print("请输入有效的数字")

        print("\n2. AI检测报告质量 (0-10分):")
        print("   - 特征识别准确性")
        print("   - 结论可靠性")
        print("   - 建议针对性")

        while True:
            try:
                ai_score = float(input("\n请评分 (0-10): "))
                if 0 <= ai_score <= 10:
                    break
                print("评分必须在0到10之间，请重新输入")
            except ValueError:
                print("请输入有效的数字")

        print("\n3. 内容审核报告质量 (0-10分):")
        print("   - 敏感内容识别")
        print("   - 合规评估准确性")
        print("   - 风险预判")

        while True:
            try:
                content_score = float(input("\n请评分 (0-10): "))
                if 0 <= content_score <= 10:
                    break
                print("评分必须在0到10之间，请重新输入")
            except ValueError:
                print("请输入有效的数字")

        print("\n4. 质量评估报告 (0-10分):")
        print("   - 评估全面性")
        print("   - 分析深度")
        print("   - 建议实用性")

        while True:
            try:
                quality_score = float(input("\n请评分 (0-10): "))
                if 0 <= quality_score <= 10:
                    break
                print("评分必须在0到10之间，请重新输入")
            except ValueError:
                print("请输入有效的数字")

        print("\n5. 终审报告质量 (0-10分):")
        print("   - 综合分析能力")
        print("   - 决策合理性")
        print("   - 改进指导价值")

        while True:
            try:
                final_score = float(input("\n请评分 (0-10): "))
                if 0 <= final_score <= 10:
                    break
                print("评分必须在0到10之间，请重新输入")
            except ValueError:
                print("请输入有效的数字")

        # 收集总体反馈
        print("\n" + "-"*50)
        print(" 总体评价 ".center(50, "-"))
        print("-"*50)

        strengths = input("\n审核报告优点: ")
        weaknesses = input("\n需要改进的地方: ")
        suggestions = input("\n对审核流程的建议: ")

        # 是否同意最终结论
        print("\n" + "-"*50)
        agree_with_conclusion = input("\n是否同意最终审核结论 (y/n): ").lower().strip() == 'y'

        # 计算平均分和归一化分数
        scores = [plagiarism_score, ai_score, content_score, quality_score, final_score]
        avg_score = sum(scores) / len(scores)
        normalized_score = avg_score / 10.0  # 转换为0-1范围

        # 更新反馈
        review_result.human_feedback = {
            "scores": {
                "plagiarism_report": plagiarism_score,
                "ai_detection_report": ai_score,
                "content_review_report": content_score,
                "quality_assessment": quality_score,
                "final_review": final_score
            },
            "normalized_scores": {
                "plagiarism_report": plagiarism_score / 10.0,
                "ai_detection_report": ai_score / 10.0,
                "content_review_report": content_score / 10.0,
                "quality_assessment": quality_score / 10.0,
                "final_review": final_score / 10.0
            },
            "average_score": avg_score,
            "normalized_average_score": normalized_score,
            "feedback": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "suggestions": suggestions
            },
            "agree_with_conclusion": agree_with_conclusion,
            "reviewed_at": datetime.now().isoformat()
        }

        logger.info(f"人工反馈收集完成，平均分: {avg_score:.1f}/10")
        return review_result

    except Exception as e:
        logger.error(f"收集人工反馈时发生错误: {str(e)}", exc_info=True)
        # 如果反馈收集过程出错，创建一个最小的反馈对象
        review_result.human_feedback = {
            "error": str(e),
            "reviewed_at": datetime.now().isoformat()
        }
        return review_result
