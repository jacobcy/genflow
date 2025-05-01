# GenFlow 平台模块 (`core.models.platform`)

## 1. 概述

本模块负责定义和管理 GenFlow 系统支持的外部发布平台（如微信公众号、知乎、Medium 等）的配置信息。平台配置主要包含平台的属性、内容发布约束以及技术对接要求。

配置数据**来源于** `core/models/platform/collection/` 目录下的各个 JSON 文件，每个文件代表一个平台。

## 2. 文件结构与职责

| 文件名                 | 主要职责                                                     |
| :--------------------- | :----------------------------------------------------------- |
| `__init__.py`          | 包标识符。 (通常为空或导出核心类)                            |
| `platform.py`          | 定义 `Platform` Pydantic 模型及其嵌套模型 `PlatformConstraints` 和 `TechnicalRequirements`，用于表示加载后的平台配置对象。该模型仅包含数据结构。 |
| `platform_db.py`       | 定义 `PlatformDB` SQLAlchemy 模型，用于在数据库中存储平台配置信息（可能包含基本字段和序列化后的约束/技术细节）。 |
| `platform_manager.py` | 定义 `PlatformManager` 类，负责在首次访问时从 `collection/` 目录加载所有平台的 JSON 配置文件到内存，并提供只读的访问接口（如按 ID、名称获取）。 |
| `collection/`          | **配置数据源目录**。包含每个平台的 JSON 配置文件 (例如 `bilibili.json`, `zhihu.json`)。 |
| `readme.md`            | 本文档。                                                     |

**已移除**: `platform_validator.py` (验证逻辑应由上层服务处理)。

## 3. 核心组件与使用

### 3.1. `collection/` 目录与 JSON 文件

这是平台配置的**数据源**。如需添加或修改平台配置，应直接编辑此目录下的相应 JSON 文件。JSON 文件的结构需要符合 `platform.py` 中定义的 `Platform` Pydantic 模型。

```json
// 示例: collection/my_platform.json
{
  "id": "my_platform_id",
  "name": "我的平台",
  "url": "https://myplatform.com",
  "description": "一个示例平台",
  "category": "blogging",
  "primary_language": "zh-CN",
  "supported_languages": ["zh-CN"],
  "constraints": {
    "min_length": 50,
    "max_length": 10000,
    // ... 其他约束字段
  },
  "technical": {
    "api_endpoint": "https://api.myplatform.com/v1",
    // ... 其他技术要求字段
  },
  "manual_review_likely": false
}
```

### 3.2. `Platform` (Pydantic)

定义在 `platform.py` 中，代表一个从 JSON 文件加载后的平台配置对象。

```python
from core.models.platform.platform import Platform

# 示例 (通常通过 Manager 获取)
# platform = Platform(id="my_id", name="我的平台", ...)
# print(platform.constraints.min_length)
```

### 3.3. `PlatformDB` (SQLAlchemy)

定义在 `platform_db.py` 中，用于数据库存储。通常由 `migrate_configs.py` 或 `initialize.py` 将 `collection/` 中的配置同步到数据库。

### 3.4. `PlatformManager`

定义在 `platform_manager.py` 中，提供对平台配置的访问接口。

```python
from core.models.platform.platform_manager import PlatformManager

# 获取指定 ID 的平台配置
zhihu_platform = PlatformManager.get_platform("zhihu") # 假设存在 zhihu.json
if zhihu_platform:
    print(zhihu_platform.description)
    print(zhihu_platform.constraints.max_title_length)

# 获取所有平台配置
all_platforms = PlatformManager.get_all_platforms()
print(f"共加载 {len(all_platforms)} 个平台")

# 根据名称获取 (大小写不敏感)
medium_platform = PlatformManager.get_platform_by_name("Medium")
```

`PlatformManager` 在首次被调用时会自动从 `collection/` 目录加载所有 JSON 文件。

## 4. 外部依赖

*   `loguru`: 用于日志记录。
*   `pydantic`: 用于定义 `Platform` 模型。
*   `sqlalchemy`: 用于定义 `PlatformDB` (在 `platform_db.py` 中)。
*   `core.models.db.session`: (在 `platform_db.py` 中) 依赖数据库会话基类。
*   `core.models.infra.json_loader`: (在 `platform_manager.py` 中) 用于加载 JSON 文件。
*   `os`: (在 `platform_manager.py` 中) 用于文件系统操作。

## 5. 注意事项

*   平台配置数据的主要来源是 `collection/` 目录下的 JSON 文件。
*   `PlatformManager` 是只读的，不提供保存配置的功能。修改配置需要直接编辑 JSON 文件。
*   数据库中的 `PlatformDB` 表主要用于可能的查询优化或与其他数据的关联，其数据应通过迁移脚本与 `collection/` 目录保持同步。
*   内容验证逻辑（如检查文章是否符合平台约束）已被移除，应由需要验证的服务或 Factory 实现。 