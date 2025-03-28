# 智能代理系统 - 分层架构

本系统采用严格的分层架构设计，确保职责清晰、代码可维护性高，并保持清晰的数据流向。

## 分层架构总览

系统分为三个主要层次：

1. **控制器层 (Controller)**
   - 处理用户请求和系统流程编排
   - 不包含业务逻辑，只负责调用适配器

2. **适配器层 (TeamAdapter)**
   - 控制器和具体团队之间的桥梁
   - 处理参数解析和转换，确保传递给底层团队的数据格式正确
   - 处理ID关联和状态映射
   - 不保存处理结果

3. **团队实现层 (Crew)**
   - 实现具体业务逻辑的工作流
   - 不处理ID关联或状态映射
   - 专注于完成特定任务

## 数据流向

```
用户请求 --> 控制器 --> 团队适配器 --> 团队实现 --> 团队适配器 --> 控制器 --> 用户响应
```

## 团队模块详细说明

### 1. 研究团队 (ResearchCrew)

#### 研究团队适配器 (ResearchTeamAdapter)

**职责**：
- 解析输入的话题信息（从Topic对象或topic_id）
- 根据content_type确定研究配置
- 调用ResearchCrew执行研究
- 返回BasicResearch或TopicResearch对象

**输入**：
- `topic`: 话题对象或topic_id或直接的文本标题
- `content_type`: 内容类型 (默认为"article")
- `depth`: 研究深度
- `options`: 其他选项

**输出**：
- 如有topic_id，返回TopicResearch对象
- 否则返回BasicResearch对象

#### 研究团队实现 (ResearchCrew)

**职责**：
- 执行背景研究、专家发现、数据分析等研究任务
- 生成研究报告

**输入**：
- `topic`: 话题标题字符串
- `research_config`: 研究配置
- `depth`: 研究深度
- `options`: 其他选项

**输出**：
- 返回BasicResearch对象

### 2. 写作团队 (WritingCrew)

#### 写作团队适配器 (WritingTeamAdapter)

**职责**：
- 解析输入的话题信息（从Topic对象或topic_id）
- 根据content_type和platform确定写作风格和配置
- 调用WritingCrew执行写作
- 返回处理后的写作结果

**输入**：
- `topic`: 话题对象
- `research_data`: 研究数据
- `content_type`: 内容类型（可选，如未提供则从topic提取）
- `platform_id`: 平台ID（可选）
- `style`: 写作风格（可选）
- `options`: 其他选项

**输出**：
- 返回写作结果字典

#### 写作团队实现 (WritingCrew)

**职责**：
- 负责创建大纲、撰写内容、事实核查和编辑

**输入**：
- `article`: 文章对象
- `research_data`: 研究资料
- `platform`: 平台信息
- `content_type`: 内容类型
- `style`: 写作风格
- `options`: 其他选项

**输出**：
- 返回WritingResult对象

### 3. 风格团队 (StyleCrew)

#### 风格团队适配器 (StyleTeamAdapter)

**职责**：
- 解析输入的内容信息（从outline_id或文本内容）
- 根据style_id或style_type确定风格配置
- 调用StyleCrew执行风格适配
- 返回BasicArticle或Article对象

**输入**：
- `content`: 需要调整风格的内容（文本、ID、outline对象或article对象）
- `platform_id`: 目标平台ID（可选）
- `style_name`: 目标风格名称或描述文本（可选）
- `options`: 其他选项

**输出**：
- 返回BasicArticle或Article对象

#### 风格团队实现 (StyleCrew)

**职责**：
- 执行风格分析和适配

**输入**：
- `article`: 文章对象
- `style_config`: 风格配置
- `platform_info`: 平台信息
- `options`: 其他选项

**输出**：
- 返回风格处理结果

## 设计原则

1. **职责分离**：每层有清晰的职责边界，不重叠
2. **单向依赖**：上层依赖下层，下层不依赖上层
3. **参数解析职责**：ID映射和内容类型解析应在适配器层完成
4. **状态管理**：适配器层负责状态跟踪，但不保存处理结果
5. **核心业务逻辑**：只在团队实现层处理

## 开发规范

1. 适配器层方法必须记录处理状态（如processing, completed, failed）
2. 团队实现层方法不应直接与数据库或状态存储交互
3. 注释必须说明每个方法的输入参数和返回值的格式和含义
4. 异常必须在适配器层被捕获并包装为友好的错误信息
