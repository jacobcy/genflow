"""审核团队工作流模块

实现了基于CrewAI的文章审核工作流，整合各种智能体协同工作。
"""
import os
import json
import logging
import traceback
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

from crewai import Task, Crew, Process
from crewai.agent import Agent

from core.models.article import Article
from core.models.platform import Platform
from .review_agents import ReviewAgents

# 配置日志
logger = logging.getLogger(__name__)

class ReviewResult:
    """审核结果类
    
    存储审核流程的各个阶段结果，包括查重、AI检测、内容合规性和最终审核。
    """
    def __init__(
        self,
        article: Article,
        plagiarism_report: Optional[Dict] = None,
        ai_detection_report: Optional[Dict] = None,
        content_review_report: Optional[Dict] = None,
        quality_assessment: Optional[Dict] = None,
        final_review: Optional[Dict] = None
    ):
        self.article = article
        self.plagiarism_report = plagiarism_report or {}
        self.ai_detection_report = ai_detection_report or {}
        self.content_review_report = content_review_report or {}
        self.quality_assessment = quality_assessment or {}
        self.final_review = final_review or {}
        self.created_at = datetime.now()
        self.human_feedback: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """将结果转换为字典格式"""
        return {
            "article_id": self.article.id,
            "title": self.article.title,
            "plagiarism_report": self.plagiarism_report,
            "ai_detection_report": self.ai_detection_report,
            "content_review_report": self.content_review_report,
            "quality_assessment": self.quality_assessment,
            "final_review": self.final_review,
            "created_at": self.created_at.isoformat(),
            "human_feedback": self.human_feedback
        }
    
    def save_to_file(self, filename: Optional[str] = None) -> str:
        """保存结果到文件
        
        Args:
            filename: 保存的文件名，默认使用文章ID和时间戳
            
        Returns:
            str: 保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"review_{self.article.id}_{timestamp}.json"
        
        # 确保output目录存在
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        file_path = output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"审核结果已保存到: {file_path}")
        return str(file_path)

class ReviewCrew:
    """审核团队
    
    管理文章审核的整个流程，包括原创性检测、AI内容识别、合规性审核和质量评估。
    采用CrewAI框架实现智能体协作。
    """

    def __init__(self, verbose: bool = True):
        """初始化审核团队
        
        Args:
            verbose: 是否启用详细日志输出
        """
        logger.info("初始化审核团队")
        self.verbose = verbose
        
        # 智能体和任务将在执行时初始化
        self.agents = None
        self.plagiarism_checker = None
        self.ai_detector = None
        self.content_reviewer = None
        self.quality_assessor = None
        self.final_reviewer = None
        
        logger.info("审核团队初始化完成")

    async def review_article(self, article: Article, platform: Platform) -> ReviewResult:
        """实现文章审核流程
        
        组织智能体团队，执行从原创性检测到最终审核的完整文章审核流程。

        Args:
            article: 文章信息对象，包含标题和内容
            platform: 目标发布平台，决定了内容规范和要求

        Returns:
            ReviewResult: 完整的审核过程结果
        """
        logger.info(f"开始文章审核流程: {article.title}, 目标平台: {platform.name}")
        
        try:
            # 初始化审核智能体团队
            self.agents = ReviewAgents(platform)
            
            # 创建所有需要的智能体
            self.plagiarism_checker = self.agents.create_plagiarism_checker(self.verbose)
            self.ai_detector = self.agents.create_ai_detector(self.verbose)
            self.content_reviewer = self.agents.create_content_reviewer(self.verbose)
            self.quality_assessor = self.agents.create_quality_assessor(self.verbose)
            self.final_reviewer = self.agents.create_final_reviewer(self.verbose)
            
            logger.info("所有智能体创建完成，开始定义任务")
            
            # 获取文章全文
            article_text = self._get_article_text(article)
            
            # 1. 查重任务
            plagiarism_task = Task(
                description=f"""对文章"{article.title}"进行原创性检测。

