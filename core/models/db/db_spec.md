# GenFlow 核心模型 - 数据库支持 (db) 模块规格

## 1. 概述

本模块 (`core.models.db`) 负责 GenFlow 系统与数据库交互的所有底层操作，包括数据库连接管理、会话管理、表结构初始化、数据模型定义（通过导入 SQLAlchemy 模型）以及配置数据的迁移同步。

它旨在提供一个稳定、可靠的数据库访问层，支撑上层 Manager 组件的数据持久化需求。

## 2. 目标文件结构与职责

根据目标架构 (`docs/arch.md`)，本模块的核心组件及其职责如下：

*   **`__init__.py`**: 模块入口，主要用于包标识，**不导出**具体的 SQLAlchemy 数据模型类 (`XxxDB`)。
*   **`session.py`**: 管理数据库连接（Engine）、会话工厂（SessionLocal）和 SQLAlchemy 的声明基类（Base）。
*   **`initialize.py`**: 负责数据库的初始化，包括创建所有定义的表结构，并可能调用配置迁移逻辑填充初始数据。
*   **`migrate_configs.py`**: 负责将 `config/` 目录下的 JSON 配置文件同步到数据库中对应的配置表中。
*   **`utils.py`**: 提供数据库相关的辅助工具函数或自定义类型（例如，用于处理 JSON 字段的 `TypeDecorator`）。

## 3. 核心组件规格

### 3.1. `__init__.py`

*   **文件**: `core/models/db/__init__.py`
*   **职责**: 作为 `db` 模块的入口和包标识符。按照当前实现，**不负责导出** SQLAlchemy 数据模型类。模型应从其定义的具体模块（如 `core.models.article.article_db`）直接导入。
*   **核心提供**: 无导出内容 (`__all__` 可能为空或不存在)。
*   **外部依赖**: 无。

### 3.2. `session.py`

*   **文件**: `core/models/db/session.py`
*   **职责**: 配置和管理数据库连接与会话。
*   **核心提供**:
    *   `engine`: SQLAlchemy 的数据库引擎实例，根据配置创建。
    *   `SessionLocal`: SQLAlchemy 的会话工厂 (`sessionmaker`)，用于创建数据库会话。
    *   `Base`: SQLAlchemy 的声明性基类 (`declarative_base()`)，所有数据库模型 (`XxxDB`) 都应继承自此类。
    *   `get_db()`: 一个上下文管理器函数，用于提供一个数据库会话，并确保在使用后正确关闭。
*   **外部依赖**: `sqlalchemy`, `sqlalchemy.orm`, `contextlib`, `core.config` (用于获取数据库连接字符串)。

### 3.3. `initialize.py`

*   **文件**: `core/models/db/initialize.py`
*   **职责**: 提供数据库初始化的功能。
*   **核心提供**:
    *   `init_database_structure_and_defaults()`: 创建表结构并确保默认数据（如默认风格/平台）存在。
    *   `initialize_all()`: 完整的初始化流程，调用结构创建、默认数据导入和配置迁移 (`migrate_configs.migrate_all`)。
*   **外部依赖**: `sqlalchemy`, `session.py` (`engine`, `Base`, `get_db`), `migrate_configs.py`, 相关DB模型 (用于默认数据), `loguru`。

### 3.4. `migrate_configs.py`

*   **文件**: `core/models/db/migrate_configs.py`
*   **职责**: 将 `config/` 目录下的 JSON 配置文件同步到数据库中。
*   **核心提供**:
    *   `migrate_content_types(sync_mode: bool)`: 同步内容类型配置。
    *   `migrate_article_styles(sync_mode: bool)`: 同步风格配置。
    *   `migrate_platforms(sync_mode: bool)`: 同步平台配置。
    *   `migrate_all(sync_mode: bool)`: 调用所有具体的迁移函数。
    *   `sync_mode` 参数控制同步行为（`False`=仅添加/更新，`True`=完全同步，删除数据库中多余的记录）。
*   **外部依赖**: `sqlalchemy.orm`, `session.py` (`get_db`), `core.models.infra.json_loader` (`get_config_file_path`, `load_json_config`), 相关 DB 模型 (用于查询和创建), `loguru`, `os`.

### 3.5. `utils.py`

*   **文件**: `core/models/db/utils.py`
*   **职责**: 存放数据库相关的通用工具或自定义 SQLAlchemy 类型。
*   **核心提供**:
    *   (可能) `JSONEncodedDict`: 一个 `TypeDecorator`，用于将 Python 字典透明地存储为数据库中的 JSON 字符串。
    *   其他可能需要的辅助函数或类。
*   **外部依赖**: `sqlalchemy.types`, `json`.

## 4. 待移除/重构的组件

根据目标架构 (`docs/arch.md`) 和清理计划 (`docs/impove_plan.md`)，以下当前存在于 `core/models/db/` 目录中的文件将在后续被移除或其功能被整合：

*   **`repository.py`**: **(已移除)** Repository 模式已被移除。
*   **`model_manager.py`**: **(已移除)** 功能已整合或不再需要。
*   **`readme.md`**: **(已更新)** 内容已根据当前规格和架构进行更新。

## 5. 总结

`db` 模块是模型层与数据库交互的基础。其目标是提供清晰的会话管理、可靠的初始化和迁移机制。移除 `Repository` 和 `model_manager` 使架构更扁平、更直接地利用 SQLAlchemy 的能力。