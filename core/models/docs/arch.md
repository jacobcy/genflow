# GenFlow 核心模型目标架构

## 1. 概述

本架构旨在定义 GenFlow 核心模型 (`core/models`) 的目标结构，以提高模块化、可维护性和可测试性。遵循关注点分离原则，将核心功能划分为配置管理、内容管理和过程管理。

**核心设计模式**: Facade Manager -> XxxFactory -> XxxManager -> Model

*   **Facade Manager (`ConfigManager`, `ContentManager`, `OperationManager`)**: 提供统一的、面向特定领域（配置、内容、过程）的入口点，隐藏内部复杂性，委托调用给相应的 Factory。
*   **XxxFactory (`ArticleFactory`, `TopicFactory`, etc.)**: 负责特定模块的业务逻辑、验证、转换、计算、协调 Manager 等。它处理 Pydantic 模型和 DB 模型之间的转换，并调用 Manager 进行持久化。
*   **XxxManager (`ArticleManager`, `TopicManager`, etc.)**: 继承自 `BaseManager`，负责与数据存储（数据库、文件系统）的直接交互，执行 CRUD 操作。支持双存储模式 (`use_db` 标志)。
*   **Model (`Article`, `ArticleDB`, etc.)**: Pydantic 模型用于数据传输和验证，SQLAlchemy 模型用于数据库映射。

## 2. 核心 Facade 管理器

### 2.1. ConfigManager

*   **职责**: 作为访问系统核心配置（内容类型、风格、平台）的统一入口 (Facade)。它将请求代理给具体的配置管理器 (`ContentTypeManager`, `StyleManager`, `PlatformManager`)。
*   **文件**: `core/models/config_manager.py`
*   **核心方法**:
    *   `initialize(use_db=True)`: 初始化所有底层配置管理器。
    *   **(ContentType)** `get_content_type(name: str) -> ContentTypeModel | None`
    *   **(ContentType)** `get_all_content_types() -> dict[str, ContentTypeModel]`
    *   **(ContentType)** `get_default_content_type() -> ContentTypeModel | None`
    *   **(ContentType)** `get_content_type_by_category(category: str) -> ContentTypeModel | None`
    *   **(Style)** `get_article_style(style_name: str) -> ArticleStyle | None`
    *   **(Style)** `get_default_style() -> ArticleStyle | None`
    *   **(Style)** `get_all_styles() -> dict[str, ArticleStyle]`
    *   **(Style)** `find_style_by_type(style_type: str) -> ArticleStyle | None` # Delegated
    *   **(Style)** `save_style(style: ArticleStyle) -> bool` # Delegated
    *   **(Platform)** `get_platform(platform_id: str) -> Platform | None`
    *   **(Platform)** `get_platform_by_name(name: str) -> Platform | None`
    *   **(Platform)** `get_all_platforms() -> dict[str, Platform]`
*   **依赖**: `StyleManager`, `ContentTypeManager`, `PlatformManager`

### 2.2. ContentManager

*   **职责**: 提供对核心内容实体（平台、话题、文章）的统一访问和操作入口。
*   **文件**: `core/models/content_manager.py`
*   **核心方法 (委托给 Factory)**:
    *   Platform: `get_platform`, `save_platform`, `delete_platform`, `get_all_platforms`
    *   Topic: `get_topic`, `save_topic`, `delete_topic`, `find_topics`
    *   Article: `get_article`, `save_article`, `delete_article`, `find_articles`
*   **依赖**: `PlatformFactory`, `TopicFactory`, `ArticleFactory`

### 2.3. OperationManager

*   **职责**: 提供对内容生成过程中产生的中间数据（进度、反馈）的统一访问和操作入口。遵循门面模式，仅封装底层子系统的功能，不添加额外的业务逻辑。
*   **文件**: `core/models/operations/operation_manager.py`
*   **核心方法 (委托给 Factory)**:
    *   Progress: `create_progress`, `get_progress`, `update_progress`, `delete_progress`
    *   Feedback: `create_research_feedback`, `create_content_feedback`, `get_research_feedback`, `get_content_feedback`, `get_feedback_by_content_id`, `get_feedback_by_research_id`, `update_research_feedback`, `update_content_feedback`, `delete_feedback`
