# GenFlow 后端实现指南

## 1. 概述

本指南面向后端开发者，详细说明如何实现 GenFlow 内容生产系统的服务端组件。GenFlow 系统通过FastAPI构建统一的API接口，调用CrewAI智能体团队执行内容创作任务，从选题到发布的全流程。

> **注意**：智能体(CrewAI)的详细实现请参考 [CrewAI开发指南](./crewai_develop_guide.md)，本文档专注于API服务和后端架构实现。

## 2. 技术栈

推荐的技术栈组合：

- **主要框架**：FastAPI
- **异步支持**：asyncio
- **智能体框架**：CrewAI (详细实现参考专门指南)
- **WebSocket**：Starlette
- **数据存储**：MongoDB/PostgreSQL
- **缓存**：Redis
- **队列**：Celery/RabbitMQ

## 3. 系统架构

### 3.1 核心组件

```
backend/
├── api/                      # API 层
│   ├── routers/              # 路由模块
│   │   ├── sessions.py       # 会话管理
│   │   ├── actions.py        # 动作执行
│   │   └── websocket.py      # WebSocket 处理
│   ├── models/               # API 数据模型
│   └── dependencies.py       # API 依赖项
├── core/                     # 核心业务逻辑
│   ├── agents/               # 智能体调用接口
│   │   ├── topic_manager.py  # 选题管理
│   │   ├── research_manager.py  # 研究管理
│   │   ├── writing_manager.py  # 写作管理
│   │   └── review_manager.py  # 审核管理
│   ├── session/              # 会话管理
│   └── services/             # 业务服务
├── db/                       # 数据访问层
│   ├── mongodb/              # MongoDB 实现
│   └── redis/                # Redis 实现
└── worker/                   # 后台任务
    ├── tasks.py              # 任务定义
    └── celery_app.py         # Celery 配置
```

### 3.2 数据流

1. 客户端请求创建会话
2. API 层接收请求并创建会话
3. 基于会话阶段调用相应的智能体管理器
4. 智能体管理器调用CrewAI组件执行任务，结果存储到数据库
5. 通过 WebSocket 实时向客户端推送更新
6. 客户端与服务端交互，推进工作流程

## 4. API 实现

### 4.1 会话管理

```python
# api/routers/sessions.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from ..models.session import SessionCreate, SessionResponse
from ...core.session.manager import SessionManager

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    session_data: SessionCreate, 
    session_manager: SessionManager = Depends()
):
    """创建新的会话"""
    try:
        session = await session_manager.create_session(
            article_id=session_data.articleId,
            initial_stage=session_data.initialStage,
            context=session_data.context
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str, 
    session_manager: SessionManager = Depends()
):
    """获取会话状态"""
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
```

### 4.2 WebSocket 实现

```python
# api/routers/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from starlette.websockets import WebSocketState
import json

from ...core.session.manager import SessionManager
from ...core.session.events import EventDispatcher

router = APIRouter()

@router.websocket("/sessions/{session_id}/realtime")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    session_manager: SessionManager = Depends(),
    event_dispatcher: EventDispatcher = Depends()
):
    await websocket.accept()
    
    # 认证
    try:
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)
        
        if auth_data.get("type") != "auth" or not auth_data.get("token"):
            await websocket.close(code=1008, reason="Authentication required")
            return
            
        token = auth_data["token"].replace("Bearer ", "")
        # 验证token...
    except Exception as e:
        await websocket.close(code=1011, reason=f"Authentication error: {str(e)}")
        return
        
    # 注册客户端
    client_id = f"client_{session_id}_{id(websocket)}"
    await event_dispatcher.register_client(session_id, client_id, websocket)
    
    try:
        # 处理客户端消息
        while websocket.client_state != WebSocketState.DISCONNECTED:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            # 处理各类客户端事件
            if data.get("type") == "request.suggestion":
                await session_manager.request_suggestion(session_id, data.get("data", {}))
            elif data.get("type") == "feedback":
                await session_manager.process_feedback(session_id, data.get("data", {}))
            # 处理其他事件类型...
            
    except WebSocketDisconnect:
        pass
    finally:
        await event_dispatcher.unregister_client(session_id, client_id)
```

## 5. 智能体管理器实现

> **注意**：智能体的详细实现请参考 [CrewAI开发指南](./crewai_develop_guide.md)，以下代码主要展示如何在后端系统中**调用**智能体，而非实现智能体本身。

