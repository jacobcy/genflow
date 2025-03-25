# GenFlow 开发指南

## 系统架构

GenFlow 是一个基于多智能体协作的内容创作系统，采用分层架构设计：

### 1. Core 层 - LLM 能力封装

核心层基于 CrewAI 框架实现多智能体协作写作：

```python
from crewai import Agent, Task, Crew
from core.models import Article, Platform

class WritingCrew:
    def __init__(self):
        # 初始化写作智能体团队
        self.planner = Agent(...)    # 负责内容规划
        self.writer = Agent(...)     # 负责内容创作
        self.editor = Agent(...)     # 负责内容优化
```

主要职责：
- 封装底层 LLM 能力
- 实现多智能体协作机制
- 定义核心数据模型
- 处理写作任务调度

### 2. Interface 层 - 服务接口

为上层应用提供统一的接口：

```python
class WritingInterface:
    def __init__(self, crew: WritingCrew):
        self.crew = crew

    async def write_article(self, title: str, summary: str,
                          platform: str, rules: Dict) -> Dict:
        # 调用 Core 层执行写作任务
        pass
```

主要职责：
- 包装 Core 层功能
- 提供标准化 API
- 处理数据格式转换
- 提供错误处理机制

### 3. FastAPI 层 - 会话管理

处理 HTTP 请求和会话状态。我们的 API 分为以下几个主要模块：

#### 3.1 认证 API

详细文档：[认证 API 文档](./api/genflow_auth_api.md)

```python
@router.post("/auth/login")
async def login(request: LoginRequest):
    """用户登录接口

    请求示例：
    {
        "username": "user@example.com",
        "password": "password123"
    }
    """
    pass

@router.post("/auth/register")
async def register(request: RegisterRequest):
    """用户注册接口"""
    pass
```

#### 3.2 文章生成 API

详细文档：[文章生成 API 文档](./api/genflow_article_api.md)

```python
@router.post("/articles")
async def create_article(request: ArticleRequest):
    """创建新文章

    请求示例：
    {
        "title": "文章标题",
        "summary": "文章摘要",
        "platform": "medium",
        "rules": {
            "min_words": 1000,
            "max_words": 2000,
            "style": "专业"
        }
    }
    """
    interface = WritingInterface()
    result = await interface.write_article(
        title=request.title,
        summary=request.summary,
        platform=request.platform,
        rules=request.rules
    )
    return result
```

#### 3.3 写作助手 API

详细文档：[写作助手 API 文档](./api/ai-writing-assistant-api.md)

```python
@router.post("/assistant/analyze")
async def analyze_article(request: AnalyzeRequest):
    """分析文章结构和质量"""
    pass

@router.post("/assistant/optimize")
async def optimize_article(request: OptimizeRequest):
    """优化文章内容"""
    pass
```

#### 3.4 写作工具 API

详细文档：[写作工具 API 文档](./api/ai-writing_tool_api.md)

```python
@router.post("/tools/keywords")
async def extract_keywords(request: KeywordRequest):
    """提取关键词"""
    pass

@router.post("/tools/seo")
async def optimize_seo(request: SeoRequest):
    """SEO 优化"""
    pass
```

### API 开发规范

请参考：[API 开发规范](./api/api-standards.md)

主要规范包括：
- RESTful API 设计原则
- 请求/响应格式规范
- 错误处理规范
- 版本控制规范
- 安全规范

### API 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

### API 认证

所有 API 请求（除登录注册外）都需要在 Header 中携带 JWT Token：

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. React 前端 - 用户交互

提供直观的用户界面：

```typescript
const WritingPage: React.FC = () => {
  const [article, setArticle] = useState<Article>();

  const handleSubmit = async (data: ArticleForm) => {
    const result = await api.createArticle(data);
    setArticle(result);
  };
}
```

主要职责：
- 用户界面交互
- 状态管理
- 实时反馈
- 结果展示

## 开发流程

### 1. 环境配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 2. 开发规范

- 遵循 PEP 8 Python 代码规范
- 使用 TypeScript 进行前端开发
- 编写完整的单元测试
- 保持代码注释最新

### 3. 提交规范

```bash
# 提交格式
<type>(<scope>): <subject>

# 示例
feat(core): 添加文章分析智能体
fix(api): 修复会话状态管理问题
docs(guide): 更新开发文档
```

## 快速开始

### 1. 创建新的智能体

```python
# core/agents/analyzer.py
from crewai import Agent

class AnalyzerAgent(Agent):
    def __init__(self):
        super().__init__(
            name="analyzer",
            goal="分析文章结构和质量",
            backstory="我是一个专业的内容分析师..."
        )
```

### 2. 实现新的接口方法

```python
# core/services/writing/interface.py
async def analyze_article(self, article_data: Dict) -> Dict:
    article = Article.from_dict(article_data)
    result = await self.crew.analyze(article)
    return result.to_dict()
```

### 3. 添加 API 端点

```python
# api/routes/writing.py
@router.post("/analyze")
async def analyze_article(request: AnalyzeRequest):
    interface = WritingInterface()
    return await interface.analyze_article(request.dict())
```

### 4. 开发前端组件

```typescript
// frontend/src/components/AnalyzePanel.tsx
const AnalyzePanel: React.FC<Props> = ({ article }) => {
  const [analysis, setAnalysis] = useState();

  useEffect(() => {
    api.analyzeArticle(article).then(setAnalysis);
  }, [article]);

  return <div>{/* 展示分析结果 */}</div>;
};
```

## 测试

### 1. 单元测试

```python
# tests/test_writing_interface.py
def test_article_generation():
    interface = WritingInterface()
    result = await interface.write_article(
        title="测试文章",
        summary="这是一个测试",
        platform="medium",
        rules={"min_words": 1000}
    )
    assert result["title"] == "测试文章"
```

### 2. 集成测试

```python
# tests/integration/test_api.py
async def test_writing_endpoint():
    async with AsyncClient(app=app) as client:
        response = await client.post("/write", json={...})
        assert response.status_code == 200
```

## 部署

### 1. Docker 部署

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### 2. 环境变量配置

```bash
OPENAI_API_KEY=your_key_here
MODEL_NAME=gpt-4
DEBUG=False
```

## 常见问题

1. **如何添加新的智能体？**
   - 在 `core/agents` 目录下创建新的智能体类
   - 在 `WritingCrew` 中集成新智能体
   - 更新相关接口和测试

2. **如何优化写作质量？**
   - 调整智能体提示词
   - 添加专门的质量检查智能体
   - 实现多轮优化机制

3. **如何处理并发请求？**
   - 使用异步队列
   - 实现请求限流
   - 优化资源分配

4. **API 调用问题**
   - 确保正确设置 Authorization Header
   - 检查请求参数格式
   - 查看具体 API 文档中的示例
   - 使用日志级别 DEBUG 进行调试

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交变更
4. 发起 Pull Request

## 联系方式

- 项目负责人：[联系方式]
- 技术支持：[邮箱]
- 问题反馈：[Issue 链接]
