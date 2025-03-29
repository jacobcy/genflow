# GenFlow 核心模型 - 使用指南

## 概述

GenFlow 核心模型提供了内容管理的基础设施，包括风格、文章和配置管理。本指南面向业务层开发人员，说明如何正确地使用这些组件。

## 快速入门

### 1. 初始化

在应用启动时，需要初始化模型服务：

```python
from core.models.content_manager import ContentManager

# 默认使用数据库
ContentManager.initialize(use_db=True)

# 或仅使用文件系统
# ContentManager.initialize(use_db=False)
```

### 2. 风格管理

```python
# 获取风格
formal_style = ContentManager.get_article_style("formal")
if formal_style:
    print(f"风格名称: {formal_style.name}")
    print(f"风格描述: {formal_style.description}")
    print(f"语气: {formal_style.tone}")

# 获取所有风格
all_styles = ContentManager.get_all_styles()
for style_id, style in all_styles.items():
    print(f"ID: {style_id}, 名称: {style.name}")

# 创建自定义风格
custom_style = ContentManager.create_style_from_description(
    "一种正式、专业的科技文章风格，适合技术博客",
    {"style_name": "tech_formal"}
)

# 保存风格
ContentManager.save_style(custom_style)
```

### 3. 文章管理

```python
# 获取文章
article = ContentManager.get_article("article_123")
if article:
    print(f"标题: {article.title}")
    print(f"状态: {article.status}")

# 保存文章
from core.models.article.article_model import Article

new_article = Article(
    title="示例文章",
    content="这是文章内容...",
    status="draft"
)
ContentManager.save_article(new_article)
print(f"文章ID: {new_article.id}")

# 获取特定状态的文章
draft_articles = ContentManager.get_articles_by_status("draft")
print(f"草稿文章数量: {len(draft_articles)}")

# 更新文章状态
ContentManager.update_article_status(new_article.id, "published")
```

## 核心API

### ModelService (ContentManager)

```python
ContentManager.initialize(use_db=True)  # 初始化服务
```

#### 风格相关方法

```python
# 获取风格
style = ContentManager.get_article_style(style_name)

# 获取默认风格
default_style = ContentManager.get_default_style()

# 获取所有风格
all_styles = ContentManager.get_all_styles()

# 创建风格
style = ContentManager.create_style_from_description(description, options)

# 查找特定类型的风格
style = ContentManager.find_style_by_type(style_type)

# 保存风格
success = ContentManager.save_style(style)
```

#### 文章相关方法

```python
# 获取文章
article = ContentManager.get_article(article_id)

# 保存文章
success = ContentManager.save_article(article)

# 获取特定状态的文章
articles = ContentManager.get_articles_by_status(status)

# 更新文章状态
success = ContentManager.update_article_status(article_id, status)
```

## 数据模型

### ArticleStyle

风格对象包含以下主要属性：

```python
class ArticleStyle:
    name: str              # 风格名称
    type: str              # 风格类型
    description: str       # 描述
    tone: str              # 语气
    formality: int         # 正式程度(1-5)
    content_types: list    # 适用的内容类型
```

### Article

文章对象包含以下主要属性：

```python
class Article:
    id: str                # 文章ID
    title: str             # 标题
    content: str           # 内容
    author: str            # 作者
    created_at: datetime   # 创建时间
    updated_at: datetime   # 更新时间
    status: str            # 状态
```

## 最佳实践

### 1. 初始化检查

确保在使用服务前已初始化：

```python
if not hasattr(ContentManager, 'initialized') or not ContentManager.initialized:
    ContentManager.initialize()
```

### 2. 错误处理

始终检查返回值，不假设操作成功：

```python
style = ContentManager.get_article_style("formal")
if not style:
    # 处理风格不存在情况
    style = ContentManager.get_default_style()

success = ContentManager.save_article(article)
if not success:
    # 处理保存失败情况
    logger.error(f"无法保存文章: {article.id}")
```

### 3. 资源释放

某些操作可能需要手动释放资源：

```python
try:
    # 执行操作
    ContentManager.sync_configs_to_db()
finally:
    # 确保资源释放
    pass  # 当前版本不需要手动释放资源
```

### 4. 批量操作

对于批量操作，使用适当的方法避免多次调用：

```python
# 错误示例：多次单独保存
for article in articles:
    ContentManager.save_article(article)  # 低效

# 正确示例：使用批量API
# ContentManager目前不支持批量操作，但未来可能会支持
# 目前可以这样优化:
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(ContentManager.save_article, article) for article in articles]
    results = [future.result() for future in futures]
```

## 常见问题

### Q: 如何获取系统中所有支持的风格？

```python
styles = ContentManager.get_all_styles()
print(f"系统支持 {len(styles)} 种风格")
```

### Q: 如何验证文章状态更新成功？

```python
article_id = "article_123"
new_status = "published"

# 更新状态
success = ContentManager.update_article_status(article_id, new_status)

# 验证更新
if success:
    article = ContentManager.get_article(article_id)
    if article and article.status == new_status:
        print("状态更新成功")
    else:
        print("状态更新失败或验证失败")
else:
    print("状态更新操作返回失败")
```

### Q: 支持哪些文章状态？

常用的文章状态包括：

- `draft` - 草稿
- `review` - 审核中
- `published` - 已发布
- `archived` - 已归档

### Q: 如何提高大量文章处理的性能？

目前核心层没有提供批量处理API，业务层可以考虑：

1. 使用线程池并行处理
2. 实现自己的缓存层
3. 优化查询频率，减少不必要的数据获取
