"""写作团队工作流模块

实现了基于CrewAI的文章写作工作流，整合各种智能体协同工作。
"""
import os
import sys
import json
import logging
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

from crewai import Task, Crew, Process
from crewai.agent import Agent

from core.models.article import Article, Section
from core.models.platform import Platform
from .writing_agents import WritingAgents

# 配置日志
logger = logging.getLogger(__name__)

class WritingResult:
    """写作结果类

    存储写作流程的各个阶段结果，包括大纲、内容、SEO优化和最终稿件。
    """
    def __init__(
        self,
        article: Article,
        outline: Optional[Dict] = None,
        content: Optional[Dict] = None,
        seo_data: Optional[Dict] = None,
        final_draft: Optional[Dict] = None
    ):
        self.article = article
        self.outline = outline or {}
        self.content = content or {}
        self.seo_data = seo_data or {}
        self.final_draft = final_draft or {}
        self.created_at = datetime.now()
        self.human_feedback: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """将结果转换为字典格式"""
        return {
            "article_id": self.article.id,
            "title": self.article.title,
            "outline": self.outline,
            "content": self.content,
            "seo_data": self.seo_data,
            "final_draft": self.final_draft,
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
            filename = f"article_{self.article.id}_{timestamp}.json"

        # 确保output目录存在
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        file_path = output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

        logger.info(f"写作结果已保存到: {file_path}")
        return str(file_path)

class WritingCrew:
    """写作团队

    管理文章写作的整个流程，包括大纲设计、内容创作、SEO优化和编辑。
    采用CrewAI框架实现智能体协作。
    """

    def __init__(self, verbose: bool = True):
        """初始化写作团队

        Args:
            verbose: 是否启用详细日志输出
        """
        logger.info("初始化写作团队")
        self.verbose = verbose

        # 智能体和任务将在执行时初始化
        self.agents = None
        self.outline_creator = None
        self.content_writer = None
        self.seo_specialist = None
        self.editor = None
        self.fact_checker = None

        logger.info("写作团队初始化完成")

    async def write_article(self, article: Article, platform: Platform) -> WritingResult:
        """实现文章写作流程

        组织智能体团队，执行从大纲设计到最终编辑的完整文章写作流程。

        Args:
            article: 文章信息对象，包含标题、主题和初始内容
            platform: 目标发布平台，决定了内容风格和要求

        Returns:
            WritingResult: 完整的写作过程结果
        """
        logger.info(f"开始文章写作流程: {article.title}, 目标平台: {platform.name}")

        try:
            # 初始化写作智能体团队
            self.agents = WritingAgents(platform)

            # 创建所有需要的智能体
            self.outline_creator = self.agents.create_outline_creator(self.verbose)
            self.content_writer = self.agents.create_content_writer(self.verbose)
            self.seo_specialist = self.agents.create_seo_specialist(self.verbose)
            self.editor = self.agents.create_editor(self.verbose)
            self.fact_checker = self.agents.create_fact_checker(self.verbose)

            logger.info("所有智能体创建完成，开始定义任务")

            # 1. 大纲设计任务
            outline_task = Task(
                description=f"""为文章"{article.title}"创建一个引人入胜且结构合理的大纲。

任务要求:
1. 分析文章主题并确定目标受众
2. 根据平台"{platform.name}"的要求设计合适的文章结构
3. 创建引人注目的标题和副标题
4. 设计引人入胜的开头和有力的结尾
5. 确保大纲逻辑流畅，各部分衔接自然
6. 考虑内容的可读性和信息价值

输出格式:
以JSON格式提供大纲，包含标题、引言、主要章节（每个都有标题和要点）、结论。""",
                expected_output="包含完整文章结构的JSON格式大纲",
                agent=self.outline_creator
            )

            # 2. 内容创作任务
            content_task = Task(
                description=f"""根据提供的大纲，创作专业、生动且信息丰富的文章内容。

任务要求:
1. 根据大纲创作完整的文章内容
2. 确保内容专业准确，观点清晰
3. 使用生动的案例和具体例子支持论点
4. 加入适当的过渡，确保内容流畅
5. 注意文章的节奏感和可读性
6. 确保内容符合平台"{platform.name}"的风格和要求

输出格式:
提供完整的文章内容，包括标题、引言、正文各部分和结论。使用JSON格式。""",
                expected_output="完整的文章内容JSON",
                agent=self.content_writer,
                context=[outline_task]  # 使用大纲任务的结果作为上下文
            )

            # 3. SEO优化任务
            seo_task = Task(
                description=f"""对文章进行SEO优化，提高其在搜索引擎中的可见性。

任务要求:
1. 分析文章内容和目标关键词
2. 优化标题、副标题和元描述
3. 提出关键词密度和分布的改进建议
4. 建议内部链接和外部链接策略
5. 确保SEO优化不影响内容质量和可读性
6. 提供符合平台"{platform.name}"要求的SEO建议

输出格式:
返回JSON格式的SEO分析和优化建议，包括优化后的标题、元描述和关键词分析。""",
                expected_output="SEO优化建议和分析报告JSON",
                agent=self.seo_specialist,
                context=[content_task]  # 使用内容任务的结果作为上下文
            )

            # 4. 事实核查任务
            fact_check_task = Task(
                description=f"""检查文章中的事实、数据和引用，确保准确性。

任务要求:
1. 仔细检查文章中的所有事实性陈述和数据
2. 验证引用和来源的可靠性
3. 标记任何可疑或需要进一步验证的信息
4. 提供修正建议和更准确的信息
5. 确保文章内容不含误导性陈述或过时信息

输出格式:
返回JSON格式的事实核查报告，包括发现的问题、修正建议和验证结果。""",
                expected_output="事实核查报告JSON",
                agent=self.fact_checker,
                context=[content_task]  # 使用内容任务的结果作为上下文
            )

            # 5. 编辑优化任务
            edit_task = Task(
                description=f"""对文章进行全面编辑和质量提升。

任务要求:
1. 基于SEO优化和事实核查的结果，审查和编辑文章
2. 优化语言表达，确保清晰流畅
3. 检查并修正语法、标点和拼写错误
4. 确保内容结构逻辑，段落衔接自然
5. 优化标题和小标题的吸引力
6. 根据平台"{platform.name}"的要求调整格式和风格
7. 确保最终内容的整体质量和专业性

输出格式:
提供JSON格式的最终文章稿件，包括标题、摘要、正文和任何特殊格式要求。""",
                expected_output="最终编辑完成的文章JSON",
                agent=self.editor,
                context=[content_task, seo_task, fact_check_task]  # 使用前面任务的结果作为上下文
            )

            # 创建工作流
            logger.info("任务定义完成，创建工作流")
            crew = Crew(
                agents=[
                    self.outline_creator,
                    self.content_writer,
                    self.seo_specialist,
                    self.fact_checker,
                    self.editor
                ],
                tasks=[
                    outline_task,
                    content_task,
                    seo_task,
                    fact_check_task,
                    edit_task
                ],
                process=Process.sequential,  # 按顺序执行任务
                verbose=self.verbose
            )

            # 执行工作流
            logger.info("开始执行写作工作流")
            result = crew.kickoff()
            logger.info("写作工作流执行完成")

            # 整理写作结果
            writing_result = WritingResult(
                article=article,
                outline=result.get("outline_task"),
                content=result.get("content_task"),
                seo_data=result.get("seo_task"),
                final_draft=result.get("edit_task")
            )

            logger.info(f"写作结果已整理，文章: {article.title}")
            return writing_result

        except Exception as e:
            logger.error(f"写作过程发生错误: {str(e)}", exc_info=True)
            # 返回部分结果，如果有的话
            return WritingResult(article=article)

    def get_human_feedback(self, writing_result: WritingResult) -> WritingResult:
        """获取人工反馈

        Args:
            writing_result: 写作结果

        Returns:
            WritingResult: 更新后的写作结果
        """
        print("\n=== 文章评审 ===\n")
        print(f"标题: {writing_result.article.title}")

        print("\n1. 内容质量 (0-1):")
        print("- 专业性")
        print("- 可读性")
        print("- 完整性")
        content_score = float(input("请评分: "))

        print("\n2. 结构设计 (0-1):")
        print("- 逻辑性")
        print("- 层次感")
        print("- 过渡自然")
        structure_score = float(input("请评分: "))

        print("\n3. SEO表现 (0-1):")
        print("- 关键词优化")
        print("- 标题吸引力")
        print("- 元描述质量")
        seo_score = float(input("请评分: "))

        print("\n4. 修改建议:")
        comments = input("评审意见: ")

        # 更新反馈
        writing_result.human_feedback = {
            "content_score": content_score,
            "structure_score": structure_score,
            "seo_score": seo_score,
            "average_score": (content_score + structure_score + seo_score) / 3,
            "comments": comments,
            "reviewed_at": datetime.now()
        }

        return writing_result

    def update_article(self, writing_result: WritingResult) -> Article:
        """更新文章

        Args:
            writing_result: 写作结果

        Returns:
            Article: 更新后的文章
        """
        # 从最终稿中提取信息
        final_draft = writing_result.final_draft

        # 更新文章
        article = writing_result.article
        article.title = final_draft["title"]
        article.summary = final_draft["summary"]
        article.sections = [
            Section(
                title=section["title"],
                content=section["content"],
                order=idx + 1
            )
            for idx, section in enumerate(final_draft["sections"])
        ]
        article.seo_data = writing_result.seo_data
        article.status = "reviewed"

        return article

# 使用示例
async def main():
    """示例运行函数"""
    import json
    from pathlib import Path

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger.info("启动写作团队示例")

    # 创建一个示例文章
    article = Article(
        id="article_001",
        topic_id="topic_001",
        title="Python异步编程最佳实践",
        summary="探讨Python异步编程的发展、应用场景和最佳实践",
        sections=[
            Section(
                title="异步编程简介",
                content="异步编程是一种编程范式，允许程序在等待I/O操作完成时执行其他任务。",
                order=1
            )
        ],
        status="draft"
    )

    # 创建一个示例平台
    platform = Platform(
        id="platform_001",
        name="掘金",
        url="https://juejin.cn",
        content_rules={
            "min_words": 1000,
            "max_words": 5000,
            "allowed_tags": ["Python", "编程", "技术"]
        }
    )

    try:
        # 创建写作团队
        crew = WritingCrew(verbose=True)
        logger.info("写作团队已创建")

        # 进行写作
        logger.info("开始写作流程")
        writing_result = await crew.write_article(article, platform)

        # 保存原始结果
        result_path = writing_result.save_to_file()
        logger.info(f"原始写作结果已保存到: {result_path}")

        # 获取人工反馈
        writing_result = crew.get_human_feedback(writing_result)

        # 更新并保存最终结果
        if writing_result.human_feedback and writing_result.human_feedback.get("normalized_average_score", 0) >= 0.7:
            logger.info("评分达标，更新文章")
            article = crew.update_article(writing_result)

            # 保存最终文章
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            article_path = output_dir / f"article_{article.id}_final.json"
            with open(article_path, "w", encoding="utf-8") as f:
                # 将文章对象转换为字典
                article_dict = {
                    "id": article.id,
                    "title": article.title,
                    "summary": article.summary,
                    "sections": [
                        {"title": s.title, "content": s.content, "order": s.order}
                        for s in article.sections
                    ],
                    "status": article.status,
                    "metadata": article.metadata
                }
                json.dump(article_dict, f, ensure_ascii=False, indent=2)

            logger.info(f"最终文章已保存到: {article_path}")

            # 打印文章摘要
            print("\n" + "="*50)
            print(" 更新后的文章 ".center(50, "="))
            print("="*50)
            print(f"\n标题: {article.title}")
            print(f"\n摘要: {article.summary}")
            print("\n章节:")
            for section in article.sections:
                print(f"\n{section.order}. {section.title}")
                print(f"  {section.content[:100]}..." if len(section.content) > 100 else section.content)
        else:
            logger.info("评分未达标，需要修改")

    except Exception as e:
        logger.error(f"运行示例时发生错误: {str(e)}", exc_info=True)

def run_example():
    """命令行入口点"""
    asyncio.run(main())

if __name__ == "__main__":
    run_example()
