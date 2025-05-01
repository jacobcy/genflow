# Research 模块

研究报告模型及其相关业务逻辑组件，用于创建、管理和操作研究数据。该模块负责处理内容研究过程中产生的各类信息，包括专家见解、关键发现和参考来源等。

## 架构设计

本模块采用分层架构，将数据模型、业务逻辑和持久化操作分离：

- **数据模型层**：`basic_research.py` 和 `research.py` 定义了研究报告的数据结构
- **业务逻辑层**：`research_factory.py` 包含研究报告的业务操作和转换逻辑
- **持久化层**：`research_manager.py` 负责研究报告的持久化存储和检索
- **临时存储层**：`research_storage.py` 和 `research_adapter.py` 提供研究的临时存储功能
- **工具层**：`utils` 包提供辅助功能，如格式化和验证

## 核心组件

### 1. BasicResearch 类

研究报告的基础数据模型，定义了研究的核心数据结构，不含ID和存储相关字段。

```python
from .basic_research import BasicResearch, KeyFinding, Source, ExpertInsight

# 创建一个来源
source = Source(
    name="学术期刊",
    url="https://example.com/paper",
    reliability_score=0.9
)

# 创建一个专家见解
insight = ExpertInsight(
    expert_name="专家姓名",
    content="专家的观点和见解",
    field="专业领域"
)

# 创建一个关键发现
finding = KeyFinding(
    content="研究发现的关键内容",
    importance=0.8,
    sources=[source]
)

# 创建一个基础研究报告
research = BasicResearch(
    title="研究标题",
    content_type="tech_analysis",
    background="研究背景描述",
    expert_insights=[insight],
    key_findings=[finding],
    sources=[source]
)
```

### 2. TopicResearch 类

针对特定话题的研究报告模型，继承自BasicResearch并添加了ID和话题关联。

```python
from .research import TopicResearch

# 创建一个话题研究报告
topic_research = TopicResearch(
    id="research_001",
    topic_id="topic_001",
    title="研究标题",
    content_type="tech_analysis",
    background="研究背景描述"
)

# 从基础研究转换为话题研究
topic_research = TopicResearch.from_basic_research(basic_research, "topic_001")
```

### 3. ResearchFactory 类

提供研究报告的业务逻辑操作，如创建、验证、存储等。

```python
from .research_factory import ResearchFactory

# 创建研究报告
research = ResearchFactory.create_research(
    title="研究标题",
    content_type="tech_analysis",
    topic_id="topic_001"
)

# 保存研究报告
research_id = ResearchFactory.save_research(research)

# 获取研究报告
research = ResearchFactory.get_research(research_id)

# 验证研究报告
is_valid = ResearchFactory.validate_research(research)

# 创建关键发现
finding = ResearchFactory.create_key_finding(
    content="关键发现内容",
    importance=0.7
)

# 创建来源信息
source = ResearchFactory.create_source(
    name="信息来源",
    url="https://example.com"
)

# 创建专家见解
insight = ResearchFactory.create_expert_insight(
    expert_name="专家姓名",
    content="专家观点"
)

# 从简化格式创建研究报告
research = ResearchFactory.from_simple_research(
    title="研究标题",
    content="研究内容",
    key_points=[{"content": "要点1", "importance": 0.8}],
    references=[{"title": "参考资料", "url": "https://example.com"}],
    content_type="tech_analysis"
)

# 删除研究报告
success = ResearchFactory.delete_research(research_id)

# 列出所有研究报告
research_ids = ResearchFactory.list_researches()
```

### 4. ResearchManager 类

负责研究报告的持久化操作，包括加载、存储和检索。

```python
from .research_manager import ResearchManager

# 初始化管理器
ResearchManager.initialize()

# 确保已初始化
ResearchManager.ensure_initialized()

# 获取研究报告
research = ResearchManager.get_research("research_001")

# 保存研究报告
success = ResearchManager.save_research(research)

# 删除研究报告
success = ResearchManager.delete_research("research_001")

# 列出所有研究报告ID
research_ids = ResearchManager.list_researches()
```

### 5. ResearchStorage 类

提供研究的临时存储功能，基于内存存储，适用于临时研究、草稿研究等不需要持久化的场景。

