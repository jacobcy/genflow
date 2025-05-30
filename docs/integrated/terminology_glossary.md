# GenFlow 术语表

## 核心概念

| 术语 | 英文对照 | 定义 |
|------|----------|------|
| 内容生产系统 | Content Production System | GenFlow 的整体系统，包含从选题到发布的完整内容创作流程 |
| 智能体团队 | Agent Crew | 执行特定写作任务的 AI 智能体集合，如选题团队、写作团队等 |
| 工具 | Tool | 智能体使用的功能模块，如搜索工具、内容采集工具等 |
| 会话 | Session | 前端与后端的交互上下文，包含状态信息和历史记录 |
| 建议 | Suggestion | 系统提供的写作辅助内容，包括自动补全、内容建议等 |

## 写作阶段

| 阶段名称 | 英文对照 | 定义 |
|---------|----------|------|
| 选题阶段 | Topic Discovery | 发现热门话题、评估话题价值和市场竞争的阶段 |
| 研究阶段 | Research | 深入研究选定话题，收集相关资料和数据的阶段 |
| 写作阶段 | Writing | 根据研究结果和大纲创作原始内容的阶段 |
| 风格化阶段 | Styling | 调整内容风格，适配目标平台和受众的阶段 |
| 审核阶段 | Review | 检查内容质量、合规性和原创性的阶段 |

## 系统组件

| 组件名称 | 英文对照 | 定义 |
|---------|----------|------|
| 选题团队 | Topic Crew | 负责发现和评估话题的智能体团队 |
| 研究团队 | Research Crew | 负责深入研究选定话题的智能体团队 |
| 写作团队 | Writing Crew | 负责根据研究结果创作内容的智能体团队 |
| 审核团队 | Review Crew | 负责审核和优化内容的智能体团队 |
| 会话管理器 | Session Manager | 管理会话生命周期和状态的系统组件 |
| 事件分发器 | Event Dispatcher | 处理实时事件通知的系统组件 |

## 数据结构

| 结构名称 | 英文对照 | 定义 |
|---------|----------|------|
| 消息 | Message | 用户与系统之间交互的信息单元 |
| 写作进度 | Writing Progress | 描述当前写作阶段、状态和完成度的结构 |
| 动作按钮 | Action Button | 用户可以执行的操作按钮定义 |
| 编辑操作 | Edit Operation | 描述内容编辑行为的数据结构 |
| 话题数据 | Topic Data | 描述发现的话题信息，包括标题、热度、竞争度等 |
| 研究报告 | Research Report | 话题研究的结果数据，包括关键信息、参考资料等 |

## API 相关

| 术语 | 英文对照 | 定义 |
|------|----------|------|
| 会话管理 API | Session Management API | 用于创建和管理写作会话的接口 |
| 内容生产 API | Content Production API | 用于内容创建和编辑的接口 |
| 阶段流转 API | Stage Transition API | 用于在写作阶段之间切换的接口 |
| WebSocket 事件 | WebSocket Events | 通过 WebSocket 传输的实时事件消息 |

## 其他术语

| 术语 | 英文对照 | 定义 |
|------|----------|------|
| 热度分析 | Trend Analysis | 评估话题热度和流行趋势的分析方法 |
| 竞争分析 | Competition Analysis | 评估话题在市场中竞争情况的分析方法 |
| 内容大纲 | Content Outline | 文章结构和主要段落的概要设计 |
| 风格适配 | Style Adaptation | 根据目标平台和受众调整内容风格的过程 |
| 实时建议 | Real-time Suggestions | 编辑过程中动态提供的写作建议 |
| 人工干预 | Human Intervention | 创作流程中允许人工参与和调整的环节 |

---

最后更新: 2024-05-15
