# GenFlow 核心模型 - 开发指南

## 设计原则

GenFlow 核心模型遵循以下关键设计原则：

1. **最小可用原则**：
   - 核心组件应仅实现必要功能，不添加猜测性的业务逻辑
   - 每个模块专注于单一职责，避免职责混淆
   - 公开简洁的 API，隐藏实现细节

2. **层次分离**：
   - 模型层与业务层严格分离
   - 核心模型不依赖业务层，不主动调用业务层方法
   - 模型层专注于数据管理和配置加载，不包含复杂业务策略

3. **适配器模式**：
   - 使用适配器将数据访问与业务逻辑解耦
   - 通过接口抽象隔离实现细节
   - 简化底层技术变更带来的影响

## 配置管理

GenFlow 使用基于 JSON 的配置系统，便于扩展和修改：

### 目录结构

```
core/models/
  ├── infra/
  │   ├── config_service.py  # 配置加载核心组件
  │   ├── db_adapter.py      # 数据库访问适配器
  │   ├── json_loader.py     # JSON配置加载工具
  │   ├── base_manager.py    # 管理器基类
  │   ├── temporary_storage.py # 临时存储服务
  │   └── enums.py           # 枚举定义
  ├── style/
  │   ├── style_manager.py   # 风格管理组件
  │   └── style_model.py     # 风格数据模型
  ├── article/
  │   ├── article_manager.py # 文章管理组件
  │   └── article_model.py   # 文章数据模型
  ├── db/                   # 数据库支持模块
  │   ├── __init__.py       # 模块入口和类型导出
  │   ├── initialize.py     # 数据库初始化
  │   ├── session.py        # 数据库会话管理
  │   ├── model_manager.py  # 数据模型关系定义
  │   ├── repository.py     # 数据仓库模式实现
  │   ├── migrate_configs.py # 配置迁移工具
  │   └── utils.py          # 数据库工具函数
  └── content_manager.py     # 统一访问接口
```

### 配置文件

系统配置存储在JSON文件中：

- 内容类型: `config/content_types/*.json`
- 文章风格: `config/styles/*.json`
- 平台配置: `config/platforms/*.json`

### 数据流关系图

配置与数据在 GenFlow 系统中的关系如下：

```
【配置组件】
ContentType --> 确定结构和规则 --> Article
ArticleStyle --> 确定表达风格 --> Article
Platform    --> 确定发布形式 --> Article

【数据流向】
Topic --> Research --> Outline --> Article
  ^          |           |
  |          v           v
  +-------- 反馈 ------- 更新
```

## 数据存储

GenFlow 使用多层次数据存储策略，根据数据类型和使用场景选择合适的存储方式。

### 存储方式一览

| 数据类型 | 主要存储 | 备份/缓存 | 持久化策略 |
|---------|---------|----------|----------|
| 配置数据 | JSON 文件 | 数据库 | 配置变更时同步到数据库 |
| 话题数据 | 数据库 | - | 创建时立即保存 |
| 研究数据 | 数据库 | 临时存储 | 完成后保存到数据库 |
| 大纲数据 | 数据库 | 临时存储 | 完成后保存到数据库 |
| 文章数据 | 数据库 | 文件系统 | 双重保存确保可恢复 |

### 配置数据存储

配置数据主要通过 JSON 文件管理，支持两种同步方式：

1. **配置优先模式**：配置文件作为主数据源，数据库作为备份
   - 系统启动时，将配置文件同步到数据库
   - 修改配置时，先更新文件再同步到数据库

2. **数据库优先模式**：数据库作为主数据源，配置文件作为备份
   - 系统首次启动时从配置文件导入到数据库
   - 后续直接从数据库读取
   - 可通过管理接口导出数据库配置到文件

配置数据使用 `DBAdapter` 的特定方法进行同步：

```python
# 从配置文件同步到数据库
DBAdapter.migrate_content_types_config()
DBAdapter.migrate_article_styles_config()
DBAdapter.migrate_platforms_config()

# 从数据库导出到配置文件
DBAdapter.export_content_types_to_config()
DBAdapter.export_article_styles_to_config()
DBAdapter.export_platforms_to_config()
```

### 内容数据存储

内容数据（话题、研究、大纲、文章）主要存储在数据库中，使用 SQLAlchemy ORM 模型定义数据结构：

