# GenFlow 数据存储说明

本文档说明 GenFlow 系统的数据存储架构、持久化策略和数据访问模式。

## 1. 存储架构概述

GenFlow 采用多层存储架构，将配置数据和业务数据分离存储：

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  JSON 配置文件  │   │   SQLite 数据库  │   │  文件系统存储   │
├─────────────────┤   ├─────────────────┤   ├─────────────────┤
│ - 内容类型配置  │   │ - 内容类型      │   │ - 完整文章内容  │
│ - 文章风格配置  │   │ - 文章风格      │   │ - 图片资源      │
│ - 平台配置      │   │ - 平台信息      │   │ - 大型二进制数据│
│                 │   │ - 话题数据      │   │                 │
│                 │   │ - 文章元数据    │   │                 │
│                 │   │ - 大纲数据      │   │                 │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

### 存储层次结构

1. **JSON 配置文件**：系统配置和规则定义
   - 存储位置：`config/` 目录
   - 主要内容：内容类型、文章风格、平台配置

2. **SQLite 数据库**：结构化数据和元数据
   - 存储位置：`core/data/genflow.db`
   - 主要内容：话题数据、文章元数据、配置映射

3. **文件系统**：大体积内容和二进制数据
   - 存储位置：`data/articles/` 目录
   - 主要内容：完整文章内容、资源文件

4. **临时存储**：会话数据和中间产物
   - 存储位置：内存
   - 主要内容：大纲草稿、临时状态

## 2. 数据模型和关系

### 主要数据表

1. **ContentTypeName**：内容类型
   - 主键：`name` (str)
   - 主要字段：`description`, `is_enabled`

2. **ArticleStyle**：文章风格
   - 主键：`name` (str)
   - 主要字段：`description`, `tone`, `style_characteristics`

3. **Platform**：发布平台
   - 主键：`id` (str)
   - 主要字段：`name`, `url`, `description`, `max_content_length`

4. **Topic**：话题
   - 主键：`id` (str)
   - 主要字段：`title`, `platform`, `description`, `hot`

5. **Article**：文章
   - 主键：`id` (str)
   - 主要字段：`title`, `content_type`, `topic_id`, `status`

6. **Outline**：大纲
   - 主键：`id` (str)
   - 主要字段：`title`, `topic_id`, `article_id`, `content_type`

### 多对多关系

- **content_type_style**：内容类型和风格的多对多关系
  - 主键：(`content_type_name`, `style_name`)

## 3. 持久化策略

### 数据同步机制

GenFlow 使用两种同步策略确保配置的一致性：

1. **增量同步**（默认）
   - 启动时自动执行
   - 只添加或更新配置，不删除现有数据
   - 保护用户自定义数据

2. **完整同步**（手动）
   - 需通过脚本手动执行
   - 执行完整的双向同步
   - 可以删除数据库中不再存在于配置文件中的记录

### 数据保存流程

1. **配置数据**：
   ```
   JSON配置文件 → JsonModelLoader → 配置对象 → DBAdapter → 数据库
   ```

2. **内容数据**：
   ```
   业务层 → ContentManager → DBAdapter → 数据库/文件系统
   ```

### 事务和并发控制

SQLite 数据库使用以下策略保证数据一致性：

- 使用 SQLAlchemy 会话管理和事务
- 默认隔离级别为 SERIALIZABLE
- 失败操作自动回滚
- 批量操作使用单一事务

## 4. 数据访问模式

### 适配器模式

GenFlow 使用适配器模式分离业务逻辑和数据访问：

```
业务层 → ContentManager → DBAdapter → 数据库仓库 → 数据库/文件系统
```

### 主要仓库类

数据库访问通过以下仓库类实现：

- `ContentTypeRepository`：内容类型数据访问
- `ArticleStyleRepository`：文章风格数据访问
- `PlatformRepository`：平台数据访问
- `TopicRepository`：话题数据访问
- `ArticleRepository`：文章数据访问

### 查询模式

系统支持以下查询模式：

1. **ID查询**：通过唯一标识符获取单个记录
2. **状态查询**：获取特定状态的记录集合
3. **关联查询**：通过关联ID获取相关记录
4. **全量查询**：获取所有记录（通常带分页）

## 5. 文件存储格式

### 文章存储

文章内容存储在文件系统中，使用JSON格式：

```
/data/articles/
  ├── article_{id}.json      # 文章主要内容
  └── article_{id}/          # 文章资源目录
      ├── images/            # 图片资源
      └── attachments/       # 其他附件
```

文章JSON格式示例：
```json
{
  "id": "article_001",
  "title": "示例文章",
  "content": "文章内容...",
  "sections": [
    {"title": "第一章", "content": "内容..."},
    {"title": "第二章", "content": "内容..."}
  ],
  "metadata": {
    "word_count": 1200,
    "read_time": 5
  }
}
```

## 6. 初始化和迁移

### 数据库初始化

使用以下命令初始化数据库：

```bash
python -m core.models.db.initialize
```

初始化流程：
1. 创建数据库文件（如不存在）
2. 创建表结构
3. 导入默认配置数据

### 配置同步

配置同步方式：

```python
# 增量同步（仅添加和更新）
ContentManager.sync_configs_to_db()

# 完整同步（包括删除）
ContentManager.sync_configs_to_db_full()
```

## 7. 常见问题与解决方案

### 数据一致性

问题：配置文件和数据库不一致
解决：执行完整同步 `ContentManager.sync_configs_to_db_full()`

### 数据丢失恢复

问题：数据库损坏导致数据丢失
解决：从文件系统恢复文章数据，从配置文件恢复配置数据

### 性能优化

大量数据查询时建议：
1. 使用分页查询
2. 使用缓存层
3. 优化查询条件
