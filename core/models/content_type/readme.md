# GenFlow 内容类型模块 (`core.models.content_type`)

## 1. 概述

本模块负责定义和管理 GenFlow 系统中的内容类型及其相关配置。内容类型的核心定义和配置数据来源于 `constants.py` 文件，本模块提供加载、访问这些配置的接口，并定义了用于数据库持久化的模型。

## 2. 文件结构与职责

| 文件名                 | 主要职责                                                     |
| :--------------------- | :----------------------------------------------------------- |
| `__init__.py`          | 包标识符。                                                   |
| `constants.py`         | 定义内容类型名称常量、研究配置 (`RESEARCH_CONFIG`)、写作配置 (`WRITING_CONFIG`)、平台分类映射 (`CATEGORY_TO_CONTENT_TYPE`) 等核心静态数据。 |
| `content_type.py`      | 定义 `ContentTypeModel` Pydantic 模型，用于表示加载后的内容类型配置对象，包含合并后的研究和写作信息。 |
| `content_type_db.py`   | 定义 `ContentTypeName` SQLAlchemy 模型，用于在数据库中存储内容类型的名称，以便进行关联。包含 `ensure_default_content_types` 函数用于初始化数据库中的默认类型名称。 |
| `content_type_manager.py` | 定义 `ContentTypeManager` 类，负责从 `constants.py` 加载配置数据到内存，并提供访问这些配置的接口（如按名称、类别获取）。这是一个只读的配置管理器。 |
| `readme.md`            | 本文档。                                                     |

## 3. 核心组件与使用

### 3.1. `constants.py`

该文件是内容类型配置的**唯一来源** (Single Source of Truth)。所有内容类型的添加、修改或配置调整都应在此文件中进行。

### 3.2. `ContentTypeModel` (Pydantic)

定义在 `content_type.py` 中，代表一个加载和合并后的内容类型配置。

```python
from core.models.content_type.content_type import ContentTypeModel

# 示例 (通常通过 Manager 获取)
# ct = ContentTypeModel(name="博客", depth="中等", ...)
# summary = ct.get_type_summary()
# print(ct.id) # -> "博客"
```

### 3.3. `ContentTypeName` (SQLAlchemy)

定义在 `content_type_db.py` 中，仅用于在数据库中存储内容类型的名称字符串，通常由 `migrate_configs.py` 或 `initialize.py` 写入。业务逻辑代码不应直接操作此模型，而是通过 `ContentTypeManager` 获取配置信息。

### 3.4. `ContentTypeManager`

定义在 `content_type_manager.py` 中，提供对常量配置的访问接口。

```python
from core.models.content_type.content_type_manager import ContentTypeManager

# 获取指定名称的内容类型配置
blog_config = ContentTypeManager.get_content_type("博客")
if blog_config:
    print(blog_config.description)

# 获取所有内容类型配置
all_configs = ContentTypeManager.get_all_content_types()
print(f"共加载 {len(all_configs)} 种内容类型")

# 根据类别获取
tech_config = ContentTypeManager.get_content_type_by_category("技术")

# 获取默认配置 (当前硬编码为"博客")
default_config = ContentTypeManager.get_default_content_type()
```

`ContentTypeManager` 在首次被调用时会自动从 `constants.py` 加载数据。

## 4. 外部依赖

*   `loguru`: 用于日志记录。
*   `pydantic`: 用于定义 `ContentTypeModel`。
*   `sqlalchemy`: 用于定义 `ContentTypeName` (在 `content_type_db.py` 中)。
*   `core.models.db.session`: (在 `content_type_db.py` 中) 依赖数据库会话基类。

## 5. 注意事项

*   本模块的设计强调配置数据来源于 `constants.py`。运行时的修改（如果未来需要）应考虑是否需要修改 Manager 的行为或引入 Factory。
*   `ContentTypeManager` 目前是纯内存加载，不直接与数据库交互。数据库中的 `ContentTypeName` 表主要用于外键关联和初始化。
