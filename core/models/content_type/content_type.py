"""内容类型模型

该模块定义内容类型的数据结构。
只包含数据结构，不包含逻辑代码。
"""

from typing import Dict, Any
from pydantic import BaseModel, Field

class ContentTypeModel(BaseModel):
    """简化的内容类型模型，仅包含必要信息"""
    name: str = Field(..., description="内容类型名称")
    depth: str = Field(..., description="研究深度(light/medium/deep)")
    description: str = Field(..., description="内容类型描述")
    word_count: str = Field(..., description="建议字数范围")
    focus: str = Field(..., description="内容重点")
    style: str = Field(..., description="推荐风格")
    structure: str = Field(..., description="内容结构")
    needs_expert: bool = Field(default=False, description="是否需要专家观点")
    needs_data_analysis: bool = Field(default=False, description="是否需要数据分析")

    class Config:
        """Pydantic配置"""
        use_enum_values = True

    def get_type_summary(self) -> Dict[str, Any]:
        """获取内容类型摘要信息

        提供内容类型的关键特征，用于研究和生成配置

        Returns:
            Dict[str, Any]: 内容类型摘要信息
        """
        return {
            "name": self.name,
            "description": self.description,
            "focus": self.focus,
            "structure": self.structure,
            "style": self.style,
            "word_count": self.word_count,
            "research_needs": {
                "depth": self.depth,
                "needs_expert": self.needs_expert,
                "needs_data_analysis": self.needs_data_analysis
            }
        }

    @property
    def id(self) -> str:
        """获取内容类型ID

        为了兼容性，使用name作为id

        Returns:
            str: 内容类型ID
        """
        return self.name
