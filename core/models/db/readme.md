# GenFlow 数据库模块使用指南

本文档介绍 GenFlow 数据库支持模块 (`core.models.db`) 的功能、使用方法和维护说明。

## 1. 数据库概述

GenFlow 使用 SQLite 数据库（默认位于 `core/data/genflow.db`）存储核心数据模型，主要包括：

*   内容类型名称 (ContentTypeName)
*   文章风格 (ArticleStyle)
*   平台 (Platform)
*   话题 (Topic)
*   文章元数据 (Article Metadata)
*   大纲 (Outline)
*   以及它们之间的关联关系。

该模块负责数据库连接、会话管理、表结构创建以及配置数据同步。

## 2. 数据库支持文件结构

`core.models.db` 模块包含以下核心文件：

| 文件名             | 主要职责                                                     |
| :----------------- | :----------------------------------------------------------- |
| `__init__.py`      | 模块入口，主要用于包标识，**不导出**具体的 SQLAlchemy 数据模型类 (`XxxDB`)。 |
| `session.py`       | 管理数据库引擎 (`engine`)、会话工厂 (`SessionLocal`) 和声明基类 (`Base`)。 |
| `initialize.py`    | 提供数据库初始化功能，包括创建表结构和导入初始配置数据。     |
| `migrate_configs.py` | 将 `config/` 目录下的 JSON 配置文件同步到数据库。            |
| `utils.py`         | 提供数据库相关的辅助工具和自定义类型（如 JSON 字段处理）。   |

**注意**: 根据最新的架构，`repository.py` 和 `model_manager.py` 文件已被移除。

## 3. 核心功能与使用

### 3.1. 数据库会话管理 (`session.py`)

所有需要与数据库交互的操作（通常在 `XxxManager` 中执行）都应通过 `session.py` 提供的会话进行。推荐使用 `get_db` 上下文管理器来获取和管理会话：

```python
from core.models.db.session import get_db
# 模型应从其定义模块导入，例如:
# from core.models.article.article_db import ArticleDB

# 在 Manager 或需要访问数据库的地方
with get_db() as db_session:
    # 使用 db_session 执行 SQLAlchemy 查询或操作
    # new_article = ArticleDB(title="新文章", ...)
    # db_session.add(new_article)
    # ... (省略查询/操作示例)
```

`session.py` 还定义了 `Base`，所有 SQLAlchemy 模型（如 `ArticleDB`, `TopicDB` 等）都需要继承自这个基类。

### 3.2. 数据库初始化 (`initialize.py`)

在首次运行或需要重置数据库时，可以使用 `initialize.py` 中的功能。

```bash
# 运行初始化脚本 (通常在项目设置脚本中调用)
# 这会创建所有表并导入默认配置数据
python -m core.models.db.initialize [--sync-mode] # --sync-mode 可选，见下一节
```

该脚本会调用 `initialize_all()` 函数，它执行主要步骤：
1.  `init_database_structure_and_defaults()`: 创建表结构并确保默认数据（如默认风格/平台）存在。
2.  调用 `migrate_configs.migrate_all()`: 将 `config/` 目录下的配置数据同步到数据库中。

### 3.3. 配置迁移/同步 (`migrate_configs.py`)

该文件负责保持 `config/` 目录下的 JSON 配置文件与数据库中对应表的数据一致。

核心函数是 `migrate_all(sync_mode: bool = False)`:

*   **`sync_mode=False` (默认，增量同步)**:
    *   只添加或更新配置文件中存在的记录。
    *   不删除数据库中存在但配置文件中已移除的记录。
    *   这是应用启动时或常规运行时推荐的方式，以保护用户可能在数据库中直接修改或添加的数据。
*   **`sync_mode=True` (完整同步)**:
    *   使数据库中的配置记录与配置文件完全一致。
    *   会删除数据库中存在但配置文件中已移除的记录。
    *   **谨慎使用**，通常只在需要强制同步或重置配置时通过初始化脚本手动触发。

可以通过 `initialize.py` 脚本传递 `--sync-mode` 参数来控制首次初始化的同步模式。

