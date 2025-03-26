> **⚠️ 文档已弃用**
> 
> 本文档已经被新版文档替代，请访问最新文档：
> - API 规范：[GenFlow API 规范](/docs/integrated/genflow_api_specification.md)
> - 前端实现指南：[前端集成指南](/docs/integrated/frontend_integration_guide.md)
> - 后端实现指南：[后端实现指南](/docs/integrated/backend_implementation_guide.md)
> - CrewAI开发指南：[CrewAI开发指南](/docs/integrated/crewai_develop_guide.md)
> - CrewAI架构指南：[CrewAI架构指南](/docs/integrated/crewai_architecture_guide.md)
> - 术语表：[GenFlow 术语表](/docs/integrated/terminology_glossary.md)
>
> 本文档将在下一个版本发布时移除。

# AI 自动写作系统 V2

## 1. 系统架构

### 1.1 核心模块
- **知识管理模块**
  - 知识收集：多源数据采集
    - 网页解析引擎
      - newspaper3k：新闻文章解析
      - trafilatura：通用网页内容提取
      - readability-lxml：可读性优化
      - beautifulsoup4：HTML解析
      - mechanicalsoup：网页交互
      - scrapy：大规模爬虫
      - selenium：动态网页处理
    - 搜索引擎集成
      - DuckDuckGo Search：网页搜索
      - Google API：趋势分析
      - PyTrends：趋势数据
  - 知识整理：信息提取与验证
    - NLTK：自然语言处理
    - spaCy：实体识别和分析
    - summa：文本摘要和关键词
    - yake：关键词提取
  - 知识存储：结构化数据管理
    - SQLAlchemy：关系型数据库
    - Redis：缓存层
    - MongoDB：文档存储
    - PostgreSQL：高级查询

- **写作引擎模块**
  - 大纲生成：主题分析与结构设计
    - OpenAI GPT：复杂主题分析
    - Anthropic Claude：辅助分析
    - summa：关键信息提取
  - 内容生成：分段写作与整合
    - OpenAI GPT：主要内容生成
    - Claude：专业领域内容
    - CrewAI：多智能体协作
  - 文章优化：语言润色与校对
    - NLTK：基础语言分析
    - spaCy：语言理解增强

### 1.2 辅助模块
- **热点发现**
  - Google Trends API
  - PyTrends 数据分析
  - 自定义主题跟踪

- **数据源管理**
  - RESTful API 集成
  - 异步数据获取
  - 分布式采集

### 1.3 智能代理模块
- **工具代理（ToolAgent）**
  - CrewAI 框架集成
  - 多智能体协作
  - 任务分配优化

- **任务代理（TaskAgent）**
  - Celery 任务队列
  - Redis 状态管理
  - 异步任务处理

## 2. 详细设计

### 2.1 数据结构

1. **内容数据结构**
```python
@dataclass
class ContentItem:
    """统一的内容数据结构"""
    title: str
    url: str
    content: str
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    publish_date: Optional[str] = None
    source_type: str = "web"  # web, news, social 等
    source_tool: str = "unknown"  # newspaper, firecrawl, custom 等

class ContentParser(ABC):
    """内容解析器抽象基类"""
    @abstractmethod
    async def parse(self, url: str) -> Optional[ContentItem]:
        """解析内容"""
        pass

class ContentSource(ABC):
    """内容源抽象基类"""
    def __init__(self, parsers: List[ContentParser]):
        self.parsers = parsers

    @abstractmethod
    async def search(self, keyword: str) -> List[Dict]:
        """搜索内容"""
        pass

2. **文章结构**
```python
@dataclass
class ArticleSection:
    """文章段落"""
    title: str
    content: str
    references: List[Dict]

@dataclass
class ArticleOutline:
    """文章大纲"""
    title: str
    sections: List[Dict]
    keywords: List[str]
    target_length: int

@dataclass
class ArticleStyle:
    """文章风格"""
    tone: str          # 语气
    format: str        # 格式
    target_audience: str  # 目标受众
    language_level: str   # 语言难度
```

2. **知识库结构**
```python
class KnowledgeBase:
    """知识库"""
    facts: List[Dict]       # 事实列表
    references: Dict        # 引用映射
    keywords: List[str]     # 关键词
    metadata: Dict         # 元数据
