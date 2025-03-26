# 风格化团队 (StyleCrew)

## 概述

风格化团队负责将内容按照不同平台的风格规范进行改写和适配。该模块实现了一个完整的风格化工作流，包括平台分析、风格建议生成、内容适配和质量检查四个主要步骤。

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

## 工作流程

风格化团队的工作流程包含以下步骤：

1. **平台分析**: 分析目标平台的内容特点和风格规范
2. **风格建议生成**: 根据平台特点和原始内容，制定风格改写策略
3. **内容适配**: 根据风格建议对内容进行实际改写
4. **质量检查**: 检查适配后内容的质量和合规性

## 智能体角色

风格团队包含四个主要角色：

1. **平台分析师(PlatformAnalystAgent)**: 负责分析平台特点和风格规范
2. **风格专家(StyleExpertAgent)**: 负责制定风格改写策略
3. **内容适配器(ContentAdapterAgent)**: 负责执行具体的改写工作
4. **质量检查员(QualityCheckerAgent)**: 负责检查改写后内容的质量

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