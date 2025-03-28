"""模型模块

包含GenFlow核心模型定义和配置。
"""

# 导出共享枚举类型
from .util.enums import (
    ArticleSectionType,
    ContentCategory,
    CategoryType,
    ProductionStage,
    StageStatus
)

# 导出主要模型和管理器
from .content_manager import ContentManager

# 避免在此处导入所有模型，防止循环导入问题
# 需要使用时再显式导入所需模型
