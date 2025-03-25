from typing import Dict, List, Optional, ClassVar
import jieba
import jieba.analyse
from core.tools.base import BaseTool, ToolResult

class ChineseNLPTool(BaseTool):
    """中文自然语言处理工具"""
    name = "chinese_nlp"
    description = "提供中文分词、关键词提取、分句等基础功能"
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        # jieba 不需要额外下载模型
    
    async def execute(self, text: str, keyword_count: int = 5) -> ToolResult:
        """执行中文文本分析
        
        Args:
            text: 要分析的文本
            keyword_count: 提取的关键词数量，默认5个
            
        Returns:
            ToolResult: 包含以下数据：
            - words: 分词结果列表
            - sentences: 分句结果列表
            - keywords: 关键词列表
        """
        try:
            # 分词
            words = jieba.lcut(text)
            
            # 分句（按常见中文标点符号分割）
            sentences = []
            current = ""
            for char in text:
                current += char
                if char in ['。', '！', '？', '…']:
                    if current.strip():
                        sentences.append(current.strip())
                    current = ""
            if current.strip():
                sentences.append(current.strip())
            
            # 提取关键词（使用 jieba 的 TF-IDF 实现）
            keywords = jieba.analyse.extract_tags(text, topK=keyword_count)
            
            return self._create_success_result({
                'words': words,
                'sentences': sentences,
                'keywords': keywords
            })
        except Exception as e:
            return self._create_error_result(str(e))

class NLPAggregator(BaseTool):
    """NLP工具聚合器"""
    name = "nlp_aggregator"
    description = "中文自然语言处理工具集合，提供分词、关键词提取、分句等功能"
    
    _instance: ClassVar[Optional['NLPAggregator']] = None
    
    @classmethod
    def get_instance(cls) -> 'NLPAggregator':
        """获取NLP工具实例（单例模式）"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def clear_cache(cls):
        """清除缓存的实例"""
        cls._instance = None
    
    def __init__(self, config: Dict = None):
        """初始化NLP工具"""
        super().__init__(config)
        self.chinese_nlp = ChineseNLPTool(config)
    
    async def execute(self, text: str, keyword_count: int = 5) -> ToolResult:
        """执行中文文本分析
        
        Args:
            text: 要分析的文本
            keyword_count: 提取的关键词数量，默认5个
            
        Returns:
            ToolResult: 包含以下数据：
            - words: 分词结果列表
            - sentences: 分句结果列表
            - keywords: 关键词列表
        """
        result = await self.chinese_nlp.execute(text, keyword_count)
        if not result.success:
            return self._create_error_result("中文处理失败：" + result.message)
        
        return result  # 直接返回 ChineseNLPTool 的结果 