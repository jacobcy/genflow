# 写作团队 (WritingCrew)

## 概述

WritingCrew 是一个基于 CrewAI 框架构建的智能写作团队，负责高效地从研究资料到成品文章的全流程创作。该模块采用多智能体协作模式，实现了从大纲设计、内容撰写、事实核查到最终编辑的完整写作流程。

## 核心功能

- **大纲创建**：根据话题或研究资料，构建结构化的文章大纲
- **内容拓展**：基于大纲进行内容创作和拓展
- **事实核查**：验证文章中的事实和引用
- **内容编辑**：优化文章风格、结构和可读性
- **灵活输入**：支持从话题、大纲或文本等多种形式输入
- **适配平台**：根据不同平台的内容需求调整内容

## 数据流

```
研究资料 → 大纲创建 → 内容拓展 → 事实核查 → 内容编辑 → 成品文章
```

## 关键类

### WritingCrew

团队管理类，协调所有写作相关的智能体和任务。

```python
writing_crew = WritingCrew(verbose=True)
result = await writing_crew.write_article(article, research_data, platform, content_type, style)
```

### WritingResult

存储写作各阶段结果的容器类，包含大纲、内容和最终稿件。

```python
result.article      # 文章对象
result.outline      # 大纲信息
result.content      # 内容信息
result.final_draft  # 最终稿件
```

### BasicOutline / ArticleOutline

大纲模型，提供结构化的文章框架。

- `BasicOutline`: 基础大纲模型，不依赖话题ID
- `ArticleOutline`: 继承自BasicOutline，关联特定话题

## 工作流程

1. **初始化**：创建团队并设置工作参数
2. **大纲设计**：
   - 分析研究资料和主题
   - 设计符合内容类型的结构化大纲
   - 优化大纲以满足目标平台要求
3. **内容创作**：
   - 根据大纲进行内容拓展
   - 确保内容准确且符合用户需求
   - 按照内容规范调整内容深度和广度
4. **事实核查**：
   - 验证文章中的事实、数据和引用
   - 标识需要修改的地方
   - 提供额外的支持信息
5. **内容编辑**：
   - 优化语言表达和风格
   - 确保内容逻辑连贯
   - 提高整体文章质量
6. **结果处理**：
   - 整合所有阶段的处理结果
   - 更新文章内容和元数据
   - 返回完整的写作结果

## 接口方法

### write_article

完整的文章写作流程，从研究资料到成品文章。

```python
async def write_article(
    self,
    article: Article,
    research_data: Optional[Dict[str, Any]] = None,
    platform: Optional[Union[str, Platform]] = None,
    content_type: Optional[str] = None,
    style: Optional[str] = None,
    **kwargs
) -> WritingResult
```

### create_outline

创建文章大纲，支持从话题或文本直接生成大纲。

```python
async def create_outline(
    self,
    topic_or_text: Union[str, Topic, Dict, Any],
    content_type: Optional[str] = None,
    platform_id: Optional[str] = None,
    style: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None
) -> BasicOutline
```

### expand_content

基于大纲或文本进行内容拓展。

```python
async def expand_content(
    self,
    outline_or_text: Union[str, BasicOutline, ArticleOutline],
    content_type: Optional[str] = None,
    platform_id: Optional[str] = None,
    style: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

## 配置管理

WritingCrew 通过 ContentManager 获取内容类型配置，支持不同内容类型的写作参数：

```python
self.current_content_config = self.get_writing_config(content_type)
```

常见配置参数：
- `content_type`: 内容类型（article/blog/news等）
- `style`: 写作风格（formal/casual/technical）
- `word_count`: 目标字数
- `depth`: 内容深度（shallow/medium/deep）
- `structure`: 文章结构（standard/creative/instructional）
- `tone`: 语气（professional/friendly/authoritative）

## 与其他团队的集成

WritingCrew 作为内容创作流程的核心组件，与其他团队有以下集成点：

- 接收 **ResearchCrew** 的研究成果作为输入
- 向 **StyleCrew** 提供文章内容进行风格适配
- 向 **ReviewCrew** 提供文章进行审核

## 使用示例

```python
from core.agents.writing_crew import WritingCrew
from core.models.article import Article
from core.models.platform import Platform

# 创建文章对象
article = Article(
    id="article-123",
    title="人工智能的未来发展",
    topic_id="topic-456"
)

# 创建写作团队
writing_crew = WritingCrew(verbose=True)

# 设置目标平台
platform = Platform(id="wechat", name="微信公众号")

# 设置研究资料
research_data = {
    "background": "AI发展历史和现状概述...",
    "key_insights": ["见解1", "见解2", "见解3"],
    "expert_opinions": ["专家观点1", "专家观点2"]
}

# 执行写作流程
result = await writing_crew.write_article(
    article=article,
    research_data=research_data,
    platform=platform,
    content_type="technical_article",
    style="authoritative"
)

# 获取结果
final_article = result.article
print(f"标题: {final_article.title}")
print(f"内容长度: {final_article.word_count} 字")
print(f"大纲部分: {len(result.outline.get('sections', []))} 个章节")

# 保存结果
result.save_to_file()
```
