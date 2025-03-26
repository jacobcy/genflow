# GenFlow 内容生产系统

GenFlow 是一个智能内容生产系统，通过AI辅助完成从选题到发布的全流程内容创作。系统支持全自动、全人工辅助和混合模式，让内容创作更加高效和个性化。

## 功能特点

- **全流程支持**：覆盖选题、研究、写作、风格适配和审核全流程
- **多模式支持**：全自动、全人工辅助、混合模式灵活切换
- **阶段可控**：精细控制每个阶段是否需要人工参与
- **风格多样化**：支持多种写作风格，满足不同内容需求
- **批量处理**：支持多话题、多文章批量生产

## 系统架构

GenFlow 由以下核心组件构成：

- **内容控制器**：整体流程协调和控制
- **专业团队**：
  - 选题团队：发现和评估热门话题
  - 研究团队：深入研究话题内容
  - 写作团队：生成高质量文章
  - 风格团队：适配不同写作风格
  - 审核团队：确保内容质量和合规

## 使用方法

### 命令行使用

#### 基础用法

```bash
python -m core.main
```

如果不提供任何参数，系统将进入交互式对话框，引导您完成以下步骤：

1. 选择内容类别（可随机选择）
2. 选择写作风格（可随机选择）
3. 输入文章数量
4. 选择生产模式（自动/人工/混合）
5. 在混合模式下，选择哪些阶段自动执行
6. 确认配置并开始生产

#### 参数说明

您也可以通过命令行参数直接指定配置：

```bash
python -m core.main --category 科技 --style 深度分析 --count 3 --mode auto
```

参数说明：
- `--category`：内容类别，可选值见下文，不指定或设为random则随机选择
- `--style`：写作风格，可选值见下文，不指定或设为random则随机选择
- `--count`：文章数量（1-5）
- `--mode`：生产模式（auto/human/mixed）
- `--auto-stages`：自动执行的阶段（仅在mixed模式下有效，多个阶段用逗号分隔）

可选内容类别：
```
科技, 财经, 教育, 健康, 娱乐, 体育, 生活, 文化, 社会, 政治, 环境, 旅游, 职场, 美食
```

可选写作风格：
```
专业严谨, 通俗易懂, 深度分析, 生动活泼, 故事化叙述, 观点鲜明, 简洁明了, 详尽全面
```

示例：
```bash
# 随机类别，指定深度分析风格，混合模式，选题和写作自动执行
python -m core.main --category random --style 深度分析 --count 2 --mode mixed --auto-stages topic_discovery,article_writing

# 不指定类别和风格（均随机选择）
python -m core.main --count 3 --mode auto
```

### FastAPI 接口

#### 启动服务

```bash
uvicorn core.api:app --reload
```

#### 使用方式

GenFlow API提供两种使用方式：

1. **完整流程** - 从选题到发布的全流程内容生产
2. **独立团队** - 单独使用某个专业团队，只执行特定阶段

#### 完整流程API端点

##### 1. 创建内容生产任务

```
POST /api/content/produce
```

请求体示例：
```json
{
  "category": "科技",
  "style": "深度分析",
  "topic_count": 3,
  "mode": "mixed",
  "auto_stages": ["topic_discovery", "article_writing"]
}
```

参数说明：
- `category`：内容类别，不指定或为"random"时随机选择
- `style`：写作风格，不指定或为"random"时随机选择
- `topic_count`：文章数量，范围1-5（默认1）
- `mode`：生产模式（auto/human/mixed，默认human）
- `auto_stages`：自动执行的阶段列表（mixed模式下必填）

可选的自动执行阶段：
- `topic_discovery`：选题发现
- `topic_research`：话题研究
- `article_writing`：文章写作
- `style_adaptation`：风格适配
- `article_review`：文章审核

响应示例：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "created",
  "config": {
    "category": "科技",
    "style": "深度分析",
    "topic_count": 3,
    "mode": "mixed",
    "auto_stages": ["topic_discovery", "article_writing"]
  }
}
```

##### 2. 获取任务状态

```
GET /api/content/tasks/{task_id}
```

响应示例：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "progress": {
    "current_stage": "article_writing",
    "progress_percentage": 45.0,
    "completed_topics": 1,
    "total_topics": 3
  }
}
```

##### 3. 获取任务结果

```
GET /api/content/tasks/{task_id}/results
```

