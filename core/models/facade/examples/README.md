# 门面模式示例

本目录包含门面模式的使用示例，展示如何使用门面类统一管理底层组件。

## 简单内容管理器示例

`simple_content_example.py` 展示了如何使用 SimpleContentManager 管理临时内容对象，包括：

1. 临时大纲的创建、保存、获取、更新和删除
2. 临时研究的创建、保存、获取、更新和删除

### 运行示例

```bash
python -m core.models.facade.examples.simple_content_example
```

### 门面模式的优势

门面模式（Facade Pattern）提供了以下优势：

1. **简化接口**：为复杂的子系统提供一个简单的接口，降低客户端的使用难度
2. **解耦合**：客户端与子系统的实现细节解耦，只需要与门面交互
3. **统一入口**：为多个子系统提供一个统一的入口，便于管理和使用
4. **隐藏复杂性**：隐藏子系统的复杂性，只暴露必要的功能

### 示例代码

```python
from core.models.facade.simple_content_manager import SimpleContentManager
from core.models.outline.basic_outline import OutlineNode
from core.models.research.basic_research import BasicResearch, KeyFinding, Source

# 初始化
SimpleContentManager.initialize()

# 创建临时大纲
outline = SimpleContentManager.create_basic_outline(
    title="临时大纲示例",
    content_type="article",
    nodes=[
        OutlineNode(title="第一章", level=1, content="内容概述")
    ]
)

# 保存临时大纲
outline_id = SimpleContentManager.save_basic_outline(outline)

# 获取临时大纲
retrieved_outline = SimpleContentManager.get_basic_outline(outline_id)

# 更新临时大纲
SimpleContentManager.update_basic_outline(outline_id, retrieved_outline)

# 删除临时大纲
SimpleContentManager.delete_basic_outline(outline_id)

# 创建临时研究
research = SimpleContentManager.create_basic_research(
    title="临时研究示例",
    background="研究背景信息",
    content_type="article",
    key_findings=[
        KeyFinding(
            content="关键发现内容",
            importance=0.8
        )
    ]
)

# 保存临时研究
research_id = SimpleContentManager.save_basic_research(research)

# 获取临时研究
retrieved_research = SimpleContentManager.get_basic_research(research_id)

# 更新临时研究
SimpleContentManager.update_basic_research(research_id, retrieved_research)

# 删除临时研究
SimpleContentManager.delete_basic_research(research_id)
```