```python
# 获取话题数据
topic = ContentManager.get_topic(topic_id)

# 保存文章到数据库
article_id = ContentManager.save_article(article)

# 查询研究数据
research = ContentManager.get_research_by_topic_id(topic_id)
```

内容处理过程中的临时数据使用 `TemporaryStorage` 服务管理：

```python
# 存储临时数据
temp_id = TemporaryStorage.store("outline", outline_data)

# 获取临时数据
outline_data = TemporaryStorage.get("outline", temp_id)

# 持久化临时数据
ContentManager.save_outline_from_temp(temp_id)
```

## 核心组件

### 1. ConfigService

专注于配置文件加载，不包含业务逻辑：

```python
from core.models.infra.config_service import ConfigService

# 初始化配置
ConfigService.initialize()

# 加载配置文件
config = ConfigService.load_config_file("app_config.json")

# 获取配置值
port = ConfigService.get_config("app.server.port", 8080)
```

### 2. DBAdapter

负责数据持久化，不关心业务规则：

```python
from core.models.infra.db_adapter import DBAdapter

# 初始化适配器
db = DBAdapter.initialize()

# 基本操作
record = db.find_one("articles", {"id": "article_123"})
result = db.insert_one("styles", style_data)
```

### 3. StyleManager

管理风格定义，无业务逻辑：

```python
from core.models.style.style_manager import StyleManager

# 初始化管理器
StyleManager.initialize()

# 获取风格
style = StyleManager.get_article_style("formal")

# 保存风格
StyleManager.save_style(new_style)
```

### 4. ArticleManager

处理文章数据，不包含内容生成逻辑：

```python
from core.models.article.article_manager import ArticleManager
from core.models.article.article_model import Article

# 初始化管理器
ArticleManager.initialize()

# 创建文章
article = Article(title="示例文章", content="内容...")

# 保存文章
ArticleManager.save_article(article)
```

## 基础设施组件（infra）

GenFlow 的基础设施组件是整个系统的核心支撑层，负责提供通用工具和服务，这些组件的设计遵循了单一职责原则和最小可用原则，确保每个组件专注于自身的核心功能。

### 1. ConfigService

**必要性**: 提供统一的配置加载和访问机制，是系统初始化的基础。

**职责**:
- 从文件系统加载配置文件
- 提供点分隔符形式的配置访问
- 管理配置缓存和更新

**设计理念**:
- 使用类方法提供无状态服务
- 所有方法返回明确的成功/失败状态
- 异常处理内部化，不向上层抛出异常

### 2. DBAdapter

**必要性**: 为上层提供统一的数据访问接口，隔离数据库实现细节。

**职责**:
- 连接数据库并处理初始化
- 转换业务对象和数据库实体
- 提供CRUD操作接口
- 执行配置同步逻辑

**设计理念**:
- 使用适配器模式分离业务逻辑和数据访问
- 所有数据库错误在适配器层处理
- 提供类型安全的接口，避免运行时错误

### 3. JsonModelLoader

**必要性**: 负责加载和解析JSON配置文件，支持多种模型类型。

**职责**:
- 从目录和文件加载JSON配置
- 将JSON数据转换为对象模型
- 提供模型保存功能

**设计理念**:
- 通用设计，支持任意模型类型
- 使用泛型保证类型安全
- 强大的错误处理确保配置加载失败不会影响系统运行

### 4. BaseManager

**必要性**: 为所有管理器提供一致的基础接口和功能。

**职责**:
- 定义管理器的通用接口
- 提供初始化和状态管理
- 实现数据库使用标志

**设计理念**:
- 使用抽象基类定义接口约束
- 提供默认实现减少重复代码
- 简化管理器实现的复杂度

### 5. TemporaryStorage

**必要性**: 为临时数据提供轻量级存储，避免不必要的数据库操作。

**职责**:
- 提供内存缓存服务
- 管理对象生命周期和自动清理
- 支持服务器重启后持久化恢复

**设计理念**:
- 使用泛型设计支持任意类型
- 线程安全实现确保并发访问
- 自动过期机制避免内存泄漏

### 6. Enums

**必要性**: 集中定义系统中使用的枚举类型，确保一致性。

**职责**:
- 定义文章结构相关枚举
- 定义内容分类枚举
- 定义生产阶段和状态枚举

