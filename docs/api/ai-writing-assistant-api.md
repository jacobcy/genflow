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

# AI 写作助手 API

## 1. 概述

GenFlow AI 写作助手提供了智能写作辅助功能，包括写作建议、内容生成、文章分析等功能。本文档描述了 AI 写作助手的 API 接口规范。

## 2. 基础信息

- 基础路径：`/api/ai-assistant`
- 所有请求需要包含标准请求头
- 所有响应遵循统一的响应格式
- WebSocket 基础路径：`ws://api/ai-assistant`

### 2.1 标准请求头
```http
Content-Type: application/json
Accept: application/json
X-Request-ID: <uuid>
X-Client-Version: <version>
Authorization: Bearer <token>
```

## 3. 数据结构

### 3.1 消息结构
```typescript
interface Message {
  id: string;
  role: 'ai' | 'user' | 'system';
  content: string;
  type: 'text' | 'markdown' | 'suggestion' | 'outline' | 'analysis';
  timestamp: string;
  metadata?: {
    stage?: WritingStage;
    confidence?: number;
    references?: string[];
    [key: string]: any;
  };
}
```

### 3.2 写作阶段
```typescript
type WritingStage = 'topic' | 'writing' | 'optimization' | 'review';

interface WritingProgress {
  stage: WritingStage;
  status: 'idle' | 'processing' | 'waiting';
  progress: number;
  estimatedTime?: number;
  currentStep?: string;
}
```

### 3.3 动作按钮
```typescript
interface ActionButton {
  id: string;
  text: string;
  action: string;
  type: 'primary' | 'secondary' | 'warning';
  disabled?: boolean;
  tooltip?: string;
  metadata?: {
    stage: WritingStage;
    priority: number;
    requiresConfirmation?: boolean;
    [key: string]: any;
  };
}
```

## 4. API 端点

### 4.1 创建会话

#### 请求
- 方法：`POST`
- 路径：`/api/ai-assistant/sessions`
- 需要认证：是
- 内容类型：`application/json`

```json
{
  "articleId": "article_123",
  "initialStage": "topic",
  "context": {
    "title": "文章标题",
    "content": "现有内容",
    "tags": ["AI", "写作"],
    "targetLength": 1000
  }
}
```

#### 成功响应
- 状态码：`201 Created`
```json
{
  "data": {
    "sessionId": "session_123",
    "progress": {
      "stage": "topic",
      "status": "idle",
      "progress": 0
    },
    "availableActions": [
      {
        "id": "generate_outline",
        "text": "生成大纲",
        "action": "generate_outline",
        "type": "primary"
      }
    ]
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

### 4.2 获取会话状态

#### 请求
- 方法：`GET`
- 路径：`/api/ai-assistant/sessions/{sessionId}`
- 需要认证：是

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "progress": {
      "stage": "writing",
      "status": "processing",
      "progress": 45,
      "estimatedTime": 120,
      "currentStep": "正在生成第二段落"
    },
    "availableActions": [],
    "lastMessage": {
      "id": "msg_123",
      "role": "ai",
      "content": "我正在帮你写作...",
      "type": "text",
      "timestamp": "2024-03-24T10:30:00Z"
    }
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

### 4.3 发送消息

#### 请求
- 方法：`POST`
- 路径：`/api/ai-assistant/sessions/{sessionId}/messages`
- 需要认证：是
- 内容类型：`application/json`

```json
{
  "content": "帮我优化这段内容",
  "type": "text",
  "metadata": {
    "selection": {
      "start": 0,
      "end": 100
    }
  }
}
```

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "message": {
      "id": "msg_124",
      "role": "ai",
      "content": "好的，我来帮你优化这段内容...",
      "type": "text",
      "timestamp": "2024-03-24T10:31:00Z"
    },
    "progress": {
      "stage": "optimization",
      "status": "processing",
      "progress": 0
    },
    "availableActions": []
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

### 4.4 获取写作建议

#### 请求
- 方法：`GET`
- 路径：`/api/ai-assistant/sessions/{sessionId}/suggestions`
- 需要认证：是
- 查询参数：
  - `type`: 建议类型（seo/readability/structure/all）
  - `section`: 文章段落（可选）

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "suggestions": [
      {
        "id": "sug_123",
        "type": "readability",
        "content": "这段话可以拆分成更短的句子，提高可读性",
        "priority": "high",
        "position": {
          "start": 100,
          "end": 200
        }
      }
    ]
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

## 5. WebSocket 事件

### 5.1 连接
```typescript
// 连接地址
ws://api/ai-assistant/sessions/{sessionId}/realtime

