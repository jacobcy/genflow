# GenFlow 内容生产系统 API 规范

## 1. 基础信息

- API 基础路径：`/api/genflow`
- WebSocket 基础路径：`ws://api/genflow`
- 所有请求需要包含标准请求头
- 所有响应遵循统一的响应格式

### 1.1 标准请求头
```http
Content-Type: application/json
Accept: application/json
X-Request-ID: <uuid>
X-Client-Version: <version>
Authorization: Bearer <token>
```

## 2. 核心概念与术语

### 2.1 会话（Session）
内容生产系统中，用户与系统交互的上下文环境，包含状态信息和历史记录。

### 2.2 写作阶段（Writing Stage）
内容生产流程分为五个核心阶段：
1. **选题阶段** (Topic Discovery)
2. **研究阶段** (Research) - 可选
3. **写作阶段** (Writing)
4. **风格化阶段** (Styling)
5. **审核阶段** (Review)

### 2.3 建议（Suggestion）
系统为用户提供的写作辅助内容，包括自动补全、内容建议、优化建议等。

### 2.4 智能体团队（Agent Crew）
执行特定写作任务的智能体集合，如选题团队、写作团队等。

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

### 3.2 写作阶段与进度
```typescript
type WritingStage = 'topic' | 'research' | 'writing' | 'styling' | 'review';

interface WritingProgress {
  stage: WritingStage;
  status: 'idle' | 'processing' | 'waiting';
  progress: number;  // 0-100
  estimatedTime?: number;  // 预估剩余时间(秒)
  currentStep?: string;  // 当前步骤描述
}
```

### 3.3 动作与交互
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

### 3.4 编辑操作
```typescript
interface EditOperation {
  type: 'insert' | 'delete' | 'replace' | 'format';
  position?: {
    start: number;
    end: number;
  };
  content?: string;
  format?: {
    type: 'bold' | 'italic' | 'heading' | string;
    value?: any;
  };
}
```

## 4. 会话管理 API

### 4.1 创建会话

#### 请求
- 方法：`POST`
- 路径：`/api/genflow/sessions`
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
    "targetLength": 1000,
    "platform": "medium" // 目标平台
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
        "id": "discover_topics",
        "text": "发现热门话题",
        "action": "discover_topics",
        "type": "primary"
      }
    ],
    "capabilities": [
      "suggestions",
      "autoComplete",
      "grammarCheck"
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
- 路径：`/api/genflow/sessions/{sessionId}`
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

## 5. 内容生产 API

### 5.1 发送消息

#### 请求
- 方法：`POST`
- 路径：`/api/genflow/sessions/{sessionId}/messages`
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
    }
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

### 5.2 获取写作建议

#### 请求
- 方法：`GET`
- 路径：`/api/genflow/sessions/{sessionId}/suggestions`
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

### 5.3 实时建议请求

#### 请求
- 方法：`POST`
- 路径：`/api/genflow/sessions/{sessionId}/realtime-suggestions`
- 需要认证：是
- 内容类型：`application/json`

```json
{
  "content": "当前编辑的内容",
  "selection": {
    "start": 0,
    "end": 100
  },
  "context": {
    "before": "前文内容",
    "after": "后文内容"
  }
}
```

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "suggestions": [
      {
        "type": "completion",
        "content": "建议的补全内容",
        "confidence": 0.95,
        "metadata": {
          "source": "gpt-4",
          "tokens": 150
        }
      }
    ]
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc",
    "processingTime": 234
  }
}
```

### 5.4 应用编辑操作

#### 请求
- 方法：`POST`
- 路径：`/api/genflow/articles/{articleId}/apply`
- 需要认证：是
- 内容类型：`application/json`

```json
{
  "operations": [
    {
      "type": "replace",
      "position": {
        "start": 100,
        "end": 200
      },
      "content": "新内容"
    }
  ],
  "sessionId": "session_123"
}
```

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "applied": true,
    "version": "v2",
    "changes": [
      {
        "type": "replace",
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

## 6. 阶段流转 API

### 6.1 切换写作阶段

#### 请求
- 方法：`POST`
- 路径：`/api/genflow/sessions/{sessionId}/stage`
- 需要认证：是
- 内容类型：`application/json`

```json
{
  "stage": "research",
  "data": {
    "selectedTopicId": "topic_123"
  }
}
```

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "progress": {
      "stage": "research",
      "status": "processing",
      "progress": 0,
      "estimatedTime": 180,
      "currentStep": "开始主题研究"
    },
    "availableActions": [
      {
        "id": "pause_research",
        "text": "暂停研究",
        "action": "pause_research",
        "type": "secondary"
      }
    ]
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

### 6.2 执行阶段操作

#### 请求
- 方法：`POST`
- 路径：`/api/genflow/sessions/{sessionId}/actions`
- 需要认证：是
- 内容类型：`application/json`

```json
{
  "action": "discover_topics",
  "parameters": {
    "category": "技术",
    "count": 5
  }
}
```

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "actionId": "action_123",
    "status": "processing",
    "progress": {
      "stage": "topic",
      "status": "processing",
      "progress": 10,
      "currentStep": "正在分析热门趋势"
    }
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

## 7. WebSocket 实时通信

### 7.1 连接
```typescript
// 连接地址
ws://api/genflow/sessions/{sessionId}/realtime

