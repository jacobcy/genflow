"""写作团队工具模块

提供文章写作、内容优化和SEO分析所需的工具集合。
"""
import logging
from typing import Dict, List, Optional, Any
from crewai.tools import tool

from core.tools.nlp_tools import NLPAggregator, SummaTool, YakeTool
from core.tools.style_tools import StyleAdapter
from core.tools.writing_tools import ArticleWriter

# 配置日志
logger = logging.getLogger(__name__)

class WritingTools:
    """写作团队工具类，按照CrewAI最佳实践组织工具"""

    def __init__(self):
        """
        初始化写作工具集
        """
        logger.info(f"初始化写作工具集")

        # 初始化核心工具
        self.nlp_tools = NLPAggregator()
        self.summa_tool = SummaTool()
        self.yake_tool = YakeTool()
        self.style_adapter = None  # 延迟初始化，在需要时传入平台信息
        self.article_writer = ArticleWriter()

        logger.info("写作工具集初始化完成")

    @tool("文章结构分析")
    def analyze_structure(self, text: str) -> Dict:
        """
        分析文章的结构，识别标题、段落、主要论点等。

        Args:
            text: 要分析的文章内容

        Returns:
            Dict: 包含文章结构分析结果的字典
        """
        logger.info("执行文章结构分析")
        result = self.nlp_tools.execute(text=text, analysis_type="structure")
        return result.data

    @tool("关键词提取")
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        从文本中提取关键词，用于SEO优化和主题分析。

        Args:
            text: 要分析的文本内容
            top_n: 要提取的关键词数量

        Returns:
            List[str]: 关键词列表
        """
        logger.info(f"提取关键词，top_n={top_n}")
        result = self.yake_tool.execute(text=text, max_keyphrases=top_n)
        return result.data

    @tool("内容摘要")
    def summarize_content(self, text: str, ratio: float = 0.2) -> str:
        """
        生成文本的摘要，用于创建文章概述或元描述。

        Args:
            text: 要摘要的文本内容
            ratio: 摘要与原文的长度比例

        Returns:
            str: 文本摘要
        """
        logger.info(f"生成内容摘要，ratio={ratio}")
        result = self.summa_tool.execute(text=text, ratio=ratio)
        return result.data

    @tool("文章撰写")
    def write_article(self,
                     title: str,
                     outline: Dict,
                     keywords: List[str],
                     tone: str = "professional") -> Dict:
        """
        根据大纲和关键词撰写文章内容。

        Args:
            title: 文章标题
            outline: 文章大纲
            keywords: 要包含的关键词
            tone: 文章风格和语调

        Returns:
            Dict: 包含文章各部分内容的字典
        """
        logger.info(f"撰写文章，标题: {title}")
        result = self.article_writer.execute(
            title=title,
            outline=outline,
            keywords=keywords,
            tone=tone
        )
        return result.data

    @tool("风格适配")
    def adapt_style(self, text: str, platform_name: str = None, style: str = None) -> str:
        """
        根据目标平台和所需风格调整文本样式。

        Args:
            text: 要调整的文本内容
            platform_name: 目标平台名称
            style: 目标风格，如'formal'、'casual'等

        Returns:
            str: 调整后的文本
        """
        logger.info(f"调整文本风格，目标风格: {style or '默认'}")

        # 由于没有在初始化时指定平台，这里需要动态调整
        # 在实际应用中，可能需要更复杂的处理逻辑
        processed_text = text

        # 根据指定的风格应用一些基本的文本处理
        if style == "formal":
            # 这里只是示例，实际应用中可能需要更复杂的处理
            processed_text = processed_text.replace("don't", "do not")
            processed_text = processed_text.replace("can't", "cannot")
        elif style == "casual":
            processed_text = processed_text.replace("therefore", "so")
            processed_text = processed_text.replace("however", "but")

        return processed_text

    @tool("SEO优化")
    def optimize_seo(self, content: Dict, keywords: List[str], platform_name: str = None) -> Dict:
        """
        优化内容以提高搜索引擎排名。

        Args:
            content: 文章内容字典
            keywords: 目标关键词列表
            platform_name: 目标平台名称

        Returns:
            Dict: 包含SEO优化建议和改进后内容的字典
        """
        logger.info(f"执行SEO优化，关键词数量: {len(keywords)}")

        # 构建优化结果
        result = {
            "original_content": content,
            "optimized_content": content.copy(),
            "keywords": keywords,
            "suggestions": []
        }

        # 分析关键词密度
        text = ""
        if isinstance(content, dict) and "text" in content:
            text = content["text"]
        elif isinstance(content, str):
            text = content

        # 计算每个关键词的出现次数
        keyword_counts = {}
        for keyword in keywords:
            count = text.lower().count(keyword.lower())
            keyword_counts[keyword] = count

        # 生成优化建议
        for keyword, count in keyword_counts.items():
            if count == 0:
                result["suggestions"].append(f"添加关键词 '{keyword}'")
            elif count < 2:
                result["suggestions"].append(f"增加关键词 '{keyword}' 的使用频率")

        # 检查标题中是否包含关键词
        if "title" in content:
            title = content["title"]
            title_contains_keywords = any(keyword.lower() in title.lower() for keyword in keywords)
            if not title_contains_keywords:
                result["suggestions"].append("在标题中添加一个主要关键词")

        return result

    @tool("文章编辑")
    def edit_article(self, content: Dict, edit_focus: str = "all") -> Dict:
        """
        编辑和改进文章内容，包括语法、风格和结构。

        Args:
            content: 文章内容字典
            edit_focus: 编辑重点，可以是'grammar'、'style'、'structure'或'all'

        Returns:
            Dict: 编辑后的文章内容
        """
        logger.info(f"编辑文章，重点关注: {edit_focus}")

        # 根据编辑重点选择不同的处理方式
        if edit_focus in ["grammar", "all"]:
            # 语法检查和修正
            content["text"] = self._process_grammar(content.get("text", ""))

        if edit_focus in ["style", "all"]:
            # 风格优化
            content["text"] = self.adapt_style(content.get("text", ""))

        if edit_focus in ["structure", "all"]:
            # 结构改进
            structure_analysis = self.analyze_structure(content.get("text", ""))
            content["structure_improvements"] = structure_analysis.get("improvement_suggestions", [])

        content["edit_history"] = content.get("edit_history", []) + [
            {"timestamp": "now", "focus": edit_focus}
        ]

        return content

    def _process_grammar(self, text: str) -> str:
        """内部方法：处理文本的语法问题"""
        # 这里可以集成第三方语法检查工具
        return text
