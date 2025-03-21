"""文章数据模型"""
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from .topic import Topic

class Section(BaseModel):
    """文章章节"""
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    order: int = Field(..., description="章节顺序")

class SEOData(BaseModel):
    """SEO数据"""
    keywords: List[str] = Field(default_list=[], description="关键词")
    description: str = Field(default="", description="SEO描述")
    title: str = Field(default="", description="SEO标题")

class ReviewResult(BaseModel):
    """审核结果"""
    plagiarism_score: float = Field(default=0.0, description="查重分数(0-1)")
    ai_detection_score: float = Field(default=0.0, description="AI检测分数(0-1)")
    readability_score: float = Field(default=0.0, description="可读性分数(0-1)")
    sensitive_words: List[str] = Field(default_list=[], description="敏感词列表")
    suggestions: List[str] = Field(default_list=[], description="改进建议")

class Article(BaseModel):
    """文章模型"""
    id: str = Field(..., description="文章ID")
    topic_id: str = Field(..., description="关联话题ID")
    title: str = Field(..., description="文章标题")
    summary: str = Field(..., description="文章摘要")
    sections: List[Section] = Field(..., description="文章章节")
    
    # 元数据
    author: str = Field(default="AI", description="作者")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    version: int = Field(default=1, description="版本号")
    status: str = Field(default="draft", description="状态(draft/review/published)")
    
    # SEO相关
    seo: SEOData = Field(default_factory=SEOData, description="SEO数据")
    
    # 平台相关
    platform: str = Field(default="default", description="目标平台")
    platform_style: Dict = Field(default_factory=dict, description="平台风格配置")
    
    # 审核相关
    review: ReviewResult = Field(default_factory=ReviewResult, description="审核结果")
    human_feedback: Optional[Dict] = Field(default=None, description="人工反馈")
    
    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": {
                "id": "article_001",
                "topic_id": "topic_001",
                "title": "Python异步编程最佳实践：从入门到精通",
                "summary": "本文详细介绍Python异步编程的核心概念、实践方法和性能优化技巧",
                "sections": [
                    {
                        "title": "引言",
                        "content": "异步编程是现代Python开发中不可或缺的一部分...",
                        "order": 1
                    },
                    {
                        "title": "异步编程基础",
                        "content": "理解异步编程首先需要掌握以下核心概念...",
                        "order": 2
                    }
                ],
                "seo": {
                    "keywords": ["Python", "异步编程", "asyncio", "性能优化"],
                    "description": "深入解析Python异步编程的最佳实践，包含实战案例和性能优化建议",
                    "title": "Python异步编程完全指南 - 最佳实践与实战技巧"
                },
                "platform": "知乎",
                "platform_style": {
                    "tone": "专业",
                    "format": "图文结合",
                    "length": "长文"
                },
                "review": {
                    "plagiarism_score": 0.05,
                    "ai_detection_score": 0.3,
                    "readability_score": 0.85,
                    "sensitive_words": [],
                    "suggestions": ["建议增加更多实战案例"]
                },
                "human_feedback": {
                    "quality_score": 0.9,
                    "improvement_notes": "性能优化部分可以再详细一些"
                }
            }
        } 