# GenFlow 前端集成指南

## 1. 简介

本指南面向前端开发者，详细说明如何将 GenFlow 内容生产系统集成到前端应用中。GenFlow 提供了一套完整的 API，用于实现从选题到发布的全流程内容创作体验。

## 2. 技术栈要求

- React 16.8+ (推荐使用 React 18)
- TypeScript 4.5+
- WebSocket 支持
- 现代浏览器 API 支持

## 3. 集成步骤

### 3.1 安装依赖

```bash
npm install @genflow/react-client
# 或使用 yarn
yarn add @genflow/react-client
```

### 3.2 初始化 GenFlow 客户端

```tsx
// src/services/genflow.ts
import { GenFlowClient } from '@genflow/react-client';

// 初始化客户端
export const genflowClient = new GenFlowClient({
  apiBaseUrl: process.env.REACT_APP_GENFLOW_API_URL || '/api/genflow',
  wsBaseUrl: process.env.REACT_APP_GENFLOW_WS_URL || 'ws://api/genflow',
  onAuthError: () => {
    // 处理认证错误，例如重定向到登录页
    window.location.href = '/login';
  }
});

// 设置认证令牌
export const setAuthToken = (token: string) => {
  genflowClient.setToken(token);
};
```

### 3.3 创建写作会话上下文

```tsx
// src/contexts/WritingSessionContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { genflowClient } from '../services/genflow';
import type { Session, WritingProgress, Message, ActionButton } from '@genflow/react-client';

interface WritingSessionContextType {
  session: Session | null;
  progress: WritingProgress | null;
  messages: Message[];
  availableActions: ActionButton[];
  isConnected: boolean;
  sendMessage: (content: string, type?: string, metadata?: any) => Promise<void>;
  executeAction: (actionId: string, parameters?: any) => Promise<void>;
  switchStage: (stage: string, data?: any) => Promise<void>;
}

const WritingSessionContext = createContext<WritingSessionContextType | undefined>(undefined);

export const WritingSessionProvider: React.FC = ({ children, articleId }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [progress, setProgress] = useState<WritingProgress | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [availableActions, setAvailableActions] = useState<ActionButton[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  
  // 初始化会话
  useEffect(() => {
    if (!articleId) return;
    
    const initSession = async () => {
      try {
        const newSession = await genflowClient.createSession({
          articleId,
          initialStage: 'topic',
          context: {
            // 初始化上下文
          }
        });
        
        setSession(newSession);
        setProgress(newSession.progress);
        setAvailableActions(newSession.availableActions);
      } catch (error) {
        console.error('Failed to initialize session:', error);
      }
    };
    
    initSession();
  }, [articleId]);
  
  // 建立 WebSocket 连接
  useEffect(() => {
    if (!session?.sessionId) return;
    
    const wsConnection = genflowClient.connectWebSocket(session.sessionId, {
      onOpen: () => setIsConnected(true),
      onClose: () => setIsConnected(false),
      onError: (error) => console.error('WebSocket error:', error),
      onEvent: (event) => {
        switch (event.type) {
          case 'suggestion.new':
            // 处理新建议
            break;
          case 'stage.change':
            setProgress(event.data);
            break;
          // 处理其他事件类型
        }
      }
    });
    
    return () => {
      wsConnection.close();
    };
  }, [session?.sessionId]);
  
  // 发送消息
  const sendMessage = async (content: string, type = 'text', metadata = {}) => {
    if (!session?.sessionId) return;
    
    try {
      const response = await genflowClient.sendMessage(session.sessionId, {
        content,
        type,
        metadata
      });
      
      setMessages(prev => [...prev, response.message]);
      setProgress(response.progress);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };
  
  // 执行动作
  const executeAction = async (actionId: string, parameters = {}) => {
    if (!session?.sessionId) return;
    
    try {
      const response = await genflowClient.executeAction(session.sessionId, {
        action: actionId,
        parameters
      });
      
      setProgress(response.progress);
    } catch (error) {
      console.error('Failed to execute action:', error);
    }
  };
  
  // 切换阶段
  const switchStage = async (stage: string, data = {}) => {
    if (!session?.sessionId) return;
    
    try {
      const response = await genflowClient.switchStage(session.sessionId, {
        stage,
        data
      });
      
      setProgress(response.progress);
      setAvailableActions(response.availableActions);
    } catch (error) {
      console.error('Failed to switch stage:', error);
    }
  };
  
  return (
    <WritingSessionContext.Provider
      value={{
        session,
        progress,
        messages,
        availableActions,
        isConnected,
        sendMessage,
        executeAction,
        switchStage
      }}
    >
      {children}
    </WritingSessionContext.Provider>
  );
};

export const useWritingSession = () => {
  const context = useContext(WritingSessionContext);
  
  if (context === undefined) {
    throw new Error('useWritingSession must be used within a WritingSessionProvider');
  }
  
  return context;
};
```

