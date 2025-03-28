# 风格化团队 (StyleCrew)

## 概述

StyleCrew 是一个基于 CrewAI 框架构建的智能风格适配团队，专门负责内容风格化调整和平台风格适配。该模块采用多智能体协作模式，提供全面的风格处理服务，从平台风格分析到内容风格调整，确保内容符合特定平台或风格的要求。

## 架构设计

风格化系统采用三层架构设计，具有清晰的职责边界和数据流：

### 1. TeamAdapter层 (StyleTeamAdapter)
- **位置**: 控制器和具体团队之间的桥梁
- **输入**: outline_id 或内容文本，style_id 或 style_type
- **处理**: 不包含业务逻辑，只负责参数传递和结果转换
  - 解析outline_id为具体内容
  - 根据style_id或style_type确定风格配置
  - 调用StyleAdapter层执行风格适配
- **输出**: 将StyleAdapter返回的BasicArticle转换为Article类

### 2. StyleAdapter层
- **位置**: TeamAdapter和StyleCrew之间的适配层
- **输入**:
  - content文本内容
  - style_config风格配置
  - 其他选项
- **处理**:
  - 解析风格配置
  - 调用StyleCrew，传递具体参数
  - 处理异常和状态跟踪
- **输出**:
  - 返回BasicArticle类
  - 不保存风格处理结果

### 3. StyleCrew层
- **位置**: 核心风格化实现层
- **输入**:
  - 具体的文本内容
  - 风格配置参数
  - 平台信息
- **处理**:
  - 执行具体风格化任务
  - 不处理ID解析或外部关联
- **输出**:
  - 返回StyleWorkflowResult对象，包含处理后的内容

## 数据流

```
控制器 → StyleTeamAdapter → StyleAdapter → StyleCrew → StyleAdapter → StyleTeamAdapter → 控制器
   |           |                |             |            |              |                |
outline_id → content    →    风格参数   → 执行风格化 →   →   → BasicArticle → Article  → 结果应用
style_id  → style_config →     |         风格检查                ↑
                                ↓                               |
                           风格化处理 ————————————————————————————
```

## 核心功能

- **平台风格分析**：分析特定平台的风格特点和偏好
- **内容风格调整**：将内容调整为符合特定风格的形式
- **风格推荐**：根据内容和平台特点提供风格建议
- **质量检查**：评估风格适配后内容的质量和符合度

## 关键类

### StyleCrew

核心风格化实现类，管理风格化智能体和执行风格化流程。

```python
style_crew = StyleCrew()
result = await style_crew.style_text(
    text="这是一段需要风格化的文本内容",
    style_config={
        "style": "formal",
        "tone": "professional",
        "formality": 3
    }
)
```

### StyleTeamAdapter

风格团队适配器，处理参数转换和结果映射。

```python
adapter = StyleTeamAdapter()
result = await adapter.adapt_style(
    content="outline_123",  # 可以是outline_id、文本内容或Article对象
    style_id="zhihu_style",  # 或使用style_type="知乎"
    platform_id="zhihu"
)
```

### StyleWorkflowResult

存储风格化处理结果的对象，包含平台分析、风格建议、处理后内容和质量检查结果。

```python
result.platform_analysis    # 平台风格分析
result.style_recommendations # 风格建议
result.adapted_content      # 适配后的内容
result.quality_check        # 质量检查结果
result.final_article        # 最终文章对象
```

## 智能体组成

StyleCrew 由四个专业智能体组成，各自负责风格化流程的不同阶段：

1. **平台分析员 (PlatformAnalystAgent)**：分析平台的风格特点和偏好
2. **风格专家 (StyleExpertAgent)**：提供具体的风格改写建议
3. **内容适配员 (ContentAdapterAgent)**：执行内容的风格适配
4. **质量检查员 (QualityCheckerAgent)**：评估风格适配结果的质量

## 工作流程

1. **参数解析**:
   - StyleTeamAdapter解析输入内容和风格ID
   - 生成风格配置和平台信息

2. **平台分析**:
   - 分析平台的风格特点
   - 确定内容应遵循的风格规范

3. **风格推荐**:
   - 根据平台分析和内容特点提供风格建议
   - 确定具体的风格调整策略

4. **内容适配**:
   - 根据风格建议调整内容
   - 保持内容核心信息的同时改变表达方式

5. **质量检查**:
   - 评估适配后内容的质量
   - 提供改进建议

6. **结果封装**:
   - 将处理结果封装为StyleWorkflowResult
   - 转换为BasicArticle或Article返回

## 使用示例

### 基本风格适配流程

```python
from core.agents.style_crew.style_adapter import StyleTeamAdapter

# 初始化风格适配器
adapter = StyleTeamAdapter()
await adapter.initialize()

# 执行风格适配
result = await adapter.adapt_style(
    content="这是一段需要调整风格的内容，当前风格可能过于口语化，需要调整为更专业的表达。",
    style_id="professional",
    platform_id="zhihu"
)

# 使用风格适配结果
print(f"适配后的内容: {result.content}")
```

### 平台风格分析流程

```python
from core.agents.style_crew.style_adapter import StyleTeamAdapter

# 初始化风格适配器
adapter = StyleTeamAdapter()
await adapter.initialize()

# 分析平台风格
platform_analysis = await adapter.analyze_platform(
    platform_id="xiaohongshu",
    options={"detail_level": "high"}
)

# 分析结果
print(f"平台名称: {platform_analysis['platform_name']}")
print(f"语言风格: {platform_analysis['analysis']['language_style']}")
print(f"内容结构建议: {platform_analysis['analysis']['content_structure']}")
```

