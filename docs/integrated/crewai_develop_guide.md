# CrewAI开发指南：创建使用自定义工具的智能体团队

## 1. 概述

CrewAI是一个强大的框架，用于创建协作型AI智能体团队。每个智能体可以拥有特定的角色、能力和工具，共同协作完成复杂任务。本指南将帮助您掌握如何在CrewAI中创建自定义工具并将其集成到智能体团队中。

## 2. 工具类型及实现方式

CrewAI支持多种创建工具的方式：

### 2.1 使用`@tool`装饰器（推荐）

这是最简洁的实现方式，适合功能相对独立的工具：

```python
from crewai.tools import tool

@tool("搜索工具")
def search_tool(query: str) -> str:
    """搜索互联网获取信息，支持关键词查询。"""
    # 实现搜索逻辑
    return f"搜索结果: {query}的相关信息..."
```

### 2.2 继承`BaseTool`类

适合需要更复杂状态管理或初始化逻辑的工具：

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# 可选：为工具定义输入结构
class SearchInput(BaseModel):
    query: str = Field(..., description="搜索关键词")

class CustomSearchTool(BaseTool):
    name: str = "搜索工具"
    description: str = "搜索互联网获取信息，支持关键词查询。"
    args_schema: BaseModel = SearchInput  # 可选：定义输入参数模式
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        super().__init__()
    
    def _run(self, query: str) -> str:
        """工具的执行逻辑"""
        # 实现搜索逻辑
        return f"搜索结果: {query}的相关信息..."
```

### 2.3 使用`CrewStructuredTool`

适合需要严格输入验证的工具：

```python
from crewai.tools.structured_tool import CrewStructuredTool
from pydantic import BaseModel

class SearchInput(BaseModel):
    query: str
    limit: int = 10

def search_function(query: str, limit: int = 10):
    # 实现搜索逻辑
    return f"为'{query}'找到{limit}条结果..."

search_tool = CrewStructuredTool.from_function(
    name="搜索工具",
    description="搜索互联网获取信息",
    args_schema=SearchInput,
    func=search_function
)
```

## 3. 在类中组织和管理工具

对于复杂项目，建议将工具组织在类中管理：

```python
class ProjectTools:
    def __init__(self):
        # 初始化所需的API客户端或资源
        self.search_client = SearchClient(api_key="your_api_key")
    
    @tool("搜索工具")
    def search(self, query: str) -> str:
        """搜索互联网获取信息。"""
        return self.search_client.search(query)
    
    @tool("数据分析工具")
    def analyze_data(self, data: str, method: str = "summary") -> str:
        """分析提供的数据。"""
        # 实现数据分析逻辑
        return f"分析结果: {data}的{method}分析..."
```

## 4. 创建智能体(Agent)

一旦定义了工具，就可以将它们分配给智能体：

```python
from crewai import Agent

# 假设已经创建了工具
tools = ProjectTools()

researcher = Agent(
    role='研究员',
    goal='收集并分析指定主题的最新信息',
    backstory="""你是一位专业研究员，擅长从多种渠道收集信息并进行初步分析。
    你的研究内容准确、全面且结构清晰。""",
    tools=[tools.search, tools.analyze_data],
    verbose=True
)
```

## 5. 定义任务(Task)

为智能体定义具体任务：

```python
from crewai import Task

research_task = Task(
    description='研究人工智能在医疗领域的最新应用，重点关注诊断技术',
    expected_output='一份包含5个主要应用方向的报告，每个方向包含具体案例和优势分析',
    agent=researcher,
    # 可选：为特定任务覆盖智能体的默认工具
    tools=[tools.search]
)
```

## 6. 组建智能体团队(Crew)

将多个智能体组织成一个团队：

```python
from crewai import Crew, Process

# 假设已经定义了多个智能体和任务
crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, writing_task],
    process=Process.sequential,  # 或 Process.hierarchical
    verbose=True
)

# 启动团队工作
result = crew.kickoff()
```

## 7. 创建工作流(Flow)

对于更复杂的场景，可以使用Flow管理多个Crew：

```python
from crewai import Flow, Step

# 假设已经定义了多个Crew
research_crew = ResearchCrew()
report_crew = ReportingCrew()

flow = Flow(
    name="完整研究流程",
    description="从主题研究到最终报告生成的完整流程"
)

# 添加步骤
step1 = Step(
    name="研究阶段",
    crew=research_crew,
    inputs={"topic": "人工智能在医疗领域的应用"}
)

step2 = Step(
    name="报告生成阶段",
    crew=report_crew,
    inputs={"research_results": step1.output}
)

flow.add_steps([step1, step2])

# 执行工作流
result = flow.run()
```

## 8. 最佳实践

1. **命名清晰**：为工具和智能体提供清晰、描述性的名称和角色
2. **详细描述**：编写详细的工具描述，这将帮助智能体正确理解和使用工具
3. **错误处理**：在工具实现中添加适当的错误处理机制
4. **模块化设计**：将相关工具组织在类中，便于管理和复用
5. **测试验证**：单独测试每个工具，确保其功能正常
6. **遵循类型提示**：使用类型提示提高代码可读性和安全性

## 9. 常见错误解决

1. **Pydantic版本兼容性问题**：如果使用Pydantic v2，确保正确设置模型配置和类型注解
   ```python
   model_config = {"arbitrary_types_allowed": True}
   ```

2. **工具调用错误**：确保工具的参数与其定义匹配

3. **智能体无法正确使用工具**：检查工具描述是否足够清晰，并验证工具实现是否正确

## 10. 示例项目：话题分析团队

以下是一个完整示例，展示如何创建一个专注于话题研究和分析的智能体团队：

```python
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

class TopicTools:
    def __init__(self):
        # 初始化资源
        self.search_engine = SearchEngine()
        self.trend_analyzer = TrendAnalyzer()
    
    @tool("趋势分析")
    def analyze_trends(self, topic: str) -> str:
        """分析指定话题的流行趋势和热度变化。"""
        return self.trend_analyzer.analyze(topic)
    
    @tool("内容搜索")
    def search_content(self, query: str, limit: int = 10) -> str:
        """搜索与查询相关的内容。"""
        return self.search_engine.search(query, limit)

# 创建工具实例
tools = TopicTools()

# 创建智能体
researcher = Agent(
    role='话题研究员',
    goal='深入研究指定话题的各个方面',
    backstory="你是一位经验丰富的研究员，擅长深入挖掘话题的各个方面。",
    tools=[tools.search_content, tools.analyze_trends]
)

analyst = Agent(
    role='趋势分析师',
    goal='分析话题趋势和潜在发展方向',
    backstory="你是一位资深趋势分析师，善于识别模式和预测发展趋势。",
    tools=[tools.analyze_trends]
)

# 创建任务
research_task = Task(
    description='研究"可持续时尚"话题的主要方面和关键概念',
    expected_output='一份包含主要子话题、关键概念和重要术语的研究报告',
    agent=researcher
)

analysis_task = Task(
    description='基于研究报告分析"可持续时尚"的趋势和未来发展方向',
    expected_output='一份包含当前趋势、增长预测和潜在机会的分析报告',
    agent=analyst,
    context=[research_task]  # 使用研究任务的结果作为上下文
)

# 创建团队
topic_crew = Crew(
    agents=[researcher, analyst],
    tasks=[research_task, analysis_task],
    process=Process.sequential,
    verbose=True
)

# 启动团队工作
result = topic_crew.kickoff()
print(result)
```

通过以上方法，您可以创建强大的智能体团队，利用自定义工具完成复杂任务。根据您的具体需求，可以选择最适合的工具实现方式和团队组织结构。
