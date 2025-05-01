# Style Module (`core/models/style`)

## 概述

该模块负责管理 GenFlow 项目中的**静态文章风格配置**。文章风格定义了内容的语气、格式、结构、目标受众等特征。

本模块遵循配置即代码的原则，风格配置以 JSON 文件的形式存储在 `collection/` 子目录中，并通过 `StyleManager` 进行加载和访问。

## 模块结构

```
core/models/style/
├── __init__.py             # 导出核心类
├── article_style.py        # 定义 ArticleStyle Pydantic 模型，用于数据校验和传输
├── style_db.py             # 定义 ArticleStyle SQLAlchemy 模型，用于数据库映射
├── style_manager.py        # 定义 StyleManager 类，继承自 BaseConfigManager，负责加载和管理配置
└── collection/             # 存放具体的风格配置文件 (JSON格式)
    ├── default.json        # 默认风格配置
    ├── bilibili.json
    ├── zhihu.json
    └── ...                 # 其他平台或自定义风格
```

##核心组件

### `ArticleStyle` (Pydantic 模型)

定义在 `article_style.py` 中，用于：
*   规范化从 JSON 文件加载的配置数据结构。
*   提供数据校验。
*   作为应用程序内部处理风格配置的数据对象。

关键字段包括：
*   `name`: (str) 风格的唯一标识符。
*   `type`: (str) 风格类型 (e.g., "general", "formal", "technical")。
*   `description`: (str) 风格描述。
*   `tone`: (str) 语气。
*   `formality`: (int) 正式程度。
*   `content_types`: (List[str]) 兼容的内容类型名称列表。
*   `target_audience`: (str) 目标受众。
*   `emotion`: (bool) 是否使用情感表达。
*   `emoji`: (bool) 是否使用表情。
*   `language_level`: (str) 语言难度。
*   `recommended_patterns`: (List[str]) 推荐的写作模式或技巧。
*   `examples`: (List[str]) 风格示例 (文本片段)。

### `StyleManager`

定义在 `style_manager.py` 中，继承自 `core.models.config.base_manager.BaseConfigManager`。

主要职责：
*   在初始化时自动从 `collection/` 目录加载所有 `.json` 风格配置文件。
*   将加载的 JSON 数据解析并校验为 `ArticleStyle` Pydantic 对象。
*   提供访问加载的风格配置的方法。

关键类方法：
*   `StyleManager.ensure_initialized()`: 确保配置已加载（由基类提供）。
*   `StyleManager.get_article_style(style_name: str) -> Optional[ArticleStyle]`: 根据名称获取单个风格配置。
*   `StyleManager.get_default_style() -> Optional[ArticleStyle]`: 获取默认风格配置 (查找名为 "default" 的配置)。
*   `StyleManager.get_all_styles() -> Dict[str, ArticleStyle]`: 获取所有已加载的风格配置字典。

### `ArticleStyle` (SQLAlchemy 模型)

定义在 `style_db.py` 中，用于将风格配置映射到数据库表 (`article_style`)。

主要作用：
*   配合 `core/models/db/migrate_configs.py` 将内存/文件中的配置同步到数据库。
*   提供数据库层面的风格数据表示。

**注意**: 该模型与数据库同步逻辑 (`migrate_configs.py`) 紧密相关，特别是关于 `compatible_content_types` 关系的定义和处理。

## 使用方式

应用程序的其他部分可以通过 `StyleManager` 来获取所需的风格配置：

```python
from core.models.style import StyleManager, ArticleStyle

# 确保配置已加载 (通常在应用启动时完成一次)
# StyleManager.ensure_initialized()

# 获取默认风格
default_style: Optional[ArticleStyle] = StyleManager.get_default_style()
if default_style:
    print(f"Default style tone: {default_style.tone}")

# 根据名称获取特定风格
zhihu_style: Optional[ArticleStyle] = StyleManager.get_article_style("zhihu")
if zhihu_style:
    print(f"Zhihu style description: {zhihu_style.description}")

# 获取所有风格
all_styles: Dict[str, ArticleStyle] = StyleManager.get_all_styles()
print(f"Loaded {len(all_styles)} styles.")
```

## 外部依赖

*   `pydantic`: 用于定义 `ArticleStyle` Pydantic 模型。
*   `sqlalchemy`: 用于定义 `ArticleStyle` SQLAlchemy 模型。
*   `loguru`: 用于日志记录。
*   `core.models.config.base_manager.BaseConfigManager`: `StyleManager` 的基类。
*   (间接) `core.models.db.session`, `core.models.db.utils`, `core.models.db.association_tables`: SQLAlchemy 相关。
*   (间接) `core.models.content_type`: 用于处理风格与内容类型的兼容性关系。

## 待办事项

*   **测试**: 添加全面的单元测试，覆盖 `StyleManager` 加载逻辑、`ArticleStyle` Pydantic 模型验证以及数据库迁移 (`migrate_article_styles`)。
*   **Pydantic 模型审视**: 再次确认 `ArticleStyle` Pydantic 模型的字段是否完全符合最终需求，特别是与 `platform` 模块的职责划分。
*   **ContentType 依赖**: 确认 `core.models.content_type` 模块提供了必要的 `ContentTypeName` 模型和相关数据库表，以确保兼容性关系正常工作。
*   **DB 模型字段**: 确认 `style_db.py` 中的 SQLAlchemy 模型字段与 Pydantic 模型和 JSON 配置保持最终一致。 