```

### 2.2 核心流程

1. **多源内容采集流程**
```python
class ContentCollector:
    """内容采集器，支持多源采集"""

    def __init__(self, config):
        # 初始化解析器
        self.parsers = [
            NewspaperParser(language=config.LANGUAGE),
            TrafilaturaParser(),
            ReadabilityParser(),
            FirecrawlParser(api_key=config.FIRECRAWL_API_KEY)
        ]

        # 初始化搜索源
        self.sources = [
            GoogleTrendsSource(config, self.parsers),
            DuckDuckGoSource(config, self.parsers),
            FirecrawlSource(config, self.parsers)
        ]

    async def search_all(self, keyword: str) -> List[Dict]:
        """并发搜索所有来源"""
        tasks = [source.search(keyword) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self._merge_results(results)

    async def get_best_content(self, url: str) -> Optional[ContentItem]:
        """获取最佳内容解析结果"""
        tasks = [parser.parse(url) for parser in self.parsers]
        contents = await asyncio.gather(*tasks, return_exceptions=True)
        return self._select_best_content(contents)
```

2. **知识采集流程**
```python
async def collect_knowledge(topic: str, collector: ContentCollector) -> KnowledgeBase:
    # 1. 搜索相关内容
    search_results = await collector.search_all(topic)

    # 2. 并发采集内容
    content_tasks = [collector.get_best_content(result['url'])
                    for result in search_results]
    contents = await asyncio.gather(*content_tasks)

    # 3. 提取关键信息
    key_points = await extract_key_points(contents)

    # 4. 验证信息准确性
    verified_points = await verify_facts(key_points)

    # 5. 构建知识库
    return build_knowledge_base(verified_points)
```

3. **写作流程**
```python
async def generate_article(topic: str, style: ArticleStyle) -> Dict:
    # 1. 收集知识
    knowledge = await collect_knowledge(topic)

    # 2. 生成大纲
    outline = await generate_outline(topic, knowledge, style)

    # 3. 分段生成
    sections = await generate_sections(outline, knowledge)

    # 4. 优化润色
    article = await polish_article(sections, style)

    # 5. 质量控制
    article = await quality_check(article, knowledge)

    return format_output(article)
```

### 2.3 API 接口

1. **LLM 接口**
```python
class LLMClient:
    """语言模型客户端"""
    async def extract_key_points(self, content: str) -> List[Dict]
    async def verify_facts(self, points: List[Dict]) -> List[Dict]
    async def generate_outline(self, topic: str, points: List[Dict], style: ArticleStyle) -> Dict
    async def generate_section(self, title: str, knowledge: List[Dict], style: ArticleStyle) -> str
    async def polish_text(self, text: str, style: ArticleStyle) -> str
```

2. **内容采集接口**
```python
class ContentCollector:
    """内容采集器"""
    async def collect_content(self, topic: str, sources: List[str]) -> List[Dict]
    async def verify_source(self, source: str) -> bool
    async def extract_content(self, url: str) -> Dict
```

### 2.4 智能代理设计

1. **CrewAI 集成**
```python
from crewai import Agent, Task, Crew, Process
from typing import List, Dict

class ArticleCrewAgent:
    """文章生成智能代理系统"""

    def __init__(self, config: Config):
        self.config = config
        # 初始化各种工具
        self.content_collector = ContentCollector(config)
        self.writing_agent = WritingAgent(config)
        self.quality_agent = QualityAgent(config)

    def create_agents(self) -> List[Agent]:
        """创建专门的代理"""
        # 研究代理 - 负责收集和分析信息
        researcher = Agent(
            name="Researcher",
            role="研究专家",
            goal="收集和分析主题相关的高质量信息",
            backstory="我是一个专业的研究专家，擅长信息收集和分析",
            tools=[
                self.content_collector.search_all,
                self.content_collector.get_best_content
            ]
        )

        # 写作代理 - 负责内容创作
        writer = Agent(
            name="Writer",
            role="内容创作者",
            goal="创作高质量、原创的文章内容",
            backstory="我是一个专业的文章写作者，擅长创作各类型文章",
            tools=[
                self.writing_agent.generate_outline,
                self.writing_agent.generate_content,
                self.writing_agent.enhance_content
            ]
        )

        # 质量控制代理 - 负责内容审查
        quality_checker = Agent(
            name="QualityChecker",
            role="质量控制专家",
            goal="确保文章质量，包括原创性、可读性和SEO优化",
            backstory="我是一个质量控制专家，负责确保内容符合各项标准",
            tools=[
                self.quality_agent.check_plagiarism,
                self.quality_agent.detect_ai_content,
                self.quality_agent.optimize_seo
            ]
        )

        return [researcher, writer, quality_checker]

    def create_tasks(self, topic: str, style: ArticleStyle) -> List[Task]:
        """创建任务列表"""
        # 研究任务
        research = Task(
            description=f"研究主题 '{topic}' 并收集相关信息",
            agent=self.agents[0],  # researcher
            expected_output="主题相关的结构化信息和参考资料"
        )

        # 写作任务
        writing = Task(
            description="根据研究结果创作文章",
            agent=self.agents[1],  # writer
            expected_output="完整的文章内容",
            context={
                "style": style.dict(),
                "previous_task": research
            }
        )

        # 质量检查任务
        quality_check = Task(
            description="对文章进行质量检查和优化",
            agent=self.agents[2],  # quality_checker
            expected_output="质量检查报告和优化建议",
            context={
                "previous_task": writing
            }
        )

        return [research, writing, quality_check]

    async def generate_article(self, topic: str, style: ArticleStyle) -> Dict:
        """生成文章的主流程"""
        # 创建代理团队
        agents = self.create_agents()
        tasks = self.create_tasks(topic, style)

        # 创建和配置 Crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,  # 按顺序执行任务
            verbose=True  # 显示详细日志
        )

        # 执行任务
        result = await crew.kickoff()

        return {
            "article": result["writing"]["content"],
            "quality_report": result["quality_check"],
            "references": result["research"]["references"]
        }

