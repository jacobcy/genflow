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