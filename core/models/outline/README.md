# Outline 模块

大纲模型及其相关业务逻辑组件，用于创建、管理和操作大纲数据。大纲是文章生成的中间结构，用于组织文章内容框架。

## 文件结构

```
core/models/outline/
├── __init__.py                # 模块初始化文件
├── basic_outline.py           # 基础大纲数据模型
├── article_outline.py         # 文章大纲数据模型
├── outline_factory.py         # 大纲业务逻辑工厂
├── outline_manager.py         # 大纲持久化管理器
├── outline_converter.py       # 大纲格式转换工具
├── outline_db.py              # 数据库模型定义
├── outline_storage.py         # 临时大纲存储
├── outline_adapter.py         # 临时存储适配器
├── examples/                  # 使用示例
└── README.md                  # 模块文档
```

## 架构设计

本模块采用分层架构，将数据模型、业务逻辑和持久化操作分离：

- **数据模型层**：`basic_outline.py` 和 `article_outline.py` 定义了大纲的基础数据结构
- **业务逻辑层**：`outline_factory.py` 包含大纲的业务操作和转换逻辑
- **持久化层**：`outline_manager.py` 负责大纲的持久化存储和检索
- **临时存储层**：`outline_storage.py` 和 `outline_adapter.py` 提供大纲的临时存储功能
- **工具层**：`outline_converter.py` 提供大纲内容转换功能
- **数据库层**：`outline_db.py` 定义了数据库模型

## 核心组件及主要方法

### 1. BasicOutline 和 OutlineNode 类 (basic_outline.py)

大纲的核心数据模型，定义了大纲的结构和属性。

**主要方法**:
- `BasicOutline.model_validate(data)` - 从字典创建大纲对象
- `BasicOutline.model_dump()` - 将大纲转换为字典
- `OutlineNode.model_validate(data)` - 从字典创建节点对象
- `OutlineNode.model_dump()` - 将节点转换为字典

```python
from core.models.outline.basic_outline import BasicOutline, OutlineNode

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

### 2. ArticleOutline 类 (article_outline.py)

继承自 BasicOutline，添加了文章相关的属性。

**主要方法**:
- `ArticleOutline.__init__()` - 初始化文章大纲，自动生成ID
- `ArticleOutline.model_validate(data)` - 从字典创建文章大纲对象

```python
from core.models.outline.article_outline import ArticleOutline

# 创建文章大纲
article_outline = ArticleOutline(
    topic_id="topic_001",
    title="文章大纲标题",
    content_type="article"
)
```

### 3. OutlineFactory 类 (outline_factory.py)

提供大纲的业务逻辑操作，如大纲创建、验证、格式转换等。

**主要方法**:
- `create_outline(title, content_type, sections, **kwargs)` - 创建新的大纲
- `create_from_json(data)` - 从JSON数据创建大纲
- `create_outline_node(title, level, content, **kwargs)` - 创建大纲节点
- `get_outline(outline_id)` - 获取大纲
- `save_outline(outline, outline_id=None)` - 保存大纲
- `delete_outline(outline_id)` - 删除大纲
- `list_outlines()` - 获取所有大纲ID列表
- `to_article(outline)` - 将大纲转换为文章对象
- `to_text(outline)` - 将大纲转换为文本
- `validate_outline(outline)` - 验证大纲有效性

```python
from core.models.outline.outline_factory import OutlineFactory

# 创建大纲
outline = OutlineFactory.create_outline(
    title="文章标题",
    content_type="article",
    sections=[{"title": "第一章", "content": "内容概要", "level": 1}]
)

# 保存大纲
outline_id = OutlineFactory.save_outline(outline)
```

### 4. OutlineManager 类 (outline_manager.py)

负责大纲的持久化操作，包括加载、存储和检索。

**主要方法**:
- `initialize(use_db=True)` - 初始化管理器
- `ensure_initialized()` - 确保已初始化
- `get_outline(outline_id)` - 获取大纲
- `save_outline(outline)` - 保存大纲
- `delete_outline(outline_id)` - 删除大纲
- `list_outlines()` - 列出所有大纲ID

```python
from core.models.outline.outline_manager import OutlineManager

# 初始化管理器
OutlineManager.initialize()

# 获取大纲
outline = OutlineManager.get_outline("outline_1")
```

### 5. OutlineStorage 类 (outline_storage.py)

提供大纲的临时存储功能，基于内存存储，适用于临时大纲、草稿大纲等不需要持久化的场景。

**主要方法**:
- `initialize()` - 初始化临时存储
- `get_outline(outline_id)` - 获取临时大纲
- `save_outline(outline, outline_id=None)` - 保存临时大纲
- `update_outline(outline_id, outline)` - 更新临时大纲
- `delete_outline(outline_id)` - 删除临时大纲
- `list_outlines()` - 列出所有临时大纲ID

```python
from core.models.outline import OutlineStorage, BasicOutline

# 初始化存储
OutlineStorage.initialize()

# 保存大纲
outline_id = OutlineStorage.save_outline(outline)

# 获取大纲
outline = OutlineStorage.get_outline(outline_id)
```

### 6. OutlineAdapter 类 (outline_adapter.py)

提供大纲临时存储的适配器，封装了 OutlineStorage 的操作，并提供异常处理。

**主要方法**:
- `initialize()` - 初始化适配器
- `get_outline(outline_id)` - 获取临时大纲
- `save_outline(outline, outline_id=None)` - 保存临时大纲
- `update_outline(outline_id, outline)` - 更新临时大纲
- `delete_outline(outline_id)` - 删除临时大纲
- `list_outlines()` - 列出所有临时大纲ID

```python
from core.models.outline import OutlineAdapter

