# GenFlow 核心模型 - 使用指南

## 1. 概述

本指南介绍了 GenFlow 核心模型 (`core/models`) 的使用方法，重点围绕三大核心 Facade 管理器：`ConfigManager`, `ContentManager`, 和 `OperationManager`。

*   **ConfigManager**: 统一管理系统配置（内容类型、风格、平台）。
*   **ContentManager**: 统一管理核心内容实体（话题、文章等）。(待完善)
*   **OperationManager**: 统一管理进度和反馈信息，遵循门面模式，仅封装底层子系统的功能。
*   **SimpleContentManager**: 统一管理不带 ID 的临时对象。(待完善)

## 2. 初始化

在应用启动时，根据需要初始化相应的 Facade 管理器。目前主要是初始化 `ConfigManager`，它会自动初始化底层的配置管理器。

```python
from core.models.config_manager import ConfigManager

# 初始化配置管理器 (会自动初始化 StyleManager, ContentTypeManager, PlatformManager)
# use_db 参数主要影响 StyleManager 是否尝试与数据库交互（如果未来需要的话）
ConfigManager.initialize(use_db=True)

# 初始化 OperationManager
from core.models.operations import OperationManager
OperationManager.initialize(use_db=True)

# 后续 ContentManager 和 SimpleContentManager 初始化类似 (待定)
# from core.models.content_manager import ContentManager
# from core.models.simple_content import SimpleContentManager
# ContentManager.initialize(use_db=True)
# SimpleContentManager.initialize(use_db=True)
```

## 3. 配置管理 (ConfigManager)

`ConfigManager` 提供了访问所有静态配置的统一入口。

### 3.1. 访问内容类型 (ContentType)

```python
from core.models.config_manager import ConfigManager

# 获取指定名称的内容类型配置
blog_config = ConfigManager.get_content_type("博客")
if blog_config:
    print(f"类型: {blog_config.name}, 描述: {blog_config.description}")
    print(f"研究深度: {blog_config.research_config.get('depth')}")

# 获取所有内容类型
all_types = ConfigManager.get_all_content_types()
print(f"支持的内容类型数量: {len(all_types)}")
for name, config in all_types.items():
    print(f"- {name}")

# 获取默认内容类型
default_type = ConfigManager.get_default_content_type()
if default_type:
    print(f"默认类型: {default_type.name}")
```

### 3.2. 访问文章风格 (ArticleStyle)

```python
from core.models.config_manager import ConfigManager

# 获取指定名称的风格
formal_style = ConfigManager.get_article_style("formal")
if formal_style:
    print(f"风格名称: {formal_style.name}")
    print(f"风格描述: {formal_style.description}")
    print(f"语气: {formal_style.tone}")

# 获取所有风格
all_styles = ConfigManager.get_all_styles()
print(f"系统支持 {len(all_styles)} 种风格")
for style_id, style in all_styles.items():
    print(f"- ID: {style_id}, 名称: {style.name}")

# 获取默认风格
default_style = ConfigManager.get_default_style()
if default_style:
    print(f"默认风格: {default_style.name}")

# 注意：创建和保存风格的操作虽然通过 ConfigManager 代理，
# 但更推荐的方式是直接修改 collection/ 中的 JSON 文件或使用专门的管理工具/脚本。
# 如果确实需要在运行时保存或更新风格，可以使用 save_style 方法：
# success = ConfigManager.save_style(existing_or_new_style_object)
```

### 3.3. 访问平台 (Platform)

```python
from core.models.config_manager import ConfigManager

# 根据 ID 获取平台配置
zhihu_platform = ConfigManager.get_platform("zhihu")
if zhihu_platform:
    print(f"平台名称: {zhihu_platform.name}")
    print(f"平台描述: {zhihu_platform.description}")
    print(f"最大标题长度: {zhihu_platform.constraints.max_title_length}")

# 根据名称获取平台配置 (大小写不敏感)
wechat_platform = ConfigManager.get_platform_by_name("微信公众号") # 假设配置中 name 为 微信公众号
if wechat_platform:
    print(f"找到平台: {wechat_platform.id}")

# 获取所有平台
all_platforms = ConfigManager.get_all_platforms()
print(f"系统支持 {len(all_platforms)} 个平台")
for platform_id, platform in all_platforms.items():
    print(f"- ID: {platform_id}, 名称: {platform.name}")
```

## 4. 内容管理 (ContentManager)

**(待填充)**

本部分将介绍如何通过 `ContentManager` 管理核心内容实体，如：

*   话题 (Topic)
*   文章 (Article)
*   (可能包括 Platform 实体的管理，如果不仅仅是配置)

示例将包括创建、获取、更新、删除这些实体。

## 5. 操作过程管理 (OperationManager)

`OperationManager` 提供了对进度和反馈模块的统一访问入口，遵循门面模式，仅封装底层子系统的功能。

### 5.1. 进度管理

```python
from core.models.operations import OperationManager

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

### 5.2. 反馈管理

```python
from core.models.operations import OperationManager

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

## 6. 数据模型

**(待根据 ContentManager 和 OperationManager 的实现进行更新)**

这里将列出核心的 Pydantic 数据模型定义，例如 `Article`, `Topic`, `Outline` 等。

*   `ContentTypeModel`: (已通过 ConfigManager 提供)
*   `ArticleStyle`: (已通过 ConfigManager 提供)
*   `Platform`: (已通过 ConfigManager 提供)
*   `Article`: (待定)
*   `Topic`: (待定)
*   `Outline`: (待定)
*   `Research`: (待定)
*   `ArticleProductionProgress`: 文章生产进度模型
*   `ResearchFeedback`: 研究反馈模型
*   `ContentFeedback`: 内容反馈模型

## 7. 最佳实践

**(待根据整体实现进行更新)**

*   **初始化**: 确保在使用前调用相应 Manager 的 `initialize` 方法。
*   **错误处理**: 对 Manager 返回的结果进行检查（例如，检查返回是否为 None）。
*   **依赖注入**: 在上层服务中，考虑使用依赖注入框架来管理 Manager 的实例。
*   **原子操作**: 尽量将相关的数据库操作封装在 Factory 或 Service 的单个方法中，以保证事务性（如果适用）。

## 8. 常见问题

**(待根据整体实现进行更新)**

---

*旧版内容 (保留参考，待移除)*

```python
# 以下为旧版 ContentManager 的示例，将被 ConfigManager, ContentManager, OperationManager 的新用法取代

# # 获取风格 (旧)
# formal_style = ContentManager.get_article_style("formal")
# # 获取所有风格 (旧)
# all_styles = ContentManager.get_all_styles()
# # 创建自定义风格 (旧)
# custom_style = ContentManager.create_style_from_description(...)
# # 保存风格 (旧)
# ContentManager.save_style(custom_style)

# # 获取文章 (旧, 未来由 ContentManager 处理)
# article = ContentManager.get_article("article_123")
# # 保存文章 (旧, 未来由 ContentManager 处理)
# ContentManager.save_article(new_article)
# # 获取特定状态的文章 (旧, 未来由 ContentManager 处理)
# draft_articles = ContentManager.get_articles_by_status("draft")
# # 更新文章状态 (旧, 未来由 ContentManager 处理)
# ContentManager.update_article_status(new_article.id, "published")
```
