"""风格管理模块

提供风格对象的加载、创建和管理功能。
简化的风格管理器实现，不依赖复杂组件。
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import os
import json
from datetime import datetime
from loguru import logger


class ArticleStyle:
    """文章风格模型

    定义文章的风格特性，包括语气、格式和结构等。
    """

    def __init__(self,
                 name: str,
                 type: str = "general",
                 description: str = "",
                 tone: str = "neutral",
                 formality: int = 3,
                 content_types: Optional[List[str]] = None,
                 **kwargs):
        """初始化风格

        Args:
            name: 风格名称
            type: 风格类型
            description: 风格描述
            tone: 语气
            formality: 正式程度（1-5）
            content_types: 适用的内容类型列表
        """
        self.name = name
        self.type = type
        self.description = description
        self.tone = tone
        self.formality = formality
        self.content_types = content_types or []

        # 保存其它属性
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        Returns:
            Dict[str, Any]: 风格属性字典
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def is_compatible_with_content_type(self, content_type: str) -> bool:
        """检查是否与内容类型兼容

        Args:
            content_type: 内容类型名称

        Returns:
            bool: 是否兼容
        """
        # 空列表表示通用风格，兼容所有内容类型
        if not self.content_types:
            return True

        # 直接匹配
        if content_type in self.content_types:
            return True

        # 模糊匹配
        for supported_type in self.content_types:
            if content_type in supported_type or supported_type in content_type:
                return True

        return False


class StyleFactory:
    """风格工厂类

    负责从描述创建风格对象。
    """

    @staticmethod
    def create_style_from_description(description: str, options: Optional[Dict[str, Any]] = None) -> ArticleStyle:
        """从描述创建风格

        Args:
            description: 描述文本
            options: 额外选项

        Returns:
            ArticleStyle: 创建的风格对象
        """
        options = options or {}  # 如果 options 为 None，则初始化为空字典

        if not description:
            name = options.get("style_name", f"default_style_{datetime.now().strftime('%Y%m%d%H%M%S')}")
            return ArticleStyle(name=name)

        # 分析描述文本
        style_attrs = StyleFactory._analyze_style_description(description)

        # 设置名称
        style_name = options.get("style_name", f"style_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        style_attrs["name"] = style_name
        style_attrs["description"] = description

        # 合并选项
        for key, value in options.items():
            style_attrs[key] = value

        # 创建风格
        return ArticleStyle(**style_attrs)

    @staticmethod
    def _analyze_style_description(text: str) -> Dict[str, Any]:
        """分析风格描述文本

        Args:
            text: 描述文本

        Returns:
            Dict[str, Any]: 分析结果
        """
        text_lower = text.lower()

        # 默认属性
        result = {
            "type": "custom",
            "tone": "neutral",
            "formality": 3,
            "content_types": []
        }

        # 分析风格类型
        if any(word in text_lower for word in ["正式", "专业", "学术"]):
            result["type"] = "formal"
            result["tone"] = "professional"
            result["formality"] = 5
        elif any(word in text_lower for word in ["随意", "休闲", "轻松"]):
            result["type"] = "casual"
            result["tone"] = "friendly"
            result["formality"] = 2
        elif any(word in text_lower for word in ["技术", "科技"]):
            result["type"] = "technical"
            result["tone"] = "informative"
            result["formality"] = 4

        return result


class StyleManager:
    """风格管理器

    管理文章风格的加载、存储和检索。
    """

    _styles: Dict[str, ArticleStyle] = {}
    _default_style: Optional[ArticleStyle] = None
    _style_dir: str = ""
    _initialized: bool = False

    @classmethod
    def initialize(cls, use_db: bool = False) -> None:
        """初始化管理器

        Args:
            use_db: 是否使用数据库，默认为False
        """
        if cls._initialized:
            return

        # 设置风格目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cls._style_dir = os.path.join(current_dir, "../../../config/styles")

        # 确保目录存在
        os.makedirs(cls._style_dir, exist_ok=True)

        # 加载风格
        cls.load_styles()

        # 创建默认风格
        if not cls._default_style:
            cls._default_style = ArticleStyle(
                name="default_style",
                type="general",
                description="默认通用风格",
                tone="neutral",
                formality=3
            )
            cls._styles[cls._default_style.name] = cls._default_style

        cls._initialized = True
        logger.info(f"风格管理器初始化完成，已加载 {len(cls._styles)} 个风格")

    @classmethod
    def load_styles(cls) -> None:
        """从文件加载风格"""
        try:
            style_files = [f for f in os.listdir(cls._style_dir) if f.endswith('.json')]

            for file_name in style_files:
                file_path = os.path.join(cls._style_dir, file_name)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        style_data = json.load(f)

                    style = ArticleStyle(**style_data)
                    cls._styles[style.name] = style

                    # 设置第一个加载的风格为默认风格
                    if not cls._default_style:
                        cls._default_style = style

                    logger.debug(f"已加载风格: {style.name}")
                except Exception as e:
                    logger.error(f"加载风格文件 {file_name} 失败: {str(e)}")

        except Exception as e:
            logger.error(f"加载风格目录失败: {str(e)}")

    @classmethod
    def get_article_style(cls, style_name: str) -> Optional[ArticleStyle]:
        """获取指定名称的风格

        Args:
            style_name: 风格名称

        Returns:
            Optional[ArticleStyle]: 风格对象或None
        """
        if not cls._initialized:
            cls.initialize()

        return cls._styles.get(style_name)

    @classmethod
    def get_default_style(cls) -> ArticleStyle:
        """获取默认风格

        Returns:
            ArticleStyle: 默认风格对象
        """
        if not cls._initialized:
            cls.initialize()

        # 确保返回的是ArticleStyle对象
        if cls._default_style is None:
            # 如果默认风格为None，创建一个新的默认风格
            cls._default_style = ArticleStyle(
                name="default_style",
                type="general",
                description="默认通用风格",
                tone="neutral",
                formality=3
            )
            cls._styles[cls._default_style.name] = cls._default_style

        return cls._default_style

    @classmethod
    def get_all_styles(cls) -> Dict[str, ArticleStyle]:
        """获取所有风格

        Returns:
            Dict[str, ArticleStyle]: 风格字典，键为风格名称
        """
        if not cls._initialized:
            cls.initialize()

        return cls._styles

    @classmethod
    def find_style_by_type(cls, style_type: str) -> Optional[ArticleStyle]:
        """根据类型查找风格

        Args:
            style_type: 风格类型

        Returns:
            Optional[ArticleStyle]: 匹配的风格对象或None
        """
        if not cls._initialized:
            cls.initialize()

        for style in cls._styles.values():
            if style.type == style_type:
                return style

        return None

    @classmethod
    def create_style_from_description(cls, description: str, options: Optional[Dict[str, Any]] = None) -> ArticleStyle:
        """从描述创建风格

        Args:
            description: 描述文本
            options: 额外选项

        Returns:
            ArticleStyle: 创建的风格对象
        """
        if not cls._initialized:
            cls.initialize()

        style = StyleFactory.create_style_from_description(description, options)

        # 保存到内存
        if style.name not in cls._styles:
            cls._styles[style.name] = style

        return style

    @classmethod
    def save_style(cls, style: ArticleStyle) -> bool:
        """保存风格

        Args:
            style: 风格对象

        Returns:
            bool: 是否成功保存
        """
        if not cls._initialized:
            cls.initialize()

        try:
            # 保存到内存
            cls._styles[style.name] = style

            # 保存到文件
            file_path = os.path.join(cls._style_dir, f"{style.name}.json")

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(style.to_dict(), f, ensure_ascii=False, indent=2)

            logger.info(f"已保存风格: {style.name}")
            return True
        except Exception as e:
            logger.error(f"保存风格失败: {str(e)}")
            return False
