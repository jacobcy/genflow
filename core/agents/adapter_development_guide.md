# 团队适配器开发指南

## 1. 概述

团队适配器是连接控制器和团队实现的关键组件，遵循明确的分层架构设计。本指南提供开发团队适配器时的最佳实践和规范。

## 2. 分层架构

系统采用三层架构：

```
控制器层 (Controller) → 适配器层 (TeamAdapter) → 团队实现层 (Crew)
```

### 各层职责

- **控制器层**：处理用户请求，组织工作流，不包含具体业务逻辑
- **适配器层**：处理参数解析、ID映射、状态跟踪，不实现业务逻辑
- **团队实现层**：实现核心业务逻辑，不处理ID关联或状态映射

## 3. 适配器开发规范

### 3.1 结构模板

每个团队适配器应遵循以下结构：

```python
class ExampleTeamAdapter(BaseTeamAdapter):
    """示例团队适配器

    职责：
    1. 解析输入的参数（从对象或ID）
    2. 根据参数确定配置
    3. 调用团队实现执行任务
    4. 返回处理后的结果

    注意：本层不保存处理结果，只负责参数转换和调用下层
    """

    def __init__(self):
        """初始化适配器"""
        super().__init__()
        self.crew = None
        self._status = {}  # 用于跟踪状态

    async def initialize(self, **kwargs) -> None:
        """初始化适配器

        Args:
            **kwargs: 初始化参数
        """
        await super().initialize(**kwargs)

        if not self.crew:
            self.crew = ExampleCrew(verbose=kwargs.get("verbose", True))
            logger.info("示例团队适配器初始化完成")

    async def process_task(
        self,
        input_data: Union[str, Dict, Any],
        param1: Optional[str] = None,
        param2: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """处理任务

        将输入数据转换为Crew需要的格式，并调用Crew执行任务。

        Args:
            input_data: 输入数据
            param1: 参数1(可选)
            param2: 参数2(可选)
            options: 其他选项

        Returns:
            Any: 处理结果
        """
        await self.initialize()

        try:
            # 1. 解析输入数据
            data_id, processed_data = self._extract_data(input_data)

            # 2. 根据参数确定配置
            config = self._create_config(param1, param2)

            # 3. 记录状态
            if data_id:
                self._status[data_id] = "processing"

            # 4. 调用Crew执行任务
            result = await self.crew.execute_task(
                data=processed_data,
                config=config,
                **options
            )

            # 5. 更新状态
            if data_id:
                self._status[data_id] = "completed"

            # 6. 处理并返回结果
            return self._process_result(result, data_id)

        except Exception as e:
            if data_id:
                self._status[data_id] = "failed"
            raise RuntimeError(f"处理任务失败: {str(e)}")

    def _extract_data(self, input_data) -> Tuple[Optional[str], Any]:
        """解析输入数据

        Args:
            input_data: 输入数据

        Returns:
            Tuple[Optional[str], Any]: (数据ID, 处理后的数据)
        """
        # 提取ID和处理数据的实现
        pass

    def _create_config(self, param1, param2) -> Dict[str, Any]:
        """创建配置

        Args:
            param1: 参数1
            param2: 参数2

        Returns:
            Dict[str, Any]: 配置字典
        """
        # 创建配置的实现
        pass

    def _process_result(self, result, data_id) -> Any:
        """处理结果

        Args:
            result: Crew返回的结果
            data_id: 数据ID

        Returns:
            Any: 处理后的结果
        """
        # 处理结果的实现
        pass

    async def get_status(self, data_id: str) -> str:
        """获取处理状态

        Args:
            data_id: 数据ID

        Returns:
            str: 处理状态
        """
        return self._status.get(data_id, "not_found")
```

### 3.2 关键原则

1. **初始化延迟**：Crew对象应在initialize方法中懒加载
2. **参数解析**：适配器负责将输入参数转换为Crew期望的格式
3. **状态跟踪**：适配器负责记录和更新处理状态
4. **错误处理**：捕获异常并包装为友好的错误信息
5. **ID映射**：处理对象ID和实例之间的映射

## 4. 代码示例

### 4.1 ResearchTeamAdapter