任务要求:
1. 检查文章全文的原创性，识别可能的抄袭或过度引用
2. 分析重复内容的来源和性质
3. 检查引用规范是否符合学术或出版标准
4. 评估文章的整体原创度
5. 对存在问题的部分提供具体的修改建议

输入:
"{article_text[:500]}..."（文章开头部分，完整内容请使用工具查看）

输出格式:
以JSON格式提供查重报告，包含查重率、重复内容列表、引用规范性评估和修改建议。""",
                expected_output="包含详细原创性分析的JSON格式查重报告",
                agent=self.plagiarism_checker,
                context=[{"role": "input", "content": f"article_title: {article.title}"}]
            )

            # 2. AI检测任务
            ai_detection_task = Task(
                description=f"""检测文章"{article.title}"是否由AI生成。

任务要求:
1. 分析文章的语言特征，识别可能的AI生成痕迹
2. 评估文章的表达多样性和语言自然度
3. 检查内容的逻辑一致性和专业准确性
4. 分析是否存在典型的AI生成文本特征
5. 考虑平台"{platform.name}"的AI内容政策，给出合规建议

输入:
"{article_text[:500]}..."（文章开头部分，完整内容请使用工具查看）

输出格式:
以JSON格式提供AI检测报告，包含AI生成可能性评分、关键特征分析、合规性评估和优化建议。""",
                expected_output="包含详细AI内容分析的JSON格式检测报告",
                agent=self.ai_detector,
                context=[{"role": "input", "content": f"article_title: {article.title}"}]
            )

            # 3. 内容审核任务
            content_review_task = Task(
                description=f"""审核文章"{article.title}"的内容合规性。

任务要求:
1. 检查内容是否包含敏感词或违规信息
2. 评估内容的价值导向和舆论倾向
3. 审核表述方式是否适当
4. 确认内容符合平台"{platform.name}"的规范和法律要求
5. 对潜在风险内容提供修改建议

输入:
"{article_text[:500]}..."（文章开头部分，完整内容请使用工具查看）

输出格式:
以JSON格式提供内容审核报告，包含敏感内容列表、合规性评估、风险等级和整改建议。""",
                expected_output="包含详细合规性分析的JSON格式审核报告",
                agent=self.content_reviewer,
                context=[{"role": "input", "content": f"article_title: {article.title}"}]
            )

            # 4. 质量评估任务
            quality_assessment_task = Task(
                description=f"""评估文章"{article.title}"的整体质量。

任务要求:
1. 评估内容的专业深度和准确性
2. 分析文章结构的合理性和逻辑性
3. 审查语言表达的清晰度和专业性
4. 评价内容的信息价值和实用性
5. 考虑平台"{platform.name}"的内容偏好，给出提升建议

输入:
"{article_text[:500]}..."（文章开头部分，完整内容请使用工具查看）

输出格式:
以JSON格式提供质量评估报告，包含各维度评分、优缺点分析和提升建议。""",
                expected_output="包含详细质量分析的JSON格式评估报告",
                agent=self.quality_assessor,
                context=[{"role": "input", "content": f"article_title: {article.title}"}]
            )

            # 5. 终审任务
            final_review_task = Task(
                description=f"""对文章"{article.title}"进行最终审核决策。

任务要求:
1. 综合分析所有前序审核报告
2. 评估文章的整体发布风险和价值
3. 权衡内容质量与合规要求
4. 做出最终的审核决定（通过、需修改或拒绝）
5. 提供详细的修改指导（如需要）

输入:
前序审核结果将作为上下文提供。

