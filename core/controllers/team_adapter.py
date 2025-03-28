"""团队适配器模块

为各个专业团队提供统一的接口适配层，处理参数转换和错误处理。
本模块导入各个具体的团队适配器实现，提供统一的访问入口。

团队适配器的职责：
1. 提供统一的API接口给控制器
2. 处理不同团队之间的参数转换
3. 转换返回结果为统一的数据模型
4. 处理异常和错误情况
5. 避免直接处理业务逻辑
"""

from typing import Dict, Any, Optional, List, Union

# 导入基础适配器
from core.controllers.base_adapter import BaseTeamAdapter

# 导入各个团队的适配器
from core.agents.topic_crew.topic_adapter import TopicTeamAdapter
from core.agents.research_crew.research_adapter import ResearchTeamAdapter
from core.agents.writing_crew.writing_adapter import WritingTeamAdapter
from core.agents.style_crew.style_adapter import StyleTeamAdapter
from core.agents.review_crew.review_adapter import ReviewTeamAdapter

# 为了向后兼容，导出所有的适配器类
__all__ = [
    'BaseTeamAdapter',
    'TopicTeamAdapter',
    'ResearchTeamAdapter',
    'WritingTeamAdapter',
    'StyleTeamAdapter',
    'ReviewTeamAdapter'
]

# 在这里可以添加更多的团队适配器统一管理逻辑
# 例如：不同团队之间的协调，全局错误处理等
