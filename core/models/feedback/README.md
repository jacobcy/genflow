# Feedback 模块

## 职责

本模块负责管理系统中的各种反馈信息，包括研究反馈和内容反馈。

## 核心组件

* **`feedback.py`**: 定义反馈的核心业务逻辑模型。
  * `ResearchFeedback`: 研究反馈的业务逻辑模型。
  * `ContentFeedback`: 内容反馈的业务逻辑模型。

* **`feedback_db.py`**: 定义反馈的数据库模型。
  * `FeedbackDB`: 反馈数据库模型基类。
  * `ResearchFeedbackDB`: 研究反馈数据库模型。
  * `ContentFeedbackDB`: 内容反馈数据库模型。

* **`feedback_manager.py`**: 实现 `FeedbackManager`，继承自 `BaseManager`，负责反馈数据的 CRUD 操作。

* **`feedback_factory.py`**: 实现 `FeedbackFactory`，负责：
  * 创建具体的反馈对象（如 `ResearchFeedback` 和 `ContentFeedback`）。
  * 调用 `FeedbackManager` 持久化反馈数据。
  * 从 `FeedbackManager` 获取数据并重建反馈对象。
  * 接收反馈对象，提取其状态，并调用 `FeedbackManager` 更新数据库。

## 设计模式

遵循 `Factory -> Manager -> DB Model / Business Logic Model` 模式。

* 外部代码应通过 `FeedbackFactory` 与反馈模块交互。
* `FeedbackFactory` 协调业务逻辑对象（`ResearchFeedback` 和 `ContentFeedback`）和持久化层（`FeedbackManager`）。
* `FeedbackManager` 只负责与数据库（`FeedbackDB` 及其子类）的直接交互。
* `ResearchFeedback` 和 `ContentFeedback` 封装特定类型的反馈逻辑，不直接依赖数据库或其他 Manager。

## 使用示例

```python
# 创建研究反馈
research_feedback = FeedbackFactory.create_research_feedback(
    feedback_text="研究结果很全面，但缺少一些关键数据",
    accuracy_rating=8.5,
    completeness_rating=7.0,
    suggested_improvements=["添加更多数据来源", "增加图表展示"],
    feedback_source="human",
    research_id="research-123"
)

# 创建内容反馈
content_feedback = FeedbackFactory.create_content_feedback(
    content_id="article-456",
    feedback_text="文章结构清晰，但有些表述不够准确",
    rating=8.0,
    feedback_categories=["clarity", "accuracy"],
    user_id="user-789"
)

# 获取特定内容的所有反馈
content_feedbacks = FeedbackFactory.get_feedback_by_content_id("article-456")

# 更新反馈
content_feedback.rating = 9.0
FeedbackFactory.update_content_feedback(feedback_id, content_feedback)

# 删除反馈
FeedbackFactory.delete_feedback(feedback_id)
```