## 4. 用户界面组件

### 4.1 写作阶段控制器

```tsx
// src/components/StageController.tsx
import React from 'react';
import { useWritingSession } from '../contexts/WritingSessionContext';

export const StageController: React.FC = () => {
  const { progress, availableActions, executeAction } = useWritingSession();
  
  if (!progress) return null;
  
  return (
    <div className="stage-controller">
      <div className="stage-info">
        <h3>当前阶段：{getStageLabel(progress.stage)}</h3>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progress.progress}%` }}
          />
        </div>
        <p className="step-description">{progress.currentStep}</p>
        {progress.estimatedTime && (
          <p className="estimated-time">
            预计完成时间：{formatTime(progress.estimatedTime)}
          </p>
        )}
      </div>
      
      <div className="actions">
        {availableActions.map(action => (
          <button
            key={action.id}
            className={`btn btn-${action.type}`}
            onClick={() => executeAction(action.action)}
            disabled={action.disabled}
            title={action.tooltip}
          >
            {action.text}
          </button>
        ))}
      </div>
    </div>
  );
};

// 工具函数
const getStageLabel = (stage: string) => {
  const labels = {
    topic: '选题阶段',
    research: '研究阶段',
    writing: '写作阶段',
    styling: '风格化阶段',
    review: '审核阶段'
  };
  return labels[stage] || stage;
};

const formatTime = (seconds: number) => {
  if (seconds < 60) return `${seconds}秒`;
  const minutes = Math.floor(seconds / 60);
  return `${minutes}分钟`;
};
```

### 4.2 编辑器集成

```tsx
// src/components/ContentEditor.tsx
import React, { useState, useRef, useEffect } from 'react';
import { useWritingSession } from '../contexts/WritingSessionContext';
import { genflowClient } from '../services/genflow';

