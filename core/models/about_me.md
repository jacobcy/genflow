# GenFlow 核心模型

## 内容类型与文章风格管理

通过新的 JSON 驱动配置模型，GenFlow 现在支持更灵活的内容类型和文章风格管理。

### 主要改进

1. **配置文件分离**：
   - 内容类型配置位于 `core/models/content_types/*.json`
   - 文章风格配置位于 `core/models/styles/*.json`
   - 平台配置位于 `core/models/platforms/*.json`
   - 通过单独的 JSON 文件管理，方便扩展和修改

2. **统一加载器**：
   - 新增 `JsonModelLoader` 通用加载器，支持从目录加载多个配置文件
   - 避免硬编码配置，提高代码可维护性
   - 对所有 Pydantic 模型通用，支持类型提示

3. **中心化管理**：
   - 新增 `ContentManager` 全局管理器，统一访问内容类型、文章风格和平台
   - 优化设计消除循环导入问题，提高代码健壮性和性能
   - 提供一致的 API 接口

4. **智能兼容性检查**：
   - 增强内容类型与风格的兼容性检查
   - 支持模糊匹配和双向检查
   - 自动推荐最适合的风格

5. **数据库持久化**：
   - 通过 `DBAdapter` 实现数据库适配器模式
   - 支持配置文件与数据库自动同步
   - 提供增量同步与完整同步两种模式

### 使用方法

```python
# 初始化管理器（仅需一次）
from core.models.content_manager import ContentManager
ContentManager.initialize()

# 获取内容类型
blog_type = ContentManager.get_content_type("blog")  # 返回 ContentType 对象或 None（未找到时）

# 获取所有内容类型
all_content_types = ContentManager.get_all_content_types()  # 返回字典 {id: ContentType}

# 获取文章风格
zhihu_style = ContentManager.get_article_style("zhihu")  # 返回 ArticleStyle 对象或 None

# 获取所有文章风格
all_styles = ContentManager.get_all_article_styles()  # 返回字典 {id: ArticleStyle}

# 获取平台
weibo_platform = ContentManager.get_platform("weibo")  # 返回 Platform 对象或 None

# 获取所有平台
all_platforms = ContentManager.get_all_platforms()  # 返回字典 {id: Platform}

# 兼容性检查
is_compatible = ContentManager.is_compatible("blog", "zhihu")  # 返回布尔值

# 获取推荐风格
recommended_style = ContentManager.get_recommended_style_for_content_type("tutorial")

# 保存新内容类型到数据库
ContentManager.save_content_type(new_content_type)

# 数据同步
ContentManager.sync_configs_to_db()  # 增量同步（不删除）
ContentManager.sync_configs_to_db_full()  # 完整同步（包括删除）
```

### 话题类 (Topic) 使用方法

```python
# 创建新话题
from core.models.topic import Topic

# 创建完整话题
topic = Topic(
    title="话题标题",
    platform="weibo",
    url="https://example.com/topic",
    hot=1000,
    categories=["科技", "AI"],  # 可选，不提供时会自动使用平台的第一个默认分类
    tags=["人工智能", "技术"]
)

# 创建最小话题 (ID会自动生成)
topic = Topic(
    title="测试话题",
    platform="weibo"
)

# 序列化与反序列化
topic_dict = topic.to_dict()
restored_topic = Topic.from_dict(topic_dict)

# 自动ID生成规则
# ID格式: platform_timestamp_uuid[:8] 例如: weibo_1717027080_4a5b6c7d
```

### 扩展内容类型

要添加新的内容类型，只需在 `content_types` 目录中创建新的 JSON 文件，符合 `ContentType` 模型定义：

```json
{
  "id": "new_type",
  "name": "新内容类型",
  "category": "OTHER",
  "description": "这是一个新的内容类型",
  "format": "long-form",
  "primary_purpose": "inform",
  "structure_templates": [...],
  "format_guidelines": {...},
  "characteristics": {...},
  "compatible_styles": [...],
  "example_topics": [...],
  "metadata": {...}
}
```

### 扩展文章风格

