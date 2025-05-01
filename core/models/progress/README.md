# Progress 模块

## 职责

本模块负责管理和跟踪系统中各种长时间运行操作的进度。

## 核心组件

*   **`progress.py`**: 定义进度跟踪的核心逻辑和状态模型。
    *   `ProgressData`: 基础进度数据的 Pydantic 模型。
    *   `ArticleProductionProgress`: 具体的文章生产进度跟踪类，包含状态转换和计算逻辑。
*   **`progress_db.py`**: 定义 `ProgressDB` SQLAlchemy 模型，用于将进度状态持久化到数据库。
*   **`progress_manager.py`**: 实现 `ProgressManager`，继承自 `BaseManager`，负责 `ProgressDB` 对象的 CRUD 操作。
*   **`progress_factory.py`**: 实现 `ProgressFactory`，负责：
    *   根据操作类型创建具体的进度对象 (如 `ArticleProductionProgress`)。
    *   调用 `ProgressManager` 持久化初始状态。
    *   从 `ProgressManager` 获取数据并重建进度对象。
    *   接收进度对象，提取其状态，并调用 `ProgressManager` 更新数据库。

## 设计模式

遵循 `Factory -> Manager -> DB Model / Business Logic Model` 模式。

*   外部代码（如 `OperationManager` 或 Service 层）应通过 `ProgressFactory` 与进度模块交互。
*   `ProgressFactory` 协调业务逻辑对象 (`ArticleProductionProgress`) 和持久化层 (`ProgressManager`)。
*   `ProgressManager` 只负责与数据库 (`ProgressDB`) 的直接交互。
*   `ArticleProductionProgress` 封装特定类型的进度跟踪逻辑，不直接依赖数据库或其他 Manager。 