// 认证
{
  "type": "auth",
  "token": "Bearer <token>"
}
```

### 5.2 事件类型
```typescript
// 助手事件类型
type AssistantEventType =
  | 'suggestion.new'      // 新的写作建议
  | 'suggestion.update'   // 建议更新
  | 'analysis.progress'   // 分析进度
  | 'outline.generated'   // 大纲生成
  | 'review.complete'     // 审阅完成
  | 'stage.change'       // 写作阶段变更
  | 'error';             // 错误信息

// 事件结构
interface AssistantEvent {
  type: AssistantEventType;
  data: {
    id?: string;
    content?: string;
    stage?: WritingStage;
    progress?: number;
    suggestions?: Array<{
      id: string;
      type: 'style' | 'content' | 'structure';
      content: string;
      priority: 'high' | 'medium' | 'low';
    }>;
    analysis?: {
      type: string;
      results: any;
    };
  };
  metadata: {
    timestamp: number;
    eventId: string;
    articleId: string;
  };
}
```

### 5.3 示例事件
```json
// 新的写作建议
{
  "type": "suggestion.new",
  "data": {
    "id": "sug_123",
    "type": "content",
    "content": "建议在这里添加一个过渡段落，使文章更流畅",
    "priority": "high"
  },
  "metadata": {
    "timestamp": 1647834567890,
    "eventId": "evt_123abc",
    "articleId": "article_123"
  }
}

// 写作阶段变更
{
  "type": "stage.change",
  "data": {
    "stage": "optimization",
    "progress": 75,
    "currentStep": "正在优化文章结构"
  },
  "metadata": {
    "timestamp": 1647834567890,
    "eventId": "evt_456def",
    "articleId": "article_123"
  }
}
```

### 5.4 客户端事件
```typescript
// 客户端可以发送的事件
type ClientEventType =
  | 'request.suggestion'    // 请求写作建议
  | 'request.analysis'      // 请求内容分析
  | 'request.outline'       // 请求生成大纲
  | 'feedback'             // 提供反馈
  | 'stage.select';        // 选择写作阶段

interface ClientEvent {
  type: ClientEventType;
  data: {
    context?: {
      selection?: {
        start: number;
        end: number;
      };
      content?: string;
    };
    stage?: WritingStage;
    feedback?: {
      suggestionId: string;
      helpful: boolean;
      comment?: string;
    };
  };
}
```

## 6. 错误代码

| 错误代码 | HTTP 状态码 | 描述 |
|----------|------------|------|
| AI_001 | 502 | AI 服务错误 |
| AI_002 | 504 | AI 服务超时 |
| AI_003 | 502 | AI 响应无效 |
| AI_004 | 422 | 内容被过滤 |
| AUTH_001 | 401 | 未认证 |
| AUTH_004 | 403 | 权限不足 |
| AUTH_005 | 401 | 会话已过期 |
| REQ_001 | 400 | 无效的请求格式 |
| REQ_004 | 429 | 请求频率超限 |

## 7. 安全措施

### 7.1 访问控制
- 所有请求必须包含有效的认证令牌
- WebSocket 连接需要进行认证
- 用户只能访问自己的会话

### 7.2 会话安全
- 会话有效期：2小时
- 最大空闲时间：30分钟
- 支持会话续期

### 7.3 速率限制
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1616789000
```

### 7.4 内容安全
- 输入内容过滤
- 敏感信息检测
- AI 响应审核

## 8. 性能优化

### 8.1 响应流式处理
- 支持 WebSocket 流式响应
- 大型内容分段传输
- 进度实时更新

### 8.2 缓存策略
- 写作建议缓存：5分钟
- 分析结果缓存：10分钟
- 会话状态缓存：实时

---

最后更新: 2024-03-24
