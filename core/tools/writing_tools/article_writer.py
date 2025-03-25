"""文章生成模块"""
from typing import List, Dict, Optional, Type, Any, ClassVar
from dataclasses import dataclass
import logging
from datetime import datetime
from core.tools.base import BaseTool, ToolResult
from core.tools.nlp_tools.processor import NLPAggregator
from core.tools.content_collectors.collector import ContentCollector
from core.tools.style_tools.adapter import StyleAdapter
from core.models.platform import Platform

@dataclass
class ArticleSection:
    """文章段落结构"""
    title: str
    content: str
    references: List[Dict]  # 引用的来源
    
@dataclass
class ArticleOutline:
    """文章大纲结构"""
    title: str
    sections: List[Dict]  # 包含标题和子标题
    keywords: List[str]
    target_length: int
    
@dataclass
class ArticleStyle:
    """文章风格定义"""
    tone: str  # 语气：专业、轻松、严肃等
    format: str  # 格式：新闻、博客、评论等
    target_audience: str  # 目标受众
    language_level: str  # 语言难度

@dataclass
class ResearchResult:
    """研究结果结构"""
    content: str  # 收集到的原始内容
    key_points: List[Dict]  # 关键信息点
    references: List[Dict]  # 引用来源
    
class ArticleWriter:
    """文章生成器"""
    
    # 类级别的工具缓存
    _nlp_instance: ClassVar[Optional[NLPAggregator]] = None
    _style_adapters: ClassVar[Dict[str, StyleAdapter]] = {}
    
    def __init__(self, 
                 config: Dict,
                 content_collector: ContentCollector,
                 llm_client: Any,
                 platform: Platform):
        """初始化
        
        Args:
            config: 配置对象
            content_collector: 内容采集器实例
            llm_client: 语言模型客户端
            platform: 目标平台
        """
        if not isinstance(content_collector, ContentCollector):
            raise TypeError("content_collector must be an instance of ContentCollector")
            
        self.config = config
        self.collector = content_collector
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
        
        # 使用工厂方法初始化工具
        self.nlp = NLPAggregator.get_instance()
        self.style_adapter = StyleAdapter.get_instance(platform)
        
    @classmethod
    def _get_nlp_instance(cls) -> NLPAggregator:
        """获取NLP工具实例（单例模式）
        
        Returns:
            NLPAggregator: NLP工具实例
        """
        if cls._nlp_instance is None:
            cls._nlp_instance = NLPAggregator()
        return cls._nlp_instance
    
    @classmethod
    def _get_style_adapter(cls, platform: Platform) -> StyleAdapter:
        """获取风格适配器实例（按平台缓存）
        
        Args:
            platform: 目标平台
            
        Returns:
            StyleAdapter: 风格适配器实例
        """
        platform_id = platform.id
        if platform_id not in cls._style_adapters:
            cls._style_adapters[platform_id] = StyleAdapter(platform)
        return cls._style_adapters[platform_id]
    
    @classmethod
    def clear_cache(cls):
        """清除工具实例缓存"""
        cls._nlp_instance = None
        cls._style_adapters.clear()
        
    async def _check_tools_health(self) -> bool:
        """检查工具实例的健康状态
        
        Returns:
            bool: 工具是否正常
        """
        try:
            # 检查NLP工具
            if not await self.nlp.health_check():
                self.logger.error("NLP工具异常")
                self._nlp_instance = None  # 清除实例以便重新初始化
                return False
                
            # 检查风格适配器
            if not await self.style_adapter.health_check():
                self.logger.error("风格适配器异常")
                platform_id = self.style_adapter.platform.id
                self._style_adapters.pop(platform_id, None)  # 清除实例以便重新初始化
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"工具健康检查失败: {str(e)}")
            return False

    async def generate_article(self, 
                             topic: str,
                             style: ArticleStyle,
                             sources: Optional[List[str]] = None) -> Dict:
        """生成文章的主流程
        
        Args:
            topic: 文章主题
            style: 文章风格配置
            sources: 可选的指定信息源
            
        Returns:
            Dict: 生成的文章信息
        """
        try:
            # 检查工具健康状态
            if not await self._check_tools_health():
                # 如果工具异常，尝试重新初始化
                self.nlp = self._get_nlp_instance()
                self.style_adapter = self._get_style_adapter(self.style_adapter.platform)
                
            # 1. 收集和整理相关知识
            research = await self._collect_research(topic, sources)
            
            # 2. 生成文章大纲
            outline = await self._generate_outline(topic, research, style)
            
            # 3. 分段生成内容
            sections = await self._generate_sections(outline, research, style)
            
            # 4. 优化和润色
            raw_article = self._combine_sections(sections)
            
            # 5. 使用 NLP 工具进行初步优化
            nlp_result = await self.nlp.execute(raw_article)
            if not nlp_result.success:
                self.logger.warning(f"NLP优化失败: {nlp_result.error}")
                processed_article = raw_article
            else:
                processed_article = nlp_result.data
            
            # 6. 使用风格适配器进行平台适配
            adapted_article = await self.style_adapter.adapt_article(processed_article)
            
            # 7. 最终润色
            final_article = await self._polish_article(adapted_article, style)
            
            # 8. 整理元数据
            metadata = self._prepare_metadata(topic, outline, style)
            
            return {
                'title': outline.title,
                'content': final_article,
                'outline': outline.__dict__,
                'references': research.references,
                'metadata': metadata
            }
            
        except Exception as e:
            self.logger.error(f"文章生成失败: {str(e)}")
            raise
            
    async def _collect_research(self, topic: str, sources: Optional[List[str]] = None) -> ResearchResult:
        """收集研究资料
        
        Args:
            topic: 主题
            sources: 可选的指定信息源
            
        Returns:
            ResearchResult: 研究结果
        """
        try:
            # 使用 ContentCollector 收集内容
            collection_result = await self.collector.execute(topic, sources)
            if not collection_result.success:
                raise ValueError(f"内容收集失败: {collection_result.error}")
                
            raw_content = collection_result.data
            
            # 使用 NLP 工具提取关键信息
            key_points_result = await self.nlp.extract_key_points(raw_content)
            if not key_points_result.success:
                raise ValueError(f"关键信息提取失败: {key_points_result.error}")
                
            key_points = key_points_result.data
            
            # 验证信息准确性
            verified_points = await self.llm.verify_facts(key_points)
            
            # 提取引用信息
            references = [point.get('source', {}) for point in verified_points if 'source' in point]
            
            return ResearchResult(
                content=raw_content,
                key_points=verified_points,
                references=references
            )
            
        except Exception as e:
            self.logger.error(f"研究资料收集失败: {str(e)}")
            raise
        
    async def _generate_outline(self, 
                              topic: str, 
                              research: ResearchResult,
                              style: ArticleStyle) -> ArticleOutline:
        """生成文章大纲
        
        Args:
            topic: 主题
            research: 研究结果
            style: 文章风格
            
        Returns:
            ArticleOutline: 文章大纲
        """
        try:
            # 1. 使用NLP工具分析主题
            topic_analysis = await self.nlp.analyze_topic(topic)
            if not topic_analysis.success:
                self.logger.warning(f"主题分析失败: {topic_analysis.error}")
                topic_keywords = []
            else:
                topic_keywords = topic_analysis.data.get('keywords', [])
            
            # 2. 分析研究内容关键词
            content_analysis = await self.nlp.analyze_content(research.content)
            if not content_analysis.success:
                self.logger.warning(f"内容分析失败: {content_analysis.error}")
                content_keywords = []
            else:
                content_keywords = content_analysis.data.get('keywords', [])
            
            # 3. 合并关键词
            all_keywords = list(set(topic_keywords + content_keywords))
            
            # 4. 生成大纲结构
            outline_structure = await self.llm.generate_outline(
                topic=topic,
                key_points=research.key_points,
                keywords=all_keywords,
                style=style
            )
            
            # 5. 使用NLP优化大纲结构
            outline_optimization = await self.nlp.optimize_structure(str(outline_structure))
            if outline_optimization.success:
                optimized_structure = outline_optimization.data
            else:
                self.logger.warning(f"大纲优化失败: {outline_optimization.error}")
                optimized_structure = outline_structure
            
            # 6. 最终LLM优化
            final_outline = await self.llm.optimize_outline(optimized_structure)
            
            return ArticleOutline(
                title=final_outline['title'],
                sections=final_outline['sections'],
                keywords=all_keywords,
                target_length=self.config.get('target_length', 2000)
            )
            
        except Exception as e:
            self.logger.error(f"大纲生成失败: {str(e)}")
            raise
        
    async def _generate_sections(self,
                               outline: ArticleOutline,
                               research: ResearchResult,
                               style: ArticleStyle) -> List[ArticleSection]:
        """生成文章各个段落
        
        Args:
            outline: 文章大纲
            research: 研究结果
            style: 文章风格
            
        Returns:
            List[ArticleSection]: 文章段落列表
        """
        sections = []
        
        for section in outline.sections:
            try:
                # 1. 从研究结果中筛选相关信息
                section_points = [
                    point for point in research.key_points 
                    if any(kw in section['title'].lower() for kw in point.get('keywords', []))
                ]
                
                # 2. 使用NLP分析段落主题
                section_analysis = await self.nlp.analyze_topic(section['title'])
                if section_analysis.success:
                    section_focus = section_analysis.data.get('focus_points', [])
                else:
                    self.logger.warning(f"段落主题分析失败: {section_analysis.error}")
                    section_focus = []
                
                # 3. 生成段落内容
                content = await self.llm.generate_section(
                    title=section['title'],
                    key_points=section_points,
                    focus_points=section_focus,
                    style=style
                )
                
                # 4. 使用NLP优化段落内容
                content_optimization = await self.nlp.optimize_text(content)
                if content_optimization.success:
                    optimized_content = content_optimization.data
                else:
                    self.logger.warning(f"段落优化失败: {content_optimization.error}")
                    optimized_content = content
                
                # 5. 提取引用信息
                references = [
                    point.get('source', {})
                    for point in section_points
                    if 'source' in point
                ]
                
                # 6. 使用NLP检查段落连贯性
                coherence_check = await self.nlp.check_coherence(optimized_content)
                if not coherence_check.success:
                    self.logger.warning(f"段落连贯性检查失败: {coherence_check.error}")
                
                sections.append(ArticleSection(
                    title=section['title'],
                    content=optimized_content,
                    references=references
                ))
                
            except Exception as e:
                self.logger.error(f"段落 '{section['title']}' 生成失败: {str(e)}")
                continue
            
        return sections
        
    async def _polish_article(self,
                            article: str,
                            style: ArticleStyle) -> str:
        """优化和润色文章
        
        Args:
            article: 文章内容
            style: 文章风格
            
        Returns:
            str: 优化后的文章内容
        """
        try:
            # 1. 使用NLP进行语言优化
            language_optimization = await self.nlp.optimize_language(
                text=article,
                style=style
            )
            if language_optimization.success:
                optimized_text = language_optimization.data
            else:
                self.logger.warning(f"语言优化失败: {language_optimization.error}")
                optimized_text = article
            
            # 2. 使用LLM优化表达
            polished_text = await self.llm.polish_text(
                text=optimized_text,
                style=style
            )
            
            # 3. 使用NLP检查语法和用词
            grammar_check = await self.nlp.check_grammar(polished_text)
            if grammar_check.success and grammar_check.data.get('issues'):
                # 如果发现语法问题，使用LLM修复
                fixes = grammar_check.data['issues']
                corrected_text = await self.llm.fix_grammar(polished_text, fixes)
            else:
                corrected_text = polished_text
            
            # 4. 使用NLP检查文章结构
            structure_check = await self.nlp.check_structure(corrected_text)
            if not structure_check.success:
                self.logger.warning(f"结构检查失败: {structure_check.error}")
            
            # 5. 最终校对
            final_text = await self.llm.proofread(corrected_text)
            
            # 6. 使用NLP进行最终质量评估
            quality_check = await self.nlp.evaluate_quality(final_text)
            if quality_check.success:
                quality_score = quality_check.data.get('score', 0)
                if quality_score < 0.8:  # 如果质量分数低于0.8
                    self.logger.warning(f"文章质量评分较低: {quality_score}")
            
            return final_text
            
        except Exception as e:
            self.logger.error(f"文章润色失败: {str(e)}")
            return article  # 如果润色过程失败，返回原文
        
    def _prepare_metadata(self,
                         topic: str,
                         outline: ArticleOutline,
                         style: ArticleStyle) -> Dict:
        """准备文章元数据
        
        Args:
            topic: 主题
            outline: 大纲
            style: 风格
            
        Returns:
            Dict: 元数据
        """
        return {
            'topic': topic,
            'keywords': outline.keywords,
            'style': style.__dict__,
            'generated_at': datetime.now().isoformat(),
            'word_count': outline.target_length
        }
        
    def _combine_sections(self, sections: List[ArticleSection]) -> str:
        """合并文章段落
        
        Args:
            sections: 段落列表
            
        Returns:
            str: 合并后的文章内容
        """
        article_parts = []
        
        for section in sections:
            article_parts.append(f"## {section.title}\n\n{section.content}\n")
            
        return "\n".join(article_parts)