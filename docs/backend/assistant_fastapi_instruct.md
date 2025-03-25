# FastAPI 写作助手开发文档

## 1. 系统架构

### 1.1 模块划分

```
backend/
├── src/
│   ├── api/
│   │   └── ai_assistant/      # AI写作助手API模块
│   │       ├── models.py      # 数据模型
│   │       ├── deps.py        # 依赖注入
│   │       └── routes.py      # WebSocket和HTTP路由
│   └── services/
│       └── ai_writing/        # 写作服务层
│           └── manager.py     # 会话管理器
```

### 1.2 核心组件

1. **数据模型 (models.py)**
   - WritingStage: 写作阶段枚举
   - WritingProgress: 写作进度模型
   - MessageType: 消息类型枚举
   - Message: 消息模型
   - WebSocketEvent: WebSocket事件模型
   - SessionContext: 会话上下文
   - ActionButton: 动作按钮

2. **会话管理器 (manager.py)**
   - WritingSession: 写作会话类
   - WritingSessionManager: 会话管理器类

3. **路由处理 (routes.py)**
   - WebSocket 连接管理
   - HTTP API 接口
   - 事件处理

## 2. WebSocket 通信协议

### 2.1 连接建立
```
WebSocket URL: ws://host:port/api/ai-assistant/sessions/{session_id}/realtime
Headers:
  Authorization: Bearer <token>
```

### 2.2 事件类型

1. **客户端事件**
```json
{
    "type": "event_type",
    "data": {
        // 事件相关数据
    },
    "timestamp": "ISO时间戳"
}
```

支持的事件类型：
- `generate_outline`: 生成文章大纲
- `generate_content`: 生成章节内容
- `optimize_content`: 优化内容
- `analyze_content`: 分析内容
- `get_suggestions`: 获取写作建议

2. **服务器响应**
```json
{
    "type": "message",
    "data": {
        "id": "消息ID",
        "role": "ai",
        "content": "内容",
        "type": "消息类型",
        "timestamp": "时间戳"
    },
    "timestamp": "ISO时间戳"
}
```

## 3. HTTP API 接口

### 3.1 创建会话
```
POST /api/ai-assistant/sessions

请求体：
{
    "article_id": "可选的文章ID",
    "initial_stage": "写作阶段",
    "context": {
        "title": "文章标题",
        "content": "现有内容",
        "tags": ["标签"],
        "target_length": 1000
    }
}

响应：
{
    "data": {
        "session_id": "会话ID",
        "progress": {
            "stage": "写作阶段",
            "status": "状态",
            "progress": 0
        },
        "available_actions": [
            {
                "id": "动作ID",
                "text": "显示文本",
                "action": "动作类型",
                "type": "按钮类型"
            }
        ]
    }
}
```

### 3.2 获取会话状态
```
GET /api/ai-assistant/sessions/{session_id}

响应：
{
    "data": {
        "progress": {
            "stage": "写作阶段",
            "status": "状态",
            "progress": 45
        },
        "available_actions": []
    }
}
```

### 3.3 获取消息历史
```
GET /api/ai-assistant/sessions/{session_id}/messages

响应：
{
    "data": [
        {
            "id": "消息ID",
            "role": "发送者角色",
            "content": "消息内容",
            "type": "消息类型",
            "timestamp": "时间戳"
        }
    ]
}
```

## 4. Core 模块接口需求

Core 模块需要实现以下接口以支持 FastAPI 服务：

### 4.1 WritingSession 类
```python
class WritingSession:
    async def generate_outline(self) -> Dict:
        """生成文章大纲"""
        pass

    async def generate_section_content(self, section_id: str) -> Dict:
        """生成章节内容"""
        pass

    async def optimize_content(self, content: str) -> Dict:
        """优化内容"""
        pass

    async def analyze_content(self, content: str) -> Dict:
        """分析内容"""
        pass

    async def get_suggestions(self, content: str) -> List[Dict]:
        """获取写作建议"""
        pass

    async def cleanup(self):
        """清理资源"""
        pass
```

### 4.2 返回数据格式

1. **大纲生成**
```python
{
    "outline": {
        "title": str,
        "sections": List[Dict],
        "keywords": List[str]
    }
}
```

2. **内容生成**
```python
{
    "content": str,
    "metadata": {
        "section_id": str,
        "word_count": int,
        "keywords": List[str]
    }
}
```

3. **内容优化**
```python
{
    "optimized_content": str,
    "changes": List[Dict],
    "improvement_summary": str
}
```

4. **内容分析**
```python
{
    "analysis": {
        "readability_score": float,
        "keyword_density": Dict[str, float],
        "sentiment": str,
        "suggestions": List[str]
    }
}
```

5. **写作建议**
```python
[
    {
        "type": str,  # style | content | structure
        "content": str,
        "position": Optional[Dict],
        "priority": str  # high | medium | low
    }
]
```

## 5. 错误处理

### 5.1 WebSocket 错误
```json
{
    "type": "error",
    "data": {
        "message": "错误信息",
        "code": "错误代码"
    },
    "timestamp": "ISO时间戳"
}
```

### 5.2 HTTP 错误
```json
{
    "error": {
        "code": "错误代码",
        "message": "错误信息",
        "details": {}
    },
    "metadata": {
        "timestamp": "ISO时间戳",
        "request_id": "请求ID"
    }
}
```

## 6. 安全性考虑

1. **认证和授权**
   - 所有请求需要有效的 JWT 令牌
   - WebSocket 连接需要在 headers 中包含认证信息
   - 用户只能访问自己的会话

2. **资源限制**
   - 单个用户的最大会话数
   - WebSocket 连接超时设置
   - 消息大小限制

3. **数据验证**
   - 输入内容过滤
   - 消息格式验证
   - 会话状态验证

## 7. 测试计划

1. **单元测试**
   - 数据模型验证
   - 会话管理逻辑
   - 事件处理逻辑

2. **集成测试**
   - WebSocket 连接测试
   - HTTP API 测试
   - Core 模块集成测试

3. **负载测试**
   - 并发连接处理
   - 消息处理性能
   - 资源使用监控
