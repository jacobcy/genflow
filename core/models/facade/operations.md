# Operations 模块

## 概述

Operations 模块实现了门面（Facade）设计模式，为 `feedback` 和 `progress` 等子系统提供了一个统一的高层接口。这个模块简化了客户端与这些子系统的交互，隐藏了子系统的复杂性。

## 主要组件

* **`OperationManager`**: 门面类，封装了对 `FeedbackFactory` 和 `ProgressFactory` 的调用。

## 设计模式

本模块采用了以下设计模式：

1. **门面模式（Facade Pattern）**：提供了一个统一的接口，隐藏了子系统的复杂性。
2. **单例模式（Singleton Pattern）**：`OperationManager` 使用类方法实现，确保全局只有一个实例。

## 使用示例

### 初始化

```python
from core.models.operations import OperationManager

# 初始化操作管理器
OperationManager.initialize(use_db=True)
```

### 进度管理

```python
# 创建进度
progress = OperationManager.create_progress(
    entity_id="article-123",
    operation_type="article_production"
)

# 获取进度
progress = OperationManager.get_progress(progress_id)

# 更新进度
success = OperationManager.update_progress(progress_id, progress)

# 删除进度
success = OperationManager.delete_progress(progress_id)
```

### 反馈管理

```python
# 创建研究反馈
research_feedback = OperationManager.create_research_feedback(
    feedback_text="研究结果很全面，但缺少一些关键数据",
    research_id="research-123",
    accuracy_rating=8.5,
    completeness_rating=7.0,
    suggested_improvements=["添加更多数据来源", "增加图表展示"],
    feedback_source="human"
)

# 创建内容反馈
content_feedback = OperationManager.create_content_feedback(
    content_id="article-456",
    feedback_text="文章结构清晰，但有些表述不够准确",
    rating=8.0,
    feedback_categories=["clarity", "accuracy"],
    user_id="user-789"
)

# 获取反馈
research_feedback = OperationManager.get_research_feedback(feedback_id)
content_feedback = OperationManager.get_content_feedback(feedback_id)

# 获取特定内容或研究的所有反馈
content_feedbacks = OperationManager.get_feedback_by_content_id(content_id)
research_feedbacks = OperationManager.get_feedback_by_research_id(research_id)

# 更新反馈
success = OperationManager.update_research_feedback(feedback_id, research_feedback)
success = OperationManager.update_content_feedback(feedback_id, content_feedback)

# 删除反馈
success = OperationManager.delete_feedback(feedback_id)
```

## 设计原则

1. **单一职责原则**：`OperationManager` 只负责封装底层子系统的接口，不添加额外的业务逻辑。
2. **接口隔离原则**：只暴露客户端需要的接口，隐藏底层实现细节。
3. **依赖倒置原则**：依赖于抽象接口，而不是具体实现。

## 扩展

如果需要添加新的子系统，只需要在 `OperationManager` 中添加相应的方法，而不需要修改客户端代码。这使得系统更容易维护和扩展。
