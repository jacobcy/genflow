# GenFlow AI 写作工具 API

## 1. 概述

GenFlow AI 写作工具提供了实时的写作辅助功能，包括智能建议、自动补全、语法检查等功能。本文档描述了 AI 写作工具的 API 接口规范。

## 2. 基础信息

- 基础路径：`/api/ai-tool`
- 所有请求需要包含标准请求头
- 所有响应遵循统一的响应格式
- WebSocket 基础路径：`ws://api/ai-tool`

### 2.1 标准请求头
```http
Content-Type: application/json
Accept: application/json
X-Request-ID: <uuid>
X-Client-Version: <version>
Authorization: Bearer <token>
```

## 3. API 端点

### 3.1 创建编辑会话

#### 请求
- 方法：`POST`
- 路径：`/api/ai-tool/sessions`
- 需要认证：是
- 内容类型：`application/json`

```json
{
  "userId": "user_123",
  "articleId": "article_123",
  "context": {
    "title": "文章标题",
    "content": "现有内容",
    "keywords": ["AI", "写作"]
  }
}
```

#### 成功响应
- 状态码：`201 Created`
```json
{
  "data": {
    "sessionId": "session_123",
    "status": "active",
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

### 3.2 获取实时建议

#### 请求
- 方法：`POST`
- 路径：`/api/ai-tool/sessions/{sessionId}/suggestions`
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

### 3.3 应用建议

#### 请求
- 方法：`POST`
- 路径：`/api/ai-tool/articles/{articleId}/apply`
- 需要认证：是
- 内容类型：`application/json`

```json
{
  "functions": [
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

## 4. WebSocket 事件

### 4.1 连接
```typescript
// 连接地址
ws://api/ai-tool/sessions/{sessionId}/realtime

// 认证
{
  "type": "auth",
  "token": "Bearer <token>"
}
```

### 4.2 事件类型
```typescript
// 编辑器事件类型
type EditorEventType =
  | 'edit.insert'        // 插入内容
  | 'edit.delete'        // 删除内容
  | 'edit.replace'       // 替换内容
  | 'edit.format'        // 格式化
  | 'cursor.move'        // 光标移动
  | 'selection.change'   // 选区变化
  | 'completion.suggest' // 自动补全建议
  | 'sync.state'        // 同步状态
  | 'error';            // 错误信息

// 事件结构
interface EditorEvent {
  type: EditorEventType;
  data: {
    id?: string;
    position?: {
      start: number;
      end: number;
    };
    content?: string;
    format?: {
      type: 'bold' | 'italic' | 'heading' | string;
      value?: any;
    };
    version?: string;
    completions?: Array<{
      id: string;
      content: string;
      confidence: number;
    }>;
  };
  metadata: {
    timestamp: number;
    eventId: string;
    articleId: string;
    userId: string;
  };
}
```

### 4.3 示例事件
```json
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
    "eventId": "evt_123abc",
    "articleId": "article_123",
    "userId": "user_123"
  }
}

// 自动补全建议
{
  "type": "completion.suggest",
  "data": {
    "completions": [
      {
        "id": "comp_123",
        "content": "建议的补全内容",
        "confidence": 0.95
      }
    ],
    "position": {
      "start": 150,
      "end": 150
    }
  },
  "metadata": {
    "timestamp": 1647834567890,
    "eventId": "evt_456def",
    "articleId": "article_123",
    "userId": "user_123"
  }
}
```

### 4.4 客户端事件
```typescript
// 客户端可以发送的事件
type ClientEditorEventType =
  | 'edit.apply'         // 应用编辑
  | 'edit.undo'          // 撤销编辑
  | 'edit.redo'          // 重做编辑
  | 'cursor.update'      // 更新光标
  | 'selection.update'   // 更新选区
  | 'completion.accept'; // 接受补全

interface ClientEditorEvent {
  type: ClientEditorEventType;
  data: {
    position?: {
      start: number;
      end: number;
    };
    content?: string;
    completionId?: string;
    version?: string;
  };
}
```

## 5. 错误代码

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
| REQ_004 | 429 | 请求频率超限 |

## 6. 安全措施

### 6.1 访问控制
- 所有请求必须包含有效的认证令牌
- WebSocket 连接需要进行认证
- 用户只能访问自己的会话和文章

### 6.2 编辑安全
- 操作审计日志
- 版本控制
- 冲突检测

### 6.3 速率限制
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1616789000
```

### 6.4 内容安全
- 输入验证
- XSS 防护
- 敏感信息过滤

## 7. 性能优化

### 7.1 响应优化
- WebSocket 实时推送
- 增量更新
- 批量处理

### 7.2 缓存策略
```typescript
interface CacheConfig {
  suggestions: {
    ttl: 300,  // 5分钟
    scope: 'user'
  },
  grammar: {
    ttl: 3600,  // 1小时
    scope: 'global'
  }
}
```

## 8. 监控指标

### 8.1 性能指标
- 响应时间
- AI 处理时间
- WebSocket 延迟
- 建议采纳率

### 8.2 质量指标
- 建议准确率
- 用户满意度
- 错误率
- 会话活跃度

---

最后更新: 2024-03-24 