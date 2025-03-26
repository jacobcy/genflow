# 选题团队智能体系统

## 1. 系统概述

选题团队智能体系统是一个基于CrewAI框架的智能体团队，专注于发现、研究和分析内容选题。系统由多个专业智能体组成，每个智能体负责特定的任务领域，通过协作完成从话题发现到分析报告生成的完整流程。

## 2. 系统架构

系统由以下核心组件构成：

### 2.1 工具集 (TopicTools)

位于 `topic_tools.py`，提供各种工具的功能实现：

* **趋势分析工具**：获取和分析各平台热点话题
* **搜索工具**：在互联网上搜索相关信息
* **内容收集工具**：收集特定平台和类别的内容
* **NLP工具**：文本分析、摘要、情感分析等

工具通过 CrewAI 的 `@tool` 装饰器注册，便于智能体调用。

### 2.2 智能体 (TopicAgents)

位于 `topic_agents.py`，定义了团队中的智能体角色：

* **趋势分析师**：发现和分析热门话题趋势
* **话题研究员**：深入研究话题的价值和可行性
* **报告撰写员**：生成专业的选题分析报告

每个智能体被赋予特定的工具集，用于完成其任务。

### 2.3 团队工作流 (TopicCrew)

位于 `topic_crew.py`，管理整个团队的工作流程：

* **话题发现**：由趋势分析师主导，发现热门话题
* **话题研究**：由话题研究员深入分析话题价值
* **报告生成**：由报告撰写员整合信息，生成分析报告
* **人工反馈**：允许用户对话题进行评估和筛选

## 3. 使用指南

### 3.1 快速开始

系统提供了便捷的运行脚本，可以直接从项目根目录运行：

```bash
# 仅运行话题发现流程
python -m core.agents.topic_crew.run --mode discover --category 科技 --count 3

# 运行完整工作流程（包含人工反馈）
python -m core.agents.topic_crew.run --mode full --category 教育 --count 5
```

命令行参数说明：
- `--mode`: 运行模式，可选 `discover`(仅发现话题) 或 `full`(完整流程)
- `--category`: 话题分类，例如"科技"、"教育"、"娱乐"等
- `--count`: 需要发现的话题数量

### 3.2 编程接口

在代码中使用选题团队：

```python
import asyncio
from core.config import Config
from core.agents.topic_crew.topic_crew import TopicCrew

async def main():
    # 初始化配置和团队
    config = Config()
    crew = TopicCrew(config=config)

    # 发现话题
    topics = await crew.discover_topics(category="科技", count=3)

    # 获取人工反馈
    topics = crew.get_human_feedback(topics)

    # 分析获批话题
    for topic in topics:
        if topic.status == "approved":
            analysis = await crew.analyze_topic(topic.id)
            print(f"\n=== {topic.title} 分析报告 ===")
            print(analysis["report"])

if __name__ == "__main__":
    asyncio.run(main())
```

### 3.3 完整工作流

系统提供了一个集成所有步骤的完整工作流方法：

```python
async def main():
    crew = TopicCrew()

    # 运行完整工作流
    result = await crew.run_full_workflow(
        category="教育",
        count=5
    )

    # 结果已包含所有话题和分析数据
    print(f"发现话题总数: {result['total_topics']}")
    print(f"获批话题数量: {result['approved_topics']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3.4 自定义智能体和任务

可以创建自定义的智能体组合和任务：

```python
from core.agents.topic_crew.topic_agents import TopicAgents
from crewai import Task, Crew

# 初始化智能体
agents = TopicAgents()
all_agents = agents.create_all_agents()

# 创建自定义任务
custom_task = Task(
    description="分析特定话题的竞争情况",
    agent=all_agents["topic_researcher"]
)

# 创建简单团队
crew = Crew(
    agents=[all_agents["topic_researcher"]],
    tasks=[custom_task]
)

# 执行任务
result = await crew.kickoff()
```

## 4. 系统扩展

### 4.1 添加新工具

要添加新工具，请在 `TopicTools` 类中使用 `@tool` 装饰器创建新方法：

```python
@tool("新工具名称")
def new_tool(self, param1: str, param2: int = 10) -> str:
    """新工具的详细描述。"""
    # 工具实现逻辑
    return "工具执行结果"
```

### 4.2 添加新智能体

要添加新智能体，请在 `TopicAgents` 类中添加新的创建方法：

```python
def create_new_agent(self) -> Agent:
    """创建新智能体"""
    return Agent(
        role='新角色',
        goal='新智能体的目标',
        backstory="新智能体的背景故事",
        tools=[self.tools.tool1, self.tools.tool2]
    )
```

同时在 `__init__` 方法中更新工具映射和配置。

## 5. 最佳实践

1. **工具设计**：工具应该设计为无状态的，便于智能体调用和组合
2. **智能体角色**：为每个智能体定义清晰的角色、目标和背景故事
3. **任务描述**：任务描述应详细、结构化，并明确期望输出格式
4. **错误处理**：系统实现了健壮的错误处理，确保流程不会因单点故障中断
5. **人机协作**：通过人工反馈环节，将人类判断融入工作流程

## 6. 故障排除

### 6.1 导入错误

如果遇到 `ModuleNotFoundError: No module named 'core'` 错误，可能是因为 Python 路径配置问题。解决方法有：

1. **使用提供的运行脚本**：直接从项目根目录运行 `python -m core.agents.topic_crew.run`

2. **手动添加项目根目录到 Python 路径**：
   ```python
   import os
   import sys

   # 添加项目根目录到 Python 路径
   current_dir = os.path.dirname(os.path.abspath(__file__))
   project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
   sys.path.insert(0, project_root)
   ```

3. **设置 PYTHONPATH 环境变量**：
   ```bash
   # Linux/Mac
   export PYTHONPATH=/path/to/your/project:$PYTHONPATH

   # Windows
   set PYTHONPATH=C:\path\to\your\project;%PYTHONPATH%
   ```

## 7. 示例和文档

- 查看 `example.py` 文件获取更多详细的使用示例
- 运行 `python -m core.agents.topic_crew.run --help` 查看命令行选项
- 更多API文档请参考各模块的文档字符串
