# GenFlow 集成架构方案

## 系统架构

### 1. 核心组件

```
                           ┌─────────────────┐
                           │    Nginx 代理    │
                           └────────┬────────┘
                                   │
                   ┌───────────────┼───────────────┐
                   │               │               │
           ┌───────┴───────┐ ┌─────┴─────┐ ┌──────┴──────┐
           │  GenFlow 前端  │ │LangManus Web│ │LangManus API│
           │  (端口:6060)  │ │ (端口:3000) │ │ (端口:8000) │
           │   [CrewAI]    │ │[LangGraph参考]│ │ [LangGraph] │
           └───────┬───────┘ └───────────┘ └─────────────┘
                   │
           ┌───────┴───────┐
           │  DailyHot UI  │
           │  (端口:6699)  │
           └───────┬───────┘
                   │
           ┌───────┴───────┐
           │ DailyHot API  │
           │  (端口:6688)  │
           └───────────────┘
```

### 2. 技术栈对比

| 特性 | GenFlow | LangManus |
|------|---------|-----------|
| 框架 | CrewAI | LangGraph |
| 特点 | 团队协作、角色管理 | 工作流编排、状态管理 |
| 用途 | AI团队任务处理 | 通用LLM工作流 |
| 前端 | 定制化UI (6060端口) | 参考实现 (3000端口) |
| API | CrewAI接口 | LangGraph接口 |

### 3. 目录结构

```
GenFlow/
├── integrations/                # 第三方集成目录
│   ├── doocs.github.io/        # Markdown 编辑器
│   ├── langmanus/             # LangManus (LangGraph实现)
│   ├── langmanus-web/         # LangManus Web UI
│   ├── daily-hot/            # DailyHot 前端界面
│   └── daily-hot-api/        # DailyHot API 服务
├── frontend/                  # GenFlow 主前端
│   ├── app/                  # Next.js 应用
│   ├── components/          # 共享组件
│   └── services/           # CrewAI 服务适配层
└── backend/
    ├── crewai/             # CrewAI 核心实现
    └── api/               # GenFlow API 服务
```

## 集成策略

### 1. 前端集成

```typescript
// frontend/services/agents/index.ts
import type { Agent } from '@/types/crewai';

// CrewAI 代理管理
export class AgentService {
  constructor(private apiUrl: string) {}

  async createAgent(agent: Agent) {
    return fetch(`${this.apiUrl}/api/agents`, {
      method: 'POST',
      body: JSON.stringify(agent)
    });
  }

  async assignTask(agentId: string, task: Task) {
    return fetch(`${this.apiUrl}/api/agents/${agentId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(task)
    });
  }
}

// frontend/services/chat/index.ts
// 聊天界面复用 LangManus Web 的 UI 组件，但使用 CrewAI 的后端逻辑
export class ChatService {
  private agentService: AgentService;

  constructor() {
    this.agentService = new AgentService(process.env.NEXT_PUBLIC_API_URL);
  }

  async sendMessage(message: ChatMessage) {
    // 1. 根据消息内容选择或创建合适的 Agent
    const agent = await this.agentService.selectAgent(message.content);
    
    // 2. 创建任务并分配给 Agent
    const task = await this.agentService.createTask(message);
    
    // 3. 执行任务并返回结果
    return this.agentService.executeTask(task);
  }
}
```

### 2. 后端集成

```python
# backend/crewai/agents.py
from crewai import Agent, Task, Crew
from typing import List, Dict

class GenFlowAgent:
    def __init__(self, config: Dict):
        self.agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=config["tools"]
        )
    
    async def handle_message(self, message: str) -> str:
        # 创建任务
        task = Task(
            description=message,
            agent=self.agent
        )
        
        # 执行任务
        result = await task.execute()
        return result

# backend/api/routes/chat.py
from fastapi import APIRouter, WebSocket
from crewai import Crew
from typing import List

router = APIRouter()

@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    
    # 初始化 CrewAI 团队
    crew = Crew(
        agents=[
            # 配置团队成员
        ],
        tasks=[
            # 配置初始任务
        ]
    )
    
    try:
        while True:
            message = await websocket.receive_text()
            
            # 通过 CrewAI 处理消息
            response = await crew.process_message(message)
            
            await websocket.send_text(response)
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()
```

## 开发环境配置

```yaml
# docker/compose/dev/docker-compose.yml
version: '3.8'
services:
  genflow-frontend:
    build: 
      context: ../../../frontend
    ports:
      - "6060:6060"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:6060
      - CREWAI_API_URL=http://genflow-backend:8080
    depends_on:
      - genflow-backend

  genflow-backend:
    build:
      context: ../../../backend
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ../../../backend:/app

  langmanus-web:
    build:
      context: ../../../integrations/langmanus-web
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://langmanus-api:8000
    depends_on:
      - langmanus-api

  langmanus-api:
    build:
      context: ../../../integrations/langmanus
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  daily-hot:
    build:
      context: ../../../integrations/daily-hot
    ports:
      - "6699:6699"
    environment:
      - VITE_API_URL=http://daily-hot-api:6688
    depends_on:
      - daily-hot-api

  daily-hot-api:
    build:
      context: ../../../integrations/daily-hot-api
    ports:
      - "6688:6688"
    environment:
      - PORT=6688
      - CACHE_TIME=60
    volumes:
      - ../../../integrations/daily-hot-api:/app
```

## 开发工作流

### 1. 本地开发

```bash
# 1. 启动 GenFlow 后端 (CrewAI)
cd backend
python main.py  # 运行在 8080 端口

# 2. 启动 GenFlow 前端
cd frontend
npm run dev  # 运行在 6060 端口

# 3. （可选）启动 LangManus 参考实现
cd integrations/langmanus
python server.py  # 运行在 8000 端口
cd ../langmanus-web
npm run dev  # 运行在 3000 端口

# 4. （可选）启动 DailyHot 服务
cd integrations/daily-hot-api
pnpm install
pnpm dev  # 运行在 6688 端口

cd ../daily-hot
pnpm install
pnpm dev  # 运行在 6699 端口
```

### 2. 开发重点

1. **CrewAI 集成**：
   - 实现 Agent 管理系统
   - 设计任务分配机制
   - 优化团队协作流程

2. **UI 开发**：
   - 参考 LangManus Web 的界面设计
   - 集成 DailyHot 的热点数据展示
   - 实现 CrewAI 特有的功能界面
   - 优化用户交互体验

3. **API 设计**：
   - 实现 CrewAI 的 RESTful API
   - 整合 DailyHot API 的数据源
   - 设计 WebSocket 通信协议
   - 处理异步任务流程

## 注意事项

1. **框架差异**：
   - CrewAI 专注于团队协作和任务管理
   - LangGraph 专注于工作流程编排
   - 需要根据各自特点设计接口

2. **数据流转**：
   - 前端统一使用 CrewAI 的数据模型
   - 参考 LangManus Web 的 UI 组件
   - 保持数据流的清晰和一致

3. **性能优化**：
   - 实现消息队列
   - 优化任务调度
   - 添加缓存层

## 后续规划

1. **功能完善**：
   - [ ] 实现完整的 Agent 管理系统
   - [ ] 添加任务监控和分析
   - [ ] 优化团队协作机制

2. **UI 优化**：
   - [ ] 实现自定义主题
   - [ ] 添加更多交互功能
   - [ ] 优化移动端适配

3. **部署优化**：
   - [ ] 配置自动扩展
   - [ ] 实现负载均衡
   - [ ] 完善监控系统