# 初始化适配器
OutlineAdapter.initialize()

# 保存大纲
outline_id = OutlineAdapter.save_outline(outline)
```

### 7. OutlineConverter 类 (outline_converter.py)

提供大纲内容转换功能，包括转换为文本、文章对象等。

**主要方法**:
- `to_full_text(outline)` - 将大纲转换为完整文本
- `to_basic_article(outline)` - 将大纲转换为BasicArticle对象
- `to_article_sections(outline)` - 将大纲转换为文章章节列表

```python
from core.models.outline.outline_converter import OutlineConverter

# 转换为文本
text = OutlineConverter.to_full_text(outline)
```

### 8. 数据库模型 (outline_db.py)

定义了大纲的数据库模型，用于持久化存储。

**主要类**:
- `Outline` - 大纲数据库模型
- `OutlineNode` - 大纲节点数据库模型

## 外部依赖

本模块依赖以下外部组件：

1. **核心依赖**:
   - `pydantic` - 用于数据验证和模型定义
   - `loguru` - 用于日志记录
   - `sqlalchemy` - 用于数据库操作

2. **内部模块依赖**:
   - `core.models.infra.base_manager` - 提供基础管理器功能
   - `core.models.infra.db_session` - 提供数据库会话管理
   - `core.models.article.basic_article` - 用于大纲转换为文章

3. **可选依赖**:
   - `core.models.content_manager` - 统一入口，推荐通过此模块访问大纲功能

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
    sections=[{"title": "第一章", "content": "内容概述", "level": 1}]
)
```

### 使用临时大纲存储

当需要存储临时大纲、草稿大纲等不需要持久化的大纲时，可以使用 OutlineStorage：

```python
from core.models.outline import OutlineStorage, BasicOutline, OutlineNode

# 初始化存储
OutlineStorage.initialize()

# 创建大纲
outline = BasicOutline(
    title="临时大纲",
    content_type="article",
    nodes=[
        OutlineNode(title="第一章", content="内容概要", level=1)
    ]
)

# 保存到临时存储
outline_id = OutlineStorage.save_outline(outline)

# 获取临时大纲
temp_outline = OutlineStorage.get_outline(outline_id)

# 删除临时大纲
OutlineStorage.delete_outline(outline_id)
```

### 创建并持久化存储大纲

当需要持久化存储大纲时，可以使用 OutlineFactory 和 OutlineManager：

```python
from core.models.outline.outline_factory import OutlineFactory

# 使用Factory
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

### 大纲转换为文章

```python
from core.models.outline.outline_factory import OutlineFactory

# 使用Factory
outline = OutlineFactory.get_outline("outline_id")
article = OutlineFactory.to_article(outline)
```

## 注意事项

1. 使用前需确保相应的初始化方法已调用：
   - 使用 ContentManager 时，调用 `ContentManager.initialize()`
   - 使用 OutlineManager 时，调用 `OutlineManager.initialize()`
   - 使用 OutlineStorage 时，调用 `OutlineStorage.initialize()`
2. 外部系统应通过 `ContentManager` 调用大纲功能，而不直接调用内部组件
3. 保存大纲前应先调用 `validate_outline` 确保数据完整性
4. `BasicOutline` 是基础数据结构，可根据需要扩展为特定类型的大纲（如ArticleOutline）
5. 转换操作通过 `OutlineConverter` 实现，由 `OutlineFactory` 统一调用
6. 临时大纲存储和持久化大纲存储的区别：
   - **临时大纲存储**：使用 `OutlineStorage` 类，基于内存存储，适用于临时大纲、草稿大纲等不需要长期保存的场景。
   - **持久化大纲存储**：使用 `OutlineManager` 类，基于数据库存储，适用于需要长期保存的正式大纲。

## 测试

模块的测试文件位于 `tests/models/outline/` 目录下：

```
tests/models/outline/
├── __init__.py
├── test_basic_outline.py         # 测试基础大纲模型
├── test_article_outline.py       # 测试文章大纲模型
├── test_outline_factory.py       # 测试大纲工厂
├── test_outline_manager.py       # 测试大纲管理器
├── test_outline_storage.py       # 测试临时大纲存储
├── test_outline_adapter.py       # 测试大纲适配器
├── test_outline_converter.py     # 测试大纲转换器
└── test_temp_outline_integration.py # 临时大纲存储集成测试
```

运行测试：

```bash
# 运行所有测试
python -m pytest tests/models/outline -v

# 运行临时大纲存储相关测试
python -m pytest tests/models/outline/test_outline_storage.py -v
python -m pytest tests/models/outline/test_outline_adapter.py -v
python -m pytest tests/models/outline/test_temp_outline_integration.py -v
```

## 示例

模块包含一些示例代码，展示如何使用大纲模块的各种功能：

```
core/models/outline/examples/
├── __init__.py                # 示例模块初始化文件
├── temp_outline_example.py     # 临时大纲存储示例
└── README.md                  # 示例文档
```

运行示例：

```bash
python -m core.models.outline.examples.temp_outline_example
```