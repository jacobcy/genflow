# GenFlow 状态管理规范

## 1. 核心状态模型

### 1.1 文章状态
```typescript
interface ArticleState {
  id: string;
  title: string;
  content: string;
  version: string;
  metadata: {
    wordCount: number;
    lastModified: string;
    author: string;
    status: 'draft' | 'published';
  };
  cursor?: {
    start: number;
    end: number;
  };
  selection?: {
    start: number;
    end: number;
    content: string;
  };
}
```

### 1.2 AI 助手状态
```typescript
interface AIAssistantState {
  sessionId: string;
  stage: WritingStage;
  status: 'idle' | 'processing' | 'waiting';
  progress: number;
  suggestions: Array<{
    id: string;
    type: 'style' | 'content' | 'structure';
    content: string;
    priority: 'high' | 'medium' | 'low';
    applied: boolean;
  }>;
  history: Array<Message>;
}
```

### 1.3 编辑器状态
```typescript
interface EditorState {
  sessionId: string;
  version: string;
  isDirty: boolean;
  history: {
    undo: Array<EditorOperation>;
    redo: Array<EditorOperation>;
  };
  format: {
    bold: boolean;
    italic: boolean;
    heading: number | null;
  };
  completions: Array<{
    id: string;
    content: string;
    position: { start: number; end: number };
  }>;
}
```

## 2. 状态管理架构

### 2.1 状态层级
```
RootState
├── article        // 文章核心数据
├── editor         // 编辑器状态
├── assistant      // AI 助手状态
├── ui             // UI 相关状态
└── session        // 用户会话状态
```

### 2.2 状态更新流程
```typescript
// 1. 操作分发
interface Action {
  type: string;
  payload: any;
  metadata: {
    timestamp: number;
    source: 'user' | 'ai' | 'system';
    sessionId: string;
  };
}

// 2. 状态变更订阅
interface StateSubscription {
  path: string[];           // 状态路径
  callback: (state) => void;// 回调函数
  options: {
    debounce?: number;     // 防抖时间
    throttle?: number;     // 节流时间
  };
}
```

## 3. 数据流转路径

### 3.1 编辑器操作流
```
用户输入 -> 编辑器状态更新 -> 内容验证 ->
本地状态更新 -> WebSocket 同步 -> 服务端确认 ->
状态确认更新 -> UI 更新
```

### 3.2 AI 助手交互流
```
用户请求 -> AI 会话状态更新 -> 发送 WebSocket 消息 ->
接收 AI 响应 -> 更新建议状态 -> 通知编辑器 ->
等待用户确认 -> 应用更改
```

### 3.3 文章保存流
```
触发保存 -> 收集编辑器状态 -> 验证变更 ->
调用保存 API -> 更新文章版本 -> 重置编辑器脏状态 ->
更新 UI 状态
```

## 4. 状态同步机制

### 4.1 实时同步
```typescript
interface SyncMessage {
  type: 'sync' | 'ack' | 'error';
  version: string;
  changes: Array<{
    type: 'insert' | 'delete' | 'replace';
    position: { start: number; end: number };
    content?: string;
  }>;
  timestamp: number;
}
```

### 4.2 冲突处理
```typescript
interface ConflictResolution {
  strategy: 'client-wins' | 'server-wins' | 'manual-merge';
  resolution?: {
    accepted: Array<Change>;
    rejected: Array<Change>;
  };
  version: {
    client: string;
    server: string;
    resolved: string;
  };
}
```

## 5. 性能优化

### 5.1 状态分片
- 按功能模块分片
- 延迟加载非关键状态
- 独立的更新周期

### 5.2 更新优化
```typescript
interface UpdateStrategy {
  batchUpdates: boolean;     // 批量更新
  debounceTime: number;      // 防抖时间
  throttleTime: number;      // 节流时间
  priority: 'high' | 'low';  // 更新优先级
}
```

## 6. 状态持久化

### 6.1 本地存储
```typescript
interface StorageConfig {
  key: string;
  version: string;
  expires: number;
  encrypt: boolean;
  compress: boolean;
}
```

### 6.2 恢复策略
```typescript
interface RecoveryStrategy {
  priority: Array<'local' | 'server' | 'backup'>;
  validation: (state: any) => boolean;
  merge: (local: any, server: any) => any;
}
```

## 7. 调试与监控

### 7.1 状态快照
```typescript
interface StateSnapshot {
  timestamp: number;
  version: string;
  state: Partial<RootState>;
  actions: Array<Action>;
}
```

### 7.2 性能指标
```typescript
interface StateMetrics {
  updateFrequency: number;  // 更新频率
  stateSize: number;       // 状态大小
  syncLatency: number;     // 同步延迟
  conflictRate: number;    // 冲突率
}
```

---

最后更新: 2024-03-24
