from crewai import Agent, Task, Crew
from typing import List, Dict

class GenFlowAgent:
    def __init__(self, config: Dict):
        self.agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=config["tools"]
        )
    
    async def handle_message(self, message: str) -> str:
        # 创建任务
        task = Task(
            description=message,
            agent=self.agent
        )
        
        # 执行任务
        result = await task.execute()
        return result