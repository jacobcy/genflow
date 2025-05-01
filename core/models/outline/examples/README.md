# 大纲模块使用示例

本目录包含大纲模块的使用示例，展示如何使用大纲模块的各种功能。

## 临时大纲存储示例

`temp_outline_example.py` 展示了如何使用临时大纲存储功能，包括：

1. 创建临时大纲
2. 保存到临时存储
3. 从临时存储获取
4. 更新临时大纲
5. 删除临时大纲

### 运行示例

```bash
python -m core.models.outline.examples.temp_outline_example
```

### 临时大纲存储与持久化大纲存储的区别

- **临时大纲存储**：使用 `OutlineStorage` 类，基于内存存储，适用于临时大纲、草稿大纲等不需要长期保存的场景。
- **持久化大纲存储**：使用 `OutlineManager` 类，基于数据库存储，适用于需要长期保存的正式大纲。

### 使用场景

临时大纲存储适用于以下场景：

1. 用户正在编辑的草稿大纲
2. 生成过程中的中间大纲
3. 临时保存的大纲版本
4. 不需要与数据库交互的大纲操作

### 示例代码

```python
from core.models.outline import BasicOutline, OutlineNode, OutlineStorage

# 初始化存储
OutlineStorage.initialize()

# 创建大纲
outline = BasicOutline(
    title="临时大纲",
    description="这是一个临时大纲示例",
    nodes=[
        OutlineNode(title="第一章", level=1, content="内容概述")
    ]
)

# 保存到临时存储
outline_id = OutlineStorage.save_outline(outline)

# 从临时存储获取
retrieved_outline = OutlineStorage.get_outline(outline_id)

# 更新临时存储
retrieved_outline.description = "已更新的描述"
OutlineStorage.update_outline(outline_id, retrieved_outline)

# 删除临时大纲
OutlineStorage.delete_outline(outline_id)
```