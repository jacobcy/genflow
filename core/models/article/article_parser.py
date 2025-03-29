"""文章解析工具

用于解析和处理文章内容，包括提取章节结构、解析AI生成的内容等。
"""

from typing import Dict, Any, Optional, List, Type
import json
import re
from loguru import logger

from .article import Section

class ArticleParser:
    """文章数据解析工具类"""

    @staticmethod
    def _parse_sections(content: str) -> List[Dict[str, Any]]:
        """从文本内容解析出章节结构

        Args:
            content: 文章内容文本

        Returns:
            List[Dict[str, Any]]: 解析出的章节列表
        """
        # 使用正则表达式匹配标题和内容
        # 标题格式：## 标题文本
        pattern = r"##\s*([^\n]+)\n(.*?)(?=##\s*[^\n]+\n|$)"
        matches = re.finditer(pattern, content, re.DOTALL)

        sections = []
        for idx, match in enumerate(matches, 1):
            title = match.group(1).strip()
            content = match.group(2).strip()
            if title and content:
                sections.append({
                    "title": title,
                    "content": content,
                    "order": idx
                })

        # 如果没有找到任何章节，将整个内容作为一个章节
        if not sections and content.strip():
            sections.append({
                "title": "正文",
                "content": content.strip(),
                "order": 1
            })

        return sections

    @staticmethod
    def parse_ai_response(response_text: str, article: Any) -> Optional[Any]:
        """解析AI返回的文章数据并更新到Article模型

        Args:
            response_text: AI返回的JSON文本
            article: 需要更新的Article实例

        Returns:
            更新后的Article实例，如果解析失败则返回None
        """
        try:
            # 尝试解析JSON
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError:
                # JSON解析失败，尝试修复
                logger.warning("JSON解析失败，尝试修复...")
                try:
                    # 简单的JSON修复尝试
                    fixed_text = response_text.replace("'", "\"")
                    data = json.loads(fixed_text)
                except:
                    # 如果简单修复失败，可以添加更复杂的修复逻辑
                    # 或者返回失败
                    logger.error("JSON修复失败")
                    return None

            # 更新文章标题
            if "title" in data:
                article.title = data["title"]

            # 更新文章摘要
            if "summary" in data:
                article.summary = data["summary"]

            # 更新文章标签
            if "tags" in data:
                article.tags = data["tags"]

            # 从content解析章节
            if "content" in data:
                sections_data = ArticleParser._parse_sections(data["content"])
                article.sections = [Section(**section_data) for section_data in sections_data]

            return article

        except Exception as e:
            logger.error(f"解析AI返回数据失败: {str(e)}")
            logger.error(f"原始数据: {response_text}")
            return None

    @staticmethod
    def validate_article(article: Any) -> bool:
        """验证文章数据的完整性

        Args:
            article: Article实例

        Returns:
            bool: 验证是否通过
        """
        try:
            # 验证必要字段
            if not article.title:
                logger.error("文章标题为空")
                return False

            if not article.summary:
                logger.error("文章摘要为空")
                return False

            if not article.sections:
                logger.error("文章章节为空")
                return False

            # 验证章节数据
            for section in article.sections:
                if not section.title or not section.content:
                    logger.error(f"章节数据不完整: {section}")
                    return False

                if not isinstance(section.order, int) or section.order < 1:
                    logger.error(f"章节顺序无效: {section.order}")
                    return False

            # 验证标签
            if not article.tags or len(article.tags) < 3:
                logger.warning("文章标签不足3个")
                # 不要因为标签不足就返回False，只是警告
                return True

            return True

        except Exception as e:
            logger.error(f"验证文章数据时发生错误: {str(e)}")
            return False
