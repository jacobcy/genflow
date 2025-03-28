"""风格工厂工具

提供文章风格创建和分析相关的功能，包括：
- 从文本描述创建临时风格
- 根据关键词分析风格特征
- 匹配现有风格
"""

from typing import Dict, Optional, Any, List
import uuid
from loguru import logger


class StyleFactory:
    """风格工厂工具类

    提供创建和分析文章风格的工具方法。
    """

    @staticmethod
    def create_style_from_description(description: str, options: Optional[Dict[str, Any]] = None) -> Any:
        """根据文本描述创建风格对象

        分析描述中的关键词，创建一个临时风格对象。

        Args:
            description: 风格的文本描述
            options: 其他选项和风格属性

        Returns:
            Any: 创建的风格对象
        """
        if not description:
            # 导入放在函数内部以避免循环导入
            from ..article_style import get_default_style
            return get_default_style()

        # 尝试匹配现有风格
        matched_style = StyleFactory.match_existing_style(description)
        if matched_style:
            logger.info(f"从描述匹配到现有风格: {matched_style.name}")
            return matched_style

        # 创建临时风格
        return StyleFactory._create_temp_style(description, options)

    @staticmethod
    def match_existing_style(text: str) -> Optional[Any]:
        """尝试匹配现有风格

        首先尝试精确匹配风格名称，再尝试模糊匹配名称、描述和类型。

        Args:
            text: 风格名称或描述文本

        Returns:
            Optional[Any]: 匹配到的风格对象，如果没有匹配到则返回None
        """
        # 导入放在函数内部以避免循环导入
        from ..article_style import load_article_styles

        # 加载所有风格
        styles = load_article_styles()
        text_lower = text.lower()

        # 1. 精确匹配 - 检查是否有完全匹配的风格名称
        if text in styles:
            return styles[text]

        # 2. 模糊匹配 - 检查名称、描述和类型
        for style_obj in styles.values():
            # 检查风格名称
            if text_lower in style_obj.name.lower():
                return style_obj

            # 检查风格描述
            if style_obj.description and text_lower in style_obj.description.lower():
                return style_obj

            # 检查风格类型
            if style_obj.type and text_lower in style_obj.type.lower():
                return style_obj

        return None

    @staticmethod
    def _create_temp_style(text: str, options: Optional[Dict[str, Any]] = None) -> Any:
        """创建临时风格对象

        根据文本描述和选项创建一个临时风格对象。

        Args:
            text: 风格描述文本
            options: 其他选项和风格属性

        Returns:
            Any: 创建的临时风格对象
        """
        # 导入放在函数内部以避免循环导入
        from ..article_style import ArticleStyle

        # 生成唯一风格名称
        style_name = options.get("style_name") if options and "style_name" in options else f"temp_style_{uuid.uuid4().hex[:8]}"

        # 分析文本中的风格特征
        style_attrs = StyleFactory._analyze_style_description(text)
        style_attrs["name"] = style_name
        style_attrs["description"] = text

        # 合并用户提供的选项
        if options:
            for key, value in options.items():
                if key in style_attrs:
                    style_attrs[key] = value

        # 创建并返回风格对象
        logger.info(f"从描述创建临时风格: {style_name}")
        return ArticleStyle(**style_attrs)

    @staticmethod
    def _analyze_style_description(text: str) -> Dict[str, Any]:
        """分析风格描述文本

        根据文本中的关键词分析风格特征。

        Args:
            text: 风格描述文本

        Returns:
            Dict[str, Any]: 风格属性字典
        """
        text_lower = text.lower()

        # 默认风格属性
        style_attrs = {
            "type": "custom",
            "tone": "neutral",
            "formality": 3,
            "emotion": False,
            "emoji": False,
            "target_audience": "通用受众",
            "content_types": ["article", "blog"]
        }

        # 风格类型和语气分析
        if any(keyword in text_lower for keyword in ["正式", "学术", "专业", "严谨"]):
            style_attrs["type"] = "formal"
            style_attrs["tone"] = "professional"
            style_attrs["formality"] = 5
        elif any(keyword in text_lower for keyword in ["随意", "休闲", "轻松", "活泼"]):
            style_attrs["type"] = "casual"
            style_attrs["tone"] = "friendly"
            style_attrs["formality"] = 2
        elif any(keyword in text_lower for keyword in ["技术", "科技"]):
            style_attrs["type"] = "technical"
            style_attrs["tone"] = "informative"
            style_attrs["formality"] = 4
        elif any(keyword in text_lower for keyword in ["幽默", "诙谐", "风趣"]):
            style_attrs["type"] = "humorous"
            style_attrs["tone"] = "playful"
            style_attrs["formality"] = 2

        # 情感和表情符号分析
        if any(keyword in text_lower for keyword in ["情感", "感性", "共鸣"]):
            style_attrs["emotion"] = True
        if any(keyword in text_lower for keyword in ["表情", "emoji", "符号"]):
            style_attrs["emoji"] = True

        # 目标受众分析
        if any(keyword in text_lower for keyword in ["专业", "技术", "行业"]):
            style_attrs["target_audience"] = "专业人士"
        elif any(keyword in text_lower for keyword in ["初学者", "新手", "入门"]):
            style_attrs["target_audience"] = "初学者"

        # 内容类型分析
        content_types = []
        if any(keyword in text_lower for keyword in ["博客", "blog"]):
            content_types.append("blog")
        if any(keyword in text_lower for keyword in ["论文", "paper"]):
            content_types.append("paper")
        if any(keyword in text_lower for keyword in ["教程", "tutorial"]):
            content_types.append("tutorial")
        if any(keyword in text_lower for keyword in ["新闻", "news"]):
            content_types.append("news")

        if content_types:
            style_attrs["content_types"] = content_types

        return style_attrs
