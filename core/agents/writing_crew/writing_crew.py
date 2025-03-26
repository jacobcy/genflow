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
from core.constants.content_types import (
    get_writing_config,
    DEFAULT_WRITING_CONFIG,
    WRITING_CONFIG
)

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

        # 使用统一的配置
        self.content_type_config = WRITING_CONFIG

        # 默认内容类型配置
        self.default_content_config = DEFAULT_WRITING_CONFIG

        # 当前配置
        self.current_content_config = self.default_content_config.copy()

        logger.info("写作团队初始化完成")

    async def write_article(self, article: Article, platform: Platform, content_type: Optional[str] = None) -> WritingResult:
        """实现文章写作流程

        组织智能体团队，执行从大纲设计到最终编辑的完整文章写作流程。

        Args:
            article: 文章信息对象，包含标题、主题和初始内容
            platform: 目标发布平台，决定了内容风格和要求
            content_type: 内容类型（如"新闻"、"论文"、"快讯"等）

        Returns:
            WritingResult: 完整的写作过程结果
        """
        logger.info(f"开始文章写作流程: {article.title}, 目标平台: {platform.name}, 内容类型: {content_type or '未指定'}")

        # 根据内容类型设置写作配置
        self.current_content_config = get_writing_config(content_type)

        logger.info(f"当前写作配置: {self.current_content_config}")

        # 如果文章元数据中没有content_type，添加它
        if hasattr(article, "metadata") and isinstance(article.metadata, dict):
            article.metadata["content_type"] = content_type
        else:
            article.metadata = {"content_type": content_type}

        # 初始化返回结果
        result = WritingResult(article=article)

        # 延迟初始化智能体，便于多次调用
        if not self.agents:
            self._initialize_agents()

        try:
            # 创建写作任务
            tasks = self._create_writing_tasks(article, platform)

            # 创建与执行写作工作流
            crew = Crew(
                agents=[
                    self.outline_creator,
                    self.content_writer,
                    self.seo_specialist,
                    self.fact_checker,
                    self.editor
                ],
                tasks=tasks,
                verbose=self.verbose,
                process=Process.sequential
            )

            # 执行工作流获取结果
            crew_results = crew.kickoff()

            # 处理结果
            result = self._process_results(crew_results, article)
            logger.info(f"文章写作完成: {article.title}")

            # 更新文章内容
            self._update_article_from_results(article, result)

            return result

        except Exception as e:
            logger.error(f"写作过程发生错误: {str(e)}")
            raise

    def _initialize_agents(self):
        """初始化写作智能体团队"""
        if self.agents:
            return

        # 创建写作智能体管理器
        self.agents = WritingAgents()

        # 初始化各种角色的智能体
        self.outline_creator = self.agents.get_outline_creator()
        self.content_writer = self.agents.get_content_writer()
        self.seo_specialist = self.agents.get_seo_specialist()
        self.fact_checker = self.agents.get_fact_checker()
        self.editor = self.agents.get_editor()

    def _create_writing_tasks(self, article: Article, platform: Platform) -> List[Task]:
        """创建写作工作流任务

        Args:
            article: 文章信息
            platform: 发布平台信息

        Returns:
            List[Task]: 写作任务列表
        """
        tasks = []

        # 1. 创建大纲任务
        outline_task = Task(
            description=f"""
            为文章《{article.title}》创建合适的大纲结构。

            文章主题：{article.topic.name if hasattr(article, 'topic') and article.topic else article.title}
            内容类型：{article.metadata.get('content_type', '未指定')}
            目标平台：{platform.name}
            平台特点：{platform.description}
            写作风格：{self.current_content_config['style']}
            内容结构：{self.current_content_config['structure']}

            请根据文章主题和内容类型，生成一个详细的大纲，包括：
            1. 文章引言方向
            2. 主要段落和小节（至少3-5个关键部分）
            3. 每个部分应包含的要点
            4. 适合的结论方向

            输出格式：JSON对象，包含outline键（大纲数组）和summary键（大纲说明）
            """,
            agent=self.outline_creator,
            expected_output="""
            {
                "outline": [
                    {"title": "引言", "points": ["要点1", "要点2", ...]},
                    {"title": "第一部分", "points": ["要点1", "要点2", ...]},
                    ...
                ],
                "summary": "大纲总体思路和结构说明"
            }
            """
        )
        tasks.append(outline_task)

        # 2. 创建内容写作任务
        content_task = Task(
            description=f"""
            根据提供的大纲，为文章《{article.title}》创建完整内容。

            文章主题：{article.topic.name if hasattr(article, 'topic') and article.topic else article.title}
            内容类型：{article.metadata.get('content_type', '未指定')}
            目标平台：{platform.name}
            字数要求：{self.current_content_config['word_count']}字左右
            写作风格：{self.current_content_config['style']}
            内容深度：{self.current_content_config['depth']}

            大纲：{{outline_task.output}}

            请创建一篇结构完整、内容丰富的文章，确保：
            1. 语言流畅自然，符合指定的写作风格
            2. 深度符合要求，{self.current_content_config['depth']}级内容
            3. 所有关键部分都有充分展开
            4. 总体字数在要求范围内
            5. 适合目标平台的受众

            输出格式：JSON对象，包含sections键（各部分内容）和metadata键（创作说明）
            """,
            agent=self.content_writer,
            expected_output="""
            {
                "sections": [
                    {"title": "部分标题", "content": "部分内容..."},
                    ...
                ],
                "metadata": {
                    "word_count": 1500,
                    "style_notes": "写作风格说明",
                    "target_audience": "目标受众描述"
                }
            }
            """
        )
        tasks.append(content_task)

        # 3. SEO优化任务
        seo_task = Task(
            description=f"""
            为文章《{article.title}》进行SEO优化分析与建议。

            文章主题：{article.topic.name if hasattr(article, 'topic') and article.topic else article.title}
            内容类型：{article.metadata.get('content_type', '未指定')}
            目标平台：{platform.name}
            SEO关注点：{self.current_content_config['seo_focus']}

            文章内容：{{content_task.output}}

            请进行SEO分析并提供优化建议，包括：
            1. 识别主要关键词和长尾关键词
            2. 评估关键词在文章中的分布
            3. 标题和小标题的SEO优化建议
            4. 内容和结构的改进建议
            5. 适合文章的元描述示例

            输出格式：JSON对象，包含keywords、suggestions和meta_description键
            """,
            agent=self.seo_specialist,
            expected_output="""
            {
                "keywords": {
                    "primary": ["关键词1", "关键词2"],
                    "secondary": ["长尾关键词1", "长尾关键词2", ...]
                },
                "suggestions": {
                    "title": "标题优化建议",
                    "headings": "小标题优化建议",
                    "content": "内容优化建议",
                    "structure": "结构优化建议"
                },
                "meta_description": "推荐的元描述"
            }
            """
        )
        tasks.append(seo_task)

        # 4. 事实核查任务
        fact_check_task = Task(
            description=f"""
            对文章《{article.title}》进行事实核查和准确性验证。

            文章内容：{{content_task.output}}

            请仔细审核文章中的事实性内容，特别注意：
            1. 数据和统计信息的准确性
            2. 引用和声明的可信度
            3. 历史事件和时间线的准确性
            4. 技术细节和专业知识的正确性
            5. 可能存在的误导性表述

            请基于内容{self.current_content_config['depth']}级深度要求进行相应级别的事实核查。

            输出格式：JSON对象，包含accuracy_score、issues和suggestions键
            """,
            agent=self.fact_checker,
            expected_output="""
            {
                "accuracy_score": 8.5,
                "issues": [
                    {"type": "数据错误", "description": "...", "correction": "..."},
                    {"type": "误导性表述", "description": "...", "correction": "..."},
                    ...
                ],
                "suggestions": "改进建议"
            }
            """
        )
        tasks.append(fact_check_task)

        # 5. 编辑和完善任务
        edit_task = Task(
            description=f"""
            对文章《{article.title}》进行最终编辑和完善。

            原始内容：{{content_task.output}}
            SEO建议：{{seo_task.output}}
            事实核查：{{fact_check_task.output}}

            内容类型：{article.metadata.get('content_type', '未指定')}
            目标平台：{platform.name}
            字数要求：{self.current_content_config['word_count']}字左右
            写作风格：{self.current_content_config['style']}

            请根据以上信息对文章进行最终编辑：
            1. 整合SEO建议和事实核查结果
            2. 确保文章风格一致，符合{self.current_content_config['style']}的要求
            3. 优化段落和句子结构，提高可读性
            4. 检查并修正语法和拼写错误
            5. 调整文章长度至{self.current_content_config['word_count']}字左右

            输出格式：完整的最终文章内容，JSON格式，包含title、sections和metadata键
            """,
            agent=self.editor,
            expected_output="""
            {
                "title": "最终文章标题",
                "subtitle": "副标题（如有）",
                "sections": [
                    {"title": "部分标题", "content": "部分内容..."},
                    ...
                ],
                "metadata": {
                    "word_count": 1500,
                    "keywords": ["关键词1", "关键词2", ...],
                    "description": "文章描述/摘要"
                }
            }
            """
        )
        tasks.append(edit_task)

        return tasks

    def _process_results(self, crew_results: Any, article: Article) -> WritingResult:
        """处理写作工作流结果

        Args:
            crew_results: CrewAI工作流结果
            article: 原始文章信息

        Returns:
            WritingResult: 处理后的写作结果
        """
        result = WritingResult(article=article)

        try:
            # 解析各个任务的结果
            if isinstance(crew_results, list) and len(crew_results) >= 5:
                result.outline = json.loads(crew_results[0]) if isinstance(crew_results[0], str) else crew_results[0]
                result.content = json.loads(crew_results[1]) if isinstance(crew_results[1], str) else crew_results[1]
                result.seo_data = json.loads(crew_results[2]) if isinstance(crew_results[2], str) else crew_results[2]
                fact_check = json.loads(crew_results[3]) if isinstance(crew_results[3], str) else crew_results[3]
                result.final_draft = json.loads(crew_results[4]) if isinstance(crew_results[4], str) else crew_results[4]

                # 合并事实核查到最终结果
                if isinstance(result.final_draft, dict) and isinstance(fact_check, dict):
                    if "metadata" not in result.final_draft:
                        result.final_draft["metadata"] = {}
                    result.final_draft["metadata"]["fact_check"] = fact_check
        except Exception as e:
            logger.error(f"处理写作结果时出错: {str(e)}")

        return result

    def _update_article_from_results(self, article: Article, result: WritingResult) -> None:
        """根据最终稿件更新文章对象

        Args:
            article: 需要更新的文章对象
            result: 写作结果
        """
        if not result.final_draft:
            logger.warning("缺少最终稿件，无法更新文章对象")
            return

        try:
            # 更新标题（如果最终稿件中有）
            if "title" in result.final_draft and result.final_draft["title"]:
                article.title = result.final_draft["title"]

            # 更新副标题
            if "subtitle" in result.final_draft and result.final_draft["subtitle"]:
                article.subtitle = result.final_draft["subtitle"]

            # 更新文章部分
            if "sections" in result.final_draft and isinstance(result.final_draft["sections"], list):
                article.sections = []
                for section_data in result.final_draft["sections"]:
                    section = Section(
                        title=section_data.get("title", ""),
                        content=section_data.get("content", "")
                    )
                    article.sections.append(section)

            # 更新元数据
            if "metadata" in result.final_draft and isinstance(result.final_draft["metadata"], dict):
                if not hasattr(article, "metadata") or not article.metadata:
                    article.metadata = {}

                for key, value in result.final_draft["metadata"].items():
                    article.metadata[key] = value

        except Exception as e:
            logger.error(f"更新文章对象时出错: {str(e)}")

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
