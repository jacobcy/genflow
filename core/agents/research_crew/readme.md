# 研究团队 (ResearchCrew)

## 概述

ResearchCrew 是一个基于 CrewAI 框架构建的智能研究团队，专门负责信息收集、事实验证和内容研究。该模块采用多智能体协作模式，提供全面的研究服务，从初步搜索到深度分析，为内容创作提供坚实的事实基础和丰富的资料支持。

## 架构设计

研究系统采用三层架构设计，具有清晰的职责边界和数据流：

### 1. TeamAdapter层
- **位置**: 控制器和具体团队之间的桥梁
- **输入**: topic_id 或 Topic对象
- **处理**: 不包含业务逻辑，只负责参数传递和结果转换
- **输出**: 将ResearchAdapter返回的研究结果传递给控制器

### 2. ResearchAdapter层 (ResearchTeamAdapter)
- **位置**: TeamAdapter和ResearchCrew之间的适配层
- **输入**:
  - topic_id、Topic对象或话题字符串
  - content_type (默认为"article")
  - 研究深度设置
- **处理**:
  - 解析话题信息(topic_title, topic_id)
  - 根据content_type生成研究配置
  - 调用ResearchCrew，传递具体参数
- **输出**:
  - 根据是否有topic_id返回BasicResearch或TopicResearch
  - 不保存研究结果

### 3. ResearchCrew层
- **位置**: 核心研究实现层
- **输入**:
  - 话题标题字符串
  - 研究配置参数(深度、专家需求等)
- **处理**:
  - 执行具体研究任务
  - 不处理content_type解析
  - 不处理topic_id关联逻辑
- **输出**:
  - 返回BasicResearch对象

## 数据流

```
控制器 → TeamAdapter → ResearchAdapter → ResearchCrew → ResearchAdapter → TeamAdapter → 控制器
   |        |               |                |               |                |             |
topic_id → topic_id → (topic_title,    → 研究参数 →   →   → BasicResearch → TopicResearch → 结果应用
                     research_config)                          ↑                ↑
                                                      (不含topic_id)    (包含topic_id)
```

## 核心功能

- **主题探索**：分析研究主题并确定关键探索点
- **信息搜索**：从多渠道收集相关资料和数据
- **事实验证**：确认关键信息的准确性和可靠性
- **深度分析**：对收集的信息进行整理和分析
- **研究报告**：生成结构化的研究结果报告
- **话题建议**：提供潜在的内容拓展方向

## 关键类

### ResearchCrew

核心研究实现类，管理研究智能体和执行研究流程。

```python
research_crew = ResearchCrew()
result = await research_crew.research_topic(
    topic="人工智能在医疗领域的应用",
    research_config={"depth": "deep", "needs_expert": True},
    depth="deep"
)
```

### ResearchTeamAdapter

研究团队适配器，处理参数转换和结果映射。

```python
adapter = ResearchTeamAdapter()
result = await adapter.research_topic(
    topic=Topic(id="123", title="人工智能在医疗领域的应用", content_type="technical"),
    depth="deep"
)
```

### BasicResearch / TopicResearch

存储研究结果的对象，包含收集的信息、验证结果和综合分析。

```python
# BasicResearch - 基础研究结果
basic_result.title           # 研究标题
basic_result.background      # 背景信息
basic_result.expert_insights # 专家见解
basic_result.key_findings    # 关键发现
basic_result.report          # 完整研究报告

# TopicResearch - 带有topic_id的研究结果
topic_result.topic_id        # 关联的话题ID
```

## 智能体组成

ResearchCrew 由四个专业智能体组成，各自负责研究流程的不同阶段：

1. **背景研究员 (BackgroundResearcherAgent)**：收集话题的基础信息和背景知识
2. **专家发现员 (ExpertFinderAgent)**：寻找并分析相关领域专家的观点和见解
3. **数据分析师 (DataAnalystAgent)**：分析与话题相关的数据和趋势
4. **研究撰写员 (ResearchWriterAgent)**：整合研究结果，生成完整的研究报告

## 工作流程

1. **参数解析**:
   - ResearchAdapter解析话题信息和内容类型
   - 生成研究配置，转换为ResearchCrew需要的格式

2. **背景研究**:
   - 分析研究主题的核心概念
   - 收集历史背景和基础知识
   - 识别关键术语和概念

3. **专家观点**（可选）:
   - 寻找领域专家和其观点
   - 整理专家见解和分析
   - 提取价值洞见

4. **数据分析**（可选）:
   - 分析相关数据和统计信息
   - 识别趋势和模式
   - 评估数据可靠性

5. **研究报告**:
   - 整合所有研究内容
   - 生成结构化报告
   - 提出基于研究的建议

6. **结果转换**:
   - 将ResearchWorkflowResult转换为BasicResearch
   - 如有topic_id，则创建TopicResearch

## 使用示例

### 基本研究流程

```python
from core.agents.research_crew.research_adapter import ResearchTeamAdapter
from core.models.topic import Topic

# 创建研究主题
topic = Topic(
    id="t123",
    title="量子计算的商业应用",
    content_type="technical"
)

# 初始化研究适配器
adapter = ResearchTeamAdapter()
await adapter.initialize()

# 执行研究
result = await adapter.research_topic(
    topic=topic,
    depth="deep"
)

# 使用研究结果
print(f"研究标题: {result.title}")
print(f"关联话题ID: {result.topic_id}")
print(f"背景信息长度: {len(result.background or '')}")
print(f"专家见解数量: {len(result.expert_insights)}")
print(f"研究报告摘要: {result.summary[:200] if result.summary else 'N/A'}")
```

### 事实验证流程

```python
from core.agents.research_crew.research_adapter import ResearchTeamAdapter

# 初始化研究适配器
adapter = ResearchTeamAdapter()
await adapter.initialize()

# 需要验证的陈述列表
statements = [
    "中国是全球最大的可再生能源投资国",
    "2023年全球AI市场规模达到1500亿美元",
    "特斯拉Model 3在2022年是全球销量最高的电动汽车"
]

# 执行事实验证
verification_results = await adapter.verify_facts(
    statements=statements,
    thoroughness="high"
)

# 分析验证结果
for statement, result in verification_results.items():
    print(f"陈述: {statement}")
    print(f"验证结果: {'✓ 正确' if result['is_verified'] else '✗ 不正确'}")
    print(f"置信度: {result['confidence_score']}/10")
    print(f"证据来源: {', '.join(result['sources'][:3])}")
    print(f"补充说明: {result['notes']}\n")
```

## 配置选项

研究系统支持多种配置选项，可以根据内容类型自动选择最合适的研究策略：

| 内容类型 | 研究深度 | 专家见解 | 数据分析 | 最大来源数 |
|---------|---------|---------|---------|----------|
| article | medium  | 是      | 是      | 10       |
| blog    | medium  | 是      | 否      | 5        |
| news    | light   | 是      | 是      | 3        |
| technical | deep  | 是      | 是      | 15       |

通过调整这些配置，可以控制研究过程的深度和广度，满足不同内容类型的需求。
