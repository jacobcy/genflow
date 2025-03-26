"""
控制AI API接口单元测试

测试控制AI的API接口功能，包括HTTP接口和WebSocket接口。
"""

import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from core.control_ai.api import app

# 创建测试客户端
client = TestClient(app)

# 测试数据
TEST_QUERY = "写一篇关于AI发展的文章"
TEST_SESSION_ID = "test-session-123"

# 模拟数据
MOCK_INTENT_RESULT = {
    "intent_type": "writing_request",
    "description": "用户请求撰写关于AI的文章",
    "confidence": 0.95,
    "entities": {
        "topic": "AI发展",
        "category": "技术",
        "style": "深度分析",
        "length": "中等"
    }
}

MOCK_TASK_PLAN = {
    "task_id": "task-123",
    "task_type": "writing_request",
    "steps": [
        {"team": "topic", "action": "validate", "parameters": {"topic": "AI发展"}},
        {"team": "research", "action": "gather", "parameters": {"topic": "AI发展", "depth": "medium"}},
        {"team": "writing", "action": "draft", "parameters": {"topic": "AI发展", "style": "深度分析"}}
    ],
    "estimated_time": 180
}

MOCK_RESPONSE = {
    "text": "我将帮您创建一篇关于AI发展的深度分析文章，预计需要3分钟完成。",
    "suggestions": [
        {"text": "添加更多关于AGI的内容", "action": "refine"},
        {"text": "使用更通俗的语言", "action": "refine"},
        {"text": "增加篇幅", "action": "refine"}
    ]
}

@pytest.fixture
def mock_control_ai():
    """提供模拟的ControlAI实例"""
    with patch("core.control_ai.api.control_ai") as mock:
        # 设置process_request方法
        process_result = {
            "response": MOCK_RESPONSE["text"],
            "session_id": TEST_SESSION_ID,
            "suggestions": MOCK_RESPONSE["suggestions"],
            "task_id": MOCK_TASK_PLAN["task_id"],
            "task_status": "completed"
        }
        mock.process_request = AsyncMock(return_value=process_result)

        # 模拟会话类
        session_mock = MagicMock()
        session_mock.to_dict.return_value = {
            "session_id": TEST_SESSION_ID,
            "created_at": "2023-07-01T12:00:00",
            "updated_at": "2023-07-01T12:01:00",
            "history_length": 1,
            "task_status": "completed"
        }

        # 设置get_session方法
        mock.get_session = MagicMock(return_value=session_mock)

        # 设置execute_task_step方法
        mock.execute_task_step = AsyncMock(return_value={
            "status": "success",
            "response": "任务已成功执行",
            "result": {"message": "任务执行成功"}
        })

        yield mock


def test_health_endpoint():
    """测试健康检查端点"""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "version" in response.json()["data"]


@pytest.mark.asyncio
async def test_process_nl_request(mock_control_ai):
    """测试自然语言处理端点 - 不带会话ID"""
    # 发送请求
    response = client.post(
        "/api/nl-request",
        json={"query": TEST_QUERY}
    )

    # 验证响应
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "response" in response.json()["data"]
    assert "task_id" in response.json()["data"]

    # 验证控制AI方法调用
    mock_control_ai.process_request.assert_called_once_with(
        user_input=TEST_QUERY,
        session_id=None
    )


@pytest.mark.asyncio
async def test_process_nl_request_with_session(mock_control_ai):
    """测试自然语言处理端点 - 带会话ID"""
    # 发送请求
    response = client.post(
        "/api/nl-request",
        json={"query": TEST_QUERY, "session_id": TEST_SESSION_ID}
    )

    # 验证响应
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # 验证控制AI方法调用
    mock_control_ai.process_request.assert_called_once_with(
        user_input=TEST_QUERY,
        session_id=TEST_SESSION_ID
    )


@pytest.mark.asyncio
async def test_execute_task(mock_control_ai):
    """测试任务执行端点"""
    # 发送请求
    response = client.post(
        "/api/execute-task",
        json={
            "session_id": TEST_SESSION_ID,
            "task_id": MOCK_TASK_PLAN["task_id"],
            "action": "confirm"
        }
    )

    # 验证响应
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "response" in response.json()["data"]

    # 验证控制AI方法调用
    mock_control_ai.execute_task_step.assert_called_once_with(
        session_id=TEST_SESSION_ID,
        task_id=MOCK_TASK_PLAN["task_id"],
        action="confirm"
    )


@pytest.mark.asyncio
async def test_execute_task_cancel(mock_control_ai):
    """测试任务取消端点"""
    # 发送请求
    response = client.post(
        "/api/execute-task",
        json={
            "session_id": TEST_SESSION_ID,
            "task_id": MOCK_TASK_PLAN["task_id"],
            "action": "cancel"
        }
    )

    # 验证响应
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # 验证控制AI方法调用
    mock_control_ai.execute_task_step.assert_called_once_with(
        session_id=TEST_SESSION_ID,
        task_id=MOCK_TASK_PLAN["task_id"],
        action="cancel"
    )


@pytest.mark.asyncio
async def test_get_session_info(mock_control_ai):
    """测试获取会话信息端点"""
    # 发送请求
    response = client.get(f"/api/session/{TEST_SESSION_ID}")

    # 验证响应
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "session_id" in response.json()["data"]

    # 验证控制AI方法调用
    mock_control_ai.get_session.assert_called_once_with(TEST_SESSION_ID)


@pytest.mark.asyncio
async def test_get_session_info_not_found(mock_control_ai):
    """测试获取不存在的会话信息"""
    # 设置get_session返回None
    mock_control_ai.get_session.return_value = None

    # 发送请求
    response = client.get(f"/api/session/non-existent-session")

    # 验证响应
    assert response.status_code == 200
    assert response.json()["status"] == "error"
    assert "找不到会话" in response.json()["message"]


@pytest.mark.asyncio
async def test_execute_task_invalid_action(mock_control_ai):
    """测试无效的任务操作"""
    # 设置execute_task_step抛出异常
    mock_control_ai.execute_task_step.side_effect = ValueError("无效的操作: invalid_action")

    # 发送请求
    response = client.post(
        "/api/execute-task",
        json={
            "session_id": TEST_SESSION_ID,
            "task_id": MOCK_TASK_PLAN["task_id"],
            "action": "invalid_action"
        }
    )

    # 验证响应
    assert response.status_code == 200
    assert response.json()["status"] == "error"
    assert "无效的操作" in response.json()["message"]


# 注: WebSocket测试需要更复杂的设置，一般在集成测试中进行
# 这里只测试了HTTP接口

if __name__ == "__main__":
    pytest.main(["-xvs", "test_api.py"])