*   **依赖**: `ProgressFactory`, `FeedbackFactory`

### 2.4. SimpleContentManager

*   **职责**: 作为临时内容的门面，统一管理不带ID的临时内容对象，如临时大纲、基础研究等。遵循门面模式，仅封装底层子系统的功能，不参与具体逻辑。
*   **文件**: `core/models/facade/simple_content_manager.py`
*   **核心方法**:
    *   临时大纲: `create_basic_outline`, `save_basic_outline`, `get_basic_outline`, `update_basic_outline`, `delete_basic_outline`
    *   基础研究: `create_basic_research`, `save_basic_research`, `get_basic_research`
*   **依赖**: `OutlineAdapter`, `ResearchManager`

## 3. 核心配置模块 (示例: content_type)

除了操作具体内容实体的 Facade Manager 外，系统还包含用于管理核心配置定义的模块，这些配置通常作为常量或从简单配置文件加载。这些模块的结构可能比内容实体模块更简单。

### 3.1. 内容类型模块: `content_type`

*   **职责**: 定义和提供对系统支持的内容类型及其相关配置（研究深度、写作风格、字数建议等）的访问。
*   **核心文件**:
    *   `constants.py`: **配置的单一来源 (Source of Truth)**，定义内容类型名称常量、研究配置 (`RESEARCH_CONFIG`)、写作配置 (`WRITING_CONFIG`) 等静态字典。
    *   `content_type.py`: 定义 `ContentTypeModel` (Pydantic)，用于表示加载和合并后的配置对象。
    *   `content_type_db.py`: 定义 `ContentTypeName` (SQLAlchemy)，用于在数据库中存储类型名称以供关联。
    *   `content_type_manager.py`: 定义 `ContentTypeManager` 类，负责在首次访问时从 `constants.py` 加载配置到内存，并提供只读的访问接口 (`get_content_type`, `get_all_content_types` 等)。**注意**: 此 Manager 不遵循标准的 CRUD 模式，也不直接操作数据库持久化配置（配置修改需在 `constants.py` 进行）。
*   **与其他模块关系**:
    *   `db/migrate_configs.py` 和 `db/initialize.py` 可能会使用 `content_type_db.ContentTypeName` 将类型名称写入数据库。
    *   其他模块（如 `ArticleFactory`, `StyleManager` 等）通过 `ContentTypeManager` 获取内容类型配置信息。

### 3.2. 平台模块: `platform`

*   **职责**: 定义和提供对系统支持的外部发布平台（如微信公众号、知乎）及其相关配置（约束、技术要求等）的访问。
*   **核心文件**:
    *   `collection/`: **配置数据源目录**，包含每个平台的独立 JSON 配置文件。
    *   `platform.py`: 定义 `Platform` (Pydantic) 模型及其嵌套模型，用于表示加载后的配置对象。
    *   `platform_db.py`: 定义 `PlatformDB` (SQLAlchemy) 模型，用于数据库存储，可能包含基本字段和序列化的约束/技术细节。
    *   `platform_manager.py`: 定义 `PlatformManager` 类，负责在首次访问时从 `collection/` 目录加载所有 JSON 配置到内存，并提供只读访问接口 (`get_platform`, `get_all_platforms` 等)。**注意**: 此 Manager 同样不遵循标准的 CRUD 模式。
*   **与其他模块关系**:
    *   `db/migrate_configs.py` (如果需要同步到 DB) 和 `db/initialize.py` 可能会使用 `PlatformDB`。
    *   上层服务（如内容发布流程）通过 `ConfigManager.get_platform` 或 `ConfigManager.get_platform_by_name` 获取特定平台的约束和技术要求。

### 3.3. 风格模块: `style`