输出格式:
以JSON格式提供最终审核决定，包含审核结果、风险等级、关键问题汇总和修改建议。""",
                expected_output="包含最终审核决定的JSON格式报告",
                agent=self.final_reviewer,
                context=[
                    plagiarism_task,
                    ai_detection_task,
                    content_review_task,
                    quality_assessment_task
                ]
            )

            # 创建工作流
            logger.info("任务定义完成，创建工作流")
            crew = Crew(
                agents=[
                    self.plagiarism_checker,
                    self.ai_detector,
                    self.content_reviewer,
                    self.quality_assessor,
                    self.final_reviewer
                ],
                tasks=[
                    plagiarism_task,
                    ai_detection_task,
                    content_review_task,
                    quality_assessment_task,
                    final_review_task
                ],
                process=Process.sequential,  # 按顺序执行任务
                verbose=self.verbose
            )

            # 执行工作流
            logger.info("开始执行审核工作流")
            result = crew.kickoff()
            logger.info("审核工作流执行完成")

            # 整理审核结果
            review_result = ReviewResult(
                article=article,
                plagiarism_report=self._parse_json_result(result.get("plagiarism_task")),
                ai_detection_report=self._parse_json_result(result.get("ai_detection_task")),
                content_review_report=self._parse_json_result(result.get("content_review_task")),
                quality_assessment=self._parse_json_result(result.get("quality_assessment_task")),
                final_review=self._parse_json_result(result.get("final_review_task"))
            )
            
            logger.info(f"审核结果已整理，文章: {article.title}")
            return review_result
            
        except Exception as e:
            logger.error(f"审核过程发生错误: {str(e)}")
            logger.debug(traceback.format_exc())
            # 返回部分结果，如果有的话
            return ReviewResult(article=article)

    def get_human_feedback(self, review_result: ReviewResult) -> ReviewResult:
        """获取人工反馈
        
        Args:
            review_result: 审核结果
            
        Returns:
            ReviewResult: 更新后的审核结果
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
            logger.error(f"收集人工反馈时发生错误: {str(e)}")
            logger.debug(traceback.format_exc())
            # 如果反馈收集过程出错，创建一个最小的反馈对象
            review_result.human_feedback = {
                "error": str(e),
                "reviewed_at": datetime.now().isoformat()
            }
            return review_result

    def update_article_status(self, review_result: ReviewResult) -> Article:
        """更新文章状态
        
        根据审核结果更新文章的状态和元数据，包括审核信息。
        
        Args:
            review_result: 审核结果
            
        Returns:
            Article: 更新后的文章
        """
        logger.info(f"更新文章状态：{review_result.article.title}")
        
        # 获取最终审核结果
        final_review = review_result.final_review
        
        # 提取关键信息
        approval_status = final_review.get("approval_status", "needs_revision")
        risk_level = final_review.get("risk_level", "medium")
        plagiarism_rate = final_review.get("plagiarism_rate", 0)
        ai_score = final_review.get("ai_score", 0)
        
        # 人工反馈可能覆盖自动判断
        if review_result.human_feedback and not review_result.human_feedback.get("agree_with_conclusion", True):
            logger.info("人工反馈覆盖自动审核结果")
            # 如果人工不同意自动结论，使用更保守的状态
            approval_status = "needs_revision"
        
        # 更新文章
        article = review_result.article
        article.review_data = {
            "plagiarism_rate": plagiarism_rate,
            "ai_score": ai_score,
            "risk_level": risk_level,
            "review_comments": final_review.get("improvement_suggestions", []),
            "reviewed_at": datetime.now().isoformat()
        }
        
        # 更新状态
        if approval_status == "approved":
            article.status = "approved"
        elif approval_status == "needs_revision":
            article.status = "needs_revision"
        else:
            article.status = "rejected"
        
        logger.info(f"文章状态已更新为: {article.status}, 风险等级: {risk_level}")
        return article
    
    def _get_article_text(self, article: Article) -> str:
        """获取文章全文
        
        Args:
            article: 文章对象
            
        Returns:
            str: 文章全文
        """
        # 合并标题、摘要和所有章节内容
        sections_text = ""
        for section in article.sections:
            sections_text += f"\n\n## {section.title}\n\n{section.content}"
        
        full_text = f"# {article.title}\n\n{article.summary}{sections_text}"
        return full_text
    
    def _parse_json_result(self, result: str) -> Dict:
        """解析JSON格式的任务结果
        
        Args:
            result: 任务结果文本
            
        Returns:
            Dict: 解析后的JSON对象
        """
        if not result:
            return {}
        
        try:
            # 尝试提取JSON部分，处理可能的额外文本
            # 先尝试直接解析
            try:
                return json.loads(result)
            except:
                # 查找JSON字符串的开始和结束
                start = result.find('{')
                end = result.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = result[start:end]
                    return json.loads(json_str)
                
                # 还可以尝试查找代码块中的JSON
                import re
                json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
                matches = re.findall(json_pattern, result)
                if matches:
                    for match in matches:
                        try:
                            if match.strip().startswith('{') and match.strip().endswith('}'):
                                return json.loads(match)
                        except:
                            continue
                
                # 所有尝试都失败
                logger.warning(f"无法解析JSON结果: {result[:100]}...")
                return {"raw_result": result}
                
        except Exception as e:
            logger.error(f"解析任务结果失败: {str(e)}")
            logger.debug(f"原始结果: {result[:100]}...")
            return {"error": str(e), "raw_result": result}