// 认证
{
  "type": "auth",
  "token": "Bearer <token>"
}
```

### 7.2 助手事件类型
```typescript
// 事件类型
type AssistantEventType =
  | 'suggestion.new'      // 新的写作建议
  | 'suggestion.update'   // 建议更新
  | 'analysis.progress'   // 分析进度
  | 'outline.generated'   // 大纲生成
  | 'review.complete'     // 审阅完成
  | 'stage.change'        // 写作阶段变更
  | 'edit.insert'         // 插入内容
  | 'edit.delete'         // 删除内容
  | 'edit.replace'        // 替换内容
  | 'edit.format'         // 格式化
  | 'completion.suggest'  // 自动补全建议
  | 'error';              // 错误信息
```

### 7.3 示例事件
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
    "stage": "styling",
    "progress": 75,
    "currentStep": "正在优化文章风格"
  },
  "metadata": {
    "timestamp": 1647834567890,
    "eventId": "evt_456def",
    "articleId": "article_123"
  }
}

// 编辑操作
{
  "type": "edit.replace",
  "data": {
    "position": {
      "start": 100,
      "end": 150
    },
    "content": "新的内容",
    "version": "v1.2"
  },
  "metadata": {
    "timestamp": 1647834567890,
    "eventId": "evt_789ghi",
    "articleId": "article_123",
    "userId": "user_123"
  }
}
```

### 7.4 客户端事件类型
```typescript
// 客户端可以发送的事件
type ClientEventType =
  | 'request.suggestion'    // 请求写作建议
  | 'request.analysis'      // 请求内容分析
  | 'request.outline'       // 请求生成大纲
  | 'feedback'              // 提供反馈
  | 'stage.select'          // 选择写作阶段
  | 'edit.apply'            // 应用编辑
  | 'edit.undo'             // 撤销编辑
  | 'edit.redo'             // 重做编辑
  | 'cursor.update'         // 更新光标
  | 'selection.update'      // 更新选区
  | 'completion.accept';    // 接受补全
```

## 8. 错误代码

| 错误代码 | HTTP 状态码 | 描述 |
|----------|------------|------|
| AI_001 | 502 | AI 服务错误 |
| AI_002 | 504 | AI 服务超时 |
| AI_003 | 502 | AI 响应无效 |
| AI_004 | 422 | 内容被过滤 |
| EDIT_001 | 409 | 编辑同步错误 |
| EDIT_002 | 409 | 版本冲突 |
| EDIT_003 | 400 | 无效的操作 |
| AUTH_001 | 401 | 未认证 |
| AUTH_004 | 403 | 权限不足 |
| AUTH_005 | 401 | 会话已过期 |
| REQ_001 | 400 | 无效的请求格式 |
| REQ_004 | 429 | 请求频率超限 |

## 9. 安全与性能

### 9.1 安全措施
- 所有请求必须包含有效的认证令牌
- WebSocket 连接需要进行认证
- 用户只能访问自己的会话和文章
- 会话有效期：2小时，最大空闲时间：30分钟
- 输入内容过滤，敏感信息检测

### 9.2 速率限制
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1616789000
```

### 9.3 性能优化
- WebSocket 流式响应
- 大型内容分段传输
- 进度实时更新
- 增量更新和批量处理
- 缓存策略：
  - 写作建议缓存：5分钟
  - 分析结果缓存：10分钟
  - 会话状态缓存：实时

## 10. API 版本控制

API 遵循语义化版本控制：
- 主版本号：不兼容的 API 更改
- 次版本号：向后兼容的功能性变更
- 修订号：向后兼容的问题修复

当前版本：`v1.0.0`

---

最后更新: 2024-05-15
