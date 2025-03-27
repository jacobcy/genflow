from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from src.models.topic import Topic  # 导入 Topic 模型

class TeamRequest(BaseModel):
    """单独团队请求"""
    topic: Topic = Field(..., description="内容主题")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="附加参数")

class InitializeRequest(BaseModel):
    """初始化请求"""
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="初始化参数，可包含配置信息、API密钥等"
    )
