"""审核工具实现"""
from typing import Dict, List, Optional, ClassVar, Tuple, Any
import jieba
import difflib
import json
import os
import re
import nltk
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
import openai
from core.tools.base import BaseTool, ToolResult

@dataclass
class ReviewResult:
    """审核结果"""
    is_original: bool = True  # 是否原创
    similarity_score: float = 0.0  # 相似度分数
    similar_segments: List[Tuple[str, str, float]] = None  # 相似片段列表
    is_ai_generated: bool = False  # 是否AI生成
    ai_probability: float = 0.0  # AI生成概率
    sensitive_words: List[Tuple[str, int]] = None  # 敏感词列表
    review_time: datetime = None  # 审核时间
    
    def __post_init__(self):
        self.similar_segments = self.similar_segments or []
        self.sensitive_words = self.sensitive_words or []
        self.review_time = self.review_time or datetime.now()

class PlagiarismChecker(BaseTool):
    """查重工具"""
    name = "plagiarism_checker"
    description = "检查文本是否存在抄袭"
    
    @classmethod
    def get_instance(cls) -> 'PlagiarismChecker':
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
        
    async def execute(self, text: str, compare_texts: List[str] = None) -> ToolResult:
        """执行查重检查"""
        try:
            result = ReviewResult()
            
            if not compare_texts:
                return self._create_success_result(result)
                
            max_similarity = 0.0
            similar_segments = []
            
            segments = [text[i:i+100] for i in range(0, len(text), 50)]
            for segment in segments:
                for compare_text in compare_texts:
                    similarity = difflib.SequenceMatcher(
                        None, segment, compare_text
                    ).ratio()
                    
                    if similarity > 0.8:
                        similar_segments.append((segment, compare_text, similarity))
                        max_similarity = max(max_similarity, similarity)
            
            result.similarity_score = max_similarity
            result.similar_segments = similar_segments
            result.is_original = max_similarity < 0.5
            
            return self._create_success_result(result)
        except Exception as e:
            return self._create_error_result(str(e))

class StatisticalAIDetector(BaseTool):
    """基于统计的AI检测工具"""
    name = "statistical_ai_detector"
    description = "使用统计方法检测AI生成的内容"
    
    @classmethod
    def get_instance(cls) -> 'StatisticalAIDetector':
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
        
    def __init__(self, config: Dict = None):
        super().__init__(config)
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
    async def execute(self, text: str) -> ToolResult:
        """执行AI检测"""
        try:
            result = ReviewResult()
            score = 0.0
            
            # 1. 句子长度规律性
            sentences = nltk.sent_tokenize(text)
            if not sentences:
                return self._create_success_result(result)
                
            lengths = [len(s) for s in sentences]
            avg_len = sum(lengths) / len(lengths)
            variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
            
            if variance < 100:
                score += 0.2
                
            # 2. 词汇重复度
            words = nltk.word_tokenize(text.lower())
            word_freq = Counter(words)
            unique_ratio = len(word_freq) / len(words)
            
            if unique_ratio < 0.4:
                score += 0.2
                
            # 3. 句式多样性
            sentence_starts = [s.split()[0] if s.split() else '' for s in sentences]
            start_freq = Counter(sentence_starts)
            start_ratio = len(start_freq) / len(sentences)
            
            if start_ratio < 0.5:
                score += 0.2
                
            # 4. AI常见模式
            ai_patterns = [
                r"让我们|接下来|首先|其次|最后|总的来说|综上所述",
                r"根据(?:上述|以上)(?:分析|内容|结果)",
                r"值得注意的是|需要指出的是|不难发现",
                r"通过(?:上述|以上)(?:分析|讨论|研究)",
                r"(?:本文|我们)(?:将|已经)(?:分析|讨论|研究)"
            ]
            
            pattern_count = sum(1 for pattern in ai_patterns if re.search(pattern, text))
            if pattern_count >= 2:
                score += 0.2
                
            result.is_ai_generated = score > 0.5
            result.ai_probability = min(1.0, score)
            
            return self._create_success_result(result)
        except Exception as e:
            return self._create_error_result(str(e))

class OpenAIDetector(BaseTool):
    """基于OpenAI的AI检测工具"""
    name = "openai_ai_detector"
    description = "使用OpenAI API检测AI生成的内容"
    
    @classmethod
    def get_instance(cls) -> 'OpenAIDetector':
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
        
    def __init__(self, config: Dict = None):
        super().__init__(config)
        openai.api_key = os.getenv("OPENAI_API_KEY")
            
    async def execute(self, text: str) -> ToolResult:
        """执行AI检测"""
        try:
            result = ReviewResult()
            
            try:
                response = await openai.Completion.acreate(
                    model="text-davinci-003",
                    prompt=f"Analyze if the following text is AI generated:\n\n{text}\n\nProvide a probability score between 0 and 1, where 1 means definitely AI generated.",
                    max_tokens=50,
                    temperature=0
                )
                
                try:
                    score = float(response.choices[0].text.strip())
                    score = max(0.0, min(1.0, score))
                except (ValueError, AttributeError):
                    score = 0.5
                    
                result.is_ai_generated = score > 0.7
                result.ai_probability = score
                
            except Exception as e:
                print(f"OpenAI detection failed: {e}")
                result.is_ai_generated = False
                result.ai_probability = 0.0
                
            return self._create_success_result(result)
        except Exception as e:
            return self._create_error_result(str(e))

class SensitiveWordChecker(BaseTool):
    """敏感词检查工具"""
    name = "sensitive_word_checker"
    description = "检查文本中的敏感词"
    
    _sensitive_words: ClassVar[Optional[set]] = None
    
    @classmethod
    def get_instance(cls) -> 'SensitiveWordChecker':
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
        
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self._load_sensitive_words()
        
    def _load_sensitive_words(self):
        """加载敏感词表"""
        if self.__class__._sensitive_words is None:
            words_file = os.path.join(
                os.path.dirname(__file__),
                "data",
                "sensitive_words.txt"
            )
            try:
                with open(words_file, 'r', encoding='utf-8') as f:
                    self.__class__._sensitive_words = set(
                        word.strip() for word in f.readlines()
                    )
            except FileNotFoundError:
                self.__class__._sensitive_words = {
                    "暴力", "色情", "赌博", "毒品",
                    "政治", "宗教", "歧视", "谣言"
                }
                
    async def execute(self, text: str) -> ToolResult:
        """执行敏感词检查"""
        try:
            result = ReviewResult()
            
            words = jieba.lcut(text)
            sensitive_found = []
            
            for i, word in enumerate(words):
                if word in self._sensitive_words:
                    position = len(''.join(words[:i]))
                    sensitive_found.append((word, position))
            
            result.sensitive_words = sensitive_found
            return self._create_success_result(result)
        except Exception as e:
            return self._create_error_result(str(e)) 