响应示例：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "articles": [
    {
      "title": "人工智能的未来发展趋势",
      "summary": "本文探讨了人工智能的最新发展方向...",
      "category": "科技",
      "style": "深度分析",
      "url": "/api/content/articles/123456"
    }
  ]
}
```

##### 4. 人工反馈接口

```
POST /api/content/tasks/{task_id}/feedback
```

请求体示例：
```json
{
  "stage": "topic_research",
  "item_id": "topic_001",
  "approved": true,
  "score": 0.85,
  "comments": "研究内容详实，但可以增加更多案例"
}
```

##### 5. 获取可用类别列表

```
GET /api/categories
```

响应示例：
```json
{
  "categories": [
    {
      "id": "1",
      "name": "科技"
    },
    {
      "id": "2",
      "name": "财经"
    }
  ]
}
```

##### 6. 获取可用写作风格

```
GET /api/styles
```

响应示例：
```json
{
  "styles": [
    {
      "id": "1",
      "name": "专业严谨"
    },
    {
      "id": "2",
      "name": "通俗易懂"
    }
  ]
}
```

#### 独立团队API端点

您可以单独使用特定团队来完成特定阶段的工作，而不必执行整个流程：

##### 1. 选题团队 - 获取热门话题

```
POST /api/teams/topic
```

**输入**：类别
**输出**：热词（可能含URL）

请求体示例：
```json
{
  "category": "科技",
  "count": 5
}
```

参数说明：
- `category`：内容类别，可设为"random"随机选择
- `count`：返回热词数量(1-10)

响应示例：
```json
{
  "topics": [
    {
      "title": "ChatGPT-5发布",
      "score": 0.95,
      "url": "https://example.com/news/chatgpt5",
      "keywords": ["AI", "大语言模型", "OpenAI"]
    }
  ],
  "category": "科技",
  "timestamp": "2023-10-20T08:30:00.000Z"
}
```

##### 2. 研究团队 - 获取话题背景资料

```
POST /api/teams/research
```

**输入**：热词（可能含URL）
**输出**：热词+背景资料

请求体示例：
```json
{
  "topic": "ChatGPT-5发布",
  "url": "https://example.com/news/chatgpt5",
  "detail_level": "detailed"
}
```

参数说明：
- `topic`：要研究的热词/话题
- `url`：参考URL（可选）
- `detail_level`：详细程度(brief/medium/detailed)

响应示例：
```json
{
  "topic": "ChatGPT-5发布",
  "background": {
    "summary": "OpenAI近日发布了ChatGPT的最新版本...",
    "key_points": ["多模态能力增强", "推理能力突破"],
    "timeline": [...]
  },
  "sources": [...],
  "timestamp": "2023-10-20T09:15:00.000Z"
}
```

##### 3. 写作团队 - 生成文章

```
POST /api/teams/writing
```

**输入**：热词+背景摘要
**输出**：文章（标题、内容、关键词、摘要）

请求体示例：
```json
{
  "topic": "ChatGPT-5发布",
  "background": {
    "summary": "OpenAI近日发布了ChatGPT的最新版本...",
    "key_points": ["多模态能力增强", "推理能力突破"],
    "sources": [...]
  },
  "format": "article"
}
```

参数说明：
- `topic`：文章主题
- `background`：背景资料
- `format`：生成格式(article/outline)

响应示例：
```json
{
  "article": {
    "title": "ChatGPT-5: AI领域的革命性突破",
    "summary": "本文深入分析了ChatGPT-5的技术创新...",
    "keywords": ["ChatGPT", "AI革命", "大语言模型"],
    "sections": [...]
  },
  "topic": "ChatGPT-5发布",
  "timestamp": "2023-10-20T10:00:00.000Z"
}
```

##### 4. 风格团队 - 风格化文章

```
POST /api/teams/style
```

**输入**：风格、文章
**输出**：风格化后的文章

请求体示例：
```json
{
  "article": {
    "title": "ChatGPT-5: AI领域的革命性突破",
    "summary": "本文深入分析了ChatGPT-5的技术创新...",
    "sections": [...]
  },
  "style": "深度分析"
}
```

参数说明：
- `article`：原始文章
- `style`：目标风格

响应示例：
```json
{
  "original_article": {...},
  "styled_article": {
    "title": "深度解析|ChatGPT-5如何重新定义AI边界",
    "summary": "通过深入剖析ChatGPT-5的核心架构...",
    "sections": [...]
  },
  "style": "深度分析",
  "timestamp": "2023-10-20T10:30:00.000Z"
}
```

##### 5. 审核团队 - 审核文章

```
POST /api/teams/review
```

**输入**：文章
**输出**：审核后的文章

请求体示例：
```json
{
  "article": {
    "title": "深度解析|ChatGPT-5如何重新定义AI边界",
    "summary": "通过深入剖析ChatGPT-5的核心架构...",
    "sections": [...]
  },
  "check_originality": true,
  "check_ai_detection": true
}
```

参数说明：
- `article`：待审核文章
- `check_originality`：是否检查原创性
- `check_ai_detection`：是否检查AI痕迹

响应示例：
```json
{
  "article": {...},
  "review_results": {
    "overall_score": 0.92,
    "originality_score": 0.95,
    "ai_detection_score": 0.12,
    "readability_score": 0.88,
    "improvement_suggestions": [...]
  },
  "timestamp": "2023-10-20T11:00:00.000Z"
}
```

### 专业团队协助

通过FastAPI接口，您可以选择性地使用不同的专业团队来协助内容创作过程。每个团队都有特定的职责和输入/输出规范：

#### 选题团队 (Topic Crew)
- **输入**：类别（默认为热门）
- **输出**：热词（可能包含URL）
- **功能**：发现和推荐当前热门话题
- **API用法**：通过`auto_stages`中包含`topic_discovery`来启用

#### 研究团队 (Research Crew)
- **输入**：热词（可能包含URL）
- **输出**：热词+背景资料
- **功能**：收集话题相关的背景信息和研究资料
- **API用法**：通过`auto_stages`中包含`topic_research`来启用

#### 写作团队 (Writing Crew)
- **输入**：热词+背景摘要
- **输出**：文章（标题、内容、关键词、摘要）
- **功能**：基于研究资料生成完整文章
- **API用法**：通过`auto_stages`中包含`article_writing`来启用

#### 风格团队 (Style Crew)
- **输入**：风格、文章
- **输出**：风格化后的文章
- **功能**：根据指定风格调整文章风格和表达方式
- **API用法**：通过`auto_stages`中包含`style_adaptation`来启用

#### 审核团队 (Review Crew)
- **输入**：文章
- **输出**：审核后的文章
- **功能**：进行查重和AI检测，确保文章质量
- **API用法**：通过`auto_stages`中包含`article_review`来启用

您可以在API请求的`auto_stages`参数中指定需要自动执行的团队，例如：

```json
{
  "category": "科技",
  "style": "深度分析",
  "topic_count": 2,
  "mode": "mixed",
  "auto_stages": ["topic_discovery", "article_writing", "article_review"]
}
```

上述配置将自动执行选题发现、文章写作和文章审核阶段，而研究和风格适配阶段则需要人工参与。

### 进阶配置

#### 自定义评估标准

各阶段的自动评估标准可以在对应的团队文件中修改：
- 选题评估：`core/agents/topic_crew/topic_agents.py`
- 研究评估：`core/agents/research_crew/research_agents.py`
- 写作评估：`core/agents/writing_crew/writing_agents.py`
- 风格评估：`core/agents/style_crew/style_agents.py`
- 审核评估：`core/agents/review_crew/review_agents.py`

## 实际应用场景

1. **内容创作加速**：使用全自动模式快速生成多篇文章草稿
2. **内容质量控制**：使用混合模式，保留关键阶段的人工审核
3. **多风格内容生成**：为不同受众生成适合其阅读偏好的内容
4. **内容创意激发**：使用AI推荐热门话题，人工筛选最有价值的方向

## 最佳实践

- **选题阶段**：建议使用自动模式获取推荐，人工做最终决策
- **研究阶段**：复杂话题建议人工参与，常规话题可以自动完成
- **写作阶段**：可以自动生成初稿，人工进行编辑和优化
- **风格适配**：随机风格可以激发创意，特定风格则适合固定栏目
- **审核阶段**：建议至少保留部分人工参与，确保内容质量和合规性

## 常见问题

**Q: 如何控制生成文章的数量？**
A: 在命令行或API中设置 `count` 或 `topic_count` 参数，范围为1-5篇。

**Q: 如何同时进行多个生产任务？**
A: 使用API创建多个独立的生产任务，每个任务有独立的任务ID和状态跟踪。

**Q: 人工参与的阶段需要如何操作？**
A: 当进入人工参与阶段时，系统会提示您进行评估和反馈。API模式下，需要通过反馈接口提交人工决策。

**Q: 如何确保随机选择的类别和风格组合合适？**
A: 系统会确保所有随机组合都能产生有意义的内容。如果特定组合不理想，您可以重新运行或指定其中一项。

**Q: 如何只使用特定团队而不执行完整流程？**
A: 使用独立团队API端点(`/api/teams/topic`、`/api/teams/research`等)，只调用您需要的特定团队。
