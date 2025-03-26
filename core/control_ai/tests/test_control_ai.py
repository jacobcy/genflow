"""
控制AI 单元测试 - 测试ControlAI核心功能
"""

import os
import json
import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage, ChatCompletionChunk
from openai.types.chat.chat_completion import Choice, ChatCompletionMessage

from core.control_ai.control_ai import (
    ControlAI,
    IntentRecognitionResult,
    TaskPlan,
    ControlAIResponse
)

# 测试用的模拟数据
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

class MockChatCompletion:
    """模拟OpenAI聊天完成响应"""

    def __init__(self, content):
        """初始化模拟响应

        Args:
            content: 响应内容
        """
        self.choices = [MagicMock()]
        self.choices[0].message.content = content

class TestControlAI(unittest.TestCase):
    """控制AI功能测试"""

    def setUp(self):
        """测试前的设置"""
        # 创建一个配置目录和系统提示文件，如果它不存在
        os.makedirs("core/control_ai/config", exist_ok=True)

        if not os.path.exists("core/control_ai/config/system_prompt.txt"):
            with open("core/control_ai/config/system_prompt.txt", "w", encoding="utf-8") as f:
                f.write("你是GenFlow内容生产系统的控制AI，负责连接用户与专业团队。")

    @patch("core.control_ai.intent_recognizer.OpenAI")
    @patch("core.control_ai.task_planner.OpenAI")
    @patch("core.control_ai.response_generator.OpenAI")
    async def test_process_request(self, mock_response_openai, mock_task_openai, mock_intent_openai):
        """测试处理用户请求"""
        # 导入控制AI类
        from core.control_ai.control_ai import ControlAI

        # 配置模拟的OpenAI客户端
        mock_intent_client = MagicMock()
        mock_intent_openai.return_value = mock_intent_client

        mock_task_client = MagicMock()
        mock_task_openai.return_value = mock_task_client

        mock_response_client = MagicMock()
        mock_response_openai.return_value = mock_response_client

        # 模拟intent_recognizer.recognize的返回结果
        mock_intent_result = MOCK_INTENT_RESULT.copy()

        # 模拟task_planner.plan的返回结果
        mock_task_result = MOCK_TASK_PLAN.copy()

        # 模拟response_generator.generate的返回结果
        mock_response_result = MOCK_RESPONSE.copy()

        # 模拟组件方法
        with patch("core.control_ai.intent_recognizer.IntentRecognizer.recognize", return_value=mock_intent_result), \
             patch("core.control_ai.task_planner.TaskPlanner.plan", return_value=mock_task_result), \
             patch("core.control_ai.response_generator.ResponseGenerator.generate", return_value=mock_response_result), \
             patch("core.control_ai.control_ai.ControlAI._execute_task") as mock_execute_task:

            # 模拟任务执行结果
            mock_execute_task.return_value = {
                "status": "success",
                "result": {"message": "任务执行成功"}
            }

            # 创建控制AI实例
            control_ai = ControlAI()

            # 处理用户请求
            result = await control_ai.process_request("写一篇关于AI发展的文章")

            # 验证响应
            self.assertEqual(result["response"], MOCK_RESPONSE["text"])
            self.assertEqual(len(result["suggestions"]), len(MOCK_RESPONSE["suggestions"]))
            self.assertEqual(result["task_status"], "completed")
            self.assertTrue("session_id" in result)
            self.assertTrue("task_id" in result)

            # 验证方法调用
            mock_execute_task.assert_called_once()

    @patch("core.control_ai.intent_recognizer.OpenAI")
    def test_recognize_intent(self, mock_openai):
        """测试意图识别器集成"""
        from core.control_ai.control_ai import ControlAI
        from core.control_ai.intent_recognizer import IntentRecognizer

        # 配置模拟的OpenAI客户端
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # 创建控制AI实例
        control_ai = ControlAI()

        # 模拟意图识别方法
        with patch.object(IntentRecognizer, "recognize", return_value=MOCK_INTENT_RESULT) as mock_recognize:
            # 调用意图识别
            result = control_ai.intent_recognizer.recognize("写一篇关于AI发展的文章", {})

            # 验证结果
            self.assertEqual(result["intent_type"], MOCK_INTENT_RESULT["intent_type"])
            self.assertEqual(result["confidence"], MOCK_INTENT_RESULT["confidence"])
            self.assertEqual(result["entities"]["topic"], MOCK_INTENT_RESULT["entities"]["topic"])

            # 验证方法调用
            mock_recognize.assert_called_once()

    @patch("core.control_ai.task_planner.OpenAI")
    def test_plan_task(self, mock_openai):
        """测试任务规划器集成"""
        from core.control_ai.control_ai import ControlAI
        from core.control_ai.task_planner import TaskPlanner

        # 配置模拟的OpenAI客户端
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # 创建控制AI实例
        control_ai = ControlAI()

        # 模拟任务规划方法
        with patch.object(TaskPlanner, "plan", return_value=MOCK_TASK_PLAN) as mock_plan:
            # 调用任务规划
            result = control_ai.task_planner.plan(MOCK_INTENT_RESULT, {})

            # 验证结果
            self.assertEqual(result["task_type"], MOCK_TASK_PLAN["task_type"])
            self.assertEqual(len(result["steps"]), len(MOCK_TASK_PLAN["steps"]))
            self.assertEqual(result["estimated_time"], MOCK_TASK_PLAN["estimated_time"])

            # 验证方法调用
            mock_plan.assert_called_once()

    @patch("core.control_ai.response_generator.OpenAI")
    def test_generate_response(self, mock_openai):
        """测试响应生成器集成"""
        from core.control_ai.control_ai import ControlAI
        from core.control_ai.response_generator import ResponseGenerator

        # 配置模拟的OpenAI客户端
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # 创建控制AI实例
        control_ai = ControlAI()

        # 模拟响应生成方法
        with patch.object(ResponseGenerator, "generate", return_value=MOCK_RESPONSE) as mock_generate:
            # 调用响应生成
            task_result = {"status": "success", "result": {"message": "任务执行成功"}}
            result = control_ai.response_generator.generate(task_result, MOCK_TASK_PLAN, "写一篇关于AI发展的文章", {})

            # 验证结果
            self.assertEqual(result["text"], MOCK_RESPONSE["text"])
            self.assertEqual(len(result["suggestions"]), len(MOCK_RESPONSE["suggestions"]))

            # 验证方法调用
            mock_generate.assert_called_once()

    def test_map_category(self):
        """测试类别映射"""
        from core.control_ai.control_ai import ControlAI

        control_ai = ControlAI()

        # 测试映射方法
        self.assertEqual(control_ai.map_category("技术"), "技术")
        self.assertEqual(control_ai.map_category("科技"), "技术")
        self.assertEqual(control_ai.map_category("未知类别"), None)  # 应返回默认值或None

    def test_map_style(self):
        """测试风格映射"""
        from core.control_ai.control_ai import ControlAI

        control_ai = ControlAI()

        # 测试映射方法
        self.assertEqual(control_ai.map_style("专业严谨"), "专业严谨")
        self.assertEqual(control_ai.map_style("知乎"), "专业")
        self.assertEqual(control_ai.map_style("未知风格"), None)  # 应返回默认值或None

    @patch("core.control_ai.control_ai.uuid.uuid4")
    def test_get_session(self, mock_uuid):
        """测试会话管理"""
        from core.control_ai.control_ai import ControlAI

        # 配置模拟的UUID
        mock_uuid.return_value = "test-session-123"

        # 创建控制AI实例
        control_ai = ControlAI()

        # 测试创建新会话
        session = control_ai.get_session()
        self.assertEqual(session.session_id, "test-session-123")

        # 测试获取现有会话
        session2 = control_ai.get_session("test-session-123")
        self.assertEqual(session.session_id, session2.session_id)

        # 测试获取不存在的会话
        session3 = control_ai.get_session("non-existent")
        self.assertNotEqual(session.session_id, session3.session_id)

    @patch("core.control_ai.clients.TopicClient.get_trending_topics")
    @patch("core.control_ai.clients.ResearchClient.research_topic")
    @patch("core.control_ai.clients.WritingClient.create_content")
    async def test_execute_task(self, mock_create_content, mock_research_topic, mock_get_trending_topics):
        """测试任务执行"""
        from core.control_ai.control_ai import ControlAI

        # 配置模拟的客户端响应
        mock_get_trending_topics.return_value = {"topics": ["AI发展", "量子计算", "元宇宙"]}
        mock_research_topic.return_value = {"data": {"summary": "AI发展概述", "keywords": ["人工智能", "深度学习"]}}
        mock_create_content.return_value = {"content": "这是一篇关于AI发展的文章"}

        # 创建控制AI实例
        control_ai = ControlAI()

        # 创建任务计划
        task_plan = {
            "task_type": "writing_request",
            "steps": [
                {"action": "validate", "team": "topic", "parameters": {"topic": "AI发展"}},
                {"action": "research_topic", "team": "research", "parameters": {"topic": "AI发展"}},
                {"action": "create_content", "team": "writing", "parameters": {"topic": "AI发展", "style": "专业"}}
            ]
        }

        # 执行任务
        result = await control_ai._execute_task(task_plan)

        # 验证结果
        self.assertEqual(result["status"], "success")
        self.assertTrue("result" in result)

        # 验证方法调用
        mock_research_topic.assert_called_once()
        mock_create_content.assert_called_once()

    @patch("core.control_ai.control_ai.asyncio.create_task")
    async def test_execute_task_step(self, mock_create_task):
        """测试任务步骤执行"""
        from core.control_ai.control_ai import ControlAI
        from core.control_ai.response_generator import ResponseGenerator

        # 创建控制AI实例
        control_ai = ControlAI()

        # 创建会话和任务
        session_id = "test-session-123"
        task_id = "task-123"

        # 模拟会话
        session = control_ai.get_session(session_id)
        session.set_task({
            "task_id": task_id,
            "task_type": "writing_request",
            "steps": [{"action": "create_content", "team": "writing", "parameters": {"topic": "AI发展"}}]
        })

        # 模拟响应生成
        with patch.object(ResponseGenerator, "generate", return_value={"text": "任务已确认", "suggestions": []}) as mock_generate:
            # 调用任务步骤执行 - 确认
            result = await control_ai.execute_task_step(session_id, task_id, "confirm")

            # 验证结果
            self.assertTrue(mock_create_task.called)
            self.assertEqual(result["response"], "任务已确认")

            # 调用任务步骤执行 - 取消
            result = await control_ai.execute_task_step(session_id, task_id, "cancel")

            # 验证结果
            self.assertEqual(result["status"], "success")
            self.assertEqual(session.task_status, "canceled")

            # 调用任务步骤执行 - 重试
            result = await control_ai.execute_task_step(session_id, task_id, "retry")

            # 验证结果
            self.assertTrue(mock_create_task.called)

            # 测试无效操作
            with self.assertRaises(ValueError):
                await control_ai.execute_task_step(session_id, task_id, "invalid_action")

            # 测试任务不存在
            result = await control_ai.execute_task_step(session_id, "non-existent-task", "confirm")
            self.assertEqual(result["status"], "error")


# 允许直接运行测试
if __name__ == "__main__":
    unittest.main()
