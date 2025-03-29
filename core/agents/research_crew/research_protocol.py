"""研究协议模块 - 协议层

定义研究请求和响应的数据协议，用于研究团队各层之间的数据传递。
这是三层架构中的协议层，提供统一的数据结构，确保层间通信的一致性。

职责：
1. 定义标准化的请求和响应对象
2. 确保适配层和实现层之间的数据传递格式一致
3. 减少不必要的数据转换和中间对象

层间数据流：
控制器 → 适配层(ResearchTeamAdapter) → 实现层(ResearchCrew) → 适配层 → 控制器
      [ResearchRequest] → [研究执行] → [ResearchResponse]
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """研究请求对象

    纯数据传输对象，用于在适配层和实现层之间传递研究请求参数。
    不包含业务逻辑和复杂配置，只定义基本参数结构。

    研究配置通过content_type_obj对象或research_instruct获取。
    """
    # 基础信息
    topic_title: str = Field(..., description="研究话题标题")

    # 基本参数 - 两种配置方式二选一，按优先级排序
    content_type_obj: Optional[Any] = Field(default=None, description="内容类型对象，直接包含深度和研究需求配置")
    research_instruct: Optional[str] = Field(default=None, description="研究指导文本，描述如何研究该话题")

    # 可选参数和元数据
    options: Dict[str, Any] = Field(default_factory=dict, description="其他选项参数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据，包含研究配置和附加信息")

    # 适配器层内部使用的参数，不传递给研究团队层
    topic_id: Optional[str] = Field(default=None, description="话题ID，仅适配器层使用")


class ResearchResponse(BaseModel):
    """研究响应对象

    统一的响应结构，用于从研究团队层返回到适配器层。
    包含所有研究结果，避免多次对象转换。
    """
    title: str = Field(..., description="研究标题")
    content_type: str = Field(..., description="内容类型")
    background: Optional[str] = Field(default=None, description="背景研究结果")
    expert_insights: Optional[str] = Field(default=None, description="专家洞见")
    data_analysis: Optional[str] = Field(default=None, description="数据分析结果")
    report: Optional[str] = Field(default=None, description="完整研究报告")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    # 直接转换到BasicResearch所需的其他信息
    experts: List[Dict[str, Any]] = Field(default_factory=list, description="专家列表")
    key_findings: List[Dict[str, Any]] = Field(default_factory=list, description="关键发现列表")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="信息来源列表")


class FactVerificationRequest(BaseModel):
    """事实验证请求对象

    用于从适配器层传递到研究团队层的事实验证请求。
    """
    statements: List[str] = Field(..., description="需要验证的陈述列表")
    thoroughness: str = Field(default="high", description="验证彻底程度(low/medium/high)")
    options: Dict[str, Any] = Field(default_factory=dict, description="其他选项参数")


class FactVerificationResponse(BaseModel):
    """事实验证响应对象

    用于从研究团队层返回到适配器层的事实验证结果。
    """
    results: List[Dict[str, Any]] = Field(..., description="验证结果列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "statement": "Python是世界上最流行的编程语言",
                        "verified": False,
                        "confidence": 0.7,
                        "explanation": "根据TIOBE指数，Python并非世界上最流行的编程语言，它位列第二，而C语言位列第一",
                        "sources": [
                            {
                                "name": "TIOBE指数2023年11月统计",
                                "url": "https://www.tiobe.com/tiobe-index/"
                            }
                        ]
                    }
                ],
                "metadata": {
                    "thoroughness": "high",
                    "verification_time": "2023-11-30T15:45:22.123456"
                }
            }
        }
