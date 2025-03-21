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