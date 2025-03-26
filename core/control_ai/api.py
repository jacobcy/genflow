"""
控制AI API - 提供与控制AI交互的接口

该模块提供了REST API和WebSocket接口，使外部应用能够与控制AI交互，
处理自然语言请求、执行任务和管理会话。
"""

import json
import logging
import os
import asyncio
import uuid
from typing import Dict, List, Any, Optional, Union

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.control_ai.control_ai import ControlAI

# 配置日志
logger = logging.getLogger(__name__)

# 创建API应用
app = FastAPI(
    title="GenFlow Control AI API",
    description="GenFlow内容生产系统的控制AI接口",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应当限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket连接管理器
class ConnectionManager:
    """WebSocket连接管理器

    管理活动的WebSocket连接。
    """

    def __init__(self):
        """初始化连接管理器"""
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """处理新的WebSocket连接

        Args:
            websocket: WebSocket连接
            client_id: 客户端标识符
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket客户端连接: {client_id}")

    def disconnect(self, client_id: str) -> None:
        """处理WebSocket断开连接

        Args:
            client_id: 客户端标识符
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket客户端断开连接: {client_id}")

    async def send_message(self, client_id: str, message: Dict[str, Any]) -> bool:
        """向指定客户端发送消息

        Args:
            client_id: 客户端标识符
            message: 要发送的消息

        Returns:
            bool: 是否成功发送
        """
        if client_id not in self.active_connections:
            return False

        websocket = self.active_connections[client_id]
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {str(e)}")
            return False

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """向所有连接的客户端广播消息

        Args:
            message: 要广播的消息
        """
        for client_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"向客户端 {client_id} 广播消息失败: {str(e)}")
                self.disconnect(client_id)


# 创建连接管理器
manager = ConnectionManager()

# 请求模型
class NaturalLanguageRequest(BaseModel):
    """自然语言请求模型"""
    query: str = Field(..., description="用户自然语言查询")
    session_id: Optional[str] = Field(None, description="会话ID，如不提供将创建新会话")

class TaskExecutionRequest(BaseModel):
    """任务执行请求模型"""
    session_id: str = Field(..., description="会话ID")
    task_id: str = Field(..., description="任务ID")
    action: str = Field(..., description="任务操作，可选值：confirm, cancel, retry")

# 响应模型
class ApiResponse(BaseModel):
    """API通用响应模型"""
    status: str = Field(..., description="状态：success或error")
    message: Optional[str] = Field(None, description="状态消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")

# 控制AI实例
control_ai = ControlAI()

# 健康检查端点
@app.get("/health", response_model=ApiResponse)
async def health_check():
    """健康检查端点"""
    return {
        "status": "success",
        "message": "控制AI服务正常运行",
        "data": {
            "version": "1.0.0",
            "uptime": "正常"
        }
    }

# 处理自然语言请求
@app.post("/api/nl-request", response_model=ApiResponse)
async def process_nl_request(request: NaturalLanguageRequest):
    """处理自然语言请求

    Args:
        request: 自然语言请求

    Returns:
        ApiResponse: API响应
    """
    try:
        result = await control_ai.process_request(
            user_input=request.query,
            session_id=request.session_id
        )

        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"处理自然语言请求失败: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

# 执行任务操作
@app.post("/api/execute-task", response_model=ApiResponse)
async def execute_task(request: TaskExecutionRequest):
    """执行任务操作

    Args:
        request: 任务执行请求

    Returns:
        ApiResponse: API响应
    """
    try:
        result = await control_ai.execute_task_step(
            session_id=request.session_id,
            task_id=request.task_id,
            action=request.action
        )

        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"执行任务操作失败: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

# 获取会话信息
@app.get("/api/session/{session_id}", response_model=ApiResponse)
async def get_session_info(session_id: str):
    """获取会话信息

    Args:
        session_id: 会话ID

    Returns:
        ApiResponse: API响应
    """
    try:
        session = control_ai.get_session(session_id)

        if not session:
            return {
                "status": "error",
                "message": f"找不到会话: {session_id}"
            }

        return {
            "status": "success",
            "data": session.to_dict()
        }
    except Exception as e:
        logger.error(f"获取会话信息失败: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

# WebSocket接口
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket连接端点

    Args:
        websocket: WebSocket连接
        client_id: 客户端ID
    """
    await manager.connect(websocket, client_id)
    try:
        while True:
            # 接收JSON消息
            data = await websocket.receive_json()

            # 提取必要字段
            request_type = data.get("type")
            session_id = data.get("session_id")

            # 根据请求类型处理
            if request_type == "nl-request":
                # 处理自然语言请求
                query = data.get("query")
                if not query:
                    await websocket.send_json({
                        "type": "error",
                        "message": "缺少必要字段: query"
                    })
                    continue

                try:
                    # 异步处理请求
                    result = await control_ai.process_request(
                        user_input=query,
                        session_id=session_id
                    )

                    # 发送响应
                    await websocket.send_json({
                        "type": "nl-response",
                        "data": result,
                        "request_id": data.get("request_id")
                    })
                except Exception as e:
                    logger.error(f"处理WebSocket自然语言请求失败: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e),
                        "request_id": data.get("request_id")
                    })

            elif request_type == "execute-task":
                # 执行任务操作
                task_id = data.get("task_id")
                action = data.get("action")

                if not all([session_id, task_id, action]):
                    await websocket.send_json({
                        "type": "error",
                        "message": "缺少必要字段: session_id, task_id, action",
                        "request_id": data.get("request_id")
                    })
                    continue

                try:
                    # 执行任务步骤
                    result = await control_ai.execute_task_step(
                        session_id=session_id,
                        task_id=task_id,
                        action=action
                    )

                    # 发送响应
                    await websocket.send_json({
                        "type": "task-result",
                        "data": result,
                        "request_id": data.get("request_id")
                    })
                except Exception as e:
                    logger.error(f"处理WebSocket任务执行请求失败: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e),
                        "request_id": data.get("request_id")
                    })

            elif request_type == "get-session":
                # 获取会话信息
                if not session_id:
                    await websocket.send_json({
                        "type": "error",
                        "message": "缺少必要字段: session_id",
                        "request_id": data.get("request_id")
                    })
                    continue

                try:
                    # 获取会话
                    session = control_ai.get_session(session_id)

                    # 发送响应
                    await websocket.send_json({
                        "type": "session-info",
                        "data": session.to_dict(),
                        "request_id": data.get("request_id")
                    })
                except Exception as e:
                    logger.error(f"处理WebSocket获取会话请求失败: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e),
                        "request_id": data.get("request_id")
                    })

            else:
                # 未知请求类型
                await websocket.send_json({
                    "type": "error",
                    "message": f"未知请求类型: {request_type}",
                    "request_id": data.get("request_id")
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket连接异常: {str(e)}")
        manager.disconnect(client_id)

# 如果直接执行模块则启动服务器
if __name__ == "__main__":
    # 从环境变量获取主机和端口
    host = os.environ.get("API_HOST", "127.0.0.1")
    port = int(os.environ.get("API_PORT", 8000))

    # 启动服务器
    uvicorn.run("core.control_ai.api:app", host=host, port=port, reload=True)
