"""文章风格适配工具"""
from typing import List, Dict, Optional, ClassVar, TYPE_CHECKING
import re
from core.tools.base import BaseTool, ToolResult
from core.tools.nlp_tools.processor import NLPAggregator

# 避免循环导入
if TYPE_CHECKING:
    from core.models.article import Article
from core.models.platform import Platform
from core.models.article_style import StyleRules

class StyleAdapter:
    """平台风格适配器"""

    # 类级别的缓存
    _nlp_instance: ClassVar[Optional[NLPAggregator]] = None
    _instances: ClassVar[Dict[str, 'StyleAdapter']] = {}

    @classmethod
    def get_instance(cls, platform: Platform) -> 'StyleAdapter':
        """获取风格适配器实例（工厂方法）

        Args:
            platform: 目标平台

        Returns:
            StyleAdapter: 风格适配器实例
        """
        platform_id = platform.id
        if platform_id not in cls._instances:
            cls._instances[platform_id] = cls(platform)
        return cls._instances[platform_id]

    @classmethod
    def clear_cache(cls):
        """清除所有缓存的实例"""
        cls._instances.clear()
        cls._nlp_instance = None

    def __init__(self, platform: Platform):
        """初始化风格适配器

        Args:
            platform: 目标平台
        """
        self.platform = platform
        self.style_rules = platform.style_rules
        if not self.style_rules:
            raise ValueError(f"平台 {platform.name} 未配置风格规则")

        # 使用缓存的NLP实例
        if self.__class__._nlp_instance is None:
            self.__class__._nlp_instance = NLPAggregator()
        self.nlp = self.__class__._nlp_instance

    async def health_check(self) -> bool:
        """检查适配器健康状态

        Returns:
            bool: 是否健康
        """
        try:
            # 检查NLP工具
            if not await self.nlp.health_check():
                return False

            # 检查风格规则
            if not self.style_rules or not self.style_rules.is_valid():
                return False

            return True

        except Exception:
            return False

    async def adapt_article(self, article: 'Article') -> 'Article':
        """适配文章风格

        Args:
            article: 原始文章

        Returns:
            Article: 适配后的文章
        """
        # 1. 调整语气和表达
        article = await self._adapt_tone(article)

        # 2. 调整格式
        article = await self._adapt_format(article)

        # 3. 优化结构
        article = await self._adapt_structure(article)

        # 4. SEO优化
        article = await self._adapt_seo(article)

        return article

    async def _adapt_tone(self, article: 'Article') -> 'Article':
        """调整文章语气

        1. 根据平台风格调整语气
        2. 调整正式程度
        3. 处理情感表达
        """
        # 获取语气规则
        tone = self.style_rules.tone
        formality = self.style_rules.formality
        emotion = self.style_rules.emotion

        # TODO: 使用 NLP 工具调整语气
        # 1. 分析当前语气
        # 2. 根据目标语气进行调整
        # 3. 调整正式程度
        # 4. 添加/移除情感表达

        return article

    async def _adapt_format(self, article: 'Article') -> 'Article':
        """调整文章格式

        1. 处理代码块
        2. 处理表情符号
        3. 调整图文比例
        4. 控制图片数量
        """
        # 获取格式规则
        code_block = self.style_rules.code_block
        emoji = self.style_rules.emoji
        image_ratio = self.style_rules.image_text_ratio
        max_images = self.style_rules.max_image_count

        # 处理代码块
        if not code_block:
            # 移除代码块,转换为文本描述
            pass

        # 处理表情
        if not emoji:
            # 移除表情符号
            pass
        elif emoji and not article.has_emoji:
            # 适当添加表情
            pass

        # 处理图片
        current_images = len(article.images)
        if current_images > max_images:
            # 删除多余图片
            article.images = article.images[:max_images]

        # 调整图文比例
        current_ratio = len(article.images) / (len(article.content) + 1)
        if abs(current_ratio - image_ratio) > 0.1:
            # 需要调整图文比例
            if current_ratio < image_ratio:
                # 需要增加图片
                pass
            else:
                # 需要增加文字或减少图片
                pass

        return article

    async def _adapt_structure(self, article: 'Article') -> 'Article':
        """调整文章结构

        1. 调整段落长度
        2. 调整段落数量
        3. 调整章节数量
        """
        # 获取结构规则
        min_para_len = self.style_rules.min_paragraph_length
        max_para_len = self.style_rules.max_paragraph_length
        para_range = self.style_rules.paragraph_count_range
        section_range = self.style_rules.section_count_range

        # 分析当前结构
        paragraphs = article.content.split('\n\n')
        sections = [s for s in article.content.split('\n') if s.startswith('#')]

        # 调整段落长度
        new_paragraphs = []
        for para in paragraphs:
            if len(para) < min_para_len:
                # 扩展段落
                pass
            elif len(para) > max_para_len:
                # 拆分段落
                pass
            else:
                new_paragraphs.append(para)

        # 调整段落数量
        current_paras = len(new_paragraphs)
        if current_paras < para_range[0]:
            # 增加段落
            pass
        elif current_paras > para_range[1]:
            # 减少段落
            pass

        # 调整章节数量
        current_sections = len(sections)
        if current_sections < section_range[0]:
            # 增加章节
            pass
        elif current_sections > section_range[1]:
            # 合并章节
            pass

        return article

    async def _adapt_seo(self, article: 'Article') -> 'Article':
        """优化SEO

        1. 关键词密度
        2. 标题优化
        3. 元标签优化
        """
        # 获取SEO规则
        keyword_density = self.style_rules.keyword_density
        has_seo_title = self.style_rules.seo_title
        has_meta_desc = self.style_rules.meta_description

        # 关键词密度优化
        if article.keywords:
            # 计算当前密度
            content = article.content.lower()
            total_words = len(content.split())

            # 检查每个关键词的密度
            for keyword in article.keywords:
                keyword = keyword.lower()
                count = content.count(keyword)
                current_density = count / max(1, total_words)

                # 调整密度
                if current_density < keyword_density:
                    # 增加关键词出现次数
                    pass
                elif current_density > keyword_density * 1.5:
                    # 减少关键词过度使用
                    pass

        # 标题SEO优化
        if has_seo_title and article.keywords:
            # 确保标题包含主要关键词
            main_keyword = article.keywords[0] if article.keywords else ""
            if main_keyword and main_keyword.lower() not in article.title.lower():
                # 尝试将关键词融入标题
                pass

        # 元描述优化
        if has_meta_desc:
            # 确保摘要符合SEO要求
            if len(article.summary) < 50:
                # 扩展摘要
                pass
            elif len(article.summary) > 160:
                # 缩减摘要
                pass

            # 确保摘要包含关键词
            if article.keywords and not any(k.lower() in article.summary.lower() for k in article.keywords):
                # 将关键词融入摘要
                pass

        return article
