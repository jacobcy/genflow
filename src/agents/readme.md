# GenFlow 智能团队说明

本目录包含了 GenFlow 系统中的各个智能团队。每个团队由多个专门的智能体组成，配备相应的工具来完成特定任务。

## 团队构成

### 1. 选题团队 (topic_crew)
负责发现和评估内容选题。

**智能体**：
- 趋势分析师：发现热门话题
- 话题研究员：评估话题价值
- 报告撰写员：生成分析报告

**工具**：
- TrendingTopics：热点话题发现
- SearchAggregator：搜索聚合
- ContentCollector：内容采集
- NLPAggregator：文本分析

### 2. 研究团队 (research_crew)
负责深入研究选定话题。

**智能体**：
- 背景研究员：收集话题背景
- 专家发现者：收集专家观点
- 数据分析师：分析研究数据
- 研究报告撰写员：撰写研究报告

**工具**：
- ContentCollector：内容采集
- SearchAggregator：搜索聚合
- NLPAggregator：文本分析

### 3. 写作团队 (writing_crew)
负责生成高质量内容。

**智能体**：
- 大纲撰写员：设计文章结构
- 内容撰写员：生成主体内容
- SEO优化师：优化搜索表现
- 编辑：提升内容质量

**工具**：
- ArticleWriter：文章生成
- NLPAggregator：文本处理
- SummaTool：摘要生成
- YakeTool：关键词提取
- StyleAdapter：风格适配

### 4. 审核团队 (review_crew)
负责内容审核和质量把控。

**智能体**：
- 查重专员：检查原创性
- AI检测员：识别AI内容
- 内容审核员：检查合规性
- 终审专员：全面评估

**工具**：
- PlagiarismChecker：查重检查
- StatisticalAIDetector：统计型AI检测
- OpenAIDetector：基于OpenAI的AI检测
- SensitiveWordChecker：敏感词检查
- NLPAggregator：文本分析

## 工作流程

1. 选题团队发现和评估话题
2. 研究团队深入研究并生成报告
3. 写作团队基于研究成果创作内容
4. 审核团队进行多维度质量检查

每个环节都保留人工干预接口，确保内容质量。
