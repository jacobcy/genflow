"""大纲转换工具

提供大纲转换为不同格式输出的工具类，支持将大纲转换为文本、文章对象等。
与模型定义分离，遵循单一职责原则。
"""

from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING, cast
import inspect

# 避免循环导入
if TYPE_CHECKING:
    from .basic_outline import BasicOutline
    from .article_outline import ArticleOutline
    from ..article.basic_article import BasicArticle

class OutlineConverter:
    """大纲转换工具类

    提供将大纲模型转换为不同形式的输出的功能，
    如将大纲转换为文本、文章对象等。
    """

    @staticmethod
    def to_full_text(outline: Union['BasicOutline', 'ArticleOutline', Dict[str, Any]]) -> str:
        """将大纲转换为完整文本

        将大纲的所有部分（包括标题、摘要、章节等）
        转换为结构化的文本内容。

        Args:
            outline: 大纲对象或包含大纲数据的字典

        Returns:
            str: 完整文本内容
        """
        # 构建内容文本
        content_parts = []

        # 获取大纲标题
        if isinstance(outline, dict):
            title = outline.get('title', '无标题')
        else:
            title = outline.title if hasattr(outline, 'title') else '无标题'

        # 添加标题
        content_parts.append(f"# {title}")
        content_parts.append("")

        # 获取摘要 - 只有ArticleOutline才有summary
        summary = ""
        if isinstance(outline, dict):
            summary = outline.get('summary', '')
        else:
            # 检查是否是ArticleOutline
            summary = getattr(outline, 'summary', '') if hasattr(outline, 'summary') else ''

        # 添加摘要
        if summary:
            content_parts.append(f"## 摘要")
            content_parts.append(summary)
            content_parts.append("")

        # 获取章节 - 只有ArticleOutline才有sections
        sections = []
        if isinstance(outline, dict):
            sections = outline.get('sections', [])
        else:
            # 检查是否是ArticleOutline
            sections = getattr(outline, 'sections', []) if hasattr(outline, 'sections') else []

        # 添加各节内容
        if sections:
            # 按顺序排列节
            def get_order(section):
                if isinstance(section, dict):
                    return section.get('order', 999)
                return getattr(section, 'order', 999)

            sorted_sections = sorted(sections, key=get_order)

            for section in sorted_sections:
                # 获取节标题
                if isinstance(section, dict):
                    section_title = section.get('title', '无标题')
                    section_content = section.get('content', '')
                    section_key_points = section.get('key_points', [])
                    section_subsections = section.get('subsections', [])
                else:
                    section_title = getattr(section, 'title', '无标题')
                    section_content = getattr(section, 'content', '')
                    section_key_points = getattr(section, 'key_points', [])
                    section_subsections = getattr(section, 'subsections', [])

                # 添加节标题
                content_parts.append(f"## {section_title}")

                # 添加节内容
                if section_content:
                    content_parts.append(section_content)

                # 添加关键点
                if section_key_points:
                    content_parts.append("\n关键点:")
                    for point in section_key_points:
                        content_parts.append(f"- {point}")

                # 添加子节
                if section_subsections:
                    for subsection in section_subsections:
                        if isinstance(subsection, dict):
                            subsection_title = subsection.get('title', '无标题')
                            subsection_content = subsection.get('content', '')
                        else:
                            subsection_title = getattr(subsection, 'title', '无标题')
                            subsection_content = getattr(subsection, 'content', '')

                        content_parts.append(f"### {subsection_title}")

                        if subsection_content:
                            content_parts.append(subsection_content)

                content_parts.append("")  # 添加空行分隔各节

        # 将所有部分连接成文本
        return "\n".join(content_parts)

    @staticmethod
    def to_basic_article(outline: Union['BasicOutline', 'ArticleOutline', Dict[str, Any]]) -> 'BasicArticle':
        """将大纲转换为BasicArticle对象

        此方法生成一个仅包含基本信息的文章对象，
        用于提交给StyleCrew进行风格处理。

        Args:
            outline: 大纲对象或包含大纲数据的字典

        Returns:
            BasicArticle: 基本文章对象
        """
        from ..article.basic_article import BasicArticle

        # 获取ID
        outline_id = None
        if isinstance(outline, dict):
            outline_id = outline.get('id')
        else:
            # 从对象获取ID，优先从metadata中获取
            if hasattr(outline, 'metadata') and isinstance(outline.metadata, dict):
                outline_id = outline.metadata.get('outline_id')
            # 如果是ArticleOutline，可能直接有id字段
            if not outline_id and hasattr(outline, 'id'):
                outline_id = getattr(outline, 'id')

        # 获取标题
        if isinstance(outline, dict):
            title = outline.get('title', '无标题')
        else:
            title = outline.title if hasattr(outline, 'title') else '无标题'

        # 将大纲各节转换为文本内容
        content = OutlineConverter.to_full_text(outline)

        return BasicArticle(
            id=outline_id,
            title=title,
            content=content
        )

    @staticmethod
    def to_article_sections(outline: Union['BasicOutline', 'ArticleOutline', Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将大纲转换为文章章节列表

        用于从大纲创建文章时，将大纲章节转换为文章章节格式。

        Args:
            outline: 大纲对象或包含大纲数据的字典

        Returns:
            List[Dict]: 文章章节列表
        """
        # 获取章节
        sections = []
        if isinstance(outline, dict):
            sections = outline.get('sections', [])
        else:
            # 检查是否是ArticleOutline
            sections = getattr(outline, 'sections', []) if hasattr(outline, 'sections') else []

        result = []
        for section in sections:
            if isinstance(section, dict):
                section_title = section.get('title', '无标题')
                section_content = section.get('content', '')
                section_order = section.get('order', 0)
            else:
                section_title = getattr(section, 'title', '无标题')
                section_content = getattr(section, 'content', '')
                section_order = getattr(section, 'order', 0)

            result.append({
                "title": section_title,
                "content": section_content or f"# {section_title}\n\n待撰写内容...",
                "order": section_order
            })

        return result
