"""模型模块

包含GenFlow核心模型定义和配置。
"""

# 导出共享枚举类型
from .infra.enums import (
    ArticleSectionType,
    ContentCategory,
    CategoryType,
    ProductionStage,
    StageStatus
)

# 不再导出旧的 ContentManager
# from .content_manager import ContentManager

# 避免在此处导入所有模型，防止循环导入问题
# 需要使用时再显式导入所需模型

# TODO: 在重构完成后，考虑导出四个新的领域管理器
# from .simple_content import SimpleContentManager
# from .persistent_content import PersistentContentManager
# from .config import ConfigManager
# from .operation import OperationManager
