# 内容管理器 (ContentManager)

## 概述

ContentManager 是 GenFlow 系统的中枢管理模块，作为内容类型、文章风格、平台配置和数据的统一接口。它采用适配器模式，将上层应用与底层实现解耦，确保系统组件间高内聚低耦合，简化了数据流和访问控制。

## 核心功能

- **内容类型管理**：加载、查询和保存内容类型配置
- **风格配置管理**：获取和维护文章风格定义
- **平台配置管理**：统一管理多平台发布规则和要求
- **文章数据管理**：存储和检索文章相关数据
- **主题数据管理**：处理研究主题的存储和状态追踪
- **兼容性检查**：验证内容类型与风格的适配性
- **配置同步**：在内存和持久化存储间同步配置

## 系统架构

ContentManager 在系统中的位置：

```
应用层(CrewAI团队) → ContentManager → 数据服务层 → 持久化存储
```

内部组织结构：

```
ContentManager
    ├── ConfigService (配置管理)
    │   ├── 内容类型配置
    │   ├── 风格配置
    │   └── 平台配置
    ├── ArticleService (文章管理)
    │   ├── 文章存储
    │   ├── 主题管理
    │   └── 状态追踪
    └── DBAdapter (数据库适配)
        ├── 数据持久化
        ├── 查询接口
        └── 事务管理
```

## 关键方法

### 初始化和基本设置

```python
# 初始化管理器
ContentManager.initialize(use_db=True)

# 确保已初始化
ContentManager.ensure_initialized()
```

### 内容类型管理

```python
# 获取特定内容类型
content_type = ContentManager.get_content_type("blog_post")

# 获取所有内容类型
all_types = ContentManager.get_all_content_types()

# 按类别获取内容类型
tech_type = ContentManager.get_content_type_by_category("technology")

# 保存内容类型配置
ContentManager.save_content_type(new_content_type)
```

### 风格管理

```python
# 获取特定风格
style = ContentManager.get_article_style("formal_academic")

# 获取所有风格配置
all_styles = ContentManager.get_all_article_styles()

# 获取平台默认风格
wechat_style = ContentManager.get_platform_style("wechat")

# 保存风格配置
ContentManager.save_article_style(new_style)
```

### 平台管理

```python
# 获取平台配置
platform = ContentManager.get_platform("medium")

# 获取所有平台配置
all_platforms = ContentManager.get_all_platforms()

# 重新加载平台配置
updated_platform = ContentManager.reload_platform("twitter")

# 保存平台配置
ContentManager.save_platform(new_platform)
```

### 兼容性和推荐

```python
# 检查内容类型和风格是否兼容
is_compatible = ContentManager.is_compatible("technical_guide", "casual_tone")

# 获取内容类型的推荐风格
recommended_style = ContentManager.get_recommended_style_for_content_type("news_article")
```

### 文章管理

```python
# 获取文章
article = ContentManager.get_article(article_id)

# 保存文章
ContentManager.save_article(article)

# 更新文章状态
ContentManager.update_article_status(article, "published")

# 获取特定状态的文章
draft_articles = ContentManager.get_articles_by_status("draft")

# 删除文章
ContentManager.delete_article(article_id)
```

### 主题管理

```python
# 获取研究主题
topic = ContentManager.get_topic(topic_id)

# 保存主题
ContentManager.save_topic(topic)

# 更新主题状态
ContentManager.update_topic_status(topic_id, "researched")

# 获取平台相关主题
platform_topics = ContentManager.get_topics_by_platform("zhihu")

# 获取特定状态的主题
pending_topics = ContentManager.get_topics_by_status("pending")

# 删除主题
ContentManager.delete_topic(topic_id)
```

### 系统同步

```python
# 同步配置到数据库
ContentManager.sync_configs_to_db()

# 完整同步配置
ContentManager.sync_configs_to_db_full()
```

### 主题选择和趋势

```python
# 获取热门主题
trending_topics = ContentManager.get_trending_topics(limit=10)

# 获取最新主题
latest_topics = ContentManager.get_latest_topics(limit=5)

```

## 设计原则

ContentManager 遵循以下设计原则：

1. **单一职责**：每个组件专注于自己的职责
2. **开放封闭**：支持扩展而不修改现有代码
3. **接口一致性**：对外提供统一稳定接口
4. **依赖注入**：松耦合设计，易于测试
5. **防御性编程**：异常处理和日志记录

## 与其他模块的集成

ContentManager 作为核心模块，与以下模块紧密集成：

- **WritingCrew**：提供内容类型配置和保存文章
- **StyleCrew**：提供风格配置和平台风格指南
- **ResearchCrew**：管理研究主题和获取待处理主题
- **ReviewCrew**：提供质量评估标准和更新文章状态

## 使用示例

### 基本配置获取

```python
from core.models.content_manager import ContentManager

# 初始化管理器
ContentManager.initialize()

# 获取博客文章类型配置
blog_type = ContentManager.get_content_type("blog_post")
print(f"博客文章要求最小字数: {blog_type.min_word_count}")
print(f"博客文章建议结构: {blog_type.structure}")

# 获取知乎平台配置
zhihu = ContentManager.get_platform("zhihu")
print(f"知乎平台特性: {zhihu.features}")
print(f"知乎平台风格指南: {zhihu.style_guide}")

# 查找适合科技类内容的风格
formal_style = ContentManager.get_article_style("tech_formal")
if ContentManager.is_compatible("tech_article", "tech_formal"):
    print("该风格适合科技文章")
```

### 内容创作流程管理

```python
from core.models.content_manager import ContentManager
from core.models.topic import Topic
from core.models.article import Article

# 获取待处理主题
pending_topics = ContentManager.get_topics_by_status("ready_for_writing")
topic = pending_topics[0]

# 更新主题状态
ContentManager.update_topic_status(topic.id, "writing_in_progress")

# 创建文章
article = Article(
    title="人工智能的未来发展趋势",
    topic_id=topic.id,
    platform="medium",
    content_type="tech_analysis",
    status="draft"
)

# 保存文章
ContentManager.save_article(article)

# 获取内容类型配置
content_type = ContentManager.get_content_type(article.content_type)
print(f"需要写作的最小字数: {content_type.min_word_count}")
print(f"建议包含的部分: {content_type.sections}")

# 获取平台风格配置
platform = ContentManager.get_platform(article.platform)
style = ContentManager.get_platform_style(article.platform)
print(f"平台风格指南: {platform.style_guide}")
print(f"文章语气建议: {style.tone}")

# 完成后更新状态
ContentManager.update_article_status(article, "ready_for_review")
ContentManager.update_topic_status(topic.id, "writing_completed")
```