```python
from core.models.research import ResearchStorage, BasicResearch

# 初始化存储
ResearchStorage.initialize()

# 获取临时研究
research = ResearchStorage.get_research("research_id")

# 保存临时研究
research_id = ResearchStorage.save_research(research)

# 更新临时研究
ResearchStorage.update_research(research_id, research)

# 删除临时研究
ResearchStorage.delete_research(research_id)

# 列出所有临时研究ID
research_ids = ResearchStorage.list_researches()
```

### 6. ResearchAdapter 类

封装对研究临时存储的操作，提供异常处理和日志记录。

```python
from core.models.research import ResearchAdapter, BasicResearch

# 初始化适配器
ResearchAdapter.initialize()

# 获取临时研究
research = ResearchAdapter.get_research("research_id")

# 保存临时研究
research_id = ResearchAdapter.save_research(research)

# 更新临时研究
ResearchAdapter.update_research(research_id, research)

# 删除临时研究
ResearchAdapter.delete_research(research_id)

# 列出所有临时研究ID
research_ids = ResearchAdapter.list_researches()
```

### 7. 辅助工具

研究模块提供了一系列辅助工具，位于`utils`包中：

```python
from core.models.research.utils import (
    format_research_as_markdown,
    format_research_as_json,
    validate_research_data,
    validate_source,
    get_research_completeness
)

# 格式化研究报告为Markdown
markdown_text = format_research_as_markdown(research)

# 格式化为JSON兼容的字典
research_dict = format_research_as_json(research)

# 验证研究报告数据
is_valid, errors = validate_research_data(research)
if not is_valid:
    print(f"验证失败: {errors}")

# 验证来源信息
is_valid_source, source_errors = validate_source(source)

# 获取研究报告完整度评估
completeness = get_research_completeness(research)
print(f"研究报告完整度: {completeness['overall']}%")
print(f"专家见解完整度: {completeness['expert_insights']}%")
```

这些工具函数可用于：

1. **数据验证**：检查研究报告数据的有效性和完整性
2. **格式转换**：将研究报告转换为不同格式，便于展示和导出
3. **质量评估**：评估研究报告的完整度和质量

## 常见使用场景

### 通过ContentManager使用（推荐）

作为系统的统一入口，推荐使用ContentManager来操作研究报告：

```python
from core.models.content_manager import ContentManager

# 初始化
ContentManager.initialize()

# 创建研究报告
research = ContentManager.create_research(
    topic_id="topic_001",
    title="研究标题",
    content_type="tech_analysis",
    background="研究背景信息"
)

# 获取研究报告
research = ContentManager.get_research("research_id")

# 保存研究报告
success = ContentManager.save_research(research)

# 删除研究报告
success = ContentManager.delete_research("research_id")

# 验证研究报告
is_valid = ContentManager.validate_research(research)
```

### 创建并保存研究报告

```python
from core.models.content_manager import ContentManager
from core.models.research.research_factory import ResearchFactory
from core.models.research.basic_research import Source, KeyFinding, ExpertInsight

# 方法1：通过ContentManager创建简单研究报告
research = ContentManager.create_research(
    topic_id="topic_001",
    title="人工智能在医疗领域的应用",
    content_type="tech_analysis",
    background="人工智能技术正在医疗领域展现出巨大潜力..."
)

# 方法2：使用ResearchFactory创建详细研究报告
# 创建来源信息
source1 = ResearchFactory.create_source(
    name="医学期刊",
    url="https://medical-journal.com/ai-research",
    author="Dr. Smith",
    reliability_score=0.95
)

# 创建专家见解
insight1 = ResearchFactory.create_expert_insight(
    expert_name="Dr. Johnson",
    content="AI在诊断领域的准确率已达到90%以上",
    field="医学影像学",
    credentials="哈佛医学院教授"
)

# 创建关键发现
finding1 = ResearchFactory.create_key_finding(
    content="AI可以减少诊断错误率达30%",
    importance=0.9,
    sources=[source1.model_dump()]
)

# 创建完整研究报告
research = ResearchFactory.create_research(
    title="AI在医疗诊断中的应用研究",
    content_type="medical_research",
    topic_id="topic_002",
    background="本研究探讨了人工智能在医疗诊断中的应用...",
    expert_insights=[insight1],
    key_findings=[finding1],
    sources=[source1]
)

# 保存研究报告
research_id = ResearchFactory.save_research(research)
```

