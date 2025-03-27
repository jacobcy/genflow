"""文章数据解析工具"""
from typing import Dict, Any, Optional, List, Type, TypeVar, Generic, TYPE_CHECKING
from json_repair import repair_json
import json
import re
import os
import glob
from pathlib import Path
from loguru import logger

# 避免循环导入
if TYPE_CHECKING:
    from .article import Article, Section

# 泛型类型变量，用于类型提示
T = TypeVar('T')

class JsonModelLoader(Generic[T]):
    """通用 JSON 配置加载器

    用于从特定目录加载 JSON 配置文件并转换为 Pydantic 模型
    """

    @staticmethod
    def load_model(json_path: str, model_class: Type[T]) -> Optional[T]:
        """从 JSON 文件加载单个模型

        Args:
            json_path: JSON 文件路径
            model_class: Pydantic 模型类

        Returns:
            Optional[T]: 模型实例，如果加载失败则返回 None
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return model_class(**data)
        except Exception as e:
            logger.error(f"加载 JSON 文件 {json_path} 失败: {str(e)}")
            return None

    @staticmethod
    def load_models_from_directory(directory: str, model_class: Type[T]) -> Dict[str, T]:
        """从目录加载多个模型

        Args:
            directory: 包含 JSON 文件的目录路径
            model_class: Pydantic 模型类

        Returns:
            Dict[str, T]: 模型字典，键为模型 ID
        """
        results = {}

        # 确保目录存在
        if not os.path.exists(directory):
            logger.warning(f"目录 {directory} 不存在")
            return results

        # 加载目录中的所有 JSON 文件
        json_files = glob.glob(os.path.join(directory, '*.json'))
        for json_file in json_files:
            try:
                model_instance = JsonModelLoader.load_model(json_file, model_class)
                if model_instance:
                    # 使用文件名（不含扩展名）作为键名，除非模型有 id 属性
                    model_id = getattr(model_instance, 'id', Path(json_file).stem)
                    results[model_id] = model_instance
            except Exception as e:
                logger.error(f"处理 {json_file} 时出错: {str(e)}")

        return results

    @staticmethod
    def get_base_directory() -> str:
        """获取模型基础目录

        Returns:
            str: 基础目录路径
        """
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return current_dir


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
                repaired_text = repair_json(response_text)
                data = json.loads(repaired_text)

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
                # 动态导入解决循环依赖
                import importlib
                article_module = importlib.import_module('.article', package='core.models')
                Section = getattr(article_module, 'Section')

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
                logger.error("文章标签不足3个")
                return False

            return True

        except Exception as e:
            logger.error(f"验证文章数据时发生错误: {str(e)}")
            return False
