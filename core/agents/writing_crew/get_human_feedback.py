"""人工反馈模块

提供从人类编辑获取文章评审反馈的功能。
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from .writing_crew import WritingResult

# 配置日志
logger = logging.getLogger(__name__)

def get_human_feedback(writing_result: WritingResult) -> WritingResult:
    """获取人工反馈

    提供交互式界面让人类编辑者评审文章并提供反馈。

    Args:
        writing_result: 写作过程的结果对象

    Returns:
        WritingResult: 包含人工反馈的更新结果对象
    """
    logger.info(f"开始收集人工反馈，文章: {writing_result.article.title}")

    try:
        print("\n" + "="*50)
        print(f" 文章评审: {writing_result.article.title} ".center(50, "="))
        print("="*50 + "\n")

        # 显示文章的基本信息
        if writing_result.final_draft and "title" in writing_result.final_draft:
            print(f"标题: {writing_result.final_draft['title']}")
        else:
            print(f"标题: {writing_result.article.title}")

        if writing_result.final_draft and "summary" in writing_result.final_draft:
            print(f"\n摘要: {writing_result.final_draft['summary']}\n")

        # 收集评分反馈
        print("\n" + "-"*50)
        print(" 评分标准 ".center(50, "-"))
        print("-"*50)

        print("\n1. 内容质量 (0-10分):")
        print("   - 专业性和准确性")
        print("   - 内容深度和广度")
        print("   - 表达清晰度")
        print("   - 例子和证据的有效性")

        while True:
            try:
                content_score = float(input("\n请评分 (0-10): "))
                if 0 <= content_score <= 10:
                    break
                print("评分必须在0到10之间，请重新输入")
            except ValueError:
                print("请输入有效的数字")

        print("\n2. 结构设计 (0-10分):")
        print("   - 逻辑流畅性")
        print("   - 段落组织")
        print("   - 引言和结论的有效性")
        print("   - 标题和小标题的质量")

        while True:
            try:
                structure_score = float(input("\n请评分 (0-10): "))
                if 0 <= structure_score <= 10:
                    break
                print("评分必须在0到10之间，请重新输入")
            except ValueError:
                print("请输入有效的数字")

        print("\n3. SEO表现 (0-10分):")
        print("   - 关键词使用")
        print("   - 标题优化")

        while True:
            try:
                seo_score = float(input("\n请评分 (0-10): "))
                if 0 <= seo_score <= 10:
                    break
                print("评分必须在0到10之间，请重新输入")
            except ValueError:
                print("请输入有效的数字")

        print("\n4. 整体风格 (0-10分):")
        print("   - 与平台风格的匹配度")
        print("   - 语言风格的一致性")
        print("   - 读者参与度")
        print("   - 视觉元素使用")

        while True:
            try:
                style_score = float(input("\n请评分 (0-10): "))
                if 0 <= style_score <= 10:
                    break
                print("评分必须在0到10之间，请重新输入")
            except ValueError:
                print("请输入有效的数字")

        # 收集具体反馈和改进建议
        print("\n" + "-"*50)
        print(" 详细反馈 ".center(50, "-"))
        print("-"*50)

        strengths = input("\n文章优点: ")
        weaknesses = input("\n需要改进的地方: ")
        suggestions = input("\n具体改进建议: ")

        # 是否需要修改
        print("\n" + "-"*50)
        need_revision = input("\n是否需要修改 (y/n): ").lower().strip() == 'y'

        # 计算平均分和归一化分数
        scores = [content_score, structure_score, seo_score, style_score]
        avg_score = sum(scores) / len(scores)
        normalized_score = avg_score / 10.0  # 转换为0-1范围

        # 更新反馈
        writing_result.human_feedback = {
            "scores": {
                "content": content_score,
                "structure": structure_score,
                "seo": seo_score,
                "style": style_score
            },
            "normalized_scores": {
                "content": content_score / 10.0,
                "structure": structure_score / 10.0,
                "seo": seo_score / 10.0,
                "style": style_score / 10.0
            },
            "average_score": avg_score,
            "normalized_average_score": normalized_score,
            "feedback": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "suggestions": suggestions
            },
            "needs_revision": need_revision,
            "reviewed_at": datetime.now().isoformat()
        }

        logger.info(f"人工反馈收集完成，平均分: {avg_score:.1f}/10")
        return writing_result

    except Exception as e:
        logger.error(f"收集人工反馈时发生错误: {str(e)}", exc_info=True)
        # 如果反馈收集过程出错，创建一个最小的反馈对象
        writing_result.human_feedback = {
            "error": str(e),
            "reviewed_at": datetime.now().isoformat()
        }
        return writing_result