```python
# core/agents/topic_manager.py
import logging
from typing import List, Dict, Optional
import uuid

# 导入CrewAI组件，具体实现参见CrewAI开发指南
from path.to.crewai.implementation import TopicCrew

logger = logging.getLogger("topic_manager")

class TopicManager:
    """选题管理器，负责调用选题智能体团队"""
    
    def __init__(self, config: Dict):
        self.config = config
        
    async def discover_topics(self, category: str, count: int = 5) -> List[Dict]:
        """发现热门话题"""
        logger.info(f"开始发现话题，类别：{category}，数量：{count}")
        
        # 创建任务ID用于跟踪
        task_id = str(uuid.uuid4())
        
        try:
            # 初始化选题团队
            topic_crew = TopicCrew(self.config)
            
            # 调用CrewAI执行话题发现
            # 这里不关心具体实现，只关心接口调用
            topics = await topic_crew.discover_topics(category, count)
            
            logger.info(f"话题发现完成，任务ID: {task_id}，共发现{len(topics)}个话题")
            return topics
            
        except Exception as e:
            logger.error(f"话题发现失败，任务ID: {task_id}, 错误: {str(e)}")
            raise
```

## 6. 会话管理实现

```python
# core/session/manager.py
from typing import Dict, Optional, List
import uuid
import logging
import asyncio
from datetime import datetime, timedelta

# 导入智能体管理器
from ..agents.topic_manager import TopicManager
from ..agents.research_manager import ResearchManager
from ..agents.writing_manager import WritingManager
from ..agents.review_manager import ReviewManager

from .events import EventDispatcher
from ...db.models import Session, Message

logger = logging.getLogger("session_manager")

class SessionManager:
    """会话管理器，负责会话生命周期和状态管理"""
    
    def __init__(
        self, 
        config: Dict,
        event_dispatcher: EventDispatcher,
        session_repo,
        message_repo
    ):
        self.config = config
        self.event_dispatcher = event_dispatcher
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.active_sessions = {}
        
        # 初始化智能体管理器
        self.topic_manager = TopicManager(config)
        self.research_manager = ResearchManager(config)
        self.writing_manager = WritingManager(config)
        self.review_manager = ReviewManager(config)
        
    async def create_session(
        self, 
        article_id: str, 
        initial_stage: str = "topic",
        context: Dict = None
    ) -> Dict:
        """创建新会话"""
        session_id = f"session_{uuid.uuid4().hex[:10]}"
        
        # 创建会话记录
        session = {
            "id": session_id,
            "articleId": article_id,
            "stage": initial_stage,
            "status": "idle",
            "progress": 0,
            "context": context or {},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "expiresAt": datetime.utcnow() + timedelta(hours=2)
        }
        
        # 保存到数据库
        await self.session_repo.create(session)
        
        # 获取可用操作
        available_actions = self._get_stage_actions(initial_stage)
        
        # 构造响应
        response = {
            "sessionId": session_id,
            "progress": {
                "stage": initial_stage,
                "status": "idle",
                "progress": 0
            },
            "availableActions": available_actions,
            "capabilities": self._get_capabilities(initial_stage)
        }
        
        return response
        
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话状态"""
        session = await self.session_repo.find_by_id(session_id)
        if not session:
            return None
            
        # 组装响应
        last_message = await self.message_repo.get_latest(session_id)
        
        return {
            "progress": {
                "stage": session["stage"],
                "status": session["status"],
                "progress": session["progress"],
                "estimatedTime": session.get("estimatedTime"),
                "currentStep": session.get("currentStep")
            },
            "availableActions": self._get_stage_actions(session["stage"], session["status"]),
            "lastMessage": last_message
        }
        
    async def execute_action(self, session_id: str, action: str, parameters: Dict = None) -> Dict:
        """执行会话动作"""
        session = await self.session_repo.find_by_id(session_id)
        if not session:
            raise ValueError("Session not found")
            
        # 更新会话状态
        await self.session_repo.update(
            session_id, 
            {"status": "processing", "updatedAt": datetime.utcnow()}
        )
        
        # 发送状态更新事件
        await self.event_dispatcher.dispatch_event(
            session_id, 
            "stage.change",
            {
                "stage": session["stage"],
                "status": "processing",
                "progress": session["progress"],
                "currentStep": f"开始执行动作: {action}"
            }
        )
        
        # 异步执行动作
        asyncio.create_task(
            self._process_action(session_id, session["stage"], action, parameters or {})
        )
        
        # 返回初始状态
        return {
            "actionId": f"action_{uuid.uuid4().hex[:8]}",
            "status": "processing",
            "progress": {
                "stage": session["stage"],
                "status": "processing",
                "progress": session["progress"],
                "currentStep": f"开始执行动作: {action}"
            }
        }
        
    async def _process_action(self, session_id: str, stage: str, action: str, parameters: Dict):
        """处理动作执行"""
        try:
            # 根据不同阶段和动作类型，调用相应的智能体管理器
            if stage == "topic" and action == "discover_topics":
                await self._run_topic_discovery(session_id, parameters)
            elif stage == "research" and action == "research_topic":
                await self._run_topic_research(session_id, parameters)
            # 其他动作类型处理...
            
        except Exception as e:
            logger.error(f"执行动作失败: {str(e)}")
            # 更新会话状态为错误
            await self.session_repo.update(
                session_id,
                {"status": "error", "errorMessage": str(e)}
            )
            # 发送错误事件
            await self.event_dispatcher.dispatch_event(
                session_id,
                "error",
                {"message": f"执行动作失败: {str(e)}"}
            )
            
    async def _run_topic_discovery(self, session_id: str, parameters: Dict):
        """执行话题发现"""
        session = await self.session_repo.find_by_id(session_id)
        
        # 更新进度
        await self._update_progress(session_id, 10, "正在分析热门趋势")
        
        try:
            # 调用智能体管理器执行话题发现
            topics = await self.topic_manager.discover_topics(
                parameters.get("category", "技术"),
                parameters.get("count", 5)
            )
            
            # 保存结果
            await self.session_repo.update(
                session_id,
                {
                    "topics": topics,
                    "status": "idle",
                    "progress": 100,
                    "currentStep": "话题发现完成"
                }
            )
            
            # 发送结果事件
            await self.event_dispatcher.dispatch_event(
                session_id,
                "topics.discovered",
                {"topics": topics}
            )
            
        except Exception as e:
            logger.error(f"话题发现失败: {str(e)}")
            raise
            
    # 其他内部方法实现...
            
    def _get_stage_actions(self, stage: str, status: str = "idle") -> List[Dict]:
        """获取当前阶段可用的操作按钮"""
        if status != "idle":
            return []  # 处理中不可执行新操作
            
        actions = {
            "topic": [
                {
                    "id": "discover_topics",
                    "text": "发现热门话题",
                    "action": "discover_topics",
                    "type": "primary"
                }
            ],
            "research": [
                {
                    "id": "start_research",
                    "text": "开始深入研究",
                    "action": "research_topic",
                    "type": "primary"
                }
            ],
            # 其他阶段操作...
        }
        
        return actions.get(stage, [])
        
    def _get_capabilities(self, stage: str) -> List[str]:
        """获取当前阶段的功能列表"""
        # 根据不同阶段返回不同的功能集
        capabilities = {
            "topic": ["suggestions"],
            "research": ["suggestions", "autoComplete"],
            "writing": ["suggestions", "autoComplete", "grammarCheck"],
            "styling": ["suggestions", "autoComplete", "grammarCheck"],
            "review": ["suggestions", "grammarCheck"]
        }
        
        return capabilities.get(stage, [])
        
    async def _update_progress(self, session_id: str, progress: int, current_step: str = None):
        """更新会话进度"""
        update_data = {
            "progress": progress,
            "updatedAt": datetime.utcnow()
        }
        
        if current_step:
            update_data["currentStep"] = current_step
            
        await self.session_repo.update(session_id, update_data)
        
        # 发送进度更新事件
        await self.event_dispatcher.dispatch_event(
            session_id,
            "progress.update",
            {
                "progress": progress,
                "currentStep": current_step
            }
        )
```