### 加载并更新研究报告

```python
from core.models.content_manager import ContentManager
from core.models.research.research_factory import ResearchFactory

# 获取研究报告
research = ContentManager.get_research("research_id")

if research:
    # 添加新的关键发现
    new_finding = ResearchFactory.create_key_finding(
        content="新的研究发现",
        importance=0.8
    )
    research.key_findings.append(new_finding)

    # 更新标题
    research.title = "更新后的研究标题"

    # 添加新的专家见解
    new_insight = ResearchFactory.create_expert_insight(
        expert_name="新专家",
        content="专家新的见解",
        field="专业领域"
    )
    research.expert_insights.append(new_insight)

    # 保存更新
    ContentManager.save_research(research)
```

### 从简化格式创建研究报告

```python
from core.models.research.research_factory import ResearchFactory

# 定义简化的研究数据
title = "人工智能发展趋势研究"
content = "人工智能技术正在快速发展，并在各行各业得到广泛应用..."
key_points = [
    {"content": "深度学习是当前AI发展的主要方向", "importance": 0.9},
    {"content": "自然语言处理技术取得突破性进展", "importance": 0.8},
    {"content": "多模态AI是未来的发展趋势", "importance": 0.95}
]
references = [
    {
        "title": "AI发展报告2023",
        "url": "https://example.com/ai-report",
        "author": "AI研究所",
        "date": "2023-06-15"
    },
    {
        "title": "深度学习最新进展",
        "url": "https://example.com/deep-learning",
        "author": "Tech Journal",
        "reliability": 0.85
    }
]

# 从简化格式创建研究报告
research = ResearchFactory.from_simple_research(
    title=title,
    content=content,
    key_points=key_points,
    references=references,
    content_type="tech_trend"
)

# 保存研究报告
research_id = ResearchFactory.save_research(research)
```

### 使用临时研究存储

当需要存储临时研究、草稿研究等不需要持久化的研究时，可以使用 ResearchStorage：

```python
from core.models.facade.simple_content_manager import SimpleContentManager
from core.models.research import BasicResearch, KeyFinding, Source

# 初始化
SimpleContentManager.initialize()

# 创建临时研究
research = SimpleContentManager.create_basic_research(
    title="临时研究示例",
    content_type="article",
    key_findings=[
        KeyFinding(
            content="这是一个关键发现",
            importance=0.8
        )
    ]
)

# 保存临时研究
research_id = SimpleContentManager.save_basic_research(research)

# 获取临时研究
retrieved_research = SimpleContentManager.get_basic_research(research_id)

# 更新临时研究
SimpleContentManager.update_basic_research(research_id, updated_research)

# 删除临时研究
SimpleContentManager.delete_basic_research(research_id)
```

## 注意事项

1. 使用前需确保相应的初始化方法已调用：
   - 使用 ContentManager 时，调用 `ContentManager.initialize()`
   - 使用 ResearchManager 时，调用 `ResearchManager.initialize()`
   - 使用 ResearchStorage 时，调用 `ResearchStorage.initialize()`
   - 使用 SimpleContentManager 时，调用 `SimpleContentManager.initialize()`
2. 外部系统应通过 `ContentManager` 或 `SimpleContentManager` 调用研究功能，而不直接调用内部组件
3. 保存研究报告前应先调用 `validate_research` 确保数据完整性
4. `BasicResearch` 是基础数据结构，与数据库交互时应使用 `TopicResearch`
5. 注意处理ID的一致性，优先使用 `metadata.research_id` 或 `TopicResearch.id`
6. 临时研究存储和持久化研究存储的区别：
   - **临时研究存储**：使用 `ResearchStorage` 类，基于内存存储，适用于临时研究、草稿研究等不需要长期保存的场景。
   - **持久化研究存储**：使用 `ResearchManager` 类，基于数据库存储，适用于需要长期保存的正式研究。