*   **职责**: 定义和提供对系统支持的文章风格及其相关配置（语气、格式、结构等）的访问。
*   **核心文件**:
    *   `collection/`: **配置数据源目录**，包含每个风格的独立 JSON 配置文件 (e.g., `default.json`, `zhihu.json`)。
    *   `article_style.py`: 定义 `ArticleStyle` (Pydantic) 模型，用于表示加载后的风格配置对象。
    *   `style_db.py`: 定义 `ArticleStyle` (SQLAlchemy) 模型，用于数据库存储。
    *   `style_manager.py`: 定义 `StyleManager` 类，负责在首次访问时从 `collection/` 目录加载所有 JSON 配置到内存，并提供只读访问接口 (`get_article_style`, `get_all_styles`, `get_default_style`)。也包含创建和保存风格的逻辑（这些可能后续移至 Factory）。**注意**: 配置修改主要通过编辑 JSON 文件或调用其保存方法。
*   **与其他模块关系**:
    *   `db/migrate_configs.py` 和 `db/initialize.py` 可能会使用 `style_db.ArticleStyle` 将配置同步到数据库。
    *   `ConfigManager` 通过 `StyleManager` 提供对风格配置的统一访问。
    *   (可能) `ArticleFactory` 或其他内容生成服务通过 `ConfigManager.get_article_style` 获取风格配置来指导内容生成。
    *   需要处理与 `ContentType` 的兼容性关系（可能在 `StyleManager` 或上层逻辑中实现）。

## 4. 核心内容模块

### 4.1. 话题模块 (topic)

*   **职责**: 管理从外部源获取的话题数据，包括话题名称、描述、关键词等。话题模块仅负责存储和管理外部获取的数据，不负责生成话题。
*   **核心文件**:
    *   `topic.py`: 定义 `Topic` Pydantic 模型，用于表示话题数据。
    *   `topic_db.py`: 定义 `TopicDB` SQLAlchemy 模型，用于数据库存储。
    *   `topic_factory.py`: 定义 `TopicFactory` 类，负责创建、获取和更新话题信息，处理业务逻辑。
    *   `topic_manager.py`: 定义 `TopicManager` 类，负责与数据库交互，执行 CRUD 操作。
*   **核心功能**:
    *   存储外部获取的话题数据
    *   提供话题查询和管理接口
    *   支持按关键词、分类等查找话题

### 4.2. 研究模块 (research)

*   **职责**: 管理内容生成前的研究数据，包括基础研究（不带ID，使用临时存储）和标准研究（带ID，存储在数据库）。
*   **核心文件**:
    *   `basic_research.py`: 定义 `BasicResearch` Pydantic 模型，用于表示基础研究数据。
    *   `research.py`: 定义 `Research` Pydantic 模型，用于表示标准研究数据。
    *   `research_db.py`: 定义 `ResearchDB` SQLAlchemy 模型，用于数据库存储。
    *   `research_factory.py`: 定义 `ResearchFactory` 类，负责创建、获取和更新研究信息，处理业务逻辑。
    *   `research_manager.py`: 定义 `ResearchManager` 类，负责与数据库交互，执行 CRUD 操作。
*   **核心功能**:
    *   管理基础研究和标准研究数据
    *   提供研究数据的创建、获取、更新和删除接口
    *   支持临时研究数据的存储和管理

### 4.3. 大纲模块 (outline)

*   **职责**: 管理内容生成的大纲数据，包括基础大纲、文章大纲等。支持临时大纲（不带ID）和持久化大纲（带ID）的存储和管理。
*   **核心文件**:
    *   `basic_outline.py`: 定义 `BasicOutline` 和 `OutlineNode` Pydantic 模型，用于表示基础大纲数据。
    *   `article_outline.py`: 定义 `ArticleOutline` Pydantic 模型，用于表示文章大纲数据。
    *   `outline_db.py`: 定义 `Outline` 和 `OutlineNodeDB` SQLAlchemy 模型，用于数据库存储。
    *   `outline_factory.py`: 定义 `OutlineFactory` 类，负责创建、获取和更新大纲信息，处理业务逻辑。
    *   `outline_manager.py`: 定义 `OutlineManager` 类，负责大纲的持久化存储和管理。
    *   `outline_storage.py`: 定义 `OutlineStorage` 类，负责临时大纲的存储和管理。
    *   `outline_adapter.py`: 定义 `OutlineAdapter` 类，作为临时大纲存储的适配器。
    *   `outline_converter.py`: 定义 `OutlineConverter` 类，负责大纲格式的转换。