```python
async def research_topic(
    self,
    topic: Union[str, Topic, Dict, Any],
    depth: str = "medium",
    options: Optional[Dict[str, Any]] = None
) -> BasicResearch:
    """研究话题

    将输入的topic信息转换为ResearchCrew需要的格式，
    并根据content_type确定研究配置。

    Args:
        topic: 话题对象、字符串或包含话题信息的字典
        depth: 研究深度(shallow/medium/deep)
        options: 其他选项

    Returns:
        BasicResearch: 研究结果，如有topic_id则返回TopicResearch
    """
    try:
        # 提取话题信息
        topic_title, topic_id, content_type = self._extract_topic_info(topic)

        # 如果没有指定content_type，使用默认类型
        if not content_type:
            content_type = "article"
            logger.info(f"未指定内容类型，使用默认类型: {content_type}")

        # 生成研究配置
        research_config = self._create_research_config(content_type)

        # 记录状态
        if topic_id:
            self._research_status[topic_id] = "processing"

        # 调用ResearchCrew执行研究
        result = await self.crew.research_topic(
            topic=topic_title,  # 只传递标题，不传递整个对象
            research_config=research_config,
            depth=depth,
            options=options or {}
        )

        # 更新状态
        if topic_id:
            self._research_status[topic_id] = "completed"
            # 如果有topic_id，返回TopicResearch对象
            return TopicResearch.from_basic_research(result, topic_id)

        # 没有topic_id，直接返回BasicResearch
        return result

    except Exception as e:
        if topic_id:
            self._research_status[topic_id] = "failed"
        raise RuntimeError(f"研究话题失败: {str(e)}")
```

### 4.2 WritingTeamAdapter

```python
async def write_content(
    self,
    topic: Topic,
    research_data: Dict[str, Any],
    style: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """写作内容

    将话题和研究数据转换为WritingCrew需要的格式，
    并根据content_type和platform确定写作风格。

    Args:
        topic: 话题对象
        research_data: 研究资料
        style: 写作风格(可选)
        options: 其他选项

    Returns:
        Dict[str, Any]: 写作结果
    """
    await self.initialize()

    try:
        # 获取内容类型
        content_type_id = self._extract_content_type(topic)
        logger.info(f"解析得到内容类型: {content_type_id or '未指定'}")

        # 获取平台ID
        platform_id = getattr(topic, 'platform', None)
        logger.info(f"从话题获取平台ID: {platform_id}")

        # 获取风格ID
        style_id = self._determine_style(style, platform_id, content_type_id)

        # 创建临时文章对象
        article = Article(
            id=topic.id if hasattr(topic, 'id') else str(uuid.uuid4()),
            title=topic.title if hasattr(topic, 'title') else "未命名",
            topic=topic
        )

        # 记录状态
        if hasattr(topic, 'id'):
            self._writing_status[topic.id] = "processing"

        # 调用WritingCrew执行写作
        result = await self.crew.write_article(
            article=article,
            research_data=research_data,
            platform=platform_id,
            content_type=content_type_id,
            style=style_id,
            **(options or {})
        )

        # 更新状态
        if hasattr(topic, 'id'):
            self._writing_status[topic.id] = "completed"

        # 返回写作结果
        return result.to_dict()
    except Exception as e:
        if hasattr(topic, 'id'):
            self._writing_status[topic.id] = "failed"
        raise RuntimeError(f"写作内容失败: {str(e)}")
```

## 5. 审核清单

开发新的团队适配器时，请检查以下项目：

- [ ] 适配器类名是否遵循`XxxTeamAdapter`命名规范
- [ ] 是否继承自`BaseTeamAdapter`
- [ ] 是否包含详细的类文档注释，说明职责
- [ ] 是否实现`initialize()`方法
- [ ] 是否实现延迟初始化Crew对象
- [ ] 是否在适配器方法中处理参数解析和转换
- [ ] 是否实现状态跟踪
- [ ] 是否捕获并包装异常
- [ ] 是否添加适当的日志记录
- [ ] 是否避免在适配器中实现业务逻辑
- [ ] 是否避免在适配器中保存处理结果

## 6. 最佳实践

1. **参数验证**：在适配器方法开始处验证必要参数
2. **结构化日志**：使用logger记录关键操作和状态变更
3. **职责分离**：适配器只负责转换和调用，不包含业务逻辑
4. **异常处理**：捕获特定异常并转换为更有意义的错误消息
5. **延迟初始化**：lazy loading模式创建Crew对象，减少资源占用
6. **参数文档**：详细注释每个参数的用途、格式和可选性
7. **返回值文档**：明确说明返回值的类型和结构
8. **状态跟踪**：使用字典记录每个任务的处理状态
