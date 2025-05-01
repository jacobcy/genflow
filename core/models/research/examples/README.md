# 研究模块使用示例

本目录包含研究模块的使用示例，展示如何使用研究模块的各种功能。

## 临时研究存储示例

`temp_research_example.py` 展示了如何使用临时研究存储功能，包括：

1. 创建临时研究
2. 保存到临时存储
3. 从临时存储获取
4. 更新临时研究
5. 删除临时研究

### 运行示例

```bash
python -m core.models.research.examples.temp_research_example
```

### 临时研究存储与持久化研究存储的区别

- **临时研究存储**：使用 `ResearchStorage` 类，基于内存存储，适用于临时研究、草稿研究等不需要长期保存的场景。
- **持久化研究存储**：使用 `ResearchManager` 类，基于数据库存储，适用于需要长期保存的正式研究。

### 使用场景

临时研究存储适用于以下场景：

1. 用户正在编辑的草稿研究
2. 生成过程中的中间研究
3. 临时保存的研究版本
4. 不需要与数据库交互的研究操作

### 示例代码

```python
from core.models.research import BasicResearch, KeyFinding, Source, ResearchStorage

# 初始化存储
ResearchStorage.initialize()

# 创建研究
research = BasicResearch(
    title="临时研究",
    content_type="article",
    key_findings=[
        KeyFinding(
            content="这是一个关键发现",
            importance=0.8,
            sources=[
                Source(
                    name="示例来源",
                    url="https://example.com",
                    reliability_score=0.9
                )
            ]
        )
    ]
)

# 保存到临时存储
research_id = ResearchStorage.save_research(research)

# 从临时存储获取
retrieved_research = ResearchStorage.get_research(research_id)

# 更新临时存储
retrieved_research.summary = "已更新的摘要"
ResearchStorage.update_research(research_id, retrieved_research)

# 删除临时研究
ResearchStorage.delete_research(research_id)
```