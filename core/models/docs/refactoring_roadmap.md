# GenFlow 模型层重构路线图

## 1. 目标

重构 `core/models` 模块，移除旧的中心化 `ContentManager` 和 `DBAdapter`，建立四个独立的领域管理器 (`SimpleContentManager`, `PersistentContentManager`, `ConfigManager`, `OperationManager`) 作为模型层的直接入口点。目标是实现更清晰的职责分离、松耦合和更高的可维护性。每个领域管理器内部采用 `Factory -> Manager (Atomic) -> Model` 模式，Manager 直接负责与存储交互（使用 SQLAlchemy 或其他方式）。

## 2. 目标架构概览

*   **当前进度**: 已完成 ConfigManager 和 OperationManager 的实现，部分完成 SimpleContentManager 的实现，正在进行文档更新。

*   **四大领域入口**: `SimpleContentManager`, `PersistentContentManager`, `ConfigManager`, `OperationManager`。
*   **内部模式**: Domain Manager -> `XxxFactory` (业务逻辑) -> `XxxManager` (CRUD & 存储交互) -> Models (Pydantic & SQLAlchemy)。
*   **移除**: 统一 `ContentManager` Facade, `DBAdapter`, `ManagerRegistry`, `Repository` 层 (若存在)。

## 3. 执行阶段与进度

按以下顺序，逐个领域完成重构、测试和文档编写（包括模块 README）：

**Phase 1: 基础设施 (Infra) 清理与准备**

*   **任务**: 清理 `DBAdapter`, `Repository`, 旧配置服务；完善 `BaseManager`；确认 DB 会话管理 (`get_db`)。
*   **状态**: ✅ **已完成**

**Phase 2: 配置管理领域 (ConfigManager)**

*   **任务**: 规范化 `style`, `category`, `platform`, `content_type` 模块，实现 `ConfigManager` 委托逻辑，编写测试和 README。
*   **状态**: ✅ **已完成** (根据用户确认和 `arch.md` 描述)

**Phase 3: 操作过程领域 (OperationManager)**

*   **任务**: 规范化 `progress`, `feedback` 等模块，实现 `OperationManager` 委托逻辑，编写测试和 README。
*   **状态**: ✅ **已完成**
*   **完成内容**:
    * 创建了 `feedback` 模块，包含 `feedback.py`, `feedback_db.py`, `feedback_factory.py`, `feedback_manager.py`
    * 创建了 `operations` 模块，实现了 `OperationManager` 类
    * 遵循门面模式，仅封装底层子系统的功能，不添加额外的业务逻辑
    * 编写了单元测试，确保功能正常
    * 更新了相关文档 (`arch.md`, `impove_plan.md`)

**Phase 4: 简单内容领域 (SimpleContentManager)**

*   **任务**: 规范化 `basic_research`, `basic_outline`, `basic_article` 等临时内容模块，实现 `SimpleContentManager` 委托逻辑，编写测试和 README (注意存储方式可能为内存或 `TemporaryStorage`)。
*   **状态**: ✅ **部分完成**
*   **完成内容**:
    * 创建了 `outline_storage.py`，实现了 `OutlineStorage` 类，基于 `TemporaryStorage` 实现临时大纲存储
    * 更新了 `outline_adapter.py`，使用 `OutlineStorage` 类进行临时大纲的存储和管理
    * 创建了 `SimpleContentManager` 类，实现了临时大纲和基础研究的管理方法
    * 编写了单元测试和集成测试，确保功能正常
    * 创建了示例代码，展示如何使用临时大纲存储和 SimpleContentManager
    * 更新了相关文档 (`arch.md`, `outline/README.md`)
*   **待办内容**:
    * 完善 `basic_research` 的临时存储功能
    * 实现 `basic_article` 的临时存储功能

**Phase 5: 持久内容领域 (PersistentContentManager)**

*   **任务**: 规范化 `topic`, `article`, `research`, `outline` 等核心内容模块，实现 `PersistentContentManager` 委托逻辑，编写测试和 README。处理旧 `ContentManager` 的迁移。
*   **状态**: ⏳ **待办** (Topic 模块部分完成)

**Phase 6: 最终文档更新与审查**

*   **任务**: 全面更新项目级文档 (`README.md`, `arch.md` 等)，确保与最终代码一致。代码审查和最终合并。
*   **状态**: ⏳ **进行中**
*   **完成内容**:
    * 更新了 `arch.md`，添加了 `progress`、`feedback`、`topic`、`research`、`outline` 模块的详细说明
    * 更新了 `arch.md`，添加了 `SimpleContentManager` 的详细说明
    * 更新了 `outline/README.md`，添加了临时大纲存储功能的说明
    * 更新了 `impove_plan.md`，反映当前的实现状态
    * 更新了 `refactoring_roadmap.md`，说明当前的进度