类似地，要添加新的文章风格，在 `styles` 目录中创建新的 JSON 文件：

```json
{
  "id": "new_style",
  "name": "新风格",
  "type": "platform",
  "description": "新的文章风格",
  "target_audience": "通用受众",
  "content_types": [...],
  "tone": "friendly",
  "formality": 3,
  "emotion": true,
  "primary_language": "zh-CN",
  "content_rules": {...},
  "style_rules": {...},
  "style_guide": {...},
  "publish_settings": {...}
}
```

### 扩展平台

类似地，要添加新的平台，在 `platforms` 目录中创建新的 JSON 文件：

```json
{
  "id": "new_platform",
  "name": "新平台",
  "url": "https://www.newplatform.com",
  "description": "新的平台",
  "category": "OTHER",
  "primary_language": "zh-CN",
  "min_length": 100,
  "max_length": 60000,
  "max_title_length": 100,
  "max_image_count": 50,
  "forbidden_words": ["广告", "推广", "违禁词"],
  "constraints": {...}
}
```

### 错误处理

所有 `ContentManager` 方法都包含适当的错误处理：

1. **查询方法异常处理**：
   - 当查询的内容不存在时，通常返回 `None` 而非抛出异常
   - 所有方法都有日志记录，方便调试和监控

2. **验证方法**：
   - 例如 `Topic.validate_categories` 在未指定分类时会使用平台默认分类
   - 失败时会提供清晰的错误信息

3. **数据同步错误**：
   - 数据库操作失败会记录详细错误信息
   - 支持事务回滚，保证数据一致性

### 兼容性检查逻辑

1. **风格 → 内容类型兼容性**：
   - 如果风格的 `content_types` 包含内容类型ID，则兼容
   - 如果 `content_types` 为空，则视为通用风格，兼容所有内容类型
   - 支持模糊匹配，如 "tech_tutorial" 与 "tutorial" 匹配

2. **内容类型 → 风格兼容性**：
   - 如果内容类型的 `compatible_styles` 包含风格ID，则兼容
   - 如果 `compatible_styles` 不存在或为空，则兼容所有风格
   - 同样支持模糊匹配

3. **双向兼容检查**：
   - 只要满足任一条件即视为兼容
   - 优先使用风格的兼容性检查

### 数据库适配器模式

GenFlow 使用数据库适配器模式实现配置持久化：

1. **架构设计**：
   - `ContentManager` - 向应用提供统一接口
   - `DBAdapter` - 数据库适配器，处理数据转换和存储
   - `Repository` - 数据访问层，执行具体数据库操作

2. **同步策略**：
   - 启动时自动增量同步 - 添加/更新配置，不删除
   - 手动完整同步 - 完全同步配置文件与数据库（包括删除）

3. **管理工具**：
   - 提供 `db_tools.py` 和 `initialize_database.py` 脚本
   - 支持数据库初始化、状态检查、一致性检验等功能

### 依赖关系

```
ContentManager
  ├── content_type.py (ContentType)
  │     └── util.py (JsonModelLoader)
  ├── article_style.py (ArticleStyle)
  │     └── util.py (JsonModelLoader)
  ├── platform.py (Platform)
  │     └── util.py (JsonModelLoader)
  └── db_adapter.py (DBAdapter)
        └── core/db/* (数据库实现)
```

更多数据库功能详情，请参阅 `docs/database_guide.md`。

## 使用示例

```python
# 内容管理器示例
from core.models.content_manager import ContentManager

# 初始化管理器
ContentManager.initialize()

# 获取话题
topic = ContentManager.get_topic("topic_id")

# 保存文章
article = Article(...)
ContentManager.save_article(article)
```

```python
# 话题服务示例
from core.models.topic_service import TopicService

# 获取热门话题
hot_topics = TopicService.get_trending_topics(10)

```python
# 文章服务示例
from core.models.article_service import ArticleService

# 应用风格
ArticleService.apply_style(article, style)

# 为平台准备文章
result = ArticleService.prepare_for_platform(article, "weibo")
```