*   **核心功能**:
    *   管理大纲数据的创建、获取、更新和删除
    *   支持临时大纲和持久化大纲的存储
    *   提供大纲格式的转换功能

## 5. 进度和反馈模块

### 5.1. 进度模块 (progress)

*   **职责**: 跟踪和管理内容生产过程中的进度信息，包括各阶段的状态、时间戳和元数据。
*   **核心文件**:
    *   `progress.py`: 定义 `ArticleProductionProgress` 和 `ProgressData` Pydantic 模型，用于表示进度信息。
    *   `progress_db.py`: 定义 `ProgressDB` SQLAlchemy 模型，用于数据库存储。
    *   `progress_factory.py`: 定义 `ProgressFactory` 类，负责创建、获取和更新进度信息，处理业务逻辑。
    *   `progress_manager.py`: 定义 `ProgressManager` 类，负责与数据库交互，执行 CRUD 操作。
*   **核心功能**:
    *   跟踪文章生产的各个阶段（研究、大纲、撰写、编辑、发布等）
    *   记录每个阶段的开始和完成时间
    *   存储阶段相关的元数据（如分配给谁、完成度等）
    *   提供进度查询和更新接口

### 5.2. 反馈模块 (feedback)

*   **职责**: 管理内容和研究的反馈信息，包括评分、评论和改进建议。
*   **核心文件**:
    *   `feedback.py`: 定义 `ResearchFeedback` 和 `ContentFeedback` Pydantic 模型，用于表示反馈信息。
    *   `feedback_db.py`: 定义 `FeedbackDB`、`ResearchFeedbackDB` 和 `ContentFeedbackDB` SQLAlchemy 模型，用于数据库存储。
    *   `feedback_factory.py`: 定义 `FeedbackFactory` 类，负责创建、获取和更新反馈信息，处理业务逻辑。
    *   `feedback_manager.py`: 定义 `FeedbackManager` 类，负责与数据库交互，执行 CRUD 操作。
*   **核心功能**:
    *   存储研究内容的准确性和完整性评分
    *   记录文章内容的质量评价和分类
    *   管理改进建议和反馈来源
    *   提供反馈查询和更新接口

## 6. 模块化结构 (Content & Operation)

每个核心数据模块（如 `article`, `topic`, `outline`）将遵循以下结构：

### 模块: `xxx` (例如: `core/models/article/`)

*   **`__init__.py`**: 导出模块的核心类，如 `Xxx`, `XxxDB`, `XxxFactory`, `XxxManager`。
*   **`xxx.py`**: 定义 Pydantic 模型 `Xxx`，用于 API 交互和数据验证。
    *   包含字段定义、验证器。
*   **`xxx_db.py`**: 定义 SQLAlchemy 模型 `XxxDB`，用于数据库映射。
    *   包含表结构定义、关系映射。
*   **`xxx_factory.py`**: 定义 `XxxFactory` 类。
    *   **职责**:
        *   处理创建、更新时的业务逻辑和验证（例如，验证 `article.topic_id` 是否存在）。
        *   协调与其他 Factory 或 Manager 的交互。
        *   处理 Pydantic 模型 (`Xxx`) 与 SQLAlchemy 模型 (`XxxDB`) 之间的转换。
        *   调用 `XxxManager` 进行数据持久化。
    *   **核心方法**: `create_xxx`, `update_xxx`, `get_xxx_details` (可能包含关联数据), `validate_xxx`。
    *   **依赖**: `XxxManager`, `Xxx` (Pydantic), `XxxDB` (SQLAlchemy), 其他 Factories/Managers (用于关联验证)。
*   **`xxx_manager.py`**: 定义 `XxxManager` 类，继承自 `BaseManager`。
    *   **职责**:
        *   提供对 `XxxDB` 实体的基本 CRUD 操作 (create, get, update, delete, list/find)。
        *   与数据库会话 (`db.session`) 或文件系统交互。
        *   处理 `use_db` 标志，支持数据库和文件系统双存储（如果需要）。
    *   **核心方法**: `create`, `get_by_id`, `update`, `delete`, `list_all`, `find_by_criteria`。
    *   **依赖**: `core.models.infra.base_manager.BaseManager`, `core.models.db.session`, `XxxDB` (SQLAlchemy), File System (如果支持文件存储)。