## 7. 事件分发系统

```python
# core/session/events.py
import logging
import json
import asyncio
from typing import Dict, Set, Optional
from fastapi import WebSocket

logger = logging.getLogger("event_dispatcher")

class EventDispatcher:
    """事件分发器，处理WebSocket实时通信"""
    
    def __init__(self):
        self.clients = {}  # session_id -> {client_id: websocket}
        
    async def register_client(self, session_id: str, client_id: str, websocket: WebSocket):
        """注册新客户端连接"""
        if session_id not in self.clients:
            self.clients[session_id] = {}
            
        self.clients[session_id][client_id] = websocket
        logger.info(f"客户端 {client_id} 已连接到会话 {session_id}")
        
    async def unregister_client(self, session_id: str, client_id: str):
        """注销客户端连接"""
        if session_id in self.clients and client_id in self.clients[session_id]:
            del self.clients[session_id][client_id]
            logger.info(f"客户端 {client_id} 已断开与会话 {session_id} 的连接")
            
            # 如果没有客户端，清理会话记录
            if not self.clients[session_id]:
                del self.clients[session_id]
                
    async def dispatch_event(self, session_id: str, event_type: str, data: Dict):
        """向会话的所有客户端分发事件"""
        if session_id not in self.clients:
            logger.warning(f"会话 {session_id} 没有连接的客户端")
            return
            
        event = {
            "type": event_type,
            "data": data,
            "metadata": {
                "timestamp": int(asyncio.get_event_loop().time() * 1000),
                "eventId": f"evt_{id(data)}",
                "sessionId": session_id
            }
        }
        
        message = json.dumps(event)
        disconnected_clients = []
        
        for client_id, websocket in self.clients[session_id].items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"向客户端 {client_id} 发送事件失败: {str(e)}")
                disconnected_clients.append(client_id)
                
        # 清理断开连接的客户端
        for client_id in disconnected_clients:
            await self.unregister_client(session_id, client_id)
```

