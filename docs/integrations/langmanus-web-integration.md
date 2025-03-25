# LangManus Web UI 集成指南

## 概述

本指南描述了如何将 LangManus Web UI 集成到 GenFlow 项目中，作为与 CrewAI 团队交互的主要界面。不同于 md-editor 的子模块集成方式，我们采用代码迁移和重构的方式来实现深度定制。

## 架构设计

### 1. 组件层次

```
frontend/
├── components/
│   ├── chat/              # 聊天相关组件
│   │   ├── ChatWindow    # 主聊天窗口
│   │   ├── MessageList   # 消息列表
│   │   ├── InputArea     # 输入区域
│   │   └── TeamInfo      # 团队信息展示
│   └── common/           # 通用组件
└── services/
    └── crewai/           # CrewAI 服务适配层
```

### 2. 状态管理

```typescript
// 使用 Zustand 进行状态管理
interface ChatState {
  messages: Message[];
  teamMembers: TeamMember[];
  activeAgent: string | null;
  // ...其他状态
}

const useChatStore = create<ChatState>((set) => ({
  messages: [],
  teamMembers: [],
  activeAgent: null,
  // ...状态更新方法
}));
```

## 实施步骤

### 1. 基础设施搭建

1. 复制必要的依赖：
```bash
# 从 langmanus-web 的 package.json 中复制相关依赖
npm install @headlessui/react @heroicons/react @tailwindcss/typography
```

2. 复制并调整配置文件：
- tailwind.config.js
- next.config.js（根据需要调整）
- 主题配置

### 2. 组件迁移

1. **聊天窗口组件**：
```typescript
// components/chat/ChatWindow.tsx
import { useState } from 'react';
import { Message, TeamMember } from '@/types';

export const ChatWindow = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeAgent, setActiveAgent] = useState<TeamMember | null>(null);

  const handleSend = async (content: string) => {
    // 1. 发送消息到 CrewAI
    const response = await crewAIService.sendMessage({
      content,
      agent: activeAgent?.id
    });
    
    // 2. 更新消息列表
    setMessages(prev => [...prev, response]);
  };

  return (
    <div className="flex flex-col h-full">
      <TeamInfo />
      <MessageList messages={messages} />
      <InputArea onSend={handleSend} />
    </div>
  );
};
```

2. **CrewAI 适配层**：
```typescript
// services/crewai/index.ts
export class CrewAIService {
  constructor(private baseUrl: string) {}

  async sendMessage(params: SendMessageParams) {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      body: JSON.stringify(params)
    });
    
    return await response.json();
  }

  async getTeamMembers(): Promise<TeamMember[]> {
    const response = await fetch(`${this.baseUrl}/api/team`);
    return await response.json();
  }
}
```

### 3. 与 CrewAI 集成

1. **消息格式适配**：
```typescript
// types/index.ts
export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  agentId?: string;
  timestamp: number;
}

// 转换为 CrewAI 消息格式
export const toCrewAIMessage = (message: Message) => ({
  content: message.content,
  agent_id: message.agentId,
  // ...其他必要字段
});
```

2. **团队成员管理**：
```typescript
// components/chat/TeamInfo.tsx
export const TeamInfo = () => {
  const { teamMembers, activeAgent, setActiveAgent } = useChatStore();

  return (
    <div className="flex items-center space-x-2 p-4">
      {teamMembers.map(member => (
        <AgentAvatar
          key={member.id}
          agent={member}
          isActive={member.id === activeAgent?.id}
          onClick={() => setActiveAgent(member)}
        />
      ))}
    </div>
  );
};
```

## 定制与扩展

### 1. 主题定制

```typescript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: colors.blue[600],
        // ... GenFlow 的主题色
      }
    }
  }
};
```

### 2. 功能扩展

1. **工具集成**：
```typescript
interface Tool {
  name: string;
  description: string;
  execute: (params: any) => Promise<any>;
}

const tools: Tool[] = [
  {
    name: 'search',
    description: '搜索相关信息',
    execute: async (params) => {
      // 实现搜索功能
    }
  },
  // ... 其他工具
];
```

2. **状态持久化**：
```typescript
const useChatStore = create(
  persist(
    (set) => ({
      // ... store implementation
    }),
    {
      name: 'chat-storage'
    }
  )
);
```

## 最佳实践

1. **性能优化**：
   - 使用虚拟滚动处理长消息列表
   - 实现消息分页加载
   - 优化图片和资源加载

2. **错误处理**：
   - 实现全局错误边界
   - 添加重试机制
   - 友好的错误提示

3. **可访问性**：
   - 遵循 WCAG 指南
   - 添加键盘导航支持
   - 提供屏幕阅读器支持

## 后续计划

1. **功能迭代**：
   - [ ] 实现文件上传/下载
   - [ ] 添加代码高亮支持
   - [ ] 集成更多 CrewAI 特性

2. **性能优化**：
   - [ ] 添加消息缓存
   - [ ] 优化首次加载性能
   - [ ] 实现离线支持

## 贡献指南

1. 代码风格遵循项目 ESLint 配置
2. 提交信息遵循 Conventional Commits
3. 新功能需要包含测试用例
4. 文档更新需要同步