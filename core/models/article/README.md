# Article 模块

文章模型及其相关业务逻辑组件，用于创建、管理和操作文章数据。

## 架构设计

本模块采用分层架构，将数据模型、业务逻辑和持久化操作分离：

- **数据模型层**：`article.py` 和 `basic_article.py` 定义了文章的数据结构
- **业务逻辑层**：`article_factory.py` 包含文章的业务操作和转换逻辑
- **持久化层**：`article_manager.py` 和 `article_db.py` 负责文章的存储和检索
- **工具层**：`article_parser.py` 提供文章内容解析功能

## 核心组件

### 1. Article 和 Section 类

文章的核心数据模型，定义了文章的结构和属性。

```python
from .article import Article, Section

# 创建一个章节
section = Section(
    id="section_1",
    title="章节标题",
    content="章节内容",
    order=1
)

# 创建一篇文章
article = Article(
    id="article_1",
    topic_id="topic_1",
    title="文章标题",
    summary="文章摘要",
    sections=[section],
    tags=["标签1", "标签2"]
)
```

### 2. BasicArticle 类

简化版的文章模型，不依赖话题和大纲，适用于直接文本输入和风格化处理。

```python
from .basic_article import BasicArticle

# 创建一个基础文章
basic_article = BasicArticle(
    title="基础文章标题",
    summary="基础文章摘要",
    content="基础文章内容",
    tags=["标签1", "标签2"]
)

# 计算基础指标
metrics = basic_article.calculate_basic_metrics()
```

### 3. ArticleFactory 类

提供文章的业务逻辑操作，如文章创建、状态管理、指标计算等。

```python
from .article_factory import ArticleFactory

# 获取默认文章
default_article = ArticleFactory.get_default_article()

# 从基础文章创建文章
article = ArticleFactory.from_basic_article(basic_article, topic_id="topic_1")

# 计算文章指标
metrics = ArticleFactory.calculate_article_metrics(article)

# 验证文章
is_valid = ArticleFactory.validate_article(article)

# 应用风格
ArticleFactory.apply_style(article, style={"id": "style_1"})

# 更新状态
ArticleFactory.update_article_status(article, "published")

# 保存文章
success = ArticleFactory.save_article(article)
```

### 4. ArticleManager 类

负责文章的持久化操作，包括加载、存储和检索。

```python
from .article_manager import ArticleManager

# 初始化管理器
ArticleManager.initialize()

# 获取文章
article = ArticleManager.get_article("article_1")

# 保存文章
success = ArticleManager.save_article(article)

# 获取指定状态的文章
draft_articles = ArticleManager.get_articles_by_status("draft")

# 删除文章
success = ArticleManager.delete_article("article_1")
```

### 5. ArticleParser 类

提供文章内容解析功能，包括解析AI生成的内容、提取章节结构等。

```python
from .article_parser import ArticleParser

# 解析AI返回的内容
updated_article = ArticleParser.parse_ai_response(response_text, article)

# 验证文章
is_valid = ArticleParser.validate_article(article)
```

## 常见使用场景

### 创建并保存文章

```python
from .article_factory import ArticleFactory
from .article import Article, Section

# 创建章节
section = Section(
    id="section_1",
    title="章节标题",
    content="章节内容",
    order=1
)

# 创建文章
article = Article(
    id="article_1",
    topic_id="topic_1",
    title="文章标题",
    summary="文章摘要",
    sections=[section],
    tags=["标签1", "标签2"]
)

# 计算指标
ArticleFactory.calculate_article_metrics(article)

# 验证文章
if ArticleFactory.validate_article(article):
    # 保存文章
    success = ArticleFactory.save_article(article)
```

### 加载并更新文章

```python
from .article_factory import ArticleFactory

# 获取文章
article = ArticleFactory.get_article("article_1")

if article:
    # 更新标题
    article.title = "新标题"

    # 更新状态
    ArticleFactory.update_article_status(article, "review")

    # 保存更新
    ArticleFactory.save_article(article)
```

### 处理AI生成的文章内容

```python
from .article_factory import ArticleFactory
from .article import Article

# 创建空文章
article = Article(
    id="article_1",
    topic_id="topic_1",
    title="",
    summary="",
    sections=[]
)

# AI返回的内容
ai_response = """
{
    "title": "AI生成的标题",
    "summary": "AI生成的摘要",
    "tags": ["AI", "内容生成", "自动写作"],
    "content": "## 第一部分\\n这是第一部分的内容\\n\\n## 第二部分\\n这是第二部分的内容"
}
"""

# 解析AI返回并更新文章
updated_article = ArticleFactory.parse_ai_response(ai_response, article)

if updated_article and ArticleFactory.validate_article(updated_article):
    # 计算指标
    ArticleFactory.calculate_article_metrics(updated_article)

    # 保存文章
    ArticleFactory.save_article(updated_article)
```

### 应用风格和平台准备

```python
from .article_factory import ArticleFactory

# 获取文章
article = ArticleFactory.get_article("article_1")

if article:
    # 应用风格
    style = {"id": "blog_style", "name": "博客风格"}
    ArticleFactory.apply_style(article, style)

    # 为平台准备
    result = ArticleFactory.prepare_for_platform(article, "wechat")

    if result["is_valid"]:
        # 保存文章
        ArticleFactory.save_article(article)
    else:
        print(f"文章不符合平台要求: {result['validation_details']}")
```

## 注意事项

1. 使用前需确保 `ArticleManager.initialize()` 已调用
2. 外部系统应通过 `ContentManager` 调用 `ArticleFactory`，而不直接调用
3. 文章状态流转：draft -> generated -> style -> review -> published
4. 保存文章前应先调用 `calculate_article_metrics` 计算指标
5. 使用 `validate_article` 确保文章数据完整性