## 8. 主应用实现

```python
# main.py
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.routers import sessions, actions, websocket
from core.session.manager import SessionManager
from core.session.events import EventDispatcher
from db.mongodb.repositories import SessionRepo, MessageRepo
from config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 创建FastAPI应用
app = FastAPI(
    title="GenFlow API",
    description="GenFlow 内容生产系统API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖注入
event_dispatcher = EventDispatcher()
session_repo = SessionRepo(settings.MONGODB_URL)
message_repo = MessageRepo(settings.MONGODB_URL)

def get_session_manager():
    return SessionManager(
        config=settings.dict(),
        event_dispatcher=event_dispatcher,
        session_repo=session_repo,
        message_repo=message_repo
    )

def get_event_dispatcher():
    return event_dispatcher

# 注册路由
app.include_router(sessions.router, prefix="/api/genflow")
app.include_router(actions.router, prefix="/api/genflow")
app.include_router(websocket.router, prefix="/api/genflow")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

## 9. 部署指南

### 9.1 Docker 部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017/genflow
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - mongo
      - redis
      
  worker:
    build: .
    command: celery -A worker.celery_app worker --loglevel=info
    environment:
      - MONGODB_URL=mongodb://mongo:27017/genflow
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - mongo
      - redis
      
  mongo:
    image: mongo:4.4
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"
      
  redis:
    image: redis:6
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
      
volumes:
  mongo_data:
  redis_data:
```

## 10. 测试与监控

### 10.1 单元测试示例

```python
# tests/test_session_manager.py
import pytest
from unittest.mock import AsyncMock, MagicMock
import asyncio

from core.session.manager import SessionManager

@pytest.fixture
def mock_event_dispatcher():
    dispatcher = AsyncMock()
    dispatcher.dispatch_event = AsyncMock()
    return dispatcher
    
@pytest.fixture
def mock_session_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.update = AsyncMock()
    return repo
    
@pytest.fixture
def mock_message_repo():
    repo = AsyncMock()
    repo.get_latest = AsyncMock(return_value=None)
    return repo
    
@pytest.fixture
def session_manager(mock_event_dispatcher, mock_session_repo, mock_message_repo):
    config = {"API_KEY": "test_key"}
    manager = SessionManager(
        config, 
        mock_event_dispatcher,
        mock_session_repo,
        mock_message_repo
    )
    # 模拟智能体管理器
    manager.topic_manager = AsyncMock()
    manager.topic_manager.discover_topics = AsyncMock(return_value=[])
    return manager

@pytest.mark.asyncio
async def test_create_session(session_manager, mock_session_repo):
    # 执行测试
    result = await session_manager.create_session("article_123", "topic")
    
    # 验证结果
    assert "sessionId" in result
    assert result["progress"]["stage"] == "topic"
    assert result["progress"]["status"] == "idle"
    
    # 验证调用
    mock_session_repo.create.assert_called_once()
```

## 11. 性能优化

1. **异步处理**：使用asyncio进行异步I/O操作
2. **任务队列**：将耗时任务放入Celery队列异步处理
3. **缓存机制**：使用Redis缓存会话状态和临时结果
4. **数据库优化**：为常用查询创建索引
5. **消息压缩**：对WebSocket消息进行压缩

## 12. 安全措施

1. **API认证**：使用JWT进行请求认证
2. **输入验证**：验证所有用户输入
3. **速率限制**：对API请求实施限流
4. **会话过期**：自动清理过期会话
5. **权限控制**：确保用户只能访问自己的数据

---

最后更新: 2024-05-15 