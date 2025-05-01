# GenFlow 核心模型 - 基础设施 (infra) 模块规格

本模块 (`core.models.infra`) 旨在提供 GenFlow 模型层通用的基础组件、工具类和枚举定义，支撑上层 Manager 和 Factory 的运作。

## 目标组件与职责

根据目标架构 (`docs/arch.md`)，本模块的核心组件及其职责如下：

### 1. `base_manager.py`

*   **文件**: `core/models/infra/base_manager.py`
*   **职责**: 定义所有 `XxxManager` 的抽象基类 `BaseManager`。
*   **核心提供**:
    *   `BaseManager` (ABC):
        *   定义了 CRUDL (Create, Read, Update, Delete, List) 相关的 **抽象方法** (`get_entity`, `save_entity`, `delete_entity`, `list_entities`)，强制子类实现具体的持久化逻辑。
        *   `use_db` 属性 (bool): 控制 Manager 是使用数据库 (`True`) 还是文件系统/内存 (`False`) 进行持久化（具体行为由子类实现决定）。
        *   通用的初始化逻辑 (`initialize`, `ensure_initialized`) 和状态管理。
*   **外部依赖**: `abc` (Python Standard Library)

### 2. `json_loader.py`

*   **文件**: `core/models/infra/json_loader.py`
*   **职责**: 提供从文件系统加载 JSON 文件并将其内容解析、验证为 Pydantic 模型实例的工具。主要用于加载 `config/` 目录下的配置文件。
*   **核心提供**:
    *   `JsonModelLoader` 类:
        *   `load_models_from_directory(...)`: 加载指定目录下所有 JSON 文件为指定 Pydantic 模型列表。
        *   `load_model_from_file(...)`: 加载单个 JSON 文件为指定 Pydantic 模型实例。
        *   `save_model_to_file(...)`: 将 Pydantic 模型实例保存为 JSON 文件（如果需要）。
    *   处理文件读取、JSON 解析和 Pydantic 验证过程中的错误。
*   **外部依赖**: `pydantic`, `loguru`, `os`, `json` (Python Standard Library)

### 3. `temporary_storage.py`

*   **文件**: `core/models/infra/temporary_storage.py`
*   **职责**: 提供一个通用的、临时的、基于内存的键值存储服务，用于存放生命周期较短的数据，如处理过程中的中间结果。
*   **核心提供**:
    *   `TemporaryStorage` 类 (通过 `get_instance` 获取具名实例):
        *   `set(...)`: 存储数据并返回唯一键。
        *   `get(...)`: 根据键获取数据。
        *   `update(...)`: 更新键对应的数据。
        *   `delete(...)`: 删除指定键的数据。
        *   `list_keys()`: 列出所有有效键。
        *   自动过期清理机制。
*   **外部依赖**: `uuid`, `datetime`, `threading` (用于锁)

### 4. `enums.py`

*   **文件**: `core/models/infra/enums.py`
*   **职责**: 集中定义项目模型层用到的通用枚举类型，确保一致性。
*   **核心提供**:
    *   各种 `enum.Enum` 子类 (如 `ArticleSectionType`, `ContentCategory`, `ProductionStage`, `StageStatus` 等)。
    *   建议枚举继承自 `str` 以方便序列化。
*   **外部依赖**: `enum` (Python Standard Library)

### 5. `__init__.py`

*   **文件**: `core/models/infra/__init__.py`
*   **职责**: 控制 `infra` 模块的公开接口，导出上述核心组件供其他模块使用。
*   **核心提供**:
    *   `__all__` 列表，包含: `'BaseManager'`, `'JsonModelLoader'`, `'TemporaryStorage'`, 以及所有定义的枚举类。
*   **外部依赖**: 无

## 总结

`infra` 模块的目标是提供稳定、通用的底层支持，其核心组件应保持简洁和高内聚，避免包含特定业务或数据实体的逻辑。该模块当前状态符合目标架构要求。