**设计理念**:
- 集中化枚举定义避免重复
- 使用str基类确保序列化兼容性
- 提供辅助方法简化枚举使用

## 数据库支持模块（db）

GenFlow 的数据库支持模块提供了数据持久化和访问的基础设施，遵循仓库模式和适配器模式设计，确保数据访问与业务逻辑解耦。

### 1. 模块入口（__init__.py）

**必要性**: 提供模块导出和类型定义，是数据库模块的入口点。

**职责**:
- 导出数据模型类
- 定义模块级别的文档
- 集中管理类型导入

**设计理念**:
- 简洁明了的类型导出
- 避免循环导入问题
- 提供明确的公共API

### 2. 数据库会话管理（session.py）

**必要性**: 提供数据库连接和会话管理，是所有数据库操作的基础。

**职责**:
- 创建和管理数据库连接
- 提供会话上下文管理
- 处理数据库事务

**设计理念**:
- 使用上下文管理器确保资源正确释放
- 统一会话管理降低连接开销
- 提供数据导入导出功能

### 3. 数据库初始化（initialize.py）

**必要性**: 负责数据库表结构创建和默认数据导入，确保系统初始状态正确。

**职责**:
- 创建数据库表结构
- 导入默认配置数据
- 提供初始化入口点

**设计理念**:
- 模块化初始化过程
- 支持增量更新或全量重置
- 详细日志记录初始化过程

### 4. 数据仓库（repository.py）

**必要性**: 实现数据仓库模式，为各类数据实体提供统一的CRUD操作接口。

**职责**:
- 提供实体的增删改查
- 封装复杂查询逻辑
- 处理对象关系映射

**设计理念**:
- 使用泛型基类减少代码重复
- 每个仓库类专注于单一实体
- 提供类型安全的方法接口

### 5. 配置迁移（migrate_configs.py）

**必要性**: 负责将JSON配置文件同步到数据库，支持增量更新和全量同步。

**职责**:
- 读取配置文件数据
- 将配置同步到数据库
- 处理冲突和删除逻辑

**设计理念**:
- 支持同步模式和增量模式
- 安全处理配置冲突
- 提供详细的操作日志

### 6. 工具函数（utils.py）

**必要性**: 提供数据库操作相关的辅助工具和类型转换功能。

**职责**:
- 提供JSON字段类型
- 处理模型转换
- 辅助时间字段处理

**设计理念**:
- 专注于通用功能
- 简化重复代码
- 提高代码可维护性

## 扩展核心模型

### 扩展内容类型

创建新的内容类型JSON配置文件：

```json
{
  "id": "new_type",
  "name": "新内容类型",
  "description": "这是一个新的内容类型",
  "format": "long-form",
  "compatible_styles": ["formal", "casual"]
}
```

### 扩展文章风格

创建新的文章风格JSON配置文件：

```json
{
  "id": "new_style",
  "name": "新风格",
  "description": "新的文章风格",
  "tone": "friendly",
  "formality": 3,
  "content_types": ["blog", "article"]
}
```

## 错误处理策略

1. **返回值而非异常**：
   - 查询方法返回 `None` 或空集合而非抛出异常
   - 操作方法返回布尔值表示成功/失败

2. **详细日志**：
   - 所有组件使用 loguru 记录详细日志
   - 错误信息包含上下文信息以便调试

3. **防御性编程**：
   - 输入参数验证
   - 空值处理
   - 类型检查

## 避免的反模式

1. **不添加猜测性业务逻辑**：
   - 不基于假设添加业务层可能需要的功能
   - 不在模型层实现内容生成或质量评估逻辑

2. **不滥用继承**：
   - 优先使用组合而非继承
   - 保持类层次简单扁平

3. **不依赖具体业务流程**：
   - 模型组件不应假设特定业务流程
   - 避免硬编码业务规则

4. **避免过度封装**：
   - 不为简单操作创建复杂抽象
   - 保持接口简单直观

## 使用建议

业务层应遵循以下原则使用核心模型：

1. **明确初始化**：
   - 在应用启动时显式初始化 ContentManager
   - 使用前检查初始化状态

2. **错误处理**：
   - 检查返回值，不假设操作总是成功
   - 实现适当的重试和失败处理策略

3. **配置扩展**：
   - 通过添加JSON配置文件扩展功能
   - 避免直接修改核心组件代码