export const ContentEditor: React.FC = () => {
  const { session, isConnected } = useWritingSession();
  const [content, setContent] = useState('');
  const [selection, setSelection] = useState({ start: 0, end: 0 });
  const [suggestions, setSuggestions] = useState([]);
  const editorRef = useRef<HTMLTextAreaElement>(null);
  
  // 处理内容变化
  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    setContent(newContent);
    
    const { selectionStart, selectionEnd } = e.target;
    setSelection({ start: selectionStart, end: selectionEnd });
    
    // 发送编辑器状态更新
    if (session?.sessionId && isConnected) {
      genflowClient.sendWebSocketEvent({
        type: 'cursor.update',
        data: {
          position: { start: selectionStart, end: selectionEnd },
          content: newContent
        }
      });
    }
  };
  
  // 获取实时建议
  useEffect(() => {
    if (!session?.sessionId || !isConnected) return;
    
    const debounceTimer = setTimeout(async () => {
      try {
        const result = await genflowClient.getRealtimeSuggestions(session.sessionId, {
          content,
          selection,
          context: {
            before: content.substring(0, selection.start),
            after: content.substring(selection.end)
          }
        });
        
        setSuggestions(result.suggestions);
      } catch (error) {
        console.error('Failed to get suggestions:', error);
      }
    }, 500); // 500ms 防抖
    
    return () => clearTimeout(debounceTimer);
  }, [content, selection, session?.sessionId, isConnected]);
  
  // 应用建议
  const applySuggestion = async (suggestion) => {
    if (!session?.sessionId || !editorRef.current) return;
    
    try {
      const result = await genflowClient.applyEdit(session.sessionId, {
        operations: [
          {
            type: 'replace',
            position: suggestion.position,
            content: suggestion.content
          }
        ]
      });
      
      if (result.applied) {
        // 更新编辑器内容
        const newContent = 
          content.substring(0, suggestion.position.start) +
          suggestion.content +
          content.substring(suggestion.position.end);
          
        setContent(newContent);
        
        // 重新定位光标
        const newPosition = suggestion.position.start + suggestion.content.length;
        editorRef.current.focus();
        editorRef.current.setSelectionRange(newPosition, newPosition);
      }
    } catch (error) {
      console.error('Failed to apply suggestion:', error);
    }
  };
  
  return (
    <div className="content-editor">
      <textarea
        ref={editorRef}
        value={content}
        onChange={handleContentChange}
        className="editor-textarea"
        placeholder="开始写作..."
      />
      
      {suggestions.length > 0 && (
        <div className="suggestions-panel">
          <h4>建议</h4>
          <ul>
            {suggestions.map((suggestion, index) => (
              <li key={index} className={`suggestion-item ${suggestion.type}`}>
                <p>{suggestion.content}</p>
                <button onClick={() => applySuggestion(suggestion)}>
                  应用
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
```

### 4.3 消息对话组件

```tsx
// src/components/ChatInterface.tsx
import React, { useState, useRef, useEffect } from 'react';
import { useWritingSession } from '../contexts/WritingSessionContext';

export const ChatInterface: React.FC = () => {
  const { messages, sendMessage } = useWritingSession();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    sendMessage(input);
    setInput('');
  };
  
  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`message ${message.role}`}
          >
            <div className="message-content">
              {message.type === 'markdown' ? (
                <div className="markdown-content">
                  {/* 使用 Markdown 渲染组件 */}
                </div>
              ) : (
                <p>{message.content}</p>
              )}
            </div>
            <div className="message-meta">
              <time>{new Date(message.timestamp).toLocaleTimeString()}</time>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSubmit} className="message-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入消息..."
        />
        <button type="submit">发送</button>
      </form>
    </div>
  );
};
```

## 5. 主要场景实现

### 5.1 选题发现流程

```tsx
// src/components/TopicDiscovery.tsx
import React, { useState } from 'react';
import { useWritingSession } from '../contexts/WritingSessionContext';

export const TopicDiscovery: React.FC = () => {
  const { executeAction, progress, switchStage } = useWritingSession();
  const [category, setCategory] = useState('技术');
  const [count, setCount] = useState(5);
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  
  const handleDiscoverTopics = async () => {
    await executeAction('discover_topics', { category, count });
    
    // 监听话题结果
    // 通常会通过 WebSocket 接收结果，这里简化处理
    // setTopics(receivedTopics);
  };
  
  const handleSelectTopic = (topic) => {
    setSelectedTopic(topic);
  };
  
  const handleConfirmTopic = async () => {
    if (!selectedTopic) return;
    
    await switchStage('research', { selectedTopicId: selectedTopic.id });
  };
  
  return (
    <div className="topic-discovery">
      <h2>选题发现</h2>
      
      <div className="discovery-controls">
        <div className="form-group">
          <label>领域类别</label>
          <select 
            value={category} 
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="技术">技术</option>
            <option value="商业">商业</option>
            <option value="生活">生活</option>
            <option value="健康">健康</option>
            <option value="教育">教育</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>话题数量</label>
          <input 
            type="number" 
            min="1" 
            max="10" 
            value={count} 
            onChange={(e) => setCount(parseInt(e.target.value))} 
          />
        </div>
        
        <button 
          onClick={handleDiscoverTopics}
          disabled={progress?.status === 'processing'}
        >
          {progress?.status === 'processing' ? '正在发现话题...' : '发现热门话题'}
        </button>
      </div>
      
      {topics.length > 0 && (
        <div className="topics-list">
          <h3>推荐话题</h3>
          
          {topics.map((topic) => (
            <div 
              key={topic.id}
              className={`topic-card ${selectedTopic?.id === topic.id ? 'selected' : ''}`}
              onClick={() => handleSelectTopic(topic)}
            >
              <h4>{topic.title}</h4>
              <div className="topic-meta">
                <span className="trend-score">热度: {topic.trendScore}</span>
                <span className="competition">竞争度: {topic.competition}</span>
              </div>
              <p>{topic.summary}</p>
            </div>
          ))}
          
          <div className="topic-actions">
            <button 
              onClick={handleConfirmTopic}
              disabled={!selectedTopic}
              className="btn btn-primary"
            >
              确认选题并开始研究
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
```

### 5.2 文章写作流程

```tsx
// src/components/ArticleWriting.tsx
import React, { useState } from 'react';
import { useWritingSession } from '../contexts/WritingSessionContext';
import { ContentEditor } from './ContentEditor';

export const ArticleWriting: React.FC = () => {
  const { progress, executeAction, switchStage } = useWritingSession();
  const [outline, setOutline] = useState(null);
  const [activeSection, setActiveSection] = useState(0);
  
  const handleGenerateOutline = async () => {
    await executeAction('generate_outline');
    // 同样通过 WebSocket 接收结果，此处简化
    // setOutline(receivedOutline);
  };
  
  const handleCompleteWriting = async () => {
    await switchStage('styling');
  };
  
  return (
    <div className="article-writing">
      <h2>文章写作</h2>
      
      {!outline ? (
        <div className="outline-generation">
          <p>开始写作前，让我们先生成一个文章大纲</p>
          <button 
            onClick={handleGenerateOutline}
            disabled={progress?.status === 'processing'}
          >
            {progress?.status === 'processing' ? '正在生成大纲...' : '生成文章大纲'}
          </button>
        </div>
      ) : (
        <div className="writing-workspace">
          <div className="outline-sidebar">
            <h3>文章大纲</h3>
            <ul>
              {outline.sections.map((section, index) => (
                <li 
                  key={index}
                  className={activeSection === index ? 'active' : ''}
                  onClick={() => setActiveSection(index)}
                >
                  {section.title}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="content-area">
            <h3>{outline.sections[activeSection]?.title || '开始写作'}</h3>
            <ContentEditor />
            
            <div className="section-navigation">
              <button 
                disabled={activeSection === 0}
                onClick={() => setActiveSection(prev => prev - 1)}
              >
                上一节
              </button>
              
              <button 
                disabled={activeSection === outline.sections.length - 1}
                onClick={() => setActiveSection(prev => prev + 1)}
              >
                下一节
              </button>
            </div>
          </div>
        </div>
      )}
      
      <div className="writing-actions">
        <button 
          onClick={handleCompleteWriting}
          className="btn btn-primary"
        >
          完成写作并进入风格化
        </button>
      </div>
    </div>
  );
};
```

## 6. 错误处理与状态管理

### 6.1 错误处理

```tsx
// src/components/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Error in component:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      
      return (
        <div className="error-boundary">
          <h2>出现错误</h2>
          <p>应用遇到了问题，请刷新页面重试。</p>
          <p className="error-message">{this.state.error?.message}</p>
          <button 
            onClick={() => window.location.reload()}
            className="btn btn-primary"
          >
            刷新页面
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### 6.2 重试机制

```tsx
// src/hooks/useRetry.ts
import { useState, useCallback } from 'react';

interface RetryOptions {
  maxRetries?: number;
  retryDelay?: number;
  onRetry?: (attempt: number, error: any) => void;
}

export function useRetry<T>(
  asyncFn: (...args: any[]) => Promise<T>,
  options: RetryOptions = {}
) {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    onRetry
  } = options;
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);
  const [data, setData] = useState<T | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  
  const execute = useCallback(
    async (...args: any[]) => {
      setLoading(true);
      setError(null);
      
      try {
        const result = await asyncFn(...args);
        setData(result);
        setRetryCount(0);
        setLoading(false);
        return result;
      } catch (err) {
        if (retryCount < maxRetries) {
          setRetryCount(prev => prev + 1);
          onRetry?.(retryCount + 1, err);
          
          // 延迟重试
          await new Promise(resolve => setTimeout(resolve, retryDelay));
          return execute(...args);
        } else {
          setError(err);
          setLoading(false);
          throw err;
        }
      }
    },
    [asyncFn, maxRetries, retryDelay, retryCount, onRetry]
  );
  
  return {
    execute,
    loading,
    error,
    data,
    retryCount
  };
}
```

## 7. 最佳实践

### 7.1 性能优化

1. **状态分片**：将大型状态对象分解为更小的部分，减少不必要的重新渲染
2. **Web Worker**：将复杂计算和数据处理移至 Web Worker
3. **虚拟列表**：对于长列表使用虚拟滚动
4. **懒加载组件**：使用 React.lazy 和 Suspense 按需加载组件
5. **防抖和节流**：对频繁触发的事件使用防抖和节流技术

### 7.2 安全注意事项

1. **数据验证**：在发送到后端之前验证用户输入
2. **XSS 防护**：安全地渲染用户生成的内容
3. **CSRF 保护**：对所有 API 请求添加 CSRF 令牌
4. **敏感数据处理**：谨慎处理和存储用户数据
5. **超时管理**：为长时间运行的请求设置超时，防止资源耗尽

### 7.3 用户体验建议

1. **加载状态**：为所有异步操作提供清晰的加载状态
2. **内联反馈**：直接在用户界面中显示错误和成功消息
3. **渐进式增强**：确保基本功能在没有 WebSocket 的情况下仍然可用
4. **响应式设计**：确保界面在各种屏幕尺寸上都能正常工作
5. **一致的主题**：使用统一的设计系统，保持视觉一致性

## 8. 故障排除

### 8.1 常见问题

1. **WebSocket 连接问题**
   - 检查浏览器支持
   - 验证网络配置
   - 确认 SSL 证书有效

2. **编辑器同步问题**
   - 监控版本冲突
   - 实现自动合并策略
   - 提供冲突解决界面

3. **性能瓶颈**
   - 使用 React DevTools 分析组件渲染
   - 优化状态管理
   - 实现分批数据加载

4. **认证失效**
   - 实现令牌刷新机制
   - 在令牌过期前提醒用户
   - 提供安全的重新认证方法

### 8.2 调试技巧

1. 使用浏览器开发工具的 Network 面板监控 API 请求
2. 启用 WebSocket 调试工具检查消息流
3. 创建专用的调试页面查看会话状态
4. 实现细粒度的客户端日志记录

## 9. 后续升级

### 9.1 即将推出的功能

- 离线支持与同步
- 协作编辑功能
- 高级内容版本控制
- 扩展的模板库
- 媒体资源集成

### 9.2 升级策略

为确保平稳升级，请遵循以下建议：

1. 订阅变更通知以获取 API 更新信息
2. 定期检查客户端库的新版本
3. 在升级之前查阅迁移指南
4. 针对主要版本更新实施逐步迁移计划
5. 维护端到端测试套件以验证每次升级

---

最后更新: 2024-05-15 