## 7. 基础设施 (infra)

*   **职责**: 提供模型层通用的基础组件和工具。
*   **目录**: `core/models/infra/`
*   **核心文件**:
    *   `base_manager.py`: 定义 `BaseManager` 抽象基类，提供通用 Manager 接口和 `use_db` 属性。
    *   `json_loader.py`: 提供加载 JSON 文件并转换为 Pydantic 模型的工具。
    *   `temporary_storage.py`: 提供内存或临时文件存储机制，用于临时内容对象的存储。
    *   `enums.py`: 定义项目范围内的枚举类型（如 `StatusEnum`）。

## 8. 数据库支持 (db)

*   **职责**: 管理数据库连接、会话、初始化和迁移。
*   **目录**: `core/models/db/`
*   **核心文件**:
    *   `__init__.py`: 导出核心 DB 模型 (`ArticleDB`, `TopicDB`, etc.)。
    *   `session.py`: 管理 SQLAlchemy 数据库引擎和会话 (`SessionLocal`, `engine`)。
    *   `initialize.py`: 包含创建数据库表 (`Base.metadata.create_all`) 和初始化数据的逻辑。
    *   `migrate_configs.py`: 包含将 JSON 配置同步到数据库的逻辑 (`migrate_all`, `migrate_content_types`, etc.)。
    *   `utils.py`: 数据库相关的工具函数（如自定义类型）。
    *   `repository.py`: **(待定)** 根据 `impove_plan.md`，可能会被简化或移除，查询逻辑直接放在 Manager 中。如果保留，将包含基于 SQLAlchemy 的通用查询构建器或特定实体的查询方法。

## 9. 数据流示例 (创建文章)

1.  **API/Service Layer** 调用 `ContentManager.save_article(article_pydantic: Article)`。
2.  **`ContentManager`** 调用 `ArticleFactory.create_or_update_article(article_pydantic)`。
3.  **`ArticleFactory`**:
    *   验证 `article_pydantic` 数据的业务规则（如标题长度、关联 Topic 是否存在 - 可能调用 `TopicFactory.get_topic`）。
    *   将 `Article` (Pydantic) 转换为 `ArticleDB` (SQLAlchemy) 模型 `article_db_instance`。
    *   调用 `ArticleManager.create(article_db_instance)` 或 `ArticleManager.update(article_db_instance)`。
4.  **`ArticleManager`**:
    *   获取数据库会话。
    *   执行 `session.add(article_db_instance)` 或 `session.merge(article_db_instance)`。
    *   `session.commit()` 或 `session.flush()`。
    *   (如果需要) 将文章数据保存到文件系统。
5.  返回结果（如创建的文章 ID 或更新后的 Pydantic 模型）逐层传递回 API 层。

## 10. 临时内容数据流示例

### 10.1. 使用 SimpleContentManager 管理临时大纲

1.  **API/Service Layer** 调用 `SimpleContentManager.create_basic_outline(title="临时大纲", ...)`。
2.  **`SimpleContentManager`** 创建 `BasicOutline` 对象。
3.  **API/Service Layer** 调用 `SimpleContentManager.save_basic_outline(outline)`。
4.  **`SimpleContentManager`** 调用 `OutlineAdapter.save_outline(outline)`。
5.  **`OutlineAdapter`** 调用 `OutlineStorage.save_outline(outline)`。
6.  **`OutlineStorage`** 将大纲存储在内存中，并返回大纲 ID。
7.  大纲 ID 逐层传递回 API 层。

### 10.2. 使用 SimpleContentManager 管理基础研究

1.  **API/Service Layer** 调用 `SimpleContentManager.create_basic_research(title="基础研究", ...)`。
2.  **`SimpleContentManager`** 创建 `BasicResearch` 对象。
3.  **API/Service Layer** 调用 `SimpleContentManager.save_basic_research(research)`。
4.  **`SimpleContentManager`** 调用 `ResearchManager.save_research(research)`。
5.  **`ResearchManager`** 将研究数据存储并返回结果。
6.  结果逐层传递回 API 层。