# 使用示例
async def main():
    """示例运行函数"""
    import logging
    from datetime import datetime
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建一个示例文章
    article = Article(
        id=f"article_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        topic_id="topic_001",
        title="Python异步编程最佳实践",
        summary="探讨Python异步编程的发展、应用场景和最佳实践",
        sections=[
            Section(
                title="异步编程简介",
                content="异步编程是一种编程范式，允许程序在等待I/O操作完成时执行其他任务。"
                "在Python中，asyncio库提供了实现异步编程的基础设施。"
                "通过使用async/await语法，开发者可以编写高效的异步代码。",
                order=1
            ),
            Section(
                title="异步编程的应用场景",
                content="异步编程特别适合I/O密集型应用，如Web服务器、数据库交互和网络爬虫。"
                "在这些场景中，程序需要等待外部资源响应，异步模式可以显著提高效率。"
                "然而，对于CPU密集型任务，异步编程的优势并不明显。",
                order=2
            )
        ],
        status="pending_review"
    )

    # 创建一个示例平台
    platform = Platform(
        id="platform_001",
        name="掘金",
        url="https://juejin.cn",
        content_rules={
            "min_words": 500,
            "max_words": 8000,
            "allowed_tags": ["Python", "编程", "技术"],
            "sensitive_words": ["违禁词1", "违禁词2"]
        }
    )

    try:
        # 创建审核团队
        crew = ReviewCrew(verbose=True)
        logger.info("审核团队已创建")

        # 进行审核
        logger.info("开始审核流程")
        review_result = await crew.review_article(article, platform)
        
        # 保存原始结果
        result_path = review_result.save_to_file()
        logger.info(f"原始审核结果已保存到: {result_path}")

        # 获取人工反馈
        review_result = crew.get_human_feedback(review_result)
        
        # 保存带反馈的结果
        feedback_path = review_result.save_to_file("review_with_feedback.json")
        logger.info(f"带反馈的审核结果已保存到: {feedback_path}")

        # 更新文章状态
        threshold = 0.7
        if review_result.human_feedback and review_result.human_feedback.get("normalized_average_score", 0) >= threshold:
            logger.info(f"评分达标(>={threshold})，更新文章状态")
            article = crew.update_article_status(review_result)
            
            # 打印更新结果
            print("\n" + "="*50)
            print(" 审核结果 ".center(50, "="))
            print("="*50)
            print(f"\n文章: {article.title}")
            print(f"状态: {article.status}")
            print(f"查重率: {article.review_data.get('plagiarism_rate', 'N/A')}")
            print(f"AI分数: {article.review_data.get('ai_score', 'N/A')}")
            print(f"风险等级: {article.review_data.get('risk_level', 'N/A')}")
            
            # 打印改进建议
            if article.review_data.get("review_comments"):
                print("\n改进建议:")
                for i, suggestion in enumerate(article.review_data.get("review_comments", []), 1):
                    print(f"{i}. {suggestion.get('aspect', '')}: {suggestion.get('suggestion', '')}")
        else:
            logger.info("评分未达标，需要重新审核")
            
    except Exception as e:
        logger.error(f"运行示例时发生错误: {str(e)}")
        logger.debug(traceback.format_exc())

def run_example():
    """命令行入口点"""
    import asyncio
    asyncio.run(main()) 