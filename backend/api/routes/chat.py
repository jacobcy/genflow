from fastapi import APIRouter, WebSocket
from crewai import Crew
from typing import List

router = APIRouter()

@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    
    # 初始化 CrewAI 团队
    crew = Crew(
        agents=[
            # 配置团队成员
        ],
        tasks=[
            # 配置初始任务
        ]
    )
    
    try:
        while True:
            message = await websocket.receive_text()
            
            # 通过 CrewAI 处理消息
            response = await crew.process_message(message)
            
            await websocket.send_text(response)
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()