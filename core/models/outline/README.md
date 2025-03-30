# Outline 模块

大纲模型及其相关业务逻辑组件，用于创建、管理和操作大纲数据。大纲是文章生成的中间结构，用于组织文章内容框架。

## 架构设计

本模块采用分层架构，将数据模型、业务逻辑和持久化操作分离：

- **数据模型层**：`basic_outline.py` 定义了大纲的基础数据结构
- **业务逻辑层**：`outline_factory.py` 包含大纲的业务操作和转换逻辑
- **持久化层**：`outline_manager.py` 负责大纲的存储和检索
- **工具层**：`outline_converter.py` 提供大纲内容转换功能

## 核心组件

### 1. BasicOutline 和 OutlineNode 类

大纲的核心数据模型，定义了大纲的结构和属性。

```python
from .basic_outline import BasicOutline, OutlineNode

# 创建一个节点
node = OutlineNode(
    id="node_1",
    title="节点标题",
    content="节点内容",
    level=1
)

# 创建一个大纲
outline = BasicOutline(
    title="大纲标题",
    nodes=[node],
    content_type="article"
)
```

### 2. OutlineFactory 类

提供大纲的业务逻辑操作，如大纲创建、验证、格式转换等。

```python
from .outline_factory import OutlineFactory

# 创建大纲
outline = OutlineFactory.create_outline(
    title="文章标题",
    content_type="article",
    sections=[{"title": "第一章", "content": "内容概要"}]
)

# 保存大纲
outline_id = OutlineFactory.save_outline(outline)

# 获取大纲
outline = OutlineFactory.get_outline(outline_id)

# 验证大纲
is_valid = OutlineFactory.validate_outline(outline)

# 转换为文本
text = OutlineFactory.to_text(outline)

# 转换为文章对象
article = OutlineFactory.to_article(outline)

# 删除大纲
success = OutlineFactory.delete_outline(outline_id)

# 列出所有大纲
outline_ids = OutlineFactory.list_outlines()
```

### 3. OutlineManager 类

负责大纲的持久化操作，包括加载、存储和检索。

```python
from .outline_manager import OutlineManager

# 初始化管理器
OutlineManager.initialize()

# 确保已初始化
OutlineManager.ensure_initialized()

# 获取大纲
outline = OutlineManager.get_outline("outline_1")

# 保存大纲
success = OutlineManager.save_outline(outline)

# 删除大纲
success = OutlineManager.delete_outline("outline_1")

# 列出所有大纲ID
outline_ids = OutlineManager.list_outlines()
```

### 4. OutlineConverter 类

提供大纲内容转换功能，包括转换为文本、文章对象等。

```python
from .outline_converter import OutlineConverter

# 转换为文本
text = OutlineConverter.to_full_text(outline)

# 转换为文章对象
article = OutlineConverter.to_basic_article(outline)

# 转换为文章章节
sections = OutlineConverter.to_article_sections(outline)
```

## 常见使用场景

### 通过ContentManager使用（推荐）

作为系统的统一入口，推荐使用ContentManager来操作大纲：

```python
from core.models.content_manager import ContentManager

# 初始化
ContentManager.initialize()

# 创建大纲
outline = ContentManager.create_outline(
    title="大纲标题",
    content_type="article",
    sections=[{"title": "第一章", "content": "内容概述"}]
)

# 获取大纲
outline = ContentManager.get_outline("outline_id")

# 保存大纲
success = ContentManager.save_outline(outline)

# 删除大纲
success = ContentManager.delete_outline("outline_id")

# 将大纲转换为文章
article = ContentManager.outline_to_article("outline_id")

# 将大纲转换为文本
text = ContentManager.outline_to_text("outline_id")
```

### 创建并保存大纲

```python
from core.models.content_manager import ContentManager
from core.models.outline.outline_factory import OutlineFactory

# 方法1：通过ContentManager
outline = ContentManager.create_outline(
    title="大纲标题",
    content_type="article",
    sections=[
        {"title": "引言", "content": "介绍主题背景", "level": 1},
        {"title": "核心内容", "content": "详细阐述", "level": 1},
        {"title": "结论", "content": "总结观点", "level": 1}
    ]
)

# 方法2：使用Factory（需要手动保存）
outline = OutlineFactory.create_outline(
    title="大纲标题",
    content_type="article",
    sections=[
        {"title": "引言", "content": "介绍主题背景", "level": 1},
        {"title": "核心内容", "content": "详细阐述", "level": 1},
        {"title": "结论", "content": "总结观点", "level": 1}
    ]
)
outline_id = OutlineFactory.save_outline(outline)
```

### 加载并更新大纲

```python
from core.models.content_manager import ContentManager

# 获取大纲
outline = ContentManager.get_outline("outline_id")

if outline:
    # 更新标题
    outline.title = "新标题"

    # 如果是通过BasicOutline类型，可以添加节点
    from core.models.outline.basic_outline import OutlineNode
    new_node = OutlineNode(
        id="new_node",
        title="新章节",
        content="新章节内容",
        level=1
    )
    outline.nodes.append(new_node)

    # 保存更新
    ContentManager.save_outline(outline)
```

### 大纲转换为文章

```python
from core.models.content_manager import ContentManager
from core.models.outline.outline_factory import OutlineFactory

# 方法1：通过ContentManager
article = ContentManager.outline_to_article("outline_id")

# 方法2：使用Factory
outline = OutlineFactory.get_outline("outline_id")
article = OutlineFactory.to_article(outline)

# 处理文章后保存
if article:
    from core.models.article.article_factory import ArticleFactory
    ArticleFactory.calculate_article_metrics(article)
    ArticleFactory.save_article(article)
```

### 大纲转换为文本

```python
from core.models.content_manager import ContentManager

# 通过ContentManager获取大纲的文本表示
text = ContentManager.outline_to_text("outline_id")

# 可以将文本用于各种场景
print(text)
```

## 注意事项

1. 使用前需确保 `ContentManager.initialize()` 或 `OutlineManager.initialize()` 已调用
2. 外部系统应通过 `ContentManager` 调用大纲功能，而不直接调用内部组件
3. 保存大纲前应先调用 `validate_outline` 确保数据完整性
4. `BasicOutline` 是基础数据结构，可根据需要扩展为特定类型的大纲（如ArticleOutline）
5. 转换操作通过 `OutlineConverter` 实现，由 `OutlineFactory` 统一调用