# 使用示例
async def main():
    # 初始化配置
    config = Config()

    # 创建代理系统
    crew_agent = ArticleCrewAgent(config)

    # 设置文章风格
    style = ArticleStyle(
        tone="professional",
        format="blog",
        target_audience="general",
        language_level="intermediate"
    )

    # 生成文章
    result = await crew_agent.generate_article(
        topic="Python异步编程最佳实践",
        style=style
    )

    print(f"文章生成完成：\n{result['article']}\n")
    print(f"质量报告：\n{result['quality_report']}\n")
    print(f"参考资料：\n{result['references']}")
```

2. **配置更新**
```python
class Config:
    # ... existing code ...

    # CrewAI配置
    CREW_CONFIG = {
        "max_iterations": 3,        # 最大重试次数
        "timeout": 600,            # 任务超时时间(秒)
        "parallel_tasks": False,   # 是否并行执行任务
        "verbose": True,          # 是否显示详细日志
    }

    # 代理配置
    AGENT_CONFIGS = {
        "researcher": {
            "temperature": 0.7,
            "max_tokens": 1500,
            "tools": ["search_all", "get_best_content"]
        },
        "writer": {
            "temperature": 0.8,
            "max_tokens": 2000,
            "tools": ["generate_outline", "generate_content", "enhance_content"]
        },
        "quality_checker": {
            "temperature": 0.5,
            "max_tokens": 1000,
            "tools": ["check_plagiarism", "detect_ai_content", "optimize_seo"]
        }
    }