```python
# 在代码中手动触发同步 (示例)
from core.models.db.migrate_configs import migrate_all

# 执行增量同步
migrate_all(sync_mode=False)

# 执行完整同步 (谨慎!)
# migrate_all(sync_mode=True)
```

### 3.4. 数据库模型导入

由于 `core.models.db.__init__.py` **不负责导出模型**，你需要从模型所在的具体模块导入 SQLAlchemy 模型类：

```python
from core.models.article.article_db import ArticleDB
from core.models.topic.topic_db import TopicDB
# ... 等等
```

### 3.5. 工具函数 (`utils.py`)

如果定义了例如 `JSONEncodedDict` 这样的自定义类型，可以在 SQLAlchemy 模型中使用它：

```python
# 示例: 在 xxx_db.py 模型定义中
from sqlalchemy import Column, Integer, String
from core.models.db.session import Base # Import Base from session
from core.models.db.utils import JSONEncodedDict # Import custom type

class MyModelDB(Base):
    __tablename__ = 'my_table'
    id = Column(Integer, primary_key=True)
    metadata = Column(JSONEncodedDict) # 使用自定义 JSON 类型
```

## 4. 数据库访问模式的变化

请注意，数据库的 **直接访问逻辑已从 `db` 模块移除**。

*   不再有 `Repository` 类。
*   不再有 `DBAdapter`。
*   数据 CRUD 操作现在由各模块的 `XxxManager` 类负责，它们直接使用 `db.session.get_db()` 获取会话，并调用 SQLAlchemy 的 Session API (如 `session.add()`, `session.query()`, `session.commit()` 等) 进行数据库交互。

`core.models.db` 模块的核心职责是提供 **基础支持**: 会话管理、模型基类、初始化、迁移和工具。

## 5. 数据库工具使用 (命令行)

(此部分可以保留，用于检查数据库状态和配置)

### 初始化和同步数据库

```bash
# 初始化数据库并执行默认的增量同步
python -m core.models.db.initialize

# 初始化数据库并执行完整同步（会删除不存在的配置）
python -m core.models.db.initialize --sync-mode
```

### 查看数据库状态和配置 (假设存在 db_tools.py 脚本)

```bash
# 查看状态
python db_tools.py status

# 检查配置一致性
python db_tools.py check

# 列出内容类型
python db_tools.py content

# 列出文章风格
python db_tools.py styles

# 列出平台配置
python db_tools.py platforms
```

## 6. 故障排除

(此部分可以保留)

### 数据库文件损坏

如果数据库文件损坏，可以删除数据库文件并重新初始化：

```bash
rm core/data/genflow.db
python -m core.models.db.initialize
```

### 配置不一致

如果配置文件和数据库不一致，可以考虑执行完整同步（谨慎）：

```bash
python -m core.models.db.initialize --sync-mode
```

### 数据库查询问题

使用 SQLite 命令行工具：

```bash
sqlite3 core/data/genflow.db
.tables
.schema content_type_name
SELECT name, created_at FROM content_type_name;
.quit
```

## 7. 开发和扩展

扩展 `db` 模块通常涉及：

1.  **添加新的 SQLAlchemy 模型**: 在相应的业务模块下创建 `xxx_db.py` 文件，定义继承自 `db.session.Base` 的模型类。
2.  **修改表结构**: 修改现有的 `xxx_db.py` 文件。注意：简单的修改（如添加列）可以通过重新运行 `initialize.py` 应用，但复杂的结构变更可能需要更复杂的迁移策略（如使用 Alembic，目前项目未引入）。
3.  **添加新的配置迁移**: 如果添加了新的配置文件类型，需要在 `migrate_configs.py` 中添加对应的 `migrate_xxx()` 函数，并在 `migrate_all()` 中调用。
4.  **添加工具函数**: 在 `utils.py` 中添加通用的数据库相关辅助功能。

**避免**: 不要在 `db` 模块内部添加特定业务实体的 CRUD 逻辑，这应由对应的 `XxxManager` 处理。
