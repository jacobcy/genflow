# Topic 模块

话题模型及其相关业务逻辑组件，用于管理和操作从外部来源抓取的话题数据。该模块负责处理创作内容的主题信息，提供存储、检索和管理功能。

## 架构设计

本模块采用分层架构，将数据模型、业务逻辑和持久化操作分离：

- **数据模型层**：`topic.py` 定义了话题的数据结构
- **业务逻辑层**：`topic_factory.py` 包含话题的业务操作和转换逻辑
- **持久化层**：`topic_manager.py` 负责话题的存储和检索
- **数据库层**：`topic_db.py` 定义数据库模型和ORM映射

## 核心组件

### 1. Topic 类

话题的数据模型，定义了话题的核心数据结构。

```python
from core.models.topic.topic import Topic

# 创建一个话题实例
topic = Topic(
    title="Python异步编程最佳实践",
    description="探讨Python中异步编程的最佳实践和常见陷阱",
    platform="medium",
    url="https://example.com/topics/python-async",
    mobile_url="https://m.example.com/topics/python-async",
    hot=100,
    cover="https://example.com/images/python-async.jpg"
)

# 转换为字典
topic_dict = topic.to_dict()

# 转换为JSON字符串
json_str = topic.to_json()

# 更新时间戳
topic.update_timestamp()
```

### 2. TopicFactory 类

负责话题的业务逻辑操作，包括验证、转换和协调。

```python
from core.models.topic.topic_factory import TopicFactory
from core.models.topic.topic import Topic

# 获取话题
topic = TopicFactory.get_topic("topic_001")

# 保存话题
success = TopicFactory.save_topic(topic)

# 删除话题
success = TopicFactory.delete_topic("topic_001")

# 获取指定平台的话题
topics = TopicFactory.get_topics_by_platform("medium")
```

### 3. TopicManager 类

负责话题的持久化操作，包括加载、存储和检索。

```python
from core.models.topic.topic_manager import TopicManager
from core.models.topic.topic import Topic

# 初始化管理器
TopicManager.initialize()

# 确保已初始化
TopicManager.ensure_initialized()

# 获取话题
topic = TopicManager.get_topic("topic_001")

# 保存话题
success = TopicManager.save_topic(topic)

# 删除话题
success = TopicManager.delete_topic("topic_001")

# 获取指定平台的话题
topics = TopicManager.get_topics_by_platform("medium")
```

## 常见使用场景

### 通过ContentManager使用（推荐）

作为系统的统一入口，推荐使用ContentManager来操作话题：

```python
from core.models.content_manager import ContentManager

# 初始化
ContentManager.initialize()

# 获取话题
topic = ContentManager.get_topic("topic_001")

# 保存话题
success = ContentManager.save_topic(topic)

# 删除话题
success = ContentManager.delete_topic("topic_001")
```

### 获取并更新话题信息

```python
from core.models.content_manager import ContentManager

# 获取话题
topic = ContentManager.get_topic("topic_001")

if topic:
    # 更新话题描述
    topic.description = "更新后的话题描述"

    # 更新热度
    topic.hot = 150

    # 更新封面图片
    topic.cover = "https://example.com/images/new-cover.jpg"

    # 保存更新
    ContentManager.save_topic(topic)
```

### 获取平台热门话题

```python
from core.models.topic.topic_manager import TopicManager

# 获取指定平台的话题
topics = TopicManager.get_topics_by_platform("medium")

# 按热度排序
hot_topics = sorted(topics, key=lambda x: x.hot, reverse=True)

# 获取前5个热门话题
top_5_topics = hot_topics[:5]

# 输出热门话题标题
for topic in top_5_topics:
    print(f"{topic.title} (热度: {topic.hot})")
```

## 注意事项

1. 使用前需确保 `ContentManager.initialize()` 或 `TopicManager.initialize()` 已调用
2. 外部系统应通过 `ContentManager` 调用话题功能，而不直接调用内部组件
3. 话题数据主要从外部来源抓取，不包含创建话题的工具方法
4. 话题数据结构保持简洁，仅包含必要的元数据和内容信息
5. 注意处理ID的一致性，确保数据库操作和模型使用同一ID格式