## 配置选项

风格化系统支持多种配置选项，可以根据不同平台和内容类型调整风格参数：

| 风格类型 | 语气 | 正式程度 | 情感表达 | 表情符号 |
|---------|------|---------|---------|---------|
| formal  | professional | 3 | 否 | 否 |
| casual  | friendly    | 1 | 是 | 是 |
| academic | serious    | 5 | 否 | 否 |
| social   | engaging   | 2 | 是 | 是 |

通过调整这些配置，可以控制风格化过程的特点，满足不同平台和内容类型的需求。

## 目录结构

```
style_crew/
├── __init__.py              # 模块导出
├── style_crew.py            # 风格化团队主类
├── style_agents.py          # 智能体定义
├── run_style_crew.py        # 独立运行脚本
├── example_article.json     # 示例文章
├── platforms/               # 平台风格配置目录
│   ├── bilibili.json        # 哔哩哔哩平台风格
│   ├── zhihu.json           # 知乎平台风格（专业）
│   ├── douyin.json          # 抖音平台风格（爆点）
│   ├── toutiao.json         # 今日头条平台风格（震惊体）
│   ├── xiaohongshu.json     # 小红书平台风格（种草）
│   ├── weibo.json           # 微博平台风格（八卦）
│   ├── csdn.json            # CSDN平台风格（技术博客）
│   └── wechat.json          # 微信公众号平台风格（深度阅读）
└── readme.md                # 使用说明
```

## 使用方法

### 作为模块集成到ContentController

```python
from core.controllers.content_controller import ContentController
from core.models.article import Article
from core.models.platform import Platform

# 创建内容控制器
controller = ContentController()
await controller.initialize(platform)

# 执行风格适配
styled_article = await controller.adapt_style(article, platform)
```

### 独立使用StyleCrew

```python
from core.agents.style_crew import StyleCrew
from core.models.article import Article
from core.models.platform import Platform

# 创建风格团队
style_crew = StyleCrew()
await style_crew.initialize(platform)

# 执行风格适配
style_result = await style_crew.adapt_style(article, platform)
styled_article = style_result.final_article
```

### 独立运行

可以使用提供的`run_style_crew.py`脚本独立运行风格适配功能：

```bash
# 列出所有可用的平台
python run_style_crew.py --list

# 基本用法（指定平台）
python run_style_crew.py example_article.json output.json --platform bilibili

# 基本用法（指定平台，显示详细日志）
python run_style_crew.py example_article.json output.json --platform zhihu --verbose
```

参数说明:
- `input_file`: 输入文章JSON文件路径
- `output_file`: 输出结果JSON文件路径
- `--platform, -p`: 目标平台名称（可指定ID或名称）
- `--verbose, -v`: 显示详细日志（可选）
- `--list, -l`: 列出所有可用平台（可选）

## 支持的平台

目前支持以下平台的风格适配：

1. **哔哩哔哩 (bilibili)**: 生动活泼，二次元风格，面向年轻人
2. **知乎 (zhihu)**: 专业严谨，深入浅出，面向知识分享
3. **抖音 (douyin)**: 爆点突出，情绪化表达，短平快内容
4. **今日头条 (toutiao)**: 震惊体，强调冲击点，吸引眼球
5. **小红书 (xiaohongshu)**: 亲切种草，个人体验分享，图文并茂
6. **微博 (weibo)**: 八卦爆料，话题引导，情绪化表达
7. **CSDN (csdn)**: 实用技术，问题解决导向，代码与讲解结合
8. **微信公众号 (wechat)**: 深度思考，价值传递，理性分析

## 输入/输出格式

### 输入文章格式

```json
{
  "id": "文章ID",
  "title": "文章标题",
  "content": "文章内容",
  "summary": "文章摘要",
  "author": "作者",
  "article_type": "文章类型",
  "creation_date": "创建时间",
  "sections": ["章节1", "章节2"],
  "keywords": ["关键词1", "关键词2"],
  "tags": ["标签1", "标签2"],
  "word_count": 1000,
  "images": []
}
```

### 输出结果格式

```json
{
  "article": {
    // 风格适配后的文章完整信息
  },
  "platform": "平台名称",
  "platform_analysis": {
    // 平台分析结果
  },
  "style_recommendations": {
    // 风格建议
  },
  "quality_check": {
    // 质量检查结果
    "overall_score": 8.5,
    "issues": []
  },
  "execution_time": 25.3
}
```

## 依赖项

- crewai: 智能体协作框架
- core.models.platform: 平台数据模型
- core.models.article: 文章数据模型
- core.tools.style_tools: 风格适配工具

## 平台扩展

要添加新的平台风格配置，只需在`platforms`目录下创建新的JSON文件，遵循已有平台的配置结构即可。平台配置包含以下主要部分：

1. **基本信息**: id、名称、描述、目标受众等
2. **内容规则**: 标题长度、内容长度、允许的HTML标签等
3. **风格规则**: 语气、正式程度、情感色彩、段落要求等
4. **风格指南**: 写作风格、内容方法、推荐模式、示例等
5. **SEO要求**: 关键词要求、元描述长度、标题数量等

---

Last Updated: 2024-05-30