```

这个设计的优点：
1. **轻量级**：使用 CrewAI 作为基础，代码简洁清晰
2. **模块化**：每个代理负责特定任务，易于维护和扩展
3. **灵活性**：可以轻松添加新的代理和工具
4. **可控性**：支持顺序执行和并行执行
5. **可观测性**：内置日志和监控功能

建议的安装依赖：
```
crewai>=0.1.0
python-dotenv>=0.19.0
```

## 3. 配置需求

```python
class Config:
    # 基础配置
    LANGUAGE: str = "zh-CN"
    MAX_SOURCES: int = 10
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1

    # 内容采集配置
    CONTENT_PARSERS: List[str] = [
        "newspaper",
        "trafilatura",
        "readability",
        "firecrawl"
    ]

    SEARCH_SOURCES: List[str] = [
        "google_trends",
        "duckduckgo",
        "firecrawl"
    ]

    # API 配置
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    FIRECRAWL_API_KEY: str
    SERP_API_KEY: str

    # 内容质量配置
    MIN_CONTENT_LENGTH: int = 100
    MIN_TITLE_LENGTH: int = 10
    REQUIRED_FIELDS: List[str] = ["title", "content"]

    # 文章配置
    STYLE_TEMPLATES: Dict[str, ArticleStyle]
    MIN_SECTION_LENGTH: int = 200
    MAX_SECTION_LENGTH: int = 1000

    # 质量控制
    MIN_SIMILARITY: float = 0.6
    MAX_AI_SCORE: float = 0.7

    # Agent配置
    AGENT_CONFIG = {
        "performance_threshold": 0.7,
        "cost_limit": 10.0,
        "max_retries": 3,
        "timeout": 30,
        "parallel_tasks": 5
    }

    # 工具选择策略
    TOOL_SELECTION = {
        "min_confidence": 0.6,
        "max_tools_per_task": 3,
        "prefer_free_tools": True,
        "performance_weight": 0.7,
        "cost_weight": 0.3
    }

    # 写作工具配置
    WRITING_TOOLS = {
        "outline_generators": ["gpt4_outliner", "textrank"],
        "content_generators": ["claude_writer", "gpt4_writer"],
        "enhancers": ["languagetool", "grammarly"],
        "default_outline_generator": "gpt4_outliner",
        "default_content_generator": "claude_writer",
        "default_enhancer": "languagetool"
    }

    # 写作风格模板
    STYLE_TEMPLATES = {
        "academic": ArticleStyle(
            tone="formal",
            format="academic",
            target_audience="researchers",
            language_level="advanced",
            citation_format="apa",
            min_length=2000,
            max_length=5000
        ),
        "blog": ArticleStyle(
            tone="casual",
            format="web",
            target_audience="general",
            language_level="intermediate",
            citation_format="hyperlink",
            min_length=800,
            max_length=1500
        )
    }

    # 写作质量控制
    WRITING_QUALITY = {
        "min_coherence": 0.7,
        "max_repetition": 0.2,
        "readability_score": "intermediate",
        "required_elements": ["introduction", "conclusion", "citations"]
    }

    # 质量控制配置
    QUALITY_CONTROL = {
        # 查重配置
        "plagiarism": {
            "enabled": True,
            "providers": ["copyscape", "turnitin"],
            "similarity_threshold": 0.2,
            "min_match_length": 30,
            "ignore_quotes": True
        },

        # AI检测配置
        "ai_detection": {
            "enabled": True,
            "providers": ["gptzero", "originality"],
            "ai_score_threshold": 0.7,
            "confidence_threshold": 0.8,
            "require_explanation": True
        },

        # SEO配置
        "seo": {
            "enabled": True,
            "providers": ["yoast", "semrush"],
            "min_keyword_density": 0.01,
            "max_keyword_density": 0.03,
            "readability_target": "general",
            "min_word_count": 800
        }
    }
```

## 4. 后续优化方向

1. **待实现功能**
   - Grammarly API 集成
   - Hemingway 编辑器集成
   - Citation.js 引用管理
   - Copyscape API 查重
   - Turnitin API 学术查重
   - GPTZero AI检测
   - Originality.ai 集成
   - ZeroGPT 检测
   - Yoast SEO 工具集成
   - SEMrush API 分析
   - CrossRef API 学术引用

2. **知识管理增强**
   - 知识图谱构建
   - 多语言支持扩展
   - 实体关系提取
   - 自动更新机制

3. **生成能力提升**
   - 多模型协同
   - 专业领域适配
   - 风格一致性
   - 引用系统完善

4. **工程化改进**
   - 测试覆盖率提升
   - 监控系统建设
   - 错误处理完善
   - 性能优化

5. **产品化方向**
   - FastAPI Web界面
   - Gradio 演示界面
   - 用户反馈系统
   - 版本控制集成

6. **智能代理优化**
   - 决策系统增强
   - 工具动态注册
   - 性能预测模型
   - 自适应策略

7. **质量控制优化**
   - 本地查重系统
   - 多模型交叉验证
   - 行业特征识别
   - SEO策略优化
