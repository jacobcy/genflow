"""写作团队工作流模块

实现了基于CrewAI的文章写作工作流，整合各种智能体协同工作。
"""
import os
import sys
import json
import logging
import asyncio
import uuid
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pathlib import Path
from json_repair import repair_json  # 添加json修复库

from crewai import Task, Crew, Process
from crewai.agent import Agent

from core.models.article.article import Article, Section
from core.models.platform.platform import Platform
from core.models.topic.topic import Topic
from core.models.content_manager import ContentManager
from core.models.outline.basic_outline import BasicOutline, OutlineSection
from core.models.outline.article_outline import ArticleOutline
from .writing_agents import WritingAgents
from core.models.util import ArticleParser

# 配置日志
logger = logging.getLogger(__name__)

# 定义写作风格常量
WRITING_STYLE_FORMAL = "formal"
WRITING_STYLE_CASUAL = "casual"
WRITING_STYLE_TECHNICAL = "technical"

# 默认写作配置
DEFAULT_WRITING_CONFIG = {
    "content_type": "article",
    "style": WRITING_STYLE_FORMAL,
    "word_count": 1500,
    "depth": "medium",
    "structure": "standard",
    "tone": "professional"
}

class WritingResult:
    """写作结果类

    存储写作流程的各个阶段结果，包括大纲、内容和最终稿件。
    """
    def __init__(
        self,
        article: Article,
        outline: Optional[Dict] = None,
        content: Optional[Dict] = None,
        final_draft: Optional[Dict] = None
    ):
        self.article = article
        self.outline = outline or {}
        self.content = content or {}
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

        # 当前配置
        self.current_content_config = DEFAULT_WRITING_CONFIG.copy()

        # 确保ContentManager已初始化
        ContentManager.ensure_initialized()

        logger.info("写作团队初始化完成")

    async def write_article(
        self,
        article: Article,
        research_data: Optional[Dict[str, Any]] = None,
        platform: Optional[Union[str, Platform]] = None,
        content_type: Optional[str] = None,
        style: Optional[str] = None,
        **kwargs
    ) -> WritingResult:
        """实现文章写作流程

        组织智能体团队，执行从大纲设计到最终编辑的完整文章写作流程。
        注意：本方法不处理content_type解析、topic_id映射或风格推断等逻辑，
        这些应该由上层WritingAdapter完成。本方法只负责执行写作流程。

        Args:
            article: 文章信息对象，包含标题、主题和初始内容
            research_data: 研究资料（可选）
            platform: 目标发布平台或平台ID
            content_type: 内容类型
            style: 写作风格
            **kwargs: 其他参数

        Returns:
            WritingResult: 完整的写作过程结果
        """
        platform_obj = None
        platform_id = None

        # 处理平台参数
        if isinstance(platform, str):
            platform_id = platform
            platform_obj = ContentManager.get_platform(platform)
            if not platform_obj:
                platform_obj = Platform(
                    id=platform,
                    name=platform,
                    description="平台描述"
                )
        elif isinstance(platform, Platform):
            platform_obj = platform
            platform_id = platform.id

        # 如果没有提供平台，创建默认平台
        if not platform_obj:
            platform_obj = Platform(
                id="default",
                name="通用平台",
                description="适用于各种内容的通用平台"
            )

        logger.info(f"开始文章写作流程: {article.title}, 目标平台: {platform_obj.name}, 内容类型: {content_type or '未指定'}")

        # 根据内容类型设置写作配置 (直接使用传入的参数，不进行解析)
        self.current_content_config = self.get_writing_config(content_type)

        # 更新文章元数据
        if not hasattr(article, "metadata") or not article.metadata:
            article.metadata = {}

        article.metadata["content_type"] = content_type

        # 添加研究资料到元数据
        if research_data:
            article.metadata["research_data"] = research_data

        # 初始化返回结果
        result = WritingResult(article=article)

        # 延迟初始化智能体
        if not self.agents:
            self._initialize_agents()

        try:
            # 创建写作任务
            tasks = []

            # 1. 创建大纲任务
            outline_task = self._create_outline_task(article, platform_obj)
            tasks.append(outline_task)

            # 2. 创建内容写作任务
            content_task = Task(
                description=f"""
                根据提供的大纲，为文章《{article.title}》创建完整内容。

                文章主题：{article.topic.name if hasattr(article, 'topic') and article.topic else article.title}
                内容类型：{article.metadata.get('content_type', '未指定')}
                目标平台：{platform_obj.name}
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

            # 3. 事实核查任务
            fact_check_task = self._create_fact_check_task(article, platform_obj)
            tasks.append(fact_check_task)

            # 4. 编辑和完善任务
            edit_task = self._create_edit_task(article, platform_obj)
            tasks.append(edit_task)

            # 创建与执行写作工作流
            crew = Crew(
                agents=[
                    self.outline_creator,
                    self.content_writer,
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

            # 不在此更新article对象，只返回处理结果
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
        self.fact_checker = self.agents.get_fact_checker()
        self.editor = self.agents.get_editor()

    def _create_outline_task(self, article: Article, platform: Platform) -> Task:
        """创建大纲任务

        Args:
            article: 文章信息
            platform: 发布平台信息

        Returns:
            Task: 大纲任务
        """
        outline_task = Task(
            description=f"""
            为文章《{article.title}》创建合适的大纲结构。

            文章主题：{article.summary}
            内容类型：{article.metadata.get('content_type', '未指定')}
            目标平台：{platform.name}
            平台特点：{platform.description}
            写作风格：{self.current_content_config['style']}
            内容结构：{self.current_content_config.get('structure', 'standard')}

            请根据文章主题和内容类型，生成一个详细的大纲，包括：
            1. 文章引言方向
            2. 主要段落和小节（至少3-5个关键部分）
            3. 每个部分应包含的要点
            4. 适合的结论方向

            输出格式：JSON对象，包含outline键（大纲数组）、summary键（大纲说明）和tags键（文章标签）
            """,
            agent=self.outline_creator,
            expected_output="""
            {
                "outline": [
                    {"title": "引言", "points": ["要点1", "要点2", ...]},
                    {"title": "第一部分", "points": ["要点1", "要点2", ...]},
                    ...
                ],
                "summary": "大纲总体思路和结构说明",
                "tags": ["标签1", "标签2", "标签3"]
            }
            """
        )
        return outline_task

    def _create_content_task(self, article: Article, platform: Platform, outline_data: List[Dict]) -> Task:
        """创建内容写作任务

        Args:
            article: 文章信息
            platform: 发布平台信息
            outline_data: 大纲数据

        Returns:
            Task: 内容任务
        """
        formatted_outline = json.dumps(outline_data, ensure_ascii=False)

        content_task = Task(
            description=f"""
            根据提供的大纲，为文章《{article.title}》创建完整内容。

            文章主题：{article.summary}
            内容类型：{article.metadata.get('content_type', '未指定')}
            目标平台：{platform.name}
            字数要求：{self.current_content_config['word_count']}字左右
            写作风格：{self.current_content_config['style']}
            内容深度：{self.current_content_config['depth']}

            大纲：{formatted_outline}

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
        return content_task

    def _create_fact_check_task(self, article: Article, platform: Platform) -> Task:
        """创建事实核查任务

        Args:
            article: 文章信息
            platform: 发布平台信息

        Returns:
            Task: 事实核查任务
        """
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
        return fact_check_task

    def _create_edit_task(self, article: Article, platform: Platform) -> Task:
        """创建编辑任务

        Args:
            article: 文章信息
            platform: 发布平台信息

        Returns:
            Task: 编辑任务
        """
        edit_task = Task(
            description=f"""
            对文章《{article.title}》进行最终编辑和完善。

            原始内容：{{content_task.output}}
            事实核查：{{fact_check_task.output}}

            内容类型：{article.metadata.get('content_type', '未指定')}
            目标平台：{platform.name}
            字数要求：{self.current_content_config['word_count']}字左右
            写作风格：{self.current_content_config['style']}

            请根据以上信息对文章进行最终编辑，并按照以下严格的JSON格式返回：
            1. title: 文章标题
            2. summary: 文章摘要（200字以内）
            3. content: 文章内容，使用Markdown格式，用##分隔章节
            4. tags: 文章标签数组（至少3个）

            注意事项：
            1. 确保返回的JSON结构完全符合要求
            2. 所有字段都必须提供值，不能为空
            3. 标签数组至少包含3个元素
            4. summary不能超过200字
            """,
            agent=self.editor,
            expected_output="""
            {
                "title": "文章标题",
                "summary": "文章摘要",
                "content": "## 引言\\n这是引言部分的内容...\\n\\n## 主要内容\\n这是主要内容部分...\\n\\n## 总结\\n这是总结部分的内容...\\n",
                "tags": ["标签1", "标签2", "标签3"]
            }
            """
        )
        return edit_task

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
            # 尝试解析各个任务的结果
            if isinstance(crew_results, list) and len(crew_results) >= 4:
                # 处理每个结果，尝试修复可能的JSON错误
                for i, res in enumerate(crew_results):
                    if isinstance(res, str):
                        try:
                            # 首先尝试常规JSON解析
                            parsed_result = json.loads(res)
                        except json.JSONDecodeError:
                            try:
                                # 如果失败，尝试修复并重新解析
                                repaired_json = repair_json(res)
                                parsed_result = json.loads(repaired_json)
                            except Exception as e:
                                logger.warning(f"JSON修复失败: {str(e)}")
                                parsed_result = {"raw_content": res}
                    else:
                        parsed_result = res

                    # 根据索引分配结果
                    if i == 0:
                        result.outline = parsed_result
                    elif i == 1:
                        result.content = parsed_result
                    elif i == 2:
                        fact_check = parsed_result
                    elif i == 3:
                        result.final_draft = parsed_result

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
            # 将最终稿件转换为JSON字符串
            final_draft_json = json.dumps(result.final_draft)

            # 使用ArticleParser解析和更新文章
            updated_article = ArticleParser.parse_ai_response(final_draft_json, article)

            if updated_article and ArticleParser.validate_article(updated_article):
                # 更新原始文章对象
                article.title = updated_article.title
                article.summary = updated_article.summary
                article.sections = updated_article.sections
                article.tags = updated_article.tags

                # 更新状态
                article.status = "reviewed"
                logger.info(f"文章《{article.title}》更新成功")
            else:
                logger.error("文章数据验证失败，保持原状")

        except Exception as e:
            logger.error(f"更新文章对象时出错: {str(e)}")
            logger.debug("最终稿件内容:", result.final_draft)

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

        print("\n3. 修改建议:")
        comments = input("评审意见: ")

        # 更新反馈
        writing_result.human_feedback = {
            "content_score": content_score,
            "structure_score": structure_score,
            "average_score": (content_score + structure_score) / 2,
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
        article.sections = ArticleParser._parse_sections(final_draft["content"])
        article.tags = final_draft["tags"]
        article.status = "reviewed"

        return article

    def get_writing_config(self, content_type=None) -> Dict[str, Any]:
        """获取指定内容类型的写作配置

        从ContentManager获取内容类型配置，或使用默认配置

        Args:
            content_type: 内容类型ID

        Returns:
            Dict: 写作配置
        """
        config = DEFAULT_WRITING_CONFIG.copy()

        if not content_type:
            return config

        # 从ContentManager获取内容类型配置
        content_type_obj = ContentManager.get_content_type(content_type)
        if content_type_obj:
            # 使用内容类型的属性更新配置
            config.update({
                "content_type": content_type,
                "style": getattr(content_type_obj, "default_style", WRITING_STYLE_FORMAL),
                "word_count": getattr(content_type_obj, "default_word_count", 1500),
                "depth": getattr(content_type_obj, "research_level", "medium"),
                "structure": getattr(content_type_obj, "default_structure", "standard"),
                "tone": getattr(content_type_obj, "default_tone", "professional")
            })
            logger.info(f"为内容类型 {content_type} 获取写作配置")

        return config

    async def create_outline(
        self,
        topic_or_text: Union[str, Topic, Dict, Any],
        content_type: Optional[str] = None,
        platform_id: Optional[str] = None,
        style: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> BasicOutline:
        """创建文章大纲

        可以基于话题对象或纯文本创建大纲。
        注意：本方法不处理topic_id映射和内容类型推断等逻辑，
        这些应该由上层WritingAdapter完成。本方法只负责执行大纲创建流程。

        Args:
            topic_or_text: 话题对象或文本字符串
            content_type: 内容类型
            platform_id: 平台ID
            style: 写作风格
            options: 其他选项

        Returns:
            BasicOutline: 基础大纲对象
        """
        logger.info(f"开始创建大纲，内容类型: {content_type or '未指定'}")

        # 处理不同类型的输入
        topic_id = None
        title = ""
        description = ""
        research_data = {}

        # 提取必要的信息
        if isinstance(topic_or_text, str):
            title = topic_or_text
            description = topic_or_text
        else:
            # 假设是Topic对象或字典
            if hasattr(topic_or_text, 'id'):
                topic_id = topic_or_text.id
            elif isinstance(topic_or_text, dict) and 'id' in topic_or_text:
                topic_id = topic_or_text['id']

            if hasattr(topic_or_text, 'title'):
                title = topic_or_text.title
            elif isinstance(topic_or_text, dict) and 'title' in topic_or_text:
                title = topic_or_text['title']

            if hasattr(topic_or_text, 'description'):
                description = topic_or_text.description
            elif isinstance(topic_or_text, dict) and 'description' in topic_or_text:
                description = topic_or_text['description']

            # 尝试获取研究数据
            if hasattr(topic_or_text, 'research_data'):
                research_data = topic_or_text.research_data
            elif isinstance(topic_or_text, dict) and 'research_data' in topic_or_text:
                research_data = topic_or_text['research_data']

            # 如果没有明确指定content_type，尝试从topic获取
            if not content_type:
                if hasattr(topic_or_text, 'content_type'):
                    content_type = topic_or_text.content_type
                elif isinstance(topic_or_text, dict) and 'content_type' in topic_or_text:
                    content_type = topic_or_text['content_type']

        # 获取内容类型配置
        self.current_content_config = self.get_writing_config(content_type)

        # 获取平台信息
        platform = None
        if platform_id:
            platform = ContentManager.get_platform(platform_id)

        # 处理风格
        if style:
            article_style = ContentManager.get_article_style(style)
            if article_style:
                self.current_content_config["style"] = style
                self.current_content_config["tone"] = getattr(article_style, "tone", "professional")

        # 延迟初始化智能体
        if not self.agents:
            self._initialize_agents()

        # 创建临时Article对象用于传递给智能体
        temp_article = Article(
            id=str(uuid.uuid4()),
            title=title,
            summary=description,
            metadata={
                "content_type": content_type,
                "research_data": research_data
            }
        )

        # 创建临时Platform对象
        temp_platform = platform or Platform(
            id="default",
            name="通用平台",
            description="适用于各种内容的通用平台"
        )

        try:
            # 只执行大纲任务
            outline_task = self._create_outline_task(temp_article, temp_platform)

            # 创建简化的工作流
            crew = Crew(
                agents=[self.outline_creator],
                tasks=[outline_task],
                verbose=self.verbose,
                process=Process.sequential
            )

            # 执行工作流
            outline_result = crew.kickoff()

            # 处理结果
            outline_data = self._parse_outline_result(outline_result[0], temp_article)

            # 创建BasicOutline或ArticleOutline对象
            if topic_id:
                # 如果有话题ID，创建ArticleOutline
                outline = ArticleOutline(
                    id=str(uuid.uuid4()),
                    topic_id=topic_id,
                    content_type=content_type or "default",
                    title=title,
                    summary=outline_data.get("summary", description),
                    sections=[
                        OutlineSection(
                            title=section["title"],
                            content=section.get("content", ""),
                            order=idx,
                            key_points=section.get("points", [])
                        )
                        for idx, section in enumerate(outline_data.get("outline", []))
                    ],
                    tags=outline_data.get("tags", []),
                    target_word_count=self.current_content_config["word_count"]
                )
            else:
                # 否则创建BasicOutline
                outline = BasicOutline(
                    id=str(uuid.uuid4()),
                    content_type=content_type or "default",
                    title=title,
                    summary=outline_data.get("summary", description),
                    sections=[
                        OutlineSection(
                            title=section["title"],
                            content=section.get("content", ""),
                            order=idx,
                            key_points=section.get("points", [])
                        )
                        for idx, section in enumerate(outline_data.get("outline", []))
                    ],
                    tags=outline_data.get("tags", []),
                    target_word_count=self.current_content_config["word_count"]
                )

            logger.info(f"大纲创建完成: {outline.title}, 包含 {len(outline.sections)} 个章节")
            return outline

        except Exception as e:
            logger.error(f"创建大纲过程发生错误: {str(e)}")
            raise

    def _parse_outline_result(self, result: Any, article: Article) -> Dict[str, Any]:
        """解析大纲结果

        Args:
            result: 大纲任务的原始结果
            article: 文章对象

        Returns:
            Dict: 解析后的大纲数据
        """
        try:
            if isinstance(result, str):
                try:
                    # 首先尝试常规JSON解析
                    parsed_result = json.loads(result)
                except json.JSONDecodeError:
                    try:
                        # 如果失败，尝试修复并重新解析
                        repaired_json = repair_json(result)
                        parsed_result = json.loads(repaired_json)
                    except Exception as e:
                        logger.warning(f"JSON修复失败: {str(e)}")
                        parsed_result = {
                            "outline": [{"title": "内容", "points": [result]}],
                            "summary": article.summary
                        }
            else:
                parsed_result = result

            # 确保结果包含必要的字段
            if "outline" not in parsed_result:
                parsed_result["outline"] = []
            if "summary" not in parsed_result:
                parsed_result["summary"] = article.summary
            if "tags" not in parsed_result:
                parsed_result["tags"] = []

            return parsed_result
        except Exception as e:
            logger.error(f"解析大纲结果失败: {str(e)}")
            return {
                "outline": [],
                "summary": article.summary,
                "tags": []
            }

    async def expand_content(
        self,
        outline_or_text: Union[str, BasicOutline, ArticleOutline],
        content_type: Optional[str] = None,
        platform_id: Optional[str] = None,
        style: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """扩展内容

        根据大纲或文本扩展生成完整内容。
        注意：本方法不处理内容类型推断等逻辑，这些应该由上层WritingAdapter完成。
        本方法只负责执行内容扩展流程。

        Args:
            outline_or_text: 大纲对象或文本
            content_type: 内容类型
            platform_id: 平台ID
            style: 写作风格
            options: 其他选项

        Returns:
            Dict[str, Any]: 扩展结果，包含文章内容
        """
        logger.info(f"开始扩展内容，内容类型: {content_type or '未指定'}")

        # 准备大纲数据
        title = ""
        summary = ""
        outline_data = []
        research_data = {}

        if isinstance(outline_or_text, str):
            # 如果输入是字符串，创建简单大纲
            title = "untitled"
            summary = outline_or_text
            outline_data = [{"title": "内容", "points": [outline_or_text]}]
        elif isinstance(outline_or_text, (BasicOutline, ArticleOutline)):
            # 处理大纲对象
            title = outline_or_text.title
            summary = outline_or_text.summary
            outline_data = [
                {
                    "title": section.title,
                    "points": section.key_points,
                    "content": section.content
                }
                for section in outline_or_text.sections
            ]

            # 直接使用传入的content_type，不进行推断


        # 获取内容类型配置
        self.current_content_config = self.get_writing_config(content_type)

        # 获取平台信息
        platform = None
        if platform_id:
            platform = ContentManager.get_platform(platform_id)

        # 处理风格
        if style:
            article_style = ContentManager.get_article_style(style)
            if article_style:
                self.current_content_config["style"] = style
                self.current_content_config["tone"] = getattr(article_style, "tone", "professional")

        # 延迟初始化智能体
        if not self.agents:
            self._initialize_agents()

        # 创建临时Article和Platform对象
        temp_article = Article(
            id=str(uuid.uuid4()),
            title=title,
            summary=summary,
            metadata={
                "content_type": content_type,
                "outline": outline_data,
                "research_data": research_data
            }
        )

        temp_platform = platform or Platform(
            id="default",
            name="通用平台",
            description="适用于各种内容的通用平台"
        )

        try:
            # 创建内容写作任务
            content_task = self._create_content_task(temp_article, temp_platform, outline_data)
            fact_check_task = self._create_fact_check_task(temp_article, temp_platform)
            edit_task = self._create_edit_task(temp_article, temp_platform)

            # 创建工作流
            crew = Crew(
                agents=[
                    self.content_writer,
                    self.fact_checker,
                    self.editor
                ],
                tasks=[content_task, fact_check_task, edit_task],
                verbose=self.verbose,
                process=Process.sequential
            )

            # 执行工作流
            content_results = crew.kickoff()

            # 处理结果
            result = self._process_expansion_results(content_results, temp_article)
            logger.info(f"内容扩展完成: {title}")

            return result

        except Exception as e:
            logger.error(f"扩展内容过程发生错误: {str(e)}")
            raise

    def _process_expansion_results(self, results: List[Any], article: Article) -> Dict[str, Any]:
        """处理内容扩展结果

        Args:
            results: 工作流结果列表
            article: 文章对象

        Returns:
            Dict: 处理后的内容扩展结果
        """
        try:
            final_result = {
                "title": article.title,
                "summary": article.summary,
                "content": "",
                "sections": [],
                "metadata": {}
            }

            # 处理各个任务的结果
            if len(results) >= 3:
                # 内容写作结果
                content_result = self._parse_json_result(results[0])
                if "sections" in content_result:
                    final_result["sections"] = content_result["sections"]
                if "metadata" in content_result:
                    final_result["metadata"]["content"] = content_result["metadata"]

                # 事实核查结果
                fact_check = self._parse_json_result(results[1])
                final_result["metadata"]["fact_check"] = fact_check

                # 编辑结果
                edit_result = self._parse_json_result(results[2])
                if "title" in edit_result:
                    final_result["title"] = edit_result["title"]
                if "summary" in edit_result:
                    final_result["summary"] = edit_result["summary"]
                if "content" in edit_result:
                    final_result["content"] = edit_result["content"]
                if "tags" in edit_result:
                    final_result["tags"] = edit_result["tags"]

            return final_result
        except Exception as e:
            logger.error(f"处理内容扩展结果失败: {str(e)}")
            return {
                "title": article.title,
                "summary": article.summary,
                "content": "",
                "error": str(e)
            }

    def _parse_json_result(self, result: Any) -> Dict[str, Any]:
        """解析并修复JSON结果

        Args:
            result: 原始结果

        Returns:
            Dict: 解析后的结果
        """
        if isinstance(result, dict):
            return result

        try:
            # 首先尝试常规JSON解析
            parsed_result = json.loads(result)
            return parsed_result
        except json.JSONDecodeError:
            try:
                # 如果失败，尝试修复并重新解析
                repaired_json = repair_json(result)
                parsed_result = json.loads(repaired_json)
                return parsed_result
            except Exception as e:
                logger.warning(f"JSON修复失败: {str(e)}")
                return {"raw_content": result}
