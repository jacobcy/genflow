# 研究团队 (ResearchCrew)

## 概述

ResearchCrew 是一个基于 CrewAI 框架构建的智能研究团队，专门负责信息收集、事实验证和内容研究。该模块采用多智能体协作模式，提供全面的研究服务，从初步搜索到深度分析，为内容创作提供坚实的事实基础和丰富的资料支持。

## 架构设计

研究系统采用三层架构设计，具有清晰的职责边界、统一的数据协议和优化的数据流：

### 1. 协议层 (Protocol Layer)
- **位置**: 所有层之间统一的数据传输协议
- **组件**: `ResearchRequest`, `ResearchResponse`, `FactVerificationRequest`, `FactVerificationResponse`
- **职责**: 定义标准化的请求和响应对象，确保层间数据传递的一致性

### 2. 适配层 (ResearchTeamAdapter)
- **位置**: 控制器和研究团队之间的桥梁
- **输入**:
  - topic_id、Topic对象或话题字符串
  - content_type (默认为"article")
  - 研究深度设置
- **处理**:
  - 解析话题信息(topic_title, topic_id)
  - 根据content_type生成研究配置
  - 创建`ResearchRequest`对象
  - 调用ResearchCrew，传递请求对象
  - 将`ResearchResponse`转换为BasicResearch或TopicResearch
- **输出**:
  - 根据是否有topic_id返回BasicResearch或TopicResearch
  - 不保存研究结果

### 3. 实现层 (ResearchCrew)
- **位置**: 核心研究实现层
- **输入**:
  - `ResearchRequest`对象，包含话题标题、内容类型和研究配置
- **处理**:
  - 执行具体研究任务
  - 不处理topic_id关联逻辑
- **输出**:
  - 返回`ResearchResponse`对象，包含所有研究结果

## 数据流

```
控制器 → ResearchAdapter → ResearchCrew → ResearchAdapter → 控制器
   |             |               |               |               |
topic_id/Topic → ResearchRequest → 执行研究 → ResearchResponse → BasicResearch/TopicResearch
                     ↑                                |
                (包含各种参数)                        ↓
                                              (完整研究结果)
```

## 核心功能

- **主题探索**：分析研究主题并确定关键探索点
- **信息搜索**：从多渠道收集相关资料和数据
- **事实验证**：确认关键信息的准确性和可靠性
- **深度分析**：对收集的信息进行整理和分析
- **研究报告**：生成结构化的研究结果报告
- **话题建议**：提供潜在的内容拓展方向

## 关键类

### 协议类 (Protocol Classes)

定义层间数据传输的标准结构，优化数据流动。

```python
# 研究请求对象
request = ResearchRequest(
    topic_title="人工智能在医疗领域的应用",
    content_type="technical",
    depth="deep",
    config=research_config,
    options={"platform_id": "medium"}
)

# 研究响应对象
response = ResearchResponse(
    title="人工智能在医疗领域的应用",
    content_type="technical",
    background="...",
    report="...",
    experts=[...],
    key_findings=[...],
    sources=[...]
)
```

### ResearchCrew

核心研究实现类，管理研究智能体和执行研究流程。

```python
research_crew = ResearchCrew()
response = await research_crew.research_topic(
    request=ResearchRequest(
        topic_title="人工智能在医疗领域的应用",
        content_type="technical",
        depth="deep",
        config=research_config,
        options={}
    )
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

1. **参数解析与请求构建**:
   - ResearchAdapter解析话题信息和内容类型
   - 生成研究配置，创建ResearchRequest对象

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

6. **响应构建与结果转换**:
   - 创建ResearchResponse对象
   - 适配器层将响应转换为BasicResearch
   - 如有topic_id，则创建TopicResearch

## 事实验证流程

事实验证功能同样使用标准化的请求/响应对象：

```python
# 创建验证请求
request = FactVerificationRequest(
    statements=[
        "中国是全球最大的可再生能源投资国",
        "2023年全球AI市场规模达到1500亿美元"
    ],
    thoroughness="high",
    options={"include_sources": True}
)

# 获取验证结果
response = await crew.verify_facts(request)

# 分析验证结果
for result in response.results:
    print(f"陈述: {result['statement']}")
    print(f"验证结果: {'✓ 正确' if result['verified'] else '✗ 不正确'}")
    print(f"置信度: {result['confidence']}")
    print(f"解释: {result['explanation']}")
    for source in result['sources']:
        print(f"  来源: {source['name']} {source['url']}")
```

## 优化设计

本模块采用以下设计优化：

1. **统一数据协议**：使用标准化的请求/响应对象，减少参数解析和数据转换的冗余
2. **简化层次结构**：使用三层架构（协议层、适配层、实现层），减少不必要的中间层
3. **清晰职责边界**：适配层负责外部接口转换，实现层专注于核心功能执行
4. **减少中间状态**：直接构建最终响应对象，避免多次对象转换
5. **一致的数据流**：所有操作遵循相同的数据流模式
6. **类型安全**：使用Pydantic模型确保数据结构的一致性和验证

## 配置选项

研究系统支持多种配置选项，可以根据内容类型自动选择最合适的研究策略：

| 内容类型 | 研究深度 | 专家见解 | 数据分析 | 最大来源数 |
|---------|---------|---------|---------|----------|
| article | medium  | 是      | 是      | 10       |
| blog    | medium  | 是      | 否      | 5        |
| news    | light   | 是      | 是      | 3        |
| technical | deep  | 是      | 是      | 15       |

通过调整这些配置，可以控制研究过程的深度和广度，满足不同内容类型的需求。
