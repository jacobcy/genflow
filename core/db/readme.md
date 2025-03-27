# GenFlow 数据库使用指南

本文档介绍如何使用和维护 GenFlow 的数据库功能。

## 数据库概述

GenFlow 使用 SQLite 数据库来存储配置和数据，主要包括以下内容：

- 内容类型配置 (content_types)
- 文章风格配置 (article_styles)
- 平台配置 (platforms)
- 内容类型与文章风格之间的关联关系

数据库位于 `core/data/genflow.db`，使用 SQLite 格式，方便本地开发和使用。

## 数据库访问模式

### 通过 ContentManager 类访问数据库

ContentManager 是访问数据库的主要接口，它通过 DBAdapter 处理与数据库的交互：

```python
from core.models.content_manager import ContentManager

# 初始化 ContentManager (默认使用数据库)
ContentManager.initialize(use_db=True)

# 获取内容类型
content_type = ContentManager.get_content_type("article")

# 保存内容类型
ContentManager.save_content_type(content_type)

# 获取文章风格
style = ContentManager.get_article_style("wechat")

# 保存文章风格
ContentManager.save_article_style(style)

# 获取平台配置
platform = ContentManager.get_platform("wechat")

# 保存平台配置
ContentManager.save_platform(platform)
```

### 数据库同步策略

GenFlow 采用了以下数据库同步策略：

1. **应用启动时**：执行增量同步（`sync_mode=False`）
   - 只添加或更新配置文件中的内容
   - 不会删除数据库中已存在但配置文件中不存在的记录
   - 保护用户数据不被意外删除

2. **手动执行全量同步**：使用 `initialize_database.py` 脚本
   - 执行完整同步（`sync_mode=True`）
   - 会删除数据库中存在但配置文件中不存在的记录
   - 确保数据库和配置文件完全一致

## 数据库工具使用

### 初始化和同步数据库

```bash
# 初始化数据库并执行完整同步（会删除不存在的配置）
python initialize_database.py

# 或者使用数据库工具
python db_tools.py init
```

### 查看数据库状态

```bash
python db_tools.py status
```

输出示例：
```
检查数据库状态...
✓ 数据库文件存在: core/data/genflow.db
✓ 数据库包含 4 个表:
  - content_type: 17 条记录
  - article_style: 8 条记录
  - platform: 9 条记录
  - content_type_style: 10 条记录
```

### 检查配置一致性

检查数据库和配置文件之间的一致性：

```bash
python db_tools.py check
```

输出示例：
```
内容类型对比:
  - 数据库中: 17 个内容类型
  - 文件中: 17 个内容类型
  ✓ 内容类型ID完全一致

文章风格对比:
  - 数据库中: 8 个文章风格
  - 文件中: 8 个文章风格
  ✓ 文章风格ID完全一致

平台配置对比:
  - 数据库中: 9 个平台配置
  - 文件中: 9 个平台配置
  ✓ 平台配置ID完全一致
```

### 查看配置信息

查看内容类型、文章风格和平台配置：

```bash
# 列出所有内容类型
python db_tools.py content

# 列出所有文章风格
python db_tools.py styles

# 列出所有平台配置
python db_tools.py platforms
```

## 代码示例

### 创建和保存新内容类型

```python
from core.models.content_manager import ContentManager
from core.models.content_type import ContentType

# 初始化 ContentManager
ContentManager.initialize(use_db=True)

# 创建新内容类型
new_content_type = ContentType(
    id="my_custom_type",
    name="我的自定义类型",
    description="这是一个自定义的内容类型",
    default_word_count=2000,
    is_enabled=True,
    prompt_template="请生成一篇关于{{topic}}的{{style}}文章",
    output_format={
        "title": "标题",
        "content": "正文内容"
    },
    required_elements={
        "introduction": "介绍部分",
        "body": "主体部分",
        "conclusion": "结论部分"
    },
    optional_elements={
        "references": "参考资料"
    }
)

# 保存到数据库
success = ContentManager.save_content_type(new_content_type)
if success:
    print(f"内容类型 {new_content_type.id} 保存成功")
else:
    print("保存失败")
```

### 数据同步模式切换

```python
from core.models.content_manager import ContentManager

# 常规增量同步（不删除）
ContentManager.sync_configs_to_db()

# 完整同步（包括删除）
ContentManager.sync_configs_to_db_full()
```

## 故障排除

### 数据库文件损坏

如果数据库文件损坏，可以删除数据库文件并重新初始化：

```bash
# 删除数据库文件
rm core/data/genflow.db

# 重新初始化
python initialize_database.py
```

### 配置不一致

如果配置文件和数据库不一致，可以执行完整同步：

```bash
python db_tools.py init
```

### 数据库查询问题

如果需要直接查询数据库，可以使用 SQLite 命令行工具：

```bash
sqlite3 core/data/genflow.db

# 查看表结构
.tables
.schema content_type

# 查询内容类型
SELECT id, name FROM content_type;

# 退出
.quit
```

## 开发和扩展

如需扩展数据库功能，可以在以下文件中添加代码：

- `core/db/models.py` - 添加新的数据库模型
- `core/db/repository.py` - 添加新的数据访问方法
- `core/models/db_adapter.py` - 扩展数据库适配器接口

## 注意事项

1. **数据备份**：在进行重要更改前，建议备份数据库文件
2. **同步模式**：请谨慎使用完整同步模式，以免意外删除数据
3. **配置修改**：修改配置后，需要重启应用或手动同步才能生效
4. **迁移方案**：将来如需迁移到其他数据库系统，可以通过 DBAdapter 接口实现

# 内容类型管理

GenFlow在数据库中存储和管理各种内容类型配置。下面是管理这些配置的示例代码：

```python
# 导入必要的模块
from core.models.content_manager import ContentManager

# 初始化内容管理器
ContentManager.initialize()

# 获取所有内容类型
content_types = ContentManager.get_all_content_types()
print(f"可用的内容类型: {list(content_types.keys())}")

# 获取特定内容类型
blog_type = ContentManager.get_content_type('blog')
print(f"博客内容类型: {blog_type.name}")
print(f"结构模板数量: {len(blog_type.structure_templates)}")

# 根据类别获取内容类型
tech_type = ContentManager.get_content_type_by_category('技术')
if tech_type:
    print(f"技术类别推荐内容类型: {tech_type